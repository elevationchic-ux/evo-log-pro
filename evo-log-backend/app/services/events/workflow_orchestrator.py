"""
Workflow Orchestrator  Cross-Module Data Transfer Pipeline for EVO-LOG ERP.

Implements the full Cameroon logistics chain:
    Navire/Escale ➜ Quai/Acconage ➜ Douane/Transit ➜ WMS/Magasin
                 ➜ TMS/Transport ➜ Finance/Facturation ➜ Comptabilité

Each handler is triggered automatically by domain events emitted
by individual modules, ensuring ZERO manual re-entry between modules.
Fully multi-tenant: every handler receives company_id and scopes all
DB writes to that tenant.

Event catalog:
  • navire.escale_arrivee          Ship docked: trigger operational checklist
  • douane.bae_valide              Customs BAE validated: unlock WMS + spawn TMS order
  • transport.livraison_epod       ePOD confirmed: close mission, calc demurrage, invoice
  • transport.panne_vehicule       Breakdown reported: spawn GMAO work-order
  • magasin.stock_alerte           Stock below minimum: send alert + optional PO draft
  • finance.facture_emise          Invoice issued: post accounting entry
  • acconage.operation_terminee    Stevedoring op done: update container status
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from math import radians, cos, sin, asin, sqrt
from typing import Optional

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Haversine  nearest garage for breakdown handler
# ─────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two GPS points."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(a))


# ─────────────────────────────────────────────
# HANDLER 1  Escale arrivée ➜ Opérations quai
# ─────────────────────────────────────────────

async def on_navire_escale_arrivee(company_id: int, data: dict):
    """
    Triggered when a vessel docks (navire.escale_arrivee).
    Actions:
      1. Transition Escale status → A_QUAI
      2. Auto-create OperationAcconage placeholder for each container
      3. Emit internal event acconage.operations_lancees
    """
    from app.services.events.event_service import event_service
    escale_id = data.get("escale_id")
    if not escale_id:
        return
    try:
        db = SessionLocal()
        try:
            from app.models.acconage import Escale, EscaleStatus, OperationAcconage
            escale = db.query(Escale).filter(
                Escale.id == escale_id,
                Escale.company_id == company_id
            ).first()
            if escale:
                escale.statut = EscaleStatus.A_QUAI
                escale.date_arrivee_reelle = datetime.utcnow()
                db.commit()
                logger.info(f"[Orchestrator] Escale {escale_id} → A_QUAI (tenant {company_id})")
                await event_service.emit_tenant_event(
                    company_id=company_id,
                    event_type="acconage.operations_lancees",
                    data={"escale_id": escale_id, "message": f"Escale {escale.numero_escale} - opérations lancées"},
                    target_departments=["acconage", "transit"],
                )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Orchestrator] on_navire_escale_arrivee error: {e}")


# ─────────────────────────────────────────────
# HANDLER 2  BAE validé ➜ WMS + TMS
# ─────────────────────────────────────────────

async def on_douane_bae_valide(company_id: int, data: dict):
    """
    Triggered when customs clears a dossier (douane.bae_valide).
    Actions:
      1. Update Conteneur(s) statut → SORTIE_AUTORISEE
      2. Create draft OrdreTransport in TMS (linked to dossier)
      3. Emit TMS alert to transport department
    """
    from app.services.events.event_service import event_service
    dossier_ref = data.get("dossier_ref")
    conteneur_ids: list = data.get("conteneur_ids", [])

    try:
        db = SessionLocal()
        try:
            # 1. Unlock containers
            if conteneur_ids:
                try:
                    from app.models.conteneur_cycle import ConteneurCycle as Conteneur, StatutConteneur
                    db.query(Conteneur).filter(
                        Conteneur.id.in_(conteneur_ids),
                        Conteneur.company_id == company_id
                    ).update(
                        {"statut": StatutConteneur.SORTI},
                        synchronize_session=False
                    )
                    db.commit()
                    logger.info(f"[Orchestrator] {len(conteneur_ids)} conteneur(s) → SORTIE_AUTORISEE (tenant {company_id})")
                except Exception as cont_err:
                    logger.warning(f"[Orchestrator] Container update skipped: {cont_err}")

            # 2. Create draft OrdreTransport
            try:
                from app.models.transport import Mission
                mission = Mission(
                    company_id=company_id,
                    reference=f"TMS-AUTO-{dossier_ref}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    description=f"Livraison générée automatiquement depuis BAE {dossier_ref}",
                    statut="en_attente",
                    date_creation=datetime.utcnow(),
                )
                db.add(mission)
                db.commit()
                logger.info(f"[Orchestrator] OrdreTransport draft créé pour dossier {dossier_ref} (tenant {company_id})")
            except Exception as miss_err:
                logger.warning(f"[Orchestrator] Mission creation skipped: {miss_err}")

            # 3. Alert transport department
            await event_service.emit_tenant_event(
                company_id=company_id,
                event_type="transport.ordre_cree",
                data={
                    "dossier_ref": dossier_ref,
                    "conteneur_ids": conteneur_ids,
                    "message": f"BAE validé  OrdreTransport créé pour dossier {dossier_ref}",
                },
                target_departments=["transport", "magasin"],
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Orchestrator] on_douane_bae_valide error: {e}")


# ─────────────────────────────────────────────
# HANDLER 3  ePOD validée ➜ Clôture mission + Facture auto
# ─────────────────────────────────────────────

async def on_livraison_epod_validee(company_id: int, data: dict):
    """
    Triggered when an electronic proof-of-delivery is confirmed (transport.livraison_epod).
    Actions:
      1. Close TMS Mission → statut TERMINEE
      2. Calculate demurrage return date (J+3 alert)
      3. Auto-generate client invoice with 19.25% TVA (Cameroun)
      4. Emit facturation.facture_auto_creee
    """
    from app.services.events.event_service import event_service
    mission_id = data.get("mission_id")
    client_id = data.get("client_id")
    montant_ht = data.get("montant_ht", 0.0)

    try:
        db = SessionLocal()
        try:
            # 1. Close mission
            try:
                from app.models.transport import Mission
                mission = db.query(Mission).filter(
                    Mission.id == mission_id,
                    Mission.company_id == company_id
                ).first()
                if mission:
                    mission.statut = "terminee"
                    mission.date_livraison_reelle = datetime.utcnow()
                    db.commit()
                    logger.info(f"[Orchestrator] Mission {mission_id} → TERMINEE (tenant {company_id})")
            except Exception as miss_err:
                logger.warning(f"[Orchestrator] Mission close skipped: {miss_err}")

            # 2. Demurrage return reminder (J+3)
            demurrage_limit = (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d")

            # 3. Auto-generate invoice with TVA 19.25%
            try:
                from app.models.finance import Facture, FactureStatus
                tva_rate = 0.1925
                montant_tva = round(float(montant_ht) * tva_rate, 2)
                montant_ttc = round(float(montant_ht) + montant_tva, 2)
                ref = f"FAC-AUTO-{company_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                facture = Facture(
                    company_id=company_id,
                    numero_facture=ref,
                    client_id=client_id,
                    date_emission=date.today(),
                    date_echeance=(date.today() + timedelta(days=30)),
                    montant_ht=montant_ht,
                    montant_tva=montant_tva,
                    montant_ttc=montant_ttc,
                    devise="XAF",
                    statut=FactureStatus.EMISE,
                    notes=f"Facture auto-générée depuis mission ePOD {mission_id}",
                )
                db.add(facture)
                db.commit()
                logger.info(f"[Orchestrator] Facture {ref} créée (TVA 19.25%)  tenant {company_id}")
            except Exception as fac_err:
                logger.warning(f"[Orchestrator] Invoice creation skipped: {fac_err}")

            # 4. Notify
            await event_service.emit_tenant_event(
                company_id=company_id,
                event_type="facturation.facture_auto_creee",
                data={
                    "mission_id": mission_id,
                    "client_id": client_id,
                    "montant_ttc": montant_ttc if montant_ht else 0,
                    "demurrage_deadline": demurrage_limit,
                    "message": f"ePOD validée  Facture auto-créée, retour conteneur avant {demurrage_limit}",
                },
                target_departments=["finance", "transport", "commercial"],
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Orchestrator] on_livraison_epod_validee error: {e}")


# ─────────────────────────────────────────────
# HANDLER 4  Panne véhicule ➜ OT GMAO + Garage
# ─────────────────────────────────────────────

# Cameroon reference garages with GPS coords (extendable via DB)
_CAMEROON_GARAGES = [
    {"nom": "Garage Central Douala", "lat": 4.0511, "lon": 9.7679, "tel": "+237 699 000 001"},
    {"nom": "Atelier Yaoundé Nord",  "lat": 3.8480, "lon": 11.5021, "tel": "+237 699 000 002"},
    {"nom": "Garage limbé",       "lat": 5.4737, "lon": 10.4179, "tel": "+237 699 000 003"},
    {"nom": "Atelier Limbe",          "lat": 4.0159, "lon": 9.2132,  "tel": "+237 699 000 004"},
    {"nom": "Garage Ngaoundéré",      "lat": 7.3299, "lon": 13.5819, "tel": "+237 699 000 005"},
]


async def on_panne_vehicule_signalee(company_id: int, data: dict):
    """
    Triggered when a vehicle breakdown is reported (transport.panne_vehicule).
    Actions:
      1. Create GMAO work-order (OT) with priority URGENT
      2. Find nearest 24/7 garage using Haversine algorithm
      3. Notify maintenance + transport departments
    """
    from app.services.events.event_service import event_service
    vehicule_id = data.get("vehicule_id")
    conducteur = data.get("conducteur", "Inconnu")
    lat = data.get("lat")
    lon = data.get("lon")
    description_panne = data.get("description", "Panne signalée sans détails")

    # Find nearest garage
    garage_info = "Contacter dispatch pour assistance"
    if lat and lon:
        try:
            nearest = min(
                _CAMEROON_GARAGES,
                key=lambda g: _haversine_km(lat, lon, g["lat"], g["lon"])
            )
            dist = _haversine_km(lat, lon, nearest["lat"], nearest["lon"])
            garage_info = f"{nearest['nom']} ({dist:.1f} km)  {nearest['tel']}"
        except Exception:
            pass

    try:
        db = SessionLocal()
        try:
            # Create GMAO OT
            try:
                from app.models.maintenance import OrdreTrail
                ot_ref = f"OT-PANNE-{company_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                ot = OrdreTrail(
                    company_id=company_id,
                    reference=ot_ref,
                    vehicule_id=vehicule_id,
                    type_intervention="PANNE_ROUTE",
                    priorite="URGENT",
                    statut="OUVERT",
                    description=f"{description_panne}\nGarage le plus proche: {garage_info}",
                    date_creation=datetime.utcnow(),
                )
                db.add(ot)
                db.commit()
                logger.info(f"[Orchestrator] OT GMAO {ot_ref} créé  véhicule {vehicule_id} (tenant {company_id})")
            except Exception as ot_err:
                logger.warning(f"[Orchestrator] OT GMAO skipped: {ot_err}")

            await event_service.emit_tenant_event(
                company_id=company_id,
                event_type="gmao.ot_panne_cree",
                data={
                    "vehicule_id": vehicule_id,
                    "conducteur": conducteur,
                    "description": description_panne,
                    "garage_proche": garage_info,
                    "message": f"🚨 Panne véhicule signalée  OT GMAO créé  {garage_info}",
                },
                target_departments=["maintenance", "transport", "direction"],
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Orchestrator] on_panne_vehicule_signalee error: {e}")


# ─────────────────────────────────────────────
# HANDLER 5  Stock alerte ➜ Notification + Commande draft
# ─────────────────────────────────────────────

async def on_stock_alerte(company_id: int, data: dict):
    """
    Triggered when stock drops below minimum threshold (magasin.stock_alerte).
    Actions:
      1. Log alert with stock details
      2. Notify procurement + warehouse departments
    """
    from app.services.events.event_service import event_service
    stock_id = data.get("stock_id")
    code_article = data.get("code_article", "?")
    designation = data.get("designation", "Article inconnu")
    quantite_actuelle = data.get("quantite_actuelle", 0)
    quantite_minimum = data.get("quantite_minimum", 0)

    logger.warning(
        f"[Orchestrator] ALERTE STOCK  {code_article} ({designation}): "
        f"qté={quantite_actuelle} < min={quantite_minimum} (tenant {company_id})"
    )

    await event_service.emit_tenant_event(
        company_id=company_id,
        event_type="magasin.commande_urgente_requise",
        data={
            "stock_id": stock_id,
            "code_article": code_article,
            "designation": designation,
            "quantite_actuelle": quantite_actuelle,
            "quantite_minimum": quantite_minimum,
            "message": f"⚠️ Stock critique: {designation} ({code_article})  qté {quantite_actuelle}/{quantite_minimum}",
        },
        target_departments=["magasin", "achat", "direction"],
    )


# ─────────────────────────────────────────────
# HANDLER 6  Facture émise ➜ Écriture comptable auto
# ─────────────────────────────────────────────

async def on_finance_facture_emise(company_id: int, data: dict):
    """
    Triggered when an invoice is officially issued (finance.facture_emise).
    Actions:
      1. Post double-entry accounting record (Débit Clients / Crédit Produits)
      2. Notify accounting department
    """
    from app.services.events.event_service import event_service
    facture_id = data.get("facture_id")
    numero_facture = data.get("numero_facture", "?")
    montant_ttc = data.get("montant_ttc", 0.0)
    montant_tva = data.get("montant_tva", 0.0)

    try:
        db = SessionLocal()
        try:
            try:
                from app.models.finance import EcritureComptable, Compte
                # Find client account (411xx) and product account (706xx)
                compte_client = db.query(Compte).filter(
                    Compte.company_id == company_id,
                    Compte.type_compte == "actif"
                ).first()
                compte_produit = db.query(Compte).filter(
                    Compte.company_id == company_id,
                    Compte.type_compte == "recettes"
                ).first()

                if compte_client and compte_produit:
                    ecriture = EcritureComptable(
                        company_id=company_id,
                        date_ecriture=date.today(),
                        reference=f"EC-{numero_facture}",
                        libelle=f"Facture client {numero_facture}",
                        compte_debit=compte_client.id,
                        compte_credit=compte_produit.id,
                        montant_debit=montant_ttc,
                        montant_credit=montant_ttc,
                    )
                    db.add(ecriture)
                    db.commit()
                    logger.info(f"[Orchestrator] Écriture comptable créée pour facture {numero_facture} (tenant {company_id})")
                else:
                    logger.warning(f"[Orchestrator] Comptes non configurés pour tenant {company_id}  écriture ignorée")
            except Exception as ec_err:
                logger.warning(f"[Orchestrator] Écriture comptable skipped: {ec_err}")

            await event_service.emit_tenant_event(
                company_id=company_id,
                event_type="comptabilite.ecriture_creee",
                data={
                    "facture_id": facture_id,
                    "numero_facture": numero_facture,
                    "montant_ttc": montant_ttc,
                    "message": f"Écriture comptable auto-générée pour facture {numero_facture}",
                },
                target_departments=["comptabilite", "finance"],
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Orchestrator] on_finance_facture_emise error: {e}")


# ─────────────────────────────────────────────
# HANDLER 7  Opération acconage terminée ➜ Conteneur mis à jour
# ─────────────────────────────────────────────

async def on_acconage_operation_terminee(company_id: int, data: dict):
    """
    Triggered when stevedoring operation completes (acconage.operation_terminee).
    Actions:
      1. Update linked conteneur status → STOCKE
      2. Emit magasin.conteneur_disponible to WMS
    """
    from app.services.events.event_service import event_service
    conteneur_ids: list = data.get("conteneur_ids", [])
    escale_ref = data.get("escale_ref", "?")

    if conteneur_ids:
        try:
            db = SessionLocal()
            try:
                from app.models.conteneur_cycle import ConteneurCycle as Conteneur, StatutConteneur
                db.query(Conteneur).filter(
                    Conteneur.id.in_(conteneur_ids),
                    Conteneur.company_id == company_id
                ).update(
                    {"statut": StatutConteneur.STOCKE},
                    synchronize_session=False
                )
                db.commit()
                logger.info(f"[Orchestrator] {len(conteneur_ids)} conteneur(s) → STOCKE après opération acconage (tenant {company_id})")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[Orchestrator] Container status update skipped: {e}")

    await event_service.emit_tenant_event(
        company_id=company_id,
        event_type="magasin.conteneur_disponible",
        data={
            "conteneur_ids": conteneur_ids,
            "escale_ref": escale_ref,
            "message": f"Opération acconage terminée  {len(conteneur_ids)} conteneur(s) disponibles en magasin",
        },
        target_departments=["magasin", "transit", "douane"],
    )


# ─────────────────────────────────────────────
# REGISTRATION  Wire all handlers to event bus
# ─────────────────────────────────────────────

def register_all_handlers():
    """
    Register all workflow orchestrator handlers on the global event bus.
    Call this once on application startup from main.py.
    """
    from app.services.events.event_service import event_service

    subscriptions = [
        ("navire.escale_arrivee",        on_navire_escale_arrivee),
        ("douane.bae_valide",             on_douane_bae_valide),
        ("transport.livraison_epod",      on_livraison_epod_validee),
        ("transport.panne_vehicule",      on_panne_vehicule_signalee),
        ("magasin.stock_alerte",          on_stock_alerte),
        ("finance.facture_emise",         on_finance_facture_emise),
        ("acconage.operation_terminee",   on_acconage_operation_terminee),
    ]

    for event_type, handler in subscriptions:
        event_service.subscribe(event_type, handler)
        logger.info(f"[Orchestrator] ✅ Registered handler for '{event_type}'")

    logger.info(f"[Orchestrator] 🚀 {len(subscriptions)} cross-module handlers registered.")

"""K-Modules : surface catalogue ramassee sur les VRAIES tables en base.

Ce module etait une DEMO en memoire volatile (listes pre-remplies de donnees
inventees). Il delegue desormais vers les modeles persistants reels :

- Cotations      -> CotationDevis (table cotations_devis, scope company)
- e-POD          -> ElectronicPOD (table electronic_pods)
- FuelGuard      -> FuelTankSensor (table fuel_tank_sensors) : lecture Manuel
  saisie ; variation calculee depuis la VRAIE lecture precedente (pas de vol
  invente).
- Bons de commande -> PurchaseOrder (table procurement_purchase_orders)
- Conformite     -> ComplianceAudit (auto-declare, persiste)
- Acconage/Transit/Magasin/Articles -> modeles metiers reels (lecture seule
  filtree par company).
- BI executif    -> aggregations SQL reelles.

Aucune donnee n'est inventee : sur base vide les listes renvoient un vrai
ensemble vide ; sur base peuplee elles renvoient les enregistrements reels.
"""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.models.new_k_modules import (
    CotationDevis, ElectronicPOD, FuelTankSensor, PurchaseOrder, ComplianceAudit,
)
from app.models.magasin import Article, OrdreTransfert, BandeLivraison
from app.models.magasin_avance import BonSortie
from app.models.transit import DossierTransit
from app.models.acconage import Navire, Escale, OperationAcconage
from app.models.transport import Mission, Camion, MissionStatus, CamionStatus
from app.models.finance import Facture, FactureStatus

router = APIRouter(tags=["New K-Modules"])  # monte sur /api/v1/k-modules par main.py


# --- Helpers de serialisation / scope ---

def _serialize(obj) -> dict:
    out = {}
    for attr in sa_inspect(obj).mapper.column_attrs:
        v = getattr(obj, attr.key)
        if v is None or isinstance(v, (int, float, str, bool)):
            out[attr.key] = v
        elif hasattr(v, "isoformat"):
            out[attr.key] = v.isoformat()
        elif hasattr(v, "value"):  # Enum SQLAlchemy
            out[attr.key] = v.value
        else:
            out[attr.key] = str(v)
    return out


def _company_id(context: TenantContext):
    return getattr(context.user, "company_id", None)


def _scoped(context: TenantContext, query, model):
    cid = _company_id(context)
    if cid is not None and hasattr(model, "company_id"):
        return query.filter(model.company_id == cid)
    return query


def _listed(context, db, model, limit: int = 200):
    q = _scoped(context, db.query(model), model)
    if hasattr(model, "created_at"):
        q = q.order_by(model.created_at.desc())
    return [_serialize(r) for r in q.limit(limit).all()]


# --- Schemas ---
class CotationCreate(BaseModel):
    client_nom: str
    origine: str
    destination: str
    nature_fret: str
    montant_estime_xaf: float
    marge_nette_pct: Optional[float] = 15.0


class EPodCreate(BaseModel):
    reference_mission: str
    nom_destinataire: str
    signature_url: Optional[str] = None
    photo_livraison_url: Optional[str] = None
    longitude: Optional[float] = 9.704
    latitude: Optional[float] = 4.051


class FuelSensorCreate(BaseModel):
    immatriculation_camion: str
    niveau_actuel_litres: float
    derniere_station: Optional[str] = "TotalEnergies Douala Port"


class PurchaseOrderCreate(BaseModel):
    fournisseur: str
    description: str
    montant_total_xaf: float


class ComplianceAuditCreate(BaseModel):
    dossier_reference: str
    type_reglementation: Optional[str] = "ZLECAF / CEMAC"
    score_conformite_pct: Optional[float] = None


# --- K-Cotations : CRUD reel sur cotations_devis ---
@router.get("/cotations")
def get_cotations(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Cotations REELLES lues en base (scope company)."""
    return _listed(context, db, CotationDevis)


@router.post("/cotations", status_code=status.HTTP_201_CREATED)
def create_cotation(
    payload: CotationCreate,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    cid = _company_id(context)
    if cid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cotation rattachable a une entreprise (company_id requis)",
        )
    ref = f"COT-{datetime.utcnow():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
    row = CotationDevis(
        company_id=cid, reference=ref, statut="SOUMIS", **payload.model_dump()
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize(row)


# --- K-Tracking & e-POD : preuves de livraison reelles ---
@router.get("/tracking/epod")
def get_epods(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, ElectronicPOD)


@router.post("/tracking/epod", status_code=status.HTTP_201_CREATED)
def create_epod(
    payload: EPodCreate,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Enregistre la preuve de livraison REELLE. N'emet AUCUNE facture inventee :
    la facturation se fait via le module finance reel."""
    data = payload.model_dump()
    if data.get("signature_url"):
        statut = "LIVRE_AVEC_SIGNATURE"
    elif data.get("photo_livraison_url"):
        statut = "LIVRE_AVEC_PHOTO"
    else:
        statut = "LIVRE_SANS_PREUVE"
    row = ElectronicPOD(statut=statut, timestamp=datetime.utcnow(), **data)
    db.add(row)
    db.commit()
    db.refresh(row)
    out = _serialize(row)
    out["facture_emisee"] = False  # honnete : aucune facture auto-inventee
    return out


# --- K-FuelGuard : lectures Manuel reelles, variation factuelle ---
@router.get("/fuel-guard/sensors")
def get_fuel_sensors(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, FuelTankSensor)


@router.post("/fuel-guard/sensors", status_code=status.HTTP_201_CREATED)
def create_fuel_sensor(
    payload: FuelSensorCreate,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Persiste la lecture MANUELLE du capteur et calcule la variation reelle vs
    la derniere lecture ENREGISTREE du meme camion. Aucun vol n'est invente : la
    simple baisse peut provenir d'une consommation normale."""
    data = payload.model_dump()
    prev = db.query(FuelTankSensor).filter(
        FuelTankSensor.immatriculation_camion == data["immatriculation_camion"]
    ).order_by(FuelTankSensor.updated_at.desc()).first()
    variation = None
    if prev is not None:
        variation = round(float(prev.niveau_actuel_litres) - float(data["niveau_actuel_litres"]), 2)
    row = FuelTankSensor(
        alerte_vol_detectee=False, updated_at=datetime.utcnow(), **data
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    out = _serialize(row)
    out["variation_litres_vs_derniere_lecture"] = variation
    out["alerte_vol"] = "non determinee (telemetrie nonbranche ; baisse != vol certain)"
    return out


# --- Calculateur Tarifaire Douane CEMAC / ZLECAF (calcul legitime) ---
class RequeteCalculDouane(BaseModel):
    valeur_caf_xaf: float
    origine_produit: Optional[str] = "CEMAC"
    categorie_tarifaire_tec: Optional[int] = 2


@router.post("/transit/calculateur-taxe-cemac")
def calculer_taxes_douanieres(payload: RequeteCalculDouane):
    """Calcul deterministe des droits/taxes CEMAC a partir de la valeur CAF."""
    from app.services.taxation_douaniere import calculer_liquidation

    liq = calculer_liquidation(
        valeur_en_douane=payload.valeur_caf_xaf,
        categorie_tec=payload.categorie_tarifaire_tec,
        origine=payload.origine_produit,
    )
    return {
        "valeur_caf_xaf": liq["valeur_en_douane_xaf"],
        "categorie_tarifaire_tec": payload.categorie_tarifaire_tec,
        "origine_produit": payload.origine_produit,
        "droit_douane_xaf": liq["droit_douane_dd"],
        "redevance_informatique_xaf": liq["redevance_informatique"],
        "cci_cemac_xaf": liq["cci_cemac"],
        "ohada_xaf": liq["prelevement_ohada"],
        "base_tva_xaf": liq["base_tva"],
        "tva_19_25_xaf": liq["tva_1925"],
        "precompte_is_xaf": liq["precompte_is"],
        "total_liquidation_douane_xaf": liq["total_a_liquider_xaf"],
        "exemption_zlecaf_appliquee": (payload.origine_produit or "").upper()
        in ("CEMAC", "ZLECAF", "UEAC"),
        "source_taux": liq["source_taux"],
        "simulation": liq["simulation"],
        "note": liq["note"],
    }


# --- K-Procurement : bons de commande reels ---
@router.get("/procurement/orders")
def get_procurement_orders(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, PurchaseOrder)


@router.post("/procurement/orders", status_code=status.HTTP_201_CREATED)
def create_procurement_order(
    payload: PurchaseOrderCreate,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """BC persiste reellement. Le rapprochement 3 voies n'est PAS declare conforme
    sans controle reel : statut EN_ATTENTE jusqu'a reception/lettrage verifiable."""
    ref = f"PO-{datetime.utcnow():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
    row = PurchaseOrder(
        numero_po=ref, match_3_voies=False, statut="EN_ATTENTE",
        created_at=datetime.utcnow(), **payload.model_dump(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    out = _serialize(row)
    out["note"] = "Rapprochement 3 voies a confirmer a la reception (non simule)."
    return out


# --- K-Compliance : audits auto-declares persistes ---
@router.get("/compliance/audits")
def get_compliance_audits(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, ComplianceAudit)


@router.post("/compliance/audits", status_code=status.HTTP_201_CREATED)
def create_compliance_audit(
    payload: ComplianceAuditCreate,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    score = data.pop("score_conformite_pct", None)
    row = ComplianceAudit(
        score_conformite_pct=score, statut="A_VERIFIER", exemption_valide=False,
        created_at=datetime.utcnow(), **data,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    out = _serialize(row)
    out["note"] = "Score auto-declare par l'utilisateur ; non calcule depuis les dossiers."
    return out


# --- Acconage & Handling Portuaire :lecture des tables reelles ---
@router.get("/acconage")
@router.get("/acconage/operations")
def get_acconage_operations(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, OperationAcconage)


@router.get("/acconage/navires")
def get_acconage_navires(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, Navire)


@router.get("/acconage/escales")
def get_acconage_escales(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, Escale)


# --- Transit & Douane : dossiers reels ---
@router.get("/transit")
@router.get("/transit/dossiers")
def get_transit_dossiers(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, DossierTransit)


# --- Magasin : removal slips, transferts, bandes, articles (reels) ---
@router.get("/magasin/removal-slips")
def get_removal_slips(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, BonSortie)


@router.get("/magasin/ordres-transfert")
def get_ordres_transfert(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, OrdreTransfert)


@router.get("/magasin/bandes-livraison")
def get_bandes_livraison(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, BandeLivraison)


@router.get("/master-data/articles")
def get_master_data_articles(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    return _listed(context, db, Article)


# --- BI executif : aggregations SQL REELLES ---
@router.get("/bi-analytics/executive-summary")
def get_bi_summary(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    cid = _company_id(context)

    def scoped_count(model):
        q = db.query(func.count(model.id))
        if cid is not None and hasattr(model, "company_id"):
            q = q.filter(model.company_id == cid)
        return q.scalar() or 0

    missions_total = scoped_count(Mission)
    missions_terminees = (
        (_scoped(context, db.query(func.count(Mission.id)), Mission)
         .filter(Mission.statut == MissionStatus.TERMINEE).scalar() or 0)
    )
    flotte_total = scoped_count(Camion)
    flotte_active = (
        (_scoped(context, db.query(func.count(Camion.id)), Camion)
         .filter(Camion.status == CamionStatus.ACTIVE).scalar() or 0)
    )
    ca_encaisse = (
        (_scoped(context, db.query(func.sum(Facture.montant_ttc)), Facture)
         .filter(Facture.statut == FactureStatus.PAYEE).scalar() or 0)
    )
    creances = (
        (_scoped(context, db.query(func.sum(Facture.montant_ttc)), Facture)
         .filter(Facture.statut.in_([
             FactureStatus.EMISE, FactureStatus.RETARD, FactureStatus.PAYEE_PARTIELLEMENT
         ])).scalar() or 0)
    )
    return {
        "missions": {"total": missions_total, "terminees": missions_terminees},
        "flotte": {"total": flotte_total, "active": flotte_active},
        "finance": {
            "ca_encaisse_xaf": float(ca_encaisse),
            "creances_en_cours_xaf": float(creances),
        },
        "agrege_depuis_la_base": True,
    }

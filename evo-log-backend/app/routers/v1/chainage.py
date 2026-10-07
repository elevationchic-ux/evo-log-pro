"""
Chaîne cross-module (interconnexion hiérarchique).

Ce routeur n'est PAS un nouveau module métier : c'est une couche de lecture et
d'orchestration au-dessus des modules existants. Il expose la hiérarchie réelle
déjà présente en base (clés étrangères), sans jamais inventer de donnée :

    Aménagement portuaire (terminal/quai)
        ➜ Navire ➜ Escale ➜ Opérations d'acconage
        ➜ Conteneurs (cycles) ➜ Transit/Douane (via n° connaissement)
        ➜ Transport (missions) ➜ Facturation (OHADA) ➜ Comptabilité

Chaque module reste indépendant (son propre CRUD, son propre routeur) ; ici on
les relie par le graphe de dépendances et par le bus d'événements. Un stade
n'apparaît dans la réponse que si des enregistrements réellement rattachés
existent en base — sinon le stade est simplement absent (honnêteté, zéro mock).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(tags=["Chaîne cross-module"])


# ─────────────────────────────────────────────────────────────
# Graphe de dépendances (métadonnées descriptives, pas de DB)
# ─────────────────────────────────────────────────────────────

# Événements du catalogue de l'orchestrateur : c'est le vocabulaire officiel de
# l'interconnexion. /propager n'accepte QUE ces types (whitelist), pour qu'aucun
# appel ne déclenche une écriture croquée dans un module non concerné.
CHAIN_EVENTS = [
    "navire.escale_arrivee",
    "acconage.operation_terminee",
    "douane.bae_valide",
    "transport.livraison_epod",
    "transport.panne_vehicule",
    "magasin.stock_alerte",
    "finance.facture_emise",
]

# Hiérarchie des moyens de transport interconnectés (vague 4 incluse).
TRANSPORT_MODES = [
    {"module": "transport", "slug": "transport", "libelle": "Routier (TMS)"},
    {"module": "acconage", "slug": "acconage", "libelle": "Acconage / manutention portuaire"},
    {"module": "transport-ferroviaire", "slug": "transport-ferroviaire", "libelle": "Ferroviaire (rail)"},
    {"module": "transport-aerien", "slug": "transport-aerien", "libelle": "Aérien (fret air)"},
    {"module": "transport-fluvial", "slug": "transport-fluvial", "libelle": "Fluvial / lacustre"},
    {"module": "logistique-3pl", "slug": "logistique-3pl", "libelle": "Logistique contractuelle (3PL)"},
]


def _modules_graph() -> dict:
    """Graphe statique des modules et de leurs liens, reflet de l'orchestrateur.

    ``de`` / ``vers`` décrivent la propagation d'un événement cross-module ;
    ``evenement`` est le type émis sur le bus. Ce n'est pas une donnée métier
    simulée : c'est la description fidèle du câblage enregistré par
    workflow_orchestrator.register_all_handlers().
    """
    return {
        "chaine": [
            "amenagement_portuaire", "navire", "escale", "acconage",
            "conteneurs", "transit_douane", "transport", "facturation", "comptabilite",
        ],
        "transitions": [
            {"de": "navire", "vers": "acconage", "evenement": "navire.escale_arrivee"},
            {"de": "acconage", "vers": "conteneurs", "evenement": "acconage.operation_terminee"},
            {"de": "transit_douane", "vers": "transport", "evenement": "douane.bae_valide"},
            {"de": "transport", "vers": "facturation", "evenement": "transport.livraison_epod"},
            {"de": "transport", "vers": "comptabilite", "evenement": "finance.facture_emise"},
            {"de": "conteneurs", "vers": "magasin", "evenement": "magasin.stock_alerte"},
        ],
        "modes_transport": TRANSPORT_MODES,
        "evenements_catalogue": CHAIN_EVENTS,
    }


@router.get("/graphe", summary="Graphe hiérarchique des modules interconnectés")
def graphe(current_user: User = Depends(get_current_user)):
    """Carte des modules reliés et des événements qui les connectent.

    Illustre le double impératif : chaque module est indépendant (CRUD propre)
    tout en étant interconnecté via ces transitions. Les modes de transport de
    la vague 4 (ferroviaire, aérien, fluvial, 3PL) y figurent au même titre que
    le maritime et l'aménagement portuaire.
    """
    return _modules_graph()


# ─────────────────────────────────────────────────────────────
# Trace réelle d'une escale à travers la hiérarchie
# ─────────────────────────────────────────────────────────────

@router.get("/escale/{escale_id}", summary="Tracer la chaîne cross-module d'une escale")
def tracer_escale(
    escale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remonte et redescend la hiérarchie à partir d'une escale.

    Chaque stade n'est renvoyé que s'il existe des enregistrements réellement
    rattachés (FK). Aucune donnée n'est complétée : un stade absent signifie
    simplement qu'aucun objet n'y est relié pour cette escale.
    """
    from app.models.acconage import Escale, Navire, OperationAcconage
    from app.models.conteneur_cycle import ConteneurCycle, CycleConteneur
    from app.models.finance_ohada import FactureNew

    company_id = getattr(current_user, "company_id", None)

    q = db.query(Escale).filter(Escale.id == escale_id)
    if company_id is not None:
        q = q.filter(Escale.company_id == company_id)
    escale = q.first()
    if not escale:
        raise HTTPException(status_code=404, detail="Escale introuvable")

    stages = {"escale_id": escale.id, "numero_escale": escale.numero_escale}

    # 1. Navire
    if escale.navire_id:
        navire = db.query(Navire).filter(Navire.id == escale.navire_id).first()
        if navire:
            stages["navire"] = {
                "id": navire.id, "nom": navire.nom, "imo": navire.imo,
                "type_navire": navire.type_navire, "pavillon": navire.pavillon,
            }

    # 2. Aménagement portuaire (terminaux desservis par les cycles du navire)
    try:
        from app.models.port_cameroun import TerminalPortuaire
        terminal_ids = {
            c.terminal_id for c in db.query(CycleConteneur).filter(
                CycleConteneur.navire_id == escale.navire_id,
                CycleConteneur.terminal_id.isnot(None),
            ).all() if c.terminal_id
        }
        if terminal_ids:
            terminaux = db.query(TerminalPortuaire).filter(
                TerminalPortuaire.id.in_(terminal_ids)
            ).all()
            stages["amenagement_portuaire"] = [
                {"id": t.id, "nom": getattr(t, "nom", None) or getattr(t, "nom_terminal", None)}
                for t in terminaux
            ]
    except Exception:
        # aménagement non rattaché : le stade est simplement absent.
        pass

    # 3. Opérations d'acconage
    ops = db.query(OperationAcconage).filter(
        OperationAcconage.escale_id == escale.id
    ).all()
    if ops:
        stages["acconage"] = [
            {"id": o.id, "reference": o.reference, "type_operation": o.type_operation,
             "statut": o.statut}
            for o in ops
        ]

    # 4. Conteneurs (via les cycles du navire de l'escale)
    conteneur_ids = []
    if escale.navire_id:
        rows = db.query(CycleConteneur.conteneur_id).filter(
            CycleConteneur.navire_id == escale.navire_id
        ).distinct().limit(200).all()
        conteneur_ids = [r[0] for r in rows if r[0]]
    if conteneur_ids:
        conteneurs = db.query(ConteneurCycle).filter(
            ConteneurCycle.id.in_(conteneur_ids)
        ).all()
        stages["conteneurs"] = [
            {"id": c.id, "numero": c.numero,
             "type_conteneur": (c.type_conteneur.value if hasattr(c.type_conteneur, "value") else str(c.type_conteneur))}
            for c in conteneurs
        ]

    # 5. Factures OHADA rattachées (escale directe ou l'un des conteneurs)
    fcond = [FactureNew.escale_id == escale.id]
    if conteneur_ids:
        fcond.append(FactureNew.conteneur_id.in_(conteneur_ids))
    factures = db.query(FactureNew).filter(
        FactureNew.numero_facture.isnot(None)
    ).filter(
        (FactureNew.escale_id == escale.id) if not conteneur_ids
        else ((FactureNew.escale_id == escale.id) | (FactureNew.conteneur_id.in_(conteneur_ids)))
    ).all()
    if factures:
        stages["facturation"] = [
            {"id": f.id, "numero_facture": f.numero_facture, "statut": f.statut,
             "montant_ttc": float(f.montant_ttc) if f.montant_ttc is not None else None}
            for f in factures
        ]

    return stages


# ─────────────────────────────────────────────────────────────
# Trace réelle d'une mission de transport
# ─────────────────────────────────────────────────────────────

@router.get("/mission/{mission_id}", summary="Tracer la chaîne cross-module d'une mission")
def tracer_mission(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Relie une mission TMS à son conteneur source, son client, son connaissement
    (Bon de Livraison document) et ses factures — via les FK réelles uniquement.
    """
    from app.models.transport import Mission
    from app.models.conteneur_cycle import ConteneurCycle
    from app.models.finance_ohada import FactureNew

    company_id = getattr(current_user, "company_id", None)
    q = db.query(Mission).filter(Mission.id == mission_id)
    if company_id is not None:
        q = q.filter(Mission.company_id == company_id)
    mission = q.first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission introuvable")

    stages = {
        "mission_id": mission.id,
        "reference": mission.reference,
        "statut": (mission.statut.value if hasattr(mission.statut, "value") else str(mission.statut)),
        "point_depart": mission.point_depart,
        "point_arrivee": mission.point_arrivee,
    }

    if mission.conteneur_id:
        c = db.query(ConteneurCycle).filter(ConteneurCycle.id == mission.conteneur_id).first()
        if c:
            stages["conteneur_source"] = {
                "id": c.id, "numero": c.numero,
                "type_conteneur": (c.type_conteneur.value if hasattr(c.type_conteneur, "value") else str(c.type_conteneur)),
            }

    if mission.numero_bl:
        stages["numero_bl"] = mission.numero_bl

    if mission.client_id:
        try:
            from app.models.tiers import Client
            client = db.query(Client).filter(Client.id == mission.client_id).first()
            if client:
                stages["client"] = {"id": client.id, "nom": getattr(client, "nom", None) or getattr(client, "raison_sociale", None)}
        except Exception:
            pass

    # Factures émises pour le conteneur de cette mission.
    if mission.conteneur_id:
        factures = db.query(FactureNew).filter(
            FactureNew.conteneur_id == mission.conteneur_id
        ).all()
        if factures:
            stages["facturation"] = [
                {"id": f.id, "numero_facture": f.numero_facture, "statut": f.statut,
                 "montant_ttc": float(f.montant_ttc) if f.montant_ttc is not None else None}
                for f in factures
            ]

    return stages


# ─────────────────────────────────────────────────────────────
# Propagation manuelle d'un événement cross-module
# ─────────────────────────────────────────────────────────────

@router.post("/propager", summary="Déclencher la propagation d'un événement cross-module")
async def propager(
    data: dict,
    current_user: User = Depends(get_current_user),
):
    """Publie un événement du catalogue sur le bus, pour que l'orchestrateur
    propage l'effet dans les modules aval (hiérarchie respectée).

    Seul un type d'événement du catalogue est accepté : on ne peut pas forcer
    une propagation vers un module non concerné par la transition.
    """
    from app.services.events.event_service import event_service

    event_type = (data or {}).get("event_type")
    payload = (data or {}).get("data", {})
    if event_type not in CHAIN_EVENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Type d'événement hors catalogue. Valeurs autorisées : "
                + ", ".join(CHAIN_EVENTS)
            ),
        )

    company_id = getattr(current_user, "company_id", None)
    await event_service.emit_tenant_event(
        company_id=company_id,
        event_type=event_type,
        data=payload,
        target_departments=[],
    )
    return {"status": "emis", "event_type": event_type, "company_id": company_id}

"""
Acconage router - manages port operations and stevedoring

CRD reel sur `operations_acconage` + jointure `escales`/`navires` : la fiche
d'une operation ne sert que des colonnes existantes. Ce qui n'est pas mesure en
base (cadence mouvements/heure, franchise) reste absent de la reponse.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.acconage import NavireCreate, NavireResponse, EscaleCreate, EscaleUpdate, EscaleResponse
from app.models.acconage import Navire, Escale, OperationAcconage, Conteneur

router = APIRouter()


@router.get("/navires", response_model=List[NavireResponse])
async def get_all_navires(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all ships"""
    navires = db.query(Navire).offset(skip).limit(limit).all()
    return navires


@router.post("/navires", response_model=NavireResponse, status_code=status.HTTP_201_CREATED)
async def create_navire(navire_data: NavireCreate, db: Session = Depends(get_db)):
    """Create a new ship"""
    db_navire = Navire(**navire_data.model_dump())
    db.add(db_navire)
    db.commit()
    db.refresh(db_navire)
    return db_navire


@router.get("/escales", response_model=List[EscaleResponse])
async def get_all_escales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all port calls"""
    escales = db.query(Escale).offset(skip).limit(limit).all()
    return escales


@router.post("/escales", response_model=EscaleResponse, status_code=status.HTTP_201_CREATED)
async def create_escale(escale_data: EscaleCreate, db: Session = Depends(get_db)):
    """Create a new port call"""
    import random
    import string
    
    data = escale_data.model_dump()
    numero_escale = data.pop("numero_escale", None) or (
        f"ESC-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    )
    
    db_escale = Escale(numero_escale=numero_escale, **data)
    db.add(db_escale)
    db.commit()
    db.refresh(db_escale)
    return db_escale


# ============ OPERATIONS D'ACCONAGE (ecran /acconage) ============
#
# Le contrat precedent etait casse : `OperationAcconageCreate` /
# `OperationAcconageResponse` declarent `numero_operation` et `navire_id`, deux
# champs qui n'existent PAS dans la table `operations_acconage` (colonnes
# reelles : reference, escale_id, type_operation, date_debut, date_fin,
# marchandise, quantite, unite, taux, montant, equipe, equipement, statut,
# notes). En consequence `GET /api/v1/acconage` echouait a la serialisation et
# `POST /api/v1/acconage` levait un TypeError (kwargs inconnus passees au
# modele) : le module etait mort malgre une table bien presente.
#
# Les ecrans designent une operation par le navire et l'escale ; ces informations
# sont reellement portees par `escales` et `navires`, donc servies par jointure
# et non par une colonne inventee.

TYPES_OPERATION = (
    "chargement", "chargement_conteneur", "dechargement", "dechargement_conteneur",
    "manutention", "manutention_vrac", "transbordement", "arrimage", "depannage",
)


def _reference_operation(db) -> str:
    """Reference OPA-AAAAMMJJ-XXXX verifiee unique en base (pas de doublon)."""
    import random
    import string
    for _ in range(50):
        cand = (
            f"OPA-{datetime.now().strftime('%Y%m%d')}-"
            f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        )
        if not db.query(OperationAcconage.id).filter(
            OperationAcconage.reference == cand
        ).first():
            return cand
    raise HTTPException(status_code=500, detail="Generation de reference impossible.")


def _resoudre_escale(db, payload: dict):
    """escale_id ou numero_escale -> escale reellement en base. Rien n'est cree."""
    escale_id = payload.get("escale_id")
    if escale_id not in (None, "", 0):
        try:
            cle = int(escale_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="escale_id doit etre un entier.")
        escale = db.get(Escale, cle)
        if not escale:
            raise HTTPException(
                status_code=400,
                detail=f"Escale {cle} inexistante : selectionnez une escale du port.",
            )
        return escale
    numero = str(payload.get("numero_escale") or "").strip()
    if numero:
        escale = db.query(Escale).filter(Escale.numero_escale == numero).first()
        if not escale:
            raise HTTPException(
                status_code=400,
                detail=f"Aucune escale ne porte le numero « {numero} » dans ce compte.",
            )
        return escale
    raise HTTPException(
        status_code=400,
        detail="escale_id ou numero_escale requis : une operation d'acconage "
               "s'enregistre toujours sur une escale existante.",
    )


def _serialize_operation(db, op: OperationAcconage) -> dict:
    """Vue ecran d'une operation : colonnes reelles + navire/escale joints."""
    escale = op.escale
    navire = escale.navire if escale else None
    repartition = _repartition_conteneurs(db, escale)
    return {
        "id": op.id,
        "reference": op.reference,
        # Alias attendu par l'ecran : l'identifiant metier de l'operation.
        "numero_operation": op.reference,
        "escale_id": op.escale_id,
        "numero_escale": escale.numero_escale if escale else None,
        "navire_id": navire.id if navire else None,
        "nom_navire": navire.nom if navire else None,
        "armateur": navire.armateur if navire else None,
        "pavillon": navire.pavillon if navire else None,
        "quai": escale.poste_quai if escale else None,
        "type_operation": op.type_operation,
        "date_debut": op.date_debut,
        "date_fin": op.date_fin,
        "date_arrivee": escale.date_arrivee_reelle if escale else None,
        "statut_escale": escale.statut.value if (escale and getattr(escale.statut, "value", None)) else None,
        "marchandise": op.marchandise,
        "quantite": float(op.quantite) if op.quantite is not None else None,
        "unite": op.unite,
        "taux": float(op.taux) if op.taux is not None else None,
        "montant": float(op.montant) if op.montant is not None else None,
        "equipe": op.equipe,
        "equipes": op.equipe,
        "equipement": op.equipement,
        "grues": op.equipement,
        # La cadence (mouvements/heure) n'est mesuree nulle part en base :
        # elle reste absente plutot que d'afficher un chiffre fabrique.
        "cadence": None,
        "statut": op.statut,
        "notes": op.notes,
        "remarques": op.notes,
        "created_at": op.created_at,
        "updated_at": op.updated_at,
        # Renseigne uniquement si l'escale porte ces donnees reellement saisies.
        "nombre_conteneurs": escale.nombre_conteneurs if escale else None,
        "tonnage": float(escale.tonnage) if (escale and escale.tonnage is not None) else None,
        **repartition,
    }


def _repartition_conteneurs(db, escale) -> dict:
    """Repartition 20'/40' et tonnage brut comptes depuis le parc conteneurs.

    Les conteneurs sont rattaches au navire de l'escale (cle etrangere
    `conteneurs.navire_id`) : ce sont des comptages reels de lignes existantes.
    Sans escale rattachee, les champs restent absents (None) au lieu d'un 0 qui
    se lirait comme « aucun conteneur traite ».
    """
    if not escale:
        return {"nb_20ft": None, "nb_40ft": None, "poids_brut_total_kg": None}
    lignes = (
        db.query(Conteneur.type_conteneur, func.count(Conteneur.id), func.sum(Conteneur.gross_weight))
        .filter(Conteneur.navire_id == escale.navire_id)
        .group_by(Conteneur.type_conteneur)
        .all()
    )
    if not lignes:
        return {"nb_20ft": None, "nb_40ft": None, "poids_brut_total_kg": None}
    nb20 = nb40 = 0
    brut = 0.0
    vu = False
    for type_conteneur, nombre, poids in lignes:
        t = (type_conteneur or "").lower()
        if "20" in t:
            nb20 += int(nombre or 0)
            vu = True
        elif "40" in t or "45" in t:
            nb40 += int(nombre or 0)
            vu = True
        if poids is not None:
            brut += float(poids)
    return {
        "nb_20ft": nb20 if vu else None,
        "nb_40ft": nb40 if vu else None,
        "poids_brut_total_kg": brut if brut else None,
    }


@router.get("")
@router.get("/")
async def list_operations(
    skip: int = 0,
    limit: int = 100,
    statut: Optional[str] = None,
    escale_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Operations d'acconage reellement enregistrees (table operations_acconage)."""
    q = db.query(OperationAcconage).order_by(OperationAcconage.id.desc())
    if escale_id:
        q = q.filter(OperationAcconage.escale_id == escale_id)
    if statut:
        q = q.filter(OperationAcconage.statut == statut.lower())
    rows = q.offset(skip).limit(min(limit, 500)).all()
    return [_serialize_operation(db, op) for op in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_operation_root(payload: dict, db: Session = Depends(get_db)):
    """Cree une operation d'acconage rattachee a une escale existante."""
    return await creer_operation(payload, db)


@router.post("/operations", status_code=status.HTTP_201_CREATED)
async def create_operation_acconage(payload: dict, db: Session = Depends(get_db)):
    """Cree une operation d'acconage rattachee a une escale existante."""
    return await creer_operation(payload, db)


async def creer_operation(payload: dict, db: Session = Depends(get_db)):
    escale = _resoudre_escale(db, payload)
    type_operation = str(payload.get("type_operation") or "").strip().lower()
    if not type_operation:
        raise HTTPException(status_code=400, detail="type_operation requis.")
    if type_operation not in TYPES_OPERATION:
        raise HTTPException(
            status_code=400,
            detail=f"Type d'operation inconnu : {payload.get('type_operation')}. "
                   f"Attendu : {list(TYPES_OPERATION)}.",
        )
    operation = OperationAcconage(
        reference=_reference_operation(db),
        escale_id=escale.id,
        type_operation=type_operation,
        marchandise=payload.get("marchandise") or None,
        unite=payload.get("unite") or None,
        equipe=payload.get("equipe") or None,
        equipement=payload.get("equipement") or None,
        statut=str(payload.get("statut") or "planifie").strip().lower(),
        notes=payload.get("notes") or payload.get("remarques") or None,
    )
    for cle in ("quantite", "taux", "montant"):
        if payload.get(cle) not in (None, ""):
            setattr(operation, cle, float(payload[cle]))
    for cle in ("date_debut", "date_fin"):
        if payload.get(cle):
            setattr(operation, cle, datetime.fromisoformat(str(payload[cle]).replace("Z", "+00:00")))
    if not operation.date_debut:
        operation.date_debut = escale.date_arrivee_reelle or escale.date_arrivee_prevue
    db.add(operation)
    db.commit()
    db.refresh(operation)
    return _serialize_operation(db, operation)


# ============ DOSSIER UNIQUE DE MARCHANDISE (vue consolidee honnete) ============
@router.get("/dossier-marchandise")
async def dossier_marchandise(
    numero_conteneur: str = None,
    numero_bl: str = None,
    db: Session = Depends(get_db),
):
    """Fiche consolidee d'une marchandise le long de la chaine portuaire.

    Cle d'entree : un numero de conteneur OU un numero de connaissement (B/L).
    Retourne, pour chaque etape, UNIQUEMENT ce qui est reellement relie (cle
    etrangere ou numero physique). Les etapes que le schema ne relie pas au
    conteneur sont signalees 'non_liciable_en_base' : rien n'est invente.
    """
    from app.services.dossier_marchandise import consigner_dossier_marchandise

    return consigner_dossier_marchandise(
        db, numero_conteneur=numero_conteneur, numero_bl=numero_bl
    )


# ============ BAPLIE EDI & TOS STOWAGE 3D ============
@router.post("/baplie/import")
async def importer_plan_baplie(payload: dict, db: Session = Depends(get_db)):
    """Import and validate BAPLIE EDIFACT message with IMDG segregation check"""
    from app.services.acconage_service import PortAdvancedTOSService
    edi_text = payload.get("edi_content", "")
    escale_id = int(payload.get("escale_id", 1))
    return PortAdvancedTOSService.parse_baplie_edi(edi_text, escale_id)


@router.get("/baplie/export/{escale_id}")
async def exporter_plan_baplie(escale_id: int, db: Session = Depends(get_db)):
    """Export vessel stowage plan into SMDG BAPLIE 2.2 EDIFACT format"""
    from app.services.acconage_service import PortAdvancedTOSService
    edi_content = PortAdvancedTOSService.generate_baplie_edi(escale_id, db)
    return {"escale_id": escale_id, "baplie_edi": edi_content, "standard": "SMDG BAPLIE 2.2"}


# ============ YARD MANAGEMENT TERRE-PLEIN ============
@router.get("/yard/positions")
@router.get("/yard/state")
async def obtenir_etat_terre_plein():
    """Get container yard state and blocks occupancy (PAD / PAK)"""
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.get_yard_state()


@router.post("/yard/assign")
async def assigner_emplacement_terre_plein(payload: dict):
    """Dynamically assign container slot minimizing re-handling"""
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.assign_yard_slot(payload)


# ============ FACTURATION DROITS DE QUAI PAD / PAK ============
@router.get("/facturation-quai/{escale_id}")
async def calculer_redevances_quai(
    escale_id: int, port_code: str = "PAD", db: Session = Depends(get_db)
):
    """Estimation des redevances portuaires PAD/PAK d'une escale relle.

    Quantities are derived from the actual port call and prices from the official
    TarifPortuaire table. If the official tariffs are not loaded, the service
    answers 501 rather than inventing rates. Nothing is certified here.
    """
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.calculate_port_dues_cemac(db, escale_id, port_code)


@router.post("/facturation-quai/{escale_id}/generer-facture")
async def generer_facture_quai(escale_id: int, payload: dict = None, db: Session = Depends(get_db)):
    """Prepare a DRAFT port-dues invoice for an armateur (no fake certification).

    Honesty fix: the previous version stamped statut_facturation='GENEREE_VALIDEE'
    on an invoice computed from hardcoded rates and fabricated container counts.
    It now returns the honest estimation draft only; certification/validation must
    come from a real, signed emission step, never simulated here.
    """
    from app.services.acconage_service import PortAdvancedTOSService
    port_code = (payload or {}).get("port_code", "PAD")
    facture = PortAdvancedTOSService.calculate_port_dues_cemac(db, escale_id, port_code)
    facture["note"] = (
        "Brouillon d'estimation. Non certifie : aucune emission signee n'a eu lieu."
    )
    return facture


# ============ FICHE OPERATION : LECTURE + EDITION ============
#
# Declarees en FIN de router : `/acconage/{operation_id}` absorberait tout
# segment litteral place apres elle (escales, navires, yard, baplie...). Le
# respect de l'ordre de declaration FastAPI est ce qui rend les deux possibles.

COLONNES_OPERATION = (
    "type_operation", "date_debut", "date_fin", "marchandise", "quantite",
    "unite", "taux", "montant", "equipe", "equipement", "statut", "notes",
)


@router.get("/{operation_id}")
async def obtenir_operation(operation_id: int, db: Session = Depends(get_db)):
    """Fiche detaillee d'une operation d'acconage (ecran /acconage/view)."""
    operation = db.get(OperationAcconage, operation_id)
    if not operation:
        raise HTTPException(
            status_code=404,
            detail=f"Operation d'acconage {operation_id} introuvable.",
        )
    return _serialize_operation(db, operation)


@router.put("/{operation_id}")
async def modifier_operation(
    operation_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    """Met a jour une operation existante, y compris son rattachement d'escale."""
    operation = db.get(OperationAcconage, operation_id)
    if not operation:
        raise HTTPException(
            status_code=404,
            detail=f"Operation d'acconage {operation_id} introuvable.",
        )
    if any(k in payload for k in ("escale_id", "numero_escale")):
        operation.escale_id = _resoudre_escale(db, payload).id
    if "type_operation" in payload:
        t = str(payload["type_operation"] or "").strip().lower()
        if t and t not in TYPES_OPERATION:
            raise HTTPException(
                status_code=400,
                detail=f"Type d'operation inconnu : {payload['type_operation']}. "
                       f"Attendu : {list(TYPES_OPERATION)}.",
            )
        if t:
            operation.type_operation = t
    for cle in COLONNES_OPERATION:
        if cle == "type_operation" or cle not in payload:
            continue
        valeur = payload[cle]
        if cle in ("statut", "unite", "equipe", "equipement", "marchandise", "notes"):
            if cle == "notes" and valeur in (None, "") and payload.get("remarques") is None:
                continue
            setattr(operation, cle, str(valeur).strip().lower() if cle == "statut" else (
                valeur if valeur not in (None, "") else None
            ))
        elif cle in ("quantite", "taux", "montant"):
            setattr(operation, cle, float(valeur) if valeur not in (None, "") else None)
        elif cle.startswith("date_"):
            if valeur:
                setattr(operation, cle, datetime.fromisoformat(str(valeur).replace("Z", "+00:00")))
            else:
                setattr(operation, cle, None)
    if "remarques" in payload and payload["remarques"] not in (None, ""):
        operation.notes = payload["remarques"]
    db.commit()
    db.refresh(operation)
    return _serialize_operation(db, operation)
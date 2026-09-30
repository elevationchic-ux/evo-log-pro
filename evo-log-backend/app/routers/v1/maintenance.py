"""
Maintenance router - manages equipment, vehicle maintenance, spare parts, and telematics

CRD rÃ©el sur le modele Maintenance (table `maintenances`) : aucun ordre de
travail codÃ© en dur. Les KPIs sont calcules depuis la base, pas inventes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.parc import Maintenance, Vehicule
from app.schemas.parc import MaintenanceCreate
from app.services.maintenance_gmao_avance_service import (
    GestionPiecesRechangeService, CarnetEntretienNumeriqueService,
    TelematicsOBD2IoTService
)

router = APIRouter()


def _iso(dt):
    return dt.isoformat() if dt else None


def _serialize(m: Maintenance) -> dict:
    """Serialise un ordre de maintenance avec les infos vehicule jointes."""
    veh = m.vehicule
    return {
        "id": m.id,
        "ordre_id": f"OT-{m.id:05d}",
        "vehicule_id": m.vehicule_id,
        "vehicule": veh.immatriculation if veh else None,
        # Alias servis a l'ecran atelier, qui designe le vehicule par sa plaque.
        "immatriculation_camion": veh.immatriculation if veh else None,
        "vehicule_immatriculation": veh.immatriculation if veh else None,
        "vehicule_detail": (
            f"{veh.immatriculation} ({veh.marque} {veh.modele})".strip() if veh else None
        ),
        "vehicule_type": veh.type_vehicule if veh else None,
        "vehicule_km": veh.kilometrage if veh else None,
        "type_intervention": (m.type_maintenance or "").upper() or None,
        "type_maintenance": (m.type_maintenance or "").upper() or None,
        "statut": (m.statut or "planifie").upper(),
        "priorite": (m.priorite or "").upper() or None,
        "pieces": m.pieces,
        "technicien": m.realisateur,
        "date_creation": _iso(m.created_at),
        "date_debut": _iso(m.date_debut),
        "date_fin": _iso(m.date_fin),
        "kilometrage": m.kilometrage,
        "description": m.description,
        "cout_estime_xaf": float(m.cout) if m.cout is not None else None,
        "notes": m.notes,
    }


@router.get("")
@router.get("/")
async def get_maintenances(
    skip: int = 0,
    limit: int = 100,
    vehicule_id: Optional[int] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Ordres de maintenance reellement enregistres en base."""
    q = (
        db.query(Maintenance)
        .options(joinedload(Maintenance.vehicule))
        .order_by(Maintenance.id.desc())
    )
    if vehicule_id:
        q = q.filter(Maintenance.vehicule_id == vehicule_id)
    if statut:
        q = q.filter(Maintenance.statut == statut.lower())
    rows = q.offset(skip).limit(min(limit, 500)).all()
    return [_serialize(m) for m in rows]


@router.get("/stats")
async def get_maintenance_stats(db: Session = Depends(get_db)):
    """Compteurs d'atelier calcules depuis la base (aucune valeur inventee)."""
    rows = db.query(Maintenance).all()
    par_statut: dict = {}
    cout_total = 0.0
    for m in rows:
        s = (m.statut or "planifie").upper()
        par_statut[s] = par_statut.get(s, 0) + 1
        if m.cout is not None:
            cout_total += float(m.cout)
    return {
        "total": len(rows),
        "par_statut": par_statut,
        "cout_total_xaf": cout_total,
    }


@router.post("/ordres", status_code=status.HTTP_201_CREATED)
async def creer_ordre_travail(payload: MaintenanceCreate, db: Session = Depends(get_db)):
    """Cree un ordre de maintenance persiste en base."""
    data = payload.model_dump(exclude_unset=True)
    vid = data.get("vehicule_id")
    if vid and not db.get(Vehicule, vid):
        raise HTTPException(status_code=400, detail="Vehicule inconnu")
    row = Maintenance(**data)
    if not row.date_debut:
        row.date_debut = datetime.now(timezone.utc)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize(row)


@router.put("/ordres/{ordre_id}")
async def mettre_a_jour_ordre(
    ordre_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    """Met a jour statut, dates, cout ou affectation d'un ordre existant."""
    row = db.get(Maintenance, ordre_id)
    if not row:
        raise HTTPException(status_code=404, detail="Ordre de maintenance introuvable")
    allowed = ("statut", "date_debut", "date_fin", "cout", "realisateur",
               "notes", "description", "kilometrage", "type_maintenance")
    for k in allowed:
        if k in payload:
            v = payload[k]
            if k.startswith("date_") and isinstance(v, str) and v:
                v = datetime.fromisoformat(v.replace("Z", "+00:00"))
            setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return _serialize(row)


# ============ GESTION PIECES DE RECHANGE & DESTOCKAGE WMS ============
@router.post("/destockage-pieces")
async def destocker_pieces_intervention(payload: dict):
    """Consume spare parts directly onto work order from WMS warehouse"""
    ordre_id = payload.get("ordre_id")
    pieces = payload.get("pieces")
    if not ordre_id or not pieces:
        raise HTTPException(status_code=400, detail="ordre_id et pieces requis")
    return GestionPiecesRechangeService.destocker_pieces_ot(ordre_id, pieces)


# ============ CARNET D'ENTRETIEN NUMERIQUE PASSEPORT ============
@router.get("/carnet-entretien/{vin_chassis}")
async def obtenir_carnet_entretien(vin_chassis: str, db: Session = Depends(get_db)):
    """Digital maintenance passport and component life history"""
    historique = (
        db.query(Maintenance)
        .options(joinedload(Maintenance.vehicule))
        .join(Vehicule, Maintenance.vehicule_id == Vehicule.id)
        .filter(Vehicule.immatriculation.ilike(f"%{vin_chassis}%"))
        .order_by(Maintenance.id.desc())
        .all()
    )
    return {
        "reference": vin_chassis,
        "ordres": [_serialize(m) for m in historique],
    }


# ============ TÃ‰LÃ‰MATIQUE IOT & CODES DÃ‰FAUTS CAN-BUS OBD2 ============
@router.get("/telematics/obd2/{immatriculation}")
async def diagnostiquer_telematics_obd2(immatriculation: str):
    """Real-time CAN-Bus / OBD2 engine diagnostics and DTC codes"""
    return TelematicsOBD2IoTService.diagnostiquer_defauts_canbus(immatriculation)


# ============ ANALYTICS RELIABILITY MTBF / MTTR & TCO ============
@router.get("/analytics/kpis")
async def obtenir_kpis_maintenance(
    vehicule_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """KPIs GMAO calcules depuis les ordres reellement enregistres."""
    from app.services.maintenance_gmao_avance_service import AnalyticsMaintenanceService

    if vehicule_id:
        return AnalyticsMaintenanceService.calculer_mtbf_mttr(
            db=db, vehicule_id=vehicule_id, periode_mois=12
        )
    rows = db.query(Maintenance).all()
    terminees = [m for m in rows if (m.statut or "").lower() == "termine"]
    corrective = [m for m in terminees if "correct" in (m.type_maintenance or "").lower()]
    prevenue = [m for m in terminees if "prevent" in (m.type_maintenance or "").lower()]
    return {
        "total_ordres": len(rows),
        "ordres_termines": len(terminees),
        "correctifs": len(corrective),
        "preventifs_realises": len(prevenue),
        "taux_preventif_pct": round(100 * len(prevenue) / len(terminees), 1) if terminees else None,
        "source": "maintenances (base de donnees)",
    }


# ============ ECRAN ATELIER : CREATION + FICHE DETAILLEE ============
#
# Routes parametriques declarees EN DERNIER : `/maintenance/{maintenance_id}`
# absorbe tout segment (y compris Â« stats Â», Â« ordres Â», Â« analytics Â»). Placee
# apres les routes litterales, l'ordre de resolution FastAPI conserve ces
# dernieres. Inverser les deux rendrait /maintenance/stats invisible.
#
# `POST /api/v1/maintenance` etait appele par /maintenance/edit et
# /maintenance (page) sans route declaree : c'est l'enveloppe rattrape-tout
# `pending_modules` qui repondait 202 {accepted:false}, et l'ecran affichait
# Â« Nouvel ordre de travail cree Â» sur une donnee jamais ecrite en base.

CHAMPS_COLONNE = (
    "type_maintenance", "date_debut", "date_fin", "kilometrage", "description",
    "cout", "realisateur", "statut", "notes", "priorite", "pieces",
)
CHAMPS_VEHICULE = ("vehicule_id", "immatriculation_camion",
                   "vehicule_immatriculation", "immatriculation")

TYPES_MAINTENANCE = ("preventive", "curative", "corrective", "visite_technique",
                     "pneumatique", "premiere_mise")
STATUTS_ATELIER = ("planifie", "en_attente", "en_cours", "attente_pieces",
                   "termine", "annule")


def _resoudre_vehicule(db: Session, payload: dict) -> Optional[Vehicule]:
    """vehicule_id ou plaque -> vehicule reellement au parc. Rien n'est cree.

    Une immatriculation inconnue est refusee : rattacher un ordre de travail a
    un vehicule inexistant (ou a un id devine) fausserait le carnet d'entretien
    et les KPIs MTBF/MTTR de toute la flotte.
    """
    vid = payload.get("vehicule_id")
    if vid not in (None, "", 0):
        try:
            cle = int(vid)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="vehicule_id doit etre un entier.")
        vehicule = db.get(Vehicule, cle)
        if not vehicule:
            raise HTTPException(
                status_code=400,
                detail=f"Aucun vehicule en base avec l'id {cle} : selectionnez un vehicule du parc.",
            )
        return vehicule

    plaque = str(
        payload.get("immatriculation_camion")
        or payload.get("vehicule_immatriculation")
        or payload.get("immatriculation")
        or ""
    ).strip()
    if not plaque:
        raise HTTPException(
            status_code=400,
            detail="Vehicule requis : vehicule_id ou immatriculation_camion.",
        )
    vehicule = (
        db.query(Vehicule)
        .filter(func.upper(Vehicule.immatriculation) == plaque.upper())
        .first()
    )
    if not vehicule:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Aucun vehicule porte l'immatriculation Â« {plaque} Â» dans ce compte : "
                "impossible d'ouvrir un ordre de travail sur un vehicule inexistant."
            ),
        )
    return vehicule


def _valider_champs(payload: dict):
    """Refuse toute cle inconnue au lieu de la jeter silencieusement."""
    autorisees = set(CHAMPS_COLONNE) | set(CHAMPS_VEHICULE)
    inconnues = sorted(k for k in payload if k not in autorisees)
    if inconnues:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Champs non enregistables : {inconnues}. Colonnes disponibles : "
                f"{sorted(CHAMPS_COLONNE)}."
            ),
        )
    if "statut" in payload and payload["statut"]:
        s = str(payload["statut"]).strip().lower()
        if s not in STATUTS_ATELIER:
            raise HTTPException(
                status_code=400,
                detail=f"Statut d'atelier inconnu : {payload['statut']}. Attendu : {list(STATUTS_ATELIER)}.",
            )
    if "type_maintenance" in payload and payload["type_maintenance"]:
        t = str(payload["type_maintenance"]).strip().lower()
        if t not in TYPES_MAINTENANCE:
            raise HTTPException(
                status_code=400,
                detail=f"Type de maintenance inconnu : {payload['type_maintenance']}. Attendu : {list(TYPES_MAINTENANCE)}.",
            )


def _appliquer_champs(row: Maintenance, payload: dict) -> None:
    """Ecrit les champs reconnus, normalises comme le reste du module (minuscules)."""
    for cle in CHAMPS_COLONNE:
        if cle not in payload:
            continue
        valeur = payload[cle]
        if cle in ("statut", "type_maintenance", "priorite"):
            setattr(row, cle, str(valeur).strip().lower() if valeur else None)
        elif cle.startswith("date_"):
            if isinstance(valeur, str) and valeur:
                valeur = datetime.fromisoformat(valeur.replace("Z", "+00:00"))
            setattr(row, cle, valeur or None)
        elif cle == "kilometrage":
            setattr(row, cle, int(valeur) if valeur not in (None, "") else None)
        elif cle == "cout":
            setattr(row, cle, float(valeur) if valeur not in (None, "") else None)
        else:
            setattr(row, cle, valeur if valeur not in (None, "") else None)


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def creer_maintenance(payload: dict, db: Session = Depends(get_db)):
    """Cree un ordre de travail reellement persiste (ecran atelier /maintenance)."""
    _valider_champs(payload)
    vehicule = _resoudre_vehicule(db, payload)
    if not (payload.get("description") or "").strip():
        raise HTTPException(
            status_code=400,
            detail="La description de l'intervention est exigee : un ordre de travail "
                   "sans travaux decrits ne peut pas etre transmis a l'atelier.",
        )
    row = Maintenance(vehicule_id=vehicule.id)
    _appliquer_champs(row, payload)
    if not row.date_debut:
        row.date_debut = datetime.now(timezone.utc)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize(row)


@router.get("/{maintenance_id}")
async def obtenir_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    """Fiche detaillee d'un ordre de maintenance (ecran /maintenance/view)."""
    row = db.get(Maintenance, maintenance_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Ordre de maintenance {maintenance_id} introuvable.",
        )
    return _serialize(row)


@router.put("/{maintenance_id}")
async def modifier_maintenance(
    maintenance_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    """Met a jour un ordre existant, y compris son rattachement vehicule."""
    row = db.get(Maintenance, maintenance_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Ordre de maintenance {maintenance_id} introuvable.",
        )
    _valider_champs(payload)
    if any(k in payload for k in CHAMPS_VEHICULE):
        row.vehicule_id = _resoudre_vehicule(db, payload).id
    _appliquer_champs(row, payload)
    db.commit()
    db.refresh(row)
    return _serialize(row)

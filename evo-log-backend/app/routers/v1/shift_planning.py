"""
Shift Planning router - manages shift planning and resource scheduling using TempsTravail and Absence from RH
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from typing import Optional
from datetime import datetime, date as date_type, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.rh import TempsTravail, Absence, Conge, StatutConge

router = APIRouter()


@router.get("/")
async def get_shift_planning(
    semaine: Optional[str] = Query(None, description="Format: YYYY-WNN (ex: 2026-W37)"),
    employe_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère le planning des shifts/temps de travail"""
    query = db.query(TempsTravail)

    if employe_id:
        query = query.filter(TempsTravail.employe_id == employe_id)

    if semaine:
        # Parser le format YYYY-WNN
        try:
            year, week = semaine.split("-W")
            week_start = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w").date()
            week_end = week_start + timedelta(days=6)
            query = query.filter(
                TempsTravail.date >= week_start,
                TempsTravail.date <= week_end
            )
        except (ValueError, AttributeError):
            pass

    total = query.count()
    shifts = query.order_by(TempsTravail.date, TempsTravail.employe_id).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": s.id,
                "employe_id": s.employe_id,
                "date": s.date.isoformat() if s.date else None,
                "heure_arrivee": s.heure_arrivee,
                "heure_depart": s.heure_depart,
                "heures_travaillees": float(s.heures_travaillees) if s.heures_travaillees else None,
                "heures_supplementaires": float(s.heures_supplementaires) if s.heures_supplementaires else None,
                "tache": s.tache,
                "statut": s.statut,
            }
            for s in shifts
        ]
    }


@router.get("/absences")
async def get_absences(
    employe_id: Optional[int] = Query(None),
    mois: Optional[str] = Query(None, description="Format: YYYY-MM"),
    justifiee: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les absences du personnel"""
    query = db.query(Absence)

    if employe_id:
        query = query.filter(Absence.employe_id == employe_id)
    if justifiee is not None:
        query = query.filter(Absence.justifiee == justifiee)
    if mois:
        try:
            year, month = mois.split("-")
            query = query.filter(
                extract("year", Absence.date) == int(year),
                extract("month", Absence.date) == int(month)
            )
        except ValueError:
            pass

    total = query.count()
    absences = query.order_by(desc(Absence.date)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "data": [
            {
                "id": a.id,
                "employe_id": a.employe_id,
                "date": a.date.isoformat() if a.date else None,
                "type_absence": a.type_absence,
                "motif": a.motif,
                "justifiee": a.justifiee,
                "heure_debut": a.heure_debut,
                "heure_fin": a.heure_fin,
                "nombre_heures": float(a.nombre_heures) if a.nombre_heures else 0.0,
            }
            for a in absences
        ]
    }


@router.get("/conges")
async def get_conges(
    employe_id: Optional[int] = Query(None),
    statut: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les demandes de congé"""
    query = db.query(Conge)

    if employe_id:
        query = query.filter(Conge.employe_id == employe_id)
    if statut:
        try:
            query = query.filter(Conge.statut == StatutConge(statut))
        except ValueError:
            pass

    total = query.count()
    conges = query.order_by(desc(Conge.date_demande)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "data": [
            {
                "id": c.id,
                "employe_id": c.employe_id,
                "type_conge": c.type_conge.value if hasattr(c.type_conge, "value") else str(c.type_conge),
                "date_debut": c.date_debut.isoformat() if c.date_debut else None,
                "date_fin": c.date_fin.isoformat() if c.date_fin else None,
                "nombre_jours": c.nombre_jours,
                "statut": c.statut.value if hasattr(c.statut, "value") else str(c.statut),
                "motif": c.motif,
                "date_demande": c.date_demande.isoformat() if c.date_demande else None,
                "commentaires_approbation": c.commentaires_approbation,
            }
            for c in conges
        ]
    }


@router.get("/stats")
async def get_shift_stats(
    mois: Optional[str] = Query(None, description="Format: YYYY-MM"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques des plannings"""
    query_tt = db.query(TempsTravail)
    query_abs = db.query(Absence)
    query_cong = db.query(Conge)

    if mois:
        try:
            year, month = mois.split("-")
            query_tt = query_tt.filter(
                extract("year", TempsTravail.date) == int(year),
                extract("month", TempsTravail.date) == int(month)
            )
            query_abs = query_abs.filter(
                extract("year", Absence.date) == int(year),
                extract("month", Absence.date) == int(month)
            )
        except ValueError:
            pass

    heures_totales = query_tt.with_entities(func.sum(TempsTravail.heures_travaillees)).scalar() or 0.0
    heures_supp = query_tt.with_entities(func.sum(TempsTravail.heures_supplementaires)).scalar() or 0.0
    nb_absences = query_abs.count()
    absences_injustifiees = query_abs.filter(Absence.justifiee == False).count()  # noqa

    conges_en_attente = query_cong.filter(Conge.statut == StatutConge.EN_ATTENTE).count()
    conges_approuves = query_cong.filter(Conge.statut == StatutConge.APPROUVE).count()

    return {
        "periode": mois or "Toutes périodes",
        "heures_travaillees": round(float(heures_totales), 1),
        "heures_supplementaires": round(float(heures_supp), 1),
        "total_absences": nb_absences,
        "absences_injustifiees": absences_injustifiees,
        "conges_en_attente": conges_en_attente,
        "conges_approuves": conges_approuves,
    }


@router.post("/temps-travail")
async def create_shift(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistrer du temps de travail"""
    if not data.get("employe_id") or not data.get("date"):
        raise HTTPException(status_code=400, detail="employe_id et date sont requis")

    shift = TempsTravail(
        employe_id=data["employe_id"],
        date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
        heure_arrivee=data.get("heure_arrivee"),
        heure_depart=data.get("heure_depart"),
        heures_travaillees=data.get("heures_travaillees"),
        heures_supplementaires=data.get("heures_supplementaires", 0),
        tache=data.get("tache"),
        statut=data.get("statut", "valide"),
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return {"message": "Temps de travail enregistré", "id": shift.id}


@router.post("/absences")
async def create_absence(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistrer une absence"""
    if not data.get("employe_id") or not data.get("date"):
        raise HTTPException(status_code=400, detail="employe_id et date sont requis")

    absence = Absence(
        employe_id=data["employe_id"],
        date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
        type_absence=data.get("type_absence"),
        motif=data.get("motif"),
        justifiee=data.get("justifiee", False),
        heure_debut=data.get("heure_debut"),
        heure_fin=data.get("heure_fin"),
        nombre_heures=data.get("nombre_heures", 0),
    )
    db.add(absence)
    db.commit()
    db.refresh(absence)
    return {"message": "Absence enregistrée", "id": absence.id}
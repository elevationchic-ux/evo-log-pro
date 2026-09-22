"""
Incidents router - manages incident reporting and tracking using AccidentTravail (QHSE) and AccidentTransport
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, date as date_type
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.qhse import AccidentTravail, AnalyseRisque, StatutAccident, InvestigationAccident
from app.models.transport_avance import AccidentTransport

router = APIRouter()


@router.get("/")
async def get_incidents(
    type_incident: Optional[str] = Query(None, description="travail | transport"),
    statut: Optional[str] = Query(None),
    gravite: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère tous les incidents (travail + transport)"""
    results = []

    # Accidents du travail (QHSE)
    if not type_incident or type_incident == "travail":
        q = db.query(AccidentTravail)
        if statut:
            q = q.filter(AccidentTravail.statut == statut)
        if gravite:
            q = q.filter(AccidentTravail.gravite == gravite)
        for a in q.order_by(desc(AccidentTravail.date_accident)).all():
            results.append({
                "id": a.id,
                "type": "travail",
                "numero": a.numero_accident,
                "date_accident": a.date_accident.isoformat() if a.date_accident else None,
                "lieu": a.lieu,
                "description": a.description,
                "gravite": a.gravite,
                "statut": a.statut.value if hasattr(a.statut, "value") else str(a.statut),
                "arret_travail_jours": a.arret_travail,
                "hospitalisation": a.hospitalisation,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })

    # Accidents transport
    if not type_incident or type_incident == "transport":
        q = db.query(AccidentTransport)
        if statut:
            q = q.filter(AccidentTransport.statut == statut)
        if gravite:
            q = q.filter(AccidentTransport.gravite == gravite)
        for a in q.order_by(desc(AccidentTransport.date_accident)).all():
            results.append({
                "id": a.id,
                "type": "transport",
                "numero": a.numero_accident,
                "date_accident": a.date_accident.isoformat() if a.date_accident else None,
                "lieu": a.lieu,
                "description": a.constat,
                "gravite": a.gravite,
                "blesses": a.blesses,
                "deces": a.deces,
                "statut": a.statut,
                "montant_dommages": float(a.montant_dommages) if a.montant_dommages else None,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })

    results.sort(key=lambda x: x.get("date_accident") or "", reverse=True)
    total = len(results)
    return {"total": total, "skip": skip, "limit": limit, "data": results[skip: skip + limit]}


@router.get("/stats")
async def get_incidents_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques des incidents"""
    now = datetime.utcnow()
    debut_annee = datetime(now.year, 1, 1)

    total_travail = db.query(func.count(AccidentTravail.id)).scalar() or 0
    total_transport = db.query(func.count(AccidentTransport.id)).scalar() or 0
    en_cours_travail = db.query(func.count(AccidentTravail.id)).filter(
        AccidentTravail.statut == StatutAccident.EN_COURS
    ).scalar() or 0
    arret_total = db.query(func.sum(AccidentTravail.arret_travail)).filter(
        AccidentTravail.date_accident >= debut_annee
    ).scalar() or 0
    deces_total = db.query(func.sum(AccidentTransport.deces)).filter(
        AccidentTransport.date_accident >= debut_annee
    ).scalar() or 0

    return {
        "total_accidents_travail": total_travail,
        "total_accidents_transport": total_transport,
        "en_cours": en_cours_travail,
        "jours_arret_annee": int(arret_total),
        "deces_annee": int(deces_total) if deces_total else 0,
    }


@router.get("/{incident_id}")
async def get_incident(
    incident_id: int,
    type_incident: str = Query("travail"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère un incident spécifique"""
    if type_incident == "travail":
        a = db.query(AccidentTravail).filter(AccidentTravail.id == incident_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Incident introuvable")
        investigations = db.query(InvestigationAccident).filter(
            InvestigationAccident.accident_id == incident_id
        ).all()
        return {
            "id": a.id,
            "type": "travail",
            "numero": a.numero_accident,
            "date_accident": a.date_accident.isoformat() if a.date_accident else None,
            "lieu": a.lieu,
            "type_accident": a.type_accident,
            "description": a.description,
            "gravite": a.gravite,
            "statut": a.statut.value if hasattr(a.statut, "value") else str(a.statut),
            "arret_travail": a.arret_travail,
            "hospitalisation": a.hospitalisation,
            "investigations": [
                {
                    "id": inv.id,
                    "date_investigation": inv.date_investigation.isoformat() if inv.date_investigation else None,
                    "investigateur": inv.investigateur,
                    "conclusions": inv.conclusions,
                    "mesures_correctives": inv.mesures_correctives,
                    "statut": inv.statut,
                }
                for inv in investigations
            ],
        }
    else:
        a = db.query(AccidentTransport).filter(AccidentTransport.id == incident_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Incident introuvable")
        return {
            "id": a.id,
            "type": "transport",
            "numero": a.numero_accident,
            "date_accident": a.date_accident.isoformat() if a.date_accident else None,
            "lieu": a.lieu,
            "gravite": a.gravite,
            "blesses": a.blesses,
            "deces": a.deces,
            "statut": a.statut,
            "montant_dommages": float(a.montant_dommages) if a.montant_dommages else None,
        }


@router.post("/")
async def create_incident(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Déclarer un incident du travail"""
    if not data.get("lieu") or not data.get("description"):
        raise HTTPException(status_code=400, detail="lieu et description sont requis")

    import uuid
    numero = f"ACC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    accident = AccidentTravail(
        numero_accident=numero,
        employe_id=data.get("employe_id", current_user.id),
        date_accident=datetime.strptime(data["date_accident"], "%Y-%m-%d") if data.get("date_accident") else datetime.utcnow(),
        lieu=data["lieu"],
        type_accident=data.get("type_accident"),
        description=data["description"],
        gravite=data.get("gravite", "leger"),
        partie_corps=data.get("partie_corps"),
        arret_travail=data.get("arret_travail", 0),
        hospitalisation=data.get("hospitalisation", False),
        declarant=f"{current_user.first_name} {current_user.last_name}" if hasattr(current_user, "first_name") else current_user.email,
        date_declaration=datetime.utcnow().date(),
        statut=StatutAccident.SIGNALE,
    )
    db.add(accident)
    db.commit()
    db.refresh(accident)
    return {"message": "Incident déclaré avec succès", "id": accident.id, "numero": numero}


@router.put("/{incident_id}/statut")
async def update_incident_statut(
    incident_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met à jour le statut d'un incident"""
    accident = db.query(AccidentTravail).filter(AccidentTravail.id == incident_id).first()
    if not accident:
        raise HTTPException(status_code=404, detail="Incident introuvable")

    nouveau_statut = data.get("statut")
    if nouveau_statut:
        try:
            accident.statut = StatutAccident(nouveau_statut)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Statut invalide: {nouveau_statut}")

    db.commit()
    return {"message": "Statut mis à jour", "id": incident_id}
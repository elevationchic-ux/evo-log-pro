"""
Port Incidents router - manages port incident reporting using AccidentTransport and QHSE models
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transport_avance import AccidentTransport
from app.models.qhse import AccidentTravail, AnalyseRisque

router = APIRouter()


@router.get("/")
async def get_port_incidents(
    gravite: Optional[str] = Query(None, description="legere | moyenne | grave | mortel"),
    statut: Optional[str] = Query(None),
    type_accident: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les incidents portuaires (transport + travail)"""
    # Incidents liés au transport (camions, véhicules port)
    q_transport = db.query(AccidentTransport)
    if gravite:
        q_transport = q_transport.filter(AccidentTransport.gravite == gravite)
    if statut:
        q_transport = q_transport.filter(AccidentTransport.statut == statut)

    total_transport = q_transport.count()
    accidents_transport = q_transport.order_by(desc(AccidentTransport.date_accident)).offset(skip).limit(limit).all()

    # Incidents de travail QHSE
    q_travail = db.query(AccidentTravail)
    if gravite:
        q_travail = q_travail.filter(AccidentTravail.gravite == gravite)
    if statut:
        q_travail = q_travail.filter(AccidentTravail.statut == statut)

    total_travail = q_travail.count()
    accidents_travail = q_travail.order_by(desc(AccidentTravail.date_accident)).offset(skip).limit(limit).all()

    return {
        "total": total_transport + total_travail,
        "incidents_transport": [
            {
                "id": a.id,
                "type": "transport",
                "numero": a.numero_accident,
                "date": a.date_accident.isoformat() if a.date_accident else None,
                "lieu": a.lieu,
                "gravite": a.gravite,
                "blesses": a.blesses,
                "deces": a.deces,
                "statut": a.statut,
                "montant_dommages": float(a.montant_dommages) if a.montant_dommages else None,
            }
            for a in accidents_transport
        ],
        "incidents_travail": [
            {
                "id": a.id,
                "type": "travail",
                "numero": a.numero_accident,
                "date": a.date_accident.isoformat() if a.date_accident else None,
                "lieu": a.lieu,
                "type_accident": a.type_accident,
                "gravite": a.gravite,
                "statut": a.statut.value if hasattr(a.statut, "value") else str(a.statut),
                "arret_travail": a.arret_travail,
            }
            for a in accidents_travail
        ],
    }


@router.get("/stats")
async def get_port_incidents_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques des incidents portuaires"""
    now = datetime.utcnow()
    debut_annee = datetime(now.year, 1, 1)

    total_transport = db.query(func.count(AccidentTransport.id)).scalar() or 0
    total_travail = db.query(func.count(AccidentTravail.id)).scalar() or 0
    graves = db.query(func.count(AccidentTransport.id)).filter(
        AccidentTransport.gravite.in_(["grave", "mortel"])
    ).scalar() or 0
    deces = db.query(func.sum(AccidentTransport.deces)).filter(
        AccidentTransport.date_accident >= debut_annee
    ).scalar() or 0
    blesses = db.query(func.sum(AccidentTransport.blesses)).filter(
        AccidentTransport.date_accident >= debut_annee
    ).scalar() or 0
    cout_total = db.query(func.sum(AccidentTransport.montant_dommages)).filter(
        AccidentTransport.date_accident >= debut_annee
    ).scalar() or 0.0

    return {
        "total_incidents_transport": total_transport,
        "total_incidents_travail": total_travail,
        "incidents_graves": graves,
        "deces_annee": int(deces) if deces else 0,
        "blesses_annee": int(blesses) if blesses else 0,
        "cout_dommages_annee": float(cout_total),
    }


@router.post("/")
async def create_port_incident(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Déclarer un incident portuaire"""
    import uuid
    numero = f"PI-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    accident = AccidentTravail(
        numero_accident=numero,
        employe_id=data.get("employe_id", current_user.id),
        date_accident=datetime.strptime(data["date"], "%Y-%m-%d") if data.get("date") else datetime.utcnow(),
        lieu=data.get("lieu", "Port"),
        type_accident=data.get("type_accident"),
        description=data.get("description", ""),
        gravite=data.get("gravite", "leger"),
        declarant=f"{getattr(current_user, 'email', 'inconnu')}",
        date_declaration=datetime.utcnow().date(),
    )
    db.add(accident)
    db.commit()
    db.refresh(accident)
    return {"message": "Incident déclaré", "id": accident.id, "numero": numero}
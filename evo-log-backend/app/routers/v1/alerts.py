"""
Alerts router - manages system alerts and performance alerts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transport_avance import AlertPerformance
from app.models.notifications import Notification

router = APIRouter()


@router.get("/")
async def get_alerts(
    statut: Optional[str] = Query(None, description="Filtrer par statut: active, resolue, ignoree"),
    gravite: Optional[str] = Query(None, description="Filtrer par gravité: faible, moyenne, haute, critique"),
    type_alerte: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les alertes de performance système"""
    query = db.query(AlertPerformance)

    if statut:
        query = query.filter(AlertPerformance.statut == statut)
    if gravite:
        query = query.filter(AlertPerformance.gravite == gravite)
    if type_alerte:
        query = query.filter(AlertPerformance.type_alerte == type_alerte)

    total = query.count()
    alerts = query.order_by(desc(AlertPerformance.date_alerte)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": a.id,
                "type_alerte": a.type_alerte,
                "gravite": a.gravite,
                "description": a.description,
                "concerne_type": a.concerne_type,
                "concerne_id": a.concerne_id,
                "valeur_actuelle": float(a.valeur_actuelle) if a.valeur_actuelle else None,
                "valeur_seuil": float(a.valeur_seuil) if a.valeur_seuil else None,
                "date_alerte": a.date_alerte.isoformat() if a.date_alerte else None,
                "statut": a.statut,
                "date_resolution": a.date_resolution.isoformat() if a.date_resolution else None,
                "resolution": a.resolution,
            }
            for a in alerts
        ]
    }


@router.get("/summary")
async def get_alerts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Résumé des alertes actives par gravité"""
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)

    total_actives = db.query(func.count(AlertPerformance.id)).filter(
        AlertPerformance.statut == "active"
    ).scalar() or 0

    critique = db.query(func.count(AlertPerformance.id)).filter(
        AlertPerformance.statut == "active",
        AlertPerformance.gravite == "critique"
    ).scalar() or 0

    haute = db.query(func.count(AlertPerformance.id)).filter(
        AlertPerformance.statut == "active",
        AlertPerformance.gravite == "haute"
    ).scalar() or 0

    nouvelles_24h = db.query(func.count(AlertPerformance.id)).filter(
        AlertPerformance.date_alerte >= last_24h
    ).scalar() or 0

    # Notifications non lues
    notifs_non_lues = db.query(func.count(Notification.id)).filter(
        Notification.destinataire_id == current_user.id,
        Notification.statut == "envoye",
        Notification.date_lecture == None  # noqa
    ).scalar() or 0

    return {
        "total_actives": total_actives,
        "critique": critique,
        "haute": haute,
        "nouvelles_24h": nouvelles_24h,
        "notifications_non_lues": notifs_non_lues,
    }


@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère une alerte spécifique"""
    alert = db.query(AlertPerformance).filter(AlertPerformance.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    return {
        "id": alert.id,
        "type_alerte": alert.type_alerte,
        "gravite": alert.gravite,
        "description": alert.description,
        "concerne_type": alert.concerne_type,
        "concerne_id": alert.concerne_id,
        "valeur_actuelle": float(alert.valeur_actuelle) if alert.valeur_actuelle else None,
        "valeur_seuil": float(alert.valeur_seuil) if alert.valeur_seuil else None,
        "date_alerte": alert.date_alerte.isoformat() if alert.date_alerte else None,
        "statut": alert.statut,
        "resolution": alert.resolution,
    }


@router.post("/{alert_id}/resoudre")
async def resoudre_alert(
    alert_id: int,
    resolution: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Résoudre une alerte"""
    alert = db.query(AlertPerformance).filter(AlertPerformance.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")

    alert.statut = "resolue"
    alert.resolue_par = current_user.id
    alert.date_resolution = datetime.utcnow()
    alert.resolution = resolution.get("resolution", "")
    db.commit()
    db.refresh(alert)

    return {"message": "Alerte résolue avec succès", "id": alert.id}


@router.post("/{alert_id}/ignorer")
async def ignorer_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ignorer une alerte"""
    alert = db.query(AlertPerformance).filter(AlertPerformance.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")

    alert.statut = "ignoree"
    db.commit()

    return {"message": "Alerte ignorée", "id": alert.id}
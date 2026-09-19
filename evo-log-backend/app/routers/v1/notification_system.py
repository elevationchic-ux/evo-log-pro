"""
Multi-Channel Notification System router
Gestion et envoi des notifications multi-canaux (SMS, WhatsApp, Email, In-App, Push)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notifications import Notification, TemplateNotification, LectureNotification

router = APIRouter()


class SendNotificationRequest(BaseModel):
    destinataire_id: Optional[int] = None
    type_canal: str = "in_app"  # email, sms, whatsapp, push, in_app
    categorie: Optional[str] = "alerte"  # alerte, transactionnel, transport, facture
    titre: str
    corps: str
    priorite: Optional[str] = "normale"  # basse, normale, haute, critique
    donnees: Optional[Dict[str, Any]] = None


class TemplateCreate(BaseModel):
    code: str
    nom: str
    type_canal: str
    type_template: Optional[str] = "transactionnel"
    sujet: Optional[str] = None
    corps: str
    variables: Optional[List[str]] = []


@router.get("/")
async def get_notifications(
    canal: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    priorite: Optional[str] = Query(None),
    destinataire_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste de toutes les notifications émises sur les différents canaux"""
    query = db.query(Notification)

    if canal:
        query = query.filter(Notification.type_canal == canal)
    if statut:
        query = query.filter(Notification.statut == statut)
    if priorite:
        query = query.filter(Notification.priorite == priorite)
    if destinataire_id:
        query = query.filter(Notification.destinataire_id == destinataire_id)
    if search:
        query = query.filter(
            or_(
                Notification.titre.ilike(f"%{search}%"),
                Notification.corps.ilike(f"%{search}%"),
                Notification.numero_notification.ilike(f"%{search}%")
            )
        )

    total = query.count()
    items = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": n.id,
                "numero_notification": n.numero_notification,
                "destinataire_id": n.destinataire_id,
                "type_canal": n.type_canal,
                "categorie": n.categorie,
                "titre": n.titre,
                "corps": n.corps,
                "priorite": n.priorite,
                "statut": n.statut,
                "date_envoi": n.date_envoi.isoformat() if n.date_envoi else None,
                "date_lecture": n.date_lecture.isoformat() if n.date_lecture else None,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in items
        ]
    }


@router.get("/stats")
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Métriques de performance de la plateforme de notifications"""
    total = db.query(func.count(Notification.id)).scalar() or 0
    envoyes = db.query(func.count(Notification.id)).filter(Notification.statut.in_(["envoye", "livre"])).scalar() or 0
    en_attente = db.query(func.count(Notification.id)).filter(Notification.statut == "en_attente").scalar() or 0
    echoues = db.query(func.count(Notification.id)).filter(Notification.statut == "echoue").scalar() or 0

    repartition_canaux = db.query(
        Notification.type_canal,
        func.count(Notification.id)
    ).group_by(Notification.type_canal).all()

    taux_delivrance = (envoyes / total * 100.0) if total > 0 else 100.0

    return {
        "total_notifications": total,
        "distribuees": envoyes,
        "en_attente": en_attente,
        "echecs": echoues,
        "taux_delivrance_pourcent": round(taux_delivrance, 2),
        "canaux": [
            {"canal": canal or "in_app", "count": count}
            for canal, count in repartition_canaux
        ]
    }


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_notification(
    payload: SendNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Émet et enregistre une notification multi-canal"""
    today_str = datetime.now().strftime("%Y%m%d%H%M%S")
    num_notif = f"NOTIF-{today_str}-{current_user.id}"

    dest_id = payload.destinataire_id or current_user.id

    notif = Notification(
        numero_notification=num_notif,
        destinataire_id=dest_id,
        type_canal=payload.type_canal,
        categorie=payload.categorie or "information",
        titre=payload.titre,
        corps=payload.corps,
        priorite=payload.priorite or "normale",
        statut="envoye",
        date_envoi=datetime.utcnow(),
        donnees=payload.donnees or {}
    )

    db.add(notif)
    db.commit()
    db.refresh(notif)

    return {
        "message": f"Notification envoyée via {payload.type_canal}",
        "id": notif.id,
        "numero_notification": notif.numero_notification,
        "statut": notif.statut
    }


@router.get("/templates")
async def get_templates(
    canal: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des modèles de notifications prédéfinis"""
    query = db.query(TemplateNotification).filter(TemplateNotification.actif == True)
    if canal:
        query = query.filter(TemplateNotification.type_canal == canal)

    templates = query.all()
    return [
        {
            "id": t.id,
            "code": t.code,
            "nom": t.nom,
            "type_canal": t.type_canal,
            "sujet": t.sujet,
            "corps": t.corps,
            "variables": t.variables
        }
        for t in templates
    ]


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crée un nouveau modèle de notification"""
    existing = db.query(TemplateNotification).filter(TemplateNotification.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Template {payload.code} existant")

    tmpl = TemplateNotification(
        code=payload.code,
        nom=payload.nom,
        type_canal=payload.type_canal,
        type_template=payload.type_template or "transactionnel",
        sujet=payload.sujet,
        corps=payload.corps,
        variables=payload.variables or [],
        cree_par=current_user.full_name or current_user.email,
        actif=True
    )
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)

    return {"message": "Template créé avec succès", "id": tmpl.id, "code": tmpl.code}


@router.get("/{id}")
async def get_notification_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détail d'une notification avec statut de lecture"""
    n = db.query(Notification).filter(Notification.id == id).first()
    if not n:
        raise HTTPException(status_code=404, detail=f"Notification #{id} non trouvée")

    return {
        "id": n.id,
        "numero_notification": n.numero_notification,
        "destinataire_id": n.destinataire_id,
        "type_canal": n.type_canal,
        "categorie": n.categorie,
        "titre": n.titre,
        "corps": n.corps,
        "donnees": n.donnees,
        "priorite": n.priorite,
        "statut": n.statut,
        "date_envoi": n.date_envoi.isoformat() if n.date_envoi else None,
        "date_lecture": n.date_lecture.isoformat() if n.date_lecture else None,
        "created_at": n.created_at.isoformat() if n.created_at else None
    }


@router.post("/{id}/read")
async def mark_as_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marque une notification comme lue"""
    n = db.query(Notification).filter(Notification.id == id).first()
    if not n:
        raise HTTPException(status_code=404, detail=f"Notification #{id} non trouvée")

    now = datetime.utcnow()
    n.date_lecture = now
    n.statut = "livre"

    # Enregistrer la lecture
    lecture = LectureNotification(
        notification_id=n.id,
        utilisateur_id=current_user.id,
        date_lecture=now
    )
    db.add(lecture)
    db.commit()

    return {"message": "Notification marquée comme lue", "id": n.id, "date_lecture": now.isoformat()}


@router.delete("/{id}")
async def delete_notification(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime une notification"""
    n = db.query(Notification).filter(Notification.id == id).first()
    if not n:
        raise HTTPException(status_code=404, detail=f"Notification #{id} non trouvée")

    db.query(LectureNotification).filter(LectureNotification.notification_id == n.id).delete()
    db.delete(n)
    db.commit()

    return {"message": f"Notification #{id} supprimée"}
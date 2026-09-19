"""Notifications router - Multi-channel notifications for Cameroon/CEMAC"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.notifications import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    TemplateNotificationCreate, TemplateNotificationUpdate, TemplateNotificationResponse,
    PreferenceNotificationCreate, PreferenceNotificationUpdate, PreferenceNotificationResponse,
    CampagneNotificationCreate, CampagneNotificationUpdate, CampagneNotificationResponse,
    HistoriqueEnvoiCreate, HistoriqueEnvoiResponse,
    EmailNotificationCreate, EmailNotificationResponse,
    SMSNotificationCreate, SMSNotificationResponse,
    WhatsAppNotificationCreate, WhatsAppNotificationResponse,
    PushNotificationCreate, PushNotificationResponse,
    RapportNotificationsResponse
)
from app.services.notifications_service import (
    NotificationService, TemplateNotificationService, PreferenceNotificationService,
    CampagneNotificationService, HistoriqueEnvoiService, EmailNotificationService,
    SMSNotificationService, WhatsAppNotificationService, PushNotificationService,
    NotificationsReportingService
)
from app.models.notifications import Notification, TemplateNotification, CampagneNotification

router = APIRouter(tags=["Notifications"])


# ============ NOTIFICATIONS ============
@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def creer_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notification"""
    return NotificationService.creer_notification(
        db, notification.numero_notification, notification.destinataire_id,
        notification.type_canal, notification.titre, notification.corps, notification.priorite
    )


@router.put("/notifications/{notification_id}/envoyer", response_model=NotificationResponse)
def envoyer_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send notification"""
    return NotificationService.envoyer_notification(db, notification_id)


@router.put("/notifications/{notification_id}", response_model=NotificationResponse)
def mettre_a_jour_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification"""
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    for field, value in notification.model_dump(exclude_unset=True).items():
        setattr(n, field, value)
    
    db.commit()
    db.refresh(n)
    return n


# ============ TEMPLATES ============
@router.post("/templates", response_model=TemplateNotificationResponse, status_code=status.HTTP_201_CREATED)
def creer_template(
    template: TemplateNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notification template"""
    return TemplateNotificationService.creer_template(
        db, template.code, template.nom, template.type_template,
        template.type_canal, template.sujet, template.corps, template.variables
    )


@router.put("/templates/{template_id}", response_model=TemplateNotificationResponse)
def mettre_a_jour_template(
    template_id: int,
    template: TemplateNotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification template"""
    t = db.query(TemplateNotification).filter(TemplateNotification.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    
    for field, value in template.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    
    db.commit()
    db.refresh(t)
    return t


# ============ PREFERENCES ============
@router.post("/preferences", response_model=PreferenceNotificationResponse, status_code=status.HTTP_201_CREATED)
def creer_preference(
    preference: PreferenceNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notification preference"""
    return PreferenceNotificationService.creer_preference(
        db, preference.utilisateur_id, preference.type_canal,
        preference.categorie, preference.active
    )


@router.put("/preferences/{preference_id}", response_model=PreferenceNotificationResponse)
def mettre_a_jour_preference(
    preference_id: int,
    preference: PreferenceNotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification preference"""
    p = db.query(PreferenceNotification).filter(PreferenceNotification.id == preference_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Préférence non trouvée")
    
    for field, value in preference.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ CAMPAGNES ============
@router.post("/campagnes", response_model=CampagneNotificationResponse, status_code=status.HTTP_201_CREATED)
def creer_campagne(
    campagne: CampagneNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notification campaign"""
    return CampagneNotificationService.creer_campagne(
        db, campagne.numero_campagne, campagne.nom, campagne.type_canal,
        campagne.date_debut, campagne.segment
    )


@router.put("/campagnes/{campagne_id}/lancer", response_model=CampagneNotificationResponse)
def lancer_campagne(
    campagne_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Launch campaign"""
    return CampagneNotificationService.lancer_campagne(db, campagne_id)


@router.put("/campagnes/{campagne_id}", response_model=CampagneNotificationResponse)
def mettre_a_jour_campagne(
    campagne_id: int,
    campagne: CampagneNotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update campaign"""
    c = db.query(CampagneNotification).filter(CampagneNotification.id == campagne_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campagne non trouvée")
    
    for field, value in campagne.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ HISTORIQUE ENVOI ============
@router.post("/historique-envoi", response_model=HistoriqueEnvoiResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_envoi(
    historique: HistoriqueEnvoiCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record send history"""
    return HistoriqueEnvoiService.enregistrer_envoi(
        db, historique.notification_id, historique.canal,
        historique.fournisseur, historique.adresse, historique.statut
    )


# ============ EMAIL ============
@router.post("/emails", response_model=EmailNotificationResponse, status_code=status.HTTP_201_CREATED)
def creer_email(
    email: EmailNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create email notification"""
    return EmailNotificationService.creer_email(
        db, email.notification_id, email.expediteur, email.destinataire,
        email.sujet, email.corps_html
    )


# ============ SMS ============
@router.post("/sms", response_model=SMSNotificationResponse, status_code=status.HTTP_201_CREATED)
def creer_sms(
    sms: SMSNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create SMS notification"""
    return SMSNotificationService.creer_sms(
        db, sms.notification_id, sms.expediteur, sms.destinataire, sms.message
    )


# ============ WHATSAPP ============
@router.post("/whatsapp", response_model=WhatsAppNotificationResponse, status_code=status.HTTP_201_CREATED)
def creer_whatsapp(
    whatsapp: WhatsAppNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create WhatsApp notification"""
    return WhatsAppNotificationService.creer_whatsapp(
        db, whatsapp.notification_id, whatsapp.expediteur, whatsapp.destinataire,
        whatsapp.template, whatsapp.message
    )


# ============ PUSH ============
@router.post("/push", response_model=PushNotificationResponse, status_code=status.HTTP_201_CREATED)
def creer_push(
    push: PushNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create push notification"""
    return PushNotificationService.creer_push(
        db, push.notification_id, push.titre, push.corps,
        push.plateforme, push.device_token
    )


@router.get("/utilisateurs/{utilisateur_id}/rapport", response_model=RapportNotificationsResponse)
def rapport_notifications(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate notifications report"""
    return NotificationsReportingService.rapport_notifications(db, utilisateur_id)

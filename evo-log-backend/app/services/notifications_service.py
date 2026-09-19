"""Notifications service - Multi-channel notifications for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.notifications import (
    Notification, TemplateNotification, PreferenceNotification, LectureNotification,
    CampagneNotification, HistoriqueEnvoi, EmailNotification, SMSNotification,
    WhatsAppNotification, PushNotification
)


class NotificationService:
    """Notification service"""
    
    @staticmethod
    def creer_notification(
        db: Session,
        numero_notification: str,
        destinataire_id: int,
        type_canal: str,
        titre: str,
        corps: str,
        priorite: str
    ) -> Notification:
        """Create notification"""
        notification = Notification(
            numero_notification=numero_notification,
            destinataire_id=destinataire_id,
            type_canal=type_canal,
            titre=titre,
            corps=corps,
            priorite=priorite,
            statut="en_attente"
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def envoyer_notification(db: Session, notification_id: int) -> Notification:
        """Send notification"""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise ValueError("Notification non trouvée")
        
        notification.statut = "envoye"
        notification.date_envoi = datetime.utcnow()
        notification.nombre_tentatives += 1
        notification.derniere_tentative = datetime.utcnow()
        
        db.commit()
        db.refresh(notification)
        return notification


class TemplateNotificationService:
    """Template notification service"""
    
    @staticmethod
    def creer_template(
        db: Session,
        code: str,
        nom: str,
        type_template: str,
        type_canal: str,
        sujet: str,
        corps: str,
        variables: dict
    ) -> TemplateNotification:
        """Create notification template"""
        template = TemplateNotification(
            code=code,
            nom=nom,
            type_template=type_template,
            type_canal=type_canal,
            sujet=sujet,
            corps=corps,
            variables=variables,
            langue="fra",
            actif=True,
            version=1
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template


class PreferenceNotificationService:
    """Notification preference service"""
    
    @staticmethod
    def creer_preference(
        db: Session,
        utilisateur_id: int,
        type_canal: str,
        categorie: str,
        active: bool
    ) -> PreferenceNotification:
        """Create notification preference"""
        preference = PreferenceNotification(
            utilisateur_id=utilisateur_id,
            type_canal=type_canal,
            categorie=categorie,
            active=active,
            frequence="immediat"
        )
        db.add(preference)
        db.commit()
        db.refresh(preference)
        return preference


class CampagneNotificationService:
    """Campaign notification service"""
    
    @staticmethod
    def creer_campagne(
        db: Session,
        numero_campagne: str,
        nom: str,
        type_canal: str,
        date_debut: datetime,
        segment: dict
    ) -> CampagneNotification:
        """Create notification campaign"""
        campagne = CampagneNotification(
            numero_campagne=numero_campagne,
            nom=nom,
            type_canal=type_canal,
            date_debut=date_debut,
            segment=segment,
            statut="planifie"
        )
        db.add(campagne)
        db.commit()
        db.refresh(campagne)
        return campagne
    
    @staticmethod
    def lancer_campagne(db: Session, campagne_id: int) -> CampagneNotification:
        """Launch campaign"""
        campagne = db.query(CampagneNotification).filter(CampagneNotification.id == campagne_id).first()
        if not campagne:
            raise ValueError("Campagne non trouvée")
        
        campagne.statut = "en_cours"
        db.commit()
        db.refresh(campagne)
        return campagne


class HistoriqueEnvoiService:
    """Send history service"""
    
    @staticmethod
    def enregistrer_envoi(
        db: Session,
        notification_id: int,
        canal: str,
        fournisseur: str,
        adresse: str,
        statut: str
    ) -> HistoriqueEnvoi:
        """Record send history"""
        historique = HistoriqueEnvoi(
            notification_id=notification_id,
            canal=canal,
            fournisseur=fournisseur,
            adresse=adresse,
            statut=statut
        )
        db.add(historique)
        db.commit()
        db.refresh(historique)
        return historique


class EmailNotificationService:
    """Email notification service"""
    
    @staticmethod
    def creer_email(
        db: Session,
        notification_id: int,
        expediteur: str,
        destinataire: str,
        sujet: str,
        corps_html: str
    ) -> EmailNotification:
        """Create email notification"""
        email = EmailNotification(
            notification_id=notification_id,
            expediteur=expediteur,
            destinataire=destinataire,
            sujet=sujet,
            corps_html=corps_html
        )
        db.add(email)
        db.commit()
        db.refresh(email)
        return email


class SMSNotificationService:
    """SMS notification service"""
    
    @staticmethod
    def creer_sms(
        db: Session,
        notification_id: int,
        expediteur: str,
        destinataire: str,
        message: str
    ) -> SMSNotification:
        """Create SMS notification"""
        sms = SMSNotification(
            notification_id=notification_id,
            expediteur=expediteur,
            destinataire=destinataire,
            message=message,
            longueur=len(message),
            nombre_segments=1
        )
        db.add(sms)
        db.commit()
        db.refresh(sms)
        return sms


class WhatsAppNotificationService:
    """WhatsApp notification service"""
    
    @staticmethod
    def creer_whatsapp(
        db: Session,
        notification_id: int,
        expediteur: str,
        destinataire: str,
        template: str,
        message: str
    ) -> WhatsAppNotification:
        """Create WhatsApp notification"""
        whatsapp = WhatsAppNotification(
            notification_id=notification_id,
            expediteur=expediteur,
            destinataire=destinataire,
            template=template,
            message=message
        )
        db.add(whatsapp)
        db.commit()
        db.refresh(whatsapp)
        return whatsapp


class PushNotificationService:
    """Push notification service"""
    
    @staticmethod
    def creer_push(
        db: Session,
        notification_id: int,
        titre: str,
        corps: str,
        plateforme: str,
        device_token: str
    ) -> PushNotification:
        """Create push notification"""
        push = PushNotification(
            notification_id=notification_id,
            titre=titre,
            corps=corps,
            plateforme=plateforme,
            device_token=device_token
        )
        db.add(push)
        db.commit()
        db.refresh(push)
        return push


class NotificationsReportingService:
    """Notifications reporting service"""
    
    @staticmethod
    def rapport_notifications(db: Session, utilisateur_id: int) -> Dict[str, Any]:
        """Generate notifications report"""
        notifications = db.query(Notification).filter(
            Notification.destinataire_id == utilisateur_id
        ).all()
        
        return {
            "utilisateur_id": utilisateur_id,
            "total_notifications": len(notifications),
            "par_canal": {n.type_canal: 1 for n in notifications},
            "par_statut": {n.statut: 1 for n in notifications},
            "non_lues": sum(1 for n in notifications if n.date_lecture is None)
        }

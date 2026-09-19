"""Unit tests for Notifications module - Multi-channel notifications"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.notifications import (
    Notification, TemplateNotification, PreferenceNotification,
    CampagneNotification, EmailNotification, SMSNotification
)
from app.services.notifications_service import (
    NotificationService, TemplateNotificationService, PreferenceNotificationService,
    CampagneNotificationService, EmailNotificationService, SMSNotificationService
)


class TestNotificationService:
    """Test Notification service"""
    
    def test_creer_notification(self, db: Session):
        """Test creating notification"""
        notification = NotificationService.creer_notification(
            db=db,
            numero_notification="NOT-2026-001",
            destinataire_id=1,
            type_canal="email",
            titre="Nouvelle facture disponible",
            corps="Votre facture F-2026-001 est disponible",
            priorite="normale"
        )
        assert notification.numero_notification == "NOT-2026-001"
        assert notification.type_canal == "email"
        assert notification.statut == "en_attente"
    
    def test_envoyer_notification(self, db: Session):
        """Test sending notification"""
        notification = NotificationService.creer_notification(
            db=db,
            numero_notification="NOT-2026-001",
            destinataire_id=1,
            type_canal="email",
            titre="Nouvelle facture disponible",
            corps="Votre facture F-2026-001 est disponible",
            priorite="normale"
        )
        
        notification_envoyee = NotificationService.envoyer_notification(
            db=db,
            notification_id=notification.id
        )
        assert notification_envoyee.statut == "envoye"
        assert notification_envoyee.date_envoi is not None


class TestTemplateNotificationService:
    """Test Template Notification service"""
    
    def test_creer_template(self, db: Session):
        """Test creating notification template"""
        template = TemplateNotificationService.creer_template(
            db=db,
            code="TPL-FACTURE",
            nom="Template Facture",
            type_template="transactionnel",
            type_canal="email",
            sujet="Facture {{numero_facture}}",
            corps="Votre facture {{numero_facture}} est disponible",
            variables={"numero_facture": "string", "montant": "number"}
        )
        assert template.code == "TPL-FACTURE"
        assert template.type_template == "transactionnel"
        assert template.actif is True


class TestPreferenceNotificationService:
    """Test Preference Notification service"""
    
    def test_creer_preference(self, db: Session):
        """Test creating notification preference"""
        preference = PreferenceNotificationService.creer_preference(
            db=db,
            utilisateur_id=1,
            type_canal="email",
            categorie="facture",
            active=True
        )
        assert preference.utilisateur_id == 1
        assert preference.type_canal == "email"
        assert preference.active is True


class TestCampagneNotificationService:
    """Test Campagne Notification service"""
    
    def test_creer_campagne(self, db: Session):
        """Test creating notification campaign"""
        campagne = CampagneNotificationService.creer_campagne(
            db=db,
            numero_campagne="CAMP-2026-001",
            nom="Campagne Factures Janvier",
            type_canal="email",
            date_debut=datetime(2026, 1, 15),
            segment={"clients": "actifs"}
        )
        assert campagne.numero_campagne == "CAMP-2026-001"
        assert campagne.type_canal == "email"
        assert campagne.statut == "planifie"
    
    def test_lancer_campagne(self, db: Session):
        """Test launching campaign"""
        campagne = CampagneNotificationService.creer_campagne(
            db=db,
            numero_campagne="CAMP-2026-001",
            nom="Campagne Factures Janvier",
            type_canal="email",
            date_debut=datetime(2026, 1, 15),
            segment={"clients": "actifs"}
        )
        
        campagne_lancee = CampagneNotificationService.lancer_campagne(
            db=db,
            campagne_id=campagne.id
        )
        assert campagne_lancee.statut == "en_cours"


class TestEmailNotificationService:
    """Test Email Notification service"""
    
    def test_creer_email(self, db: Session):
        """Test creating email notification"""
        email = EmailNotificationService.creer_email(
            db=db,
            notification_id=1,
            expediteur="noreply@evolog.cm",
            destinataire="client@example.com",
            sujet="Facture F-2026-001",
            corps_html="<h1>Votre facture</h1>"
        )
        assert email.expediteur == "noreply@evolog.cm"
        assert email.destinataire == "client@example.com"
        assert email.sujet == "Facture F-2026-001"


class TestSMSNotificationService:
    """Test SMS Notification service"""
    
    def test_creer_sms(self, db: Session):
        """Test creating SMS notification"""
        sms = SMSNotificationService.creer_sms(
            db=db,
            notification_id=1,
            expediteur="EVOLOG",
            destinataire="+237699123456",
            message="Votre facture F-2026-001 est disponible"
        )
        assert sms.expediteur == "EVOLOG"
        assert sms.destinataire == "+237699123456"
        assert sms.nombre_segments == 1

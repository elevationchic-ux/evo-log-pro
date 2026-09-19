"""Notifications models - Multi-channel notifications for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeCanal(str, enum.Enum):
    """Channel type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    IN_APP = "in_app"
    AUTRE = "autre"


class StatutNotification(str, enum.Enum):
    """Notification status enumeration"""
    EN_ATTENTE = "en_attente"
    ENVOYE = "envoye"
    LIVRE = "livre"
    ECHOUE = "echoue"
    RELANCE = "relance"
    ANNULE = "annule"


class PrioriteNotification(str, enum.Enum):
    """Notification priority enumeration"""
    CRITIQUE = "critique"
    HAUTE = "haute"
    NORMALE = "normale"
    BASSE = "basse"


class TypeTemplate(str, enum.Enum):
    """Template type enumeration"""
    TRANSACTIONNEL = "transactionnel"
    MARKETING = "marketing"
    ALERTE = "alerte"
    RAPPEL = "rappel"
    INFORMATION = "information"
    AUTRE = "autre"


class Notification(Base):
    """Notification entity"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_notification = Column(String(50), unique=True, nullable=False, index=True)
    destinataire_id = Column(Integer, ForeignKey('users.id'))
    type_canal = Column(String(50))
    categorie = Column(String(50))
    titre = Column(String(200), nullable=False)
    corps = Column(Text, nullable=False)
    donnees = Column(JSON)  # Additional data
    priorite = Column(String(20))
    statut = Column(String(20), default="en_attente")
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_envoi = Column(DateTime(timezone=True))
    date_livraison = Column(DateTime(timezone=True))
    date_lecture = Column(DateTime(timezone=True))
    nombre_tentatives = Column(Integer, default=0)
    derniere_tentative = Column(DateTime(timezone=True))
    expire_le = Column(DateTime(timezone=True))
    reference_externe = Column(String(100))
    correlation_id = Column(String(100))
    reponse_canal = Column(Text)
    erreur = Column(Text)
    template_id = Column(Integer, ForeignKey('templates_notification.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("TemplateNotification", back_populates="notifications")
    lectures = relationship("LectureNotification", back_populates="notification")


class TemplateNotification(Base):
    """Notification template"""
    __tablename__ = "templates_notification"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    type_template = Column(String(50))
    type_canal = Column(String(50))
    sujet = Column(String(200))
    corps = Column(Text, nullable=False)
    variables = Column(JSON)  # Template variables
    langue = Column(String(10), default="fra")
    actif = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    cree_par = Column(String(100))
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    notifications = relationship("Notification", back_populates="template")


class PreferenceNotification(Base):
    """User notification preferences"""
    __tablename__ = "preferences_notification"
    
    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey('users.id'))
    type_canal = Column(String(50))
    categorie = Column(String(50))
    active = Column(Boolean, default=True)
    frequence = Column(String(50))  # "immediat", "quotidien", "hebdomadaire"
    heures_silence = Column(JSON)  # JSON array [start, end]
    jours_silence = Column(JSON)  # JSON array of days
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LectureNotification(Base):
    """Notification read status"""
    __tablename__ = "lectures_notification"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    utilisateur_id = Column(Integer, ForeignKey('users.id'))
    date_lecture = Column(DateTime(timezone=True), server_default=func.now())
    device_info = Column(String(255))
    ip_adresse = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    notification = relationship("Notification", back_populates="lectures")


class CampagneNotification(Base):
    """Notification campaign"""
    __tablename__ = "campagnes_notification"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_campagne = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    description = Column(Text)
    type_canal = Column(String(50))
    template_id = Column(Integer, ForeignKey('templates_notification.id'))
    segment = Column(JSON)  # Target segment criteria
    date_debut = Column(DateTime(timezone=True), nullable=False)
    date_fin = Column(DateTime(timezone=True))
    statut = Column(String(20), default="planifie")  # planifie, en_cours, terminee, annulee
    nombre_destinataires = Column(Integer, default=0)
    nombre_envoyes = Column(Integer, default=0)
    nombre_livres = Column(Integer, default=0)
    nombre_echecs = Column(Integer, default=0)
    taux_ouverture = Column(Numeric)
    taux_clic = Column(Numeric)
    cree_par = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HistoriqueEnvoi(Base):
    """Send history"""
    __tablename__ = "historique_envoi"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    canal = Column(Enum(TypeCanal))
    fournisseur = Column(String(100))  # "sendgrid", "twilio", "firebase", etc.
    adresse = Column(String(255))
    date_envoi = Column(DateTime(timezone=True), server_default=func.now())
    reponse = Column(Text)
    statut = Column(String(20))  # "succes", "echoue", "bounced"
    code_erreur = Column(String(50))
    duree_ms = Column(Integer)
    cout = Column(Numeric)
    devise = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmailNotification(Base):
    """Email notification specific"""
    __tablename__ = "email_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    expediteur = Column(String(255))
    expediteur_nom = Column(String(200))
    destinataire = Column(String(255), nullable=False)
    cc = Column(Text)  # JSON array
    bcc = Column(Text)  # JSON array
    sujet = Column(String(200), nullable=False)
    corps_html = Column(Text)
    corps_text = Column(Text)
    pieces_jointes = Column(JSON)  # JSON array
    retour_lecture = Column(Boolean, default=False)
    date_ouverture = Column(DateTime(timezone=True))
    nombre_clics = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SMSNotification(Base):
    """SMS notification specific"""
    __tablename__ = "sms_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    expediteur = Column(String(50))
    destinataire = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    longueur = Column(Integer)
    nombre_segments = Column(Integer, default=1)
    date_envoi = Column(DateTime(timezone=True))
    statut_livraison = Column(String(20))
    reponse_operateur = Column(Text)
    cout = Column(Numeric)
    devise = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WhatsAppNotification(Base):
    """WhatsApp notification specific"""
    __tablename__ = "whatsapp_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    expediteur = Column(String(50))
    destinataire = Column(String(50), nullable=False)
    template = Column(String(100))
    message = Column(Text)
    media_url = Column(String(500))
    type_media = Column(String(50))  # "image", "video", "document", "audio"
    date_envoi = Column(DateTime(timezone=True))
    statut_livraison = Column(String(20))
    reponse = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PushNotification(Base):
    """Push notification specific"""
    __tablename__ = "push_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    titre = Column(String(200), nullable=False)
    corps = Column(Text)
    icone = Column(String(255))
    image = Column(String(255))
    badge = Column(Integer)
    donnees = Column(JSON)
    son = Column(String(100))
    action = Column(String(100))
    url_action = Column(String(500))
    date_envoi = Column(DateTime(timezone=True))
    plateforme = Column(String(50))  # "ios", "android", "web"
    device_token = Column(String(255))
    statut_livraison = Column(String(20))
    date_ouverture = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

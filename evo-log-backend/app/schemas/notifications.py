"""Pydantic schemas for Notifications module - Multi-channel notifications for Cameroon/CEMAC"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Notification schemas
class NotificationBase(BaseModel):
    numero_notification: str
    destinataire_id: int
    type_canal: str
    titre: str
    corps: str


class NotificationCreate(NotificationBase):
    categorie: str = ""
    donnees: dict = {}
    priorite: str = "normale"
    expire_le: Optional[datetime] = None
    reference_externe: str = ""
    correlation_id: str = ""
    template_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    statut: Optional[str] = None
    date_livraison: Optional[datetime] = None
    date_lecture: Optional[datetime] = None
    reponse_canal: Optional[str] = None
    erreur: Optional[str] = None


class NotificationResponse(NotificationBase):
    id: int
    categorie: Optional[str] = None
    donnees: Optional[dict] = None
    priorite: str
    statut: str
    date_creation: datetime
    date_envoi: Optional[datetime] = None
    date_livraison: Optional[datetime] = None
    date_lecture: Optional[datetime] = None
    nombre_tentatives: int
    derniere_tentative: Optional[datetime] = None
    expire_le: Optional[datetime] = None
    reference_externe: Optional[str] = None
    correlation_id: Optional[str] = None
    reponse_canal: Optional[str] = None
    erreur: Optional[str] = None
    template_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Template Notification schemas
class TemplateNotificationBase(BaseModel):
    code: str
    nom: str
    type_template: str
    type_canal: str
    sujet: str
    corps: str
    variables: dict


class TemplateNotificationCreate(TemplateNotificationBase):
    langue: str = "fra"
    cree_par: str = ""


class TemplateNotificationUpdate(BaseModel):
    langue: Optional[str] = None
    actif: Optional[bool] = None
    updated_at: Optional[datetime] = None


class TemplateNotificationResponse(TemplateNotificationBase):
    id: int
    langue: str
    actif: bool
    version: int
    cree_par: str
    date_creation: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Preference Notification schemas
class PreferenceNotificationBase(BaseModel):
    utilisateur_id: int
    type_canal: str
    categorie: str
    active: bool


class PreferenceNotificationCreate(PreferenceNotificationBase):
    frequence: str = "immediat"
    heures_silence: list = []
    jours_silence: list = []


class PreferenceNotificationUpdate(BaseModel):
    frequence: Optional[str] = None
    heures_silence: Optional[list] = None
    jours_silence: Optional[list] = None


class PreferenceNotificationResponse(PreferenceNotificationBase):
    id: int
    frequence: str
    heures_silence: Optional[list] = None
    jours_silence: Optional[list] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Campagne Notification schemas
class CampagneNotificationBase(BaseModel):
    numero_campagne: str
    nom: str
    type_canal: str
    date_debut: datetime


class CampagneNotificationCreate(CampagneNotificationBase):
    description: str = ""
    template_id: int = None
    segment: dict = {}
    date_fin: datetime = None


class CampagneNotificationUpdate(BaseModel):
    description: Optional[str] = None
    template_id: Optional[int] = None
    segment: Optional[dict] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    nombre_destinataires: Optional[int] = None
    nombre_envoyes: Optional[int] = None
    nombre_livres: Optional[int] = None
    nombre_echecs: Optional[int] = None
    taux_ouverture: Optional[float] = None
    taux_clic: Optional[float] = None


class CampagneNotificationResponse(CampagneNotificationBase):
    id: int
    description: Optional[str] = None
    template_id: Optional[int] = None
    segment: Optional[dict] = None
    date_fin: Optional[datetime] = None
    statut: str
    nombre_destinataires: int
    nombre_envoyes: int
    nombre_livres: int
    nombre_echecs: int
    taux_ouverture: Optional[float] = None
    taux_clic: Optional[float] = None
    cree_par: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Historique Envoi schemas
class HistoriqueEnvoiBase(BaseModel):
    notification_id: int
    canal: str
    fournisseur: str
    adresse: str


class HistoriqueEnvoiCreate(HistoriqueEnvoiBase):
    reponse: str = ""
    code_erreur: str = ""
    duree_ms: int = 0
    cout: float = 0.0


class HistoriqueEnvoiResponse(HistoriqueEnvoiBase):
    id: int
    reponse: Optional[str] = None
    statut: str
    code_erreur: Optional[str] = None
    duree_ms: int
    cout: float
    devise: str
    date_envoi: datetime
    
    class Config:
        from_attributes = True


# Email Notification schemas
class EmailNotificationBase(BaseModel):
    notification_id: int
    expediteur: str
    destinataire: str
    sujet: str


class EmailNotificationCreate(EmailNotificationBase):
    expediteur_nom: str = ""
    cc: list = []
    bcc: list = []
    corps_html: str = ""
    corps_text: str = ""
    pieces_jointes: list = []
    retour_lecture: bool = False


class EmailNotificationResponse(EmailNotificationBase):
    id: int
    expediteur_nom: Optional[str] = None
    cc: Optional[list] = None
    bcc: Optional[list] = None
    corps_html: Optional[str] = None
    corps_text: Optional[str] = None
    pieces_jointes: Optional[list] = None
    retour_lecture: bool
    date_ouverture: Optional[datetime] = None
    nombre_clics: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# SMS Notification schemas
class SMSNotificationBase(BaseModel):
    notification_id: int
    expediteur: str
    destinataire: str
    message: str


class SMSNotificationCreate(SMSNotificationBase):
    pass


class SMSNotificationResponse(SMSNotificationBase):
    id: int
    longueur: int
    nombre_segments: int
    date_envoi: Optional[datetime] = None
    statut_livraison: Optional[str] = None
    reponse_operateur: Optional[str] = None
    cout: float
    devise: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# WhatsApp Notification schemas
class WhatsAppNotificationBase(BaseModel):
    notification_id: int
    expediteur: str
    destinataire: str
    template: str
    message: str


class WhatsAppNotificationCreate(WhatsAppNotificationBase):
    media_url: str = ""
    type_media: str = ""


class WhatsAppNotificationResponse(WhatsAppNotificationBase):
    id: int
    media_url: Optional[str] = None
    type_media: Optional[str] = None
    date_envoi: Optional[datetime] = None
    statut_livraison: Optional[str] = None
    reponse: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Push Notification schemas
class PushNotificationBase(BaseModel):
    notification_id: int
    titre: str
    corps: str
    plateforme: str
    device_token: str


class PushNotificationCreate(PushNotificationBase):
    icone: str = ""
    image: str = ""
    badge: int = 0
    donnees: dict = {}
    son: str = ""
    action: str = ""
    url_action: str = ""


class PushNotificationResponse(PushNotificationBase):
    id: int
    icone: Optional[str] = None
    image: Optional[str] = None
    badge: int
    donnees: Optional[dict] = None
    son: Optional[str] = None
    action: Optional[str] = None
    url_action: Optional[str] = None
    date_envoi: Optional[datetime] = None
    statut_livraison: Optional[str] = None
    date_ouverture: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Rapport Notifications
class RapportNotificationsResponse(BaseModel):
    utilisateur_id: int
    total_notifications: int
    par_canal: dict
    par_statut: dict
    non_lues: int

"""Pydantic schemas for Integration module - External integrations for Cameroon/CEMAC"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Integration schemas
class IntegrationBase(BaseModel):
    code_integration: str
    type_integration: str
    nom: str
    url_api: str
    api_key: str


class IntegrationCreate(IntegrationBase):
    description: str = ""
    api_secret: str = ""
    cert_path: str = ""
    timeout: int = 30
    retry_attempts: int = 3
    frequence_synchronisation: str = ""
    configuration: str = ""
    parametres: str = ""
    logs_retention_jours: int = 30


class IntegrationUpdate(BaseModel):
    description: Optional[str] = None
    url_api: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    cert_path: Optional[str] = None
    timeout: Optional[int] = None
    retry_attempts: Optional[int] = None
    statut: Optional[str] = None
    date_desactivation: Optional[date] = None
    frequence_synchronisation: Optional[str] = None
    configuration: Optional[str] = None
    parametres: Optional[str] = None
    logs_retention_jours: Optional[int] = None
    actif: Optional[bool] = None


class IntegrationResponse(IntegrationBase):
    id: int
    description: Optional[str] = None
    api_secret: Optional[str] = None
    cert_path: Optional[str] = None
    timeout: int
    retry_attempts: int
    statut: str
    date_activation: Optional[date] = None
    date_desactivation: Optional[date] = None
    derniere_synchronisation: Optional[datetime] = None
    frequence_synchronisation: Optional[str] = None
    configuration: Optional[str] = None
    parametres: Optional[str] = None
    logs_retention_jours: int
    actif: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Requete Integration schemas
class RequeteIntegrationBase(BaseModel):
    integration_id: int
    numero_requete: str
    type_requete: str
    direction: str
    donnees_envoyees: str


class RequeteIntegrationCreate(RequeteIntegrationBase):
    headers: str = ""


class RequeteIntegrationUpdate(BaseModel):
    donnees_recues: Optional[str] = None
    headers: Optional[str] = None
    statut: Optional[str] = None
    code_reponse: Optional[int] = None
    message_erreur: Optional[str] = None
    reference_externe: Optional[str] = None
    correlation_id: Optional[str] = None


class RequeteIntegrationResponse(RequeteIntegrationBase):
    id: int
    headers: Optional[str] = None
    donnees_recues: Optional[str] = None
    statut: str
    date_creation: datetime
    date_envoi: Optional[datetime] = None
    date_reponse: Optional[datetime] = None
    duree_ms: Optional[int] = None
    code_reponse: Optional[int] = None
    message_erreur: Optional[str] = None
    reference_externe: Optional[str] = None
    correlation_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# Webhook Integration schemas
class WebhookIntegrationBase(BaseModel):
    integration_id: int
    nom: str
    url_webhook: str


class WebhookIntegrationCreate(WebhookIntegrationBase):
    evenements: str = ""
    secret: str = ""


class WebhookIntegrationUpdate(BaseModel):
    evenements: Optional[str] = None
    secret: Optional[str] = None
    statut: Optional[str] = None


class WebhookIntegrationResponse(WebhookIntegrationBase):
    id: int
    evenements: Optional[str] = None
    secret: Optional[str] = None
    statut: str
    derniere_utilisation: Optional[datetime] = None
    nombre_reussites: int
    nombre_echecs: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# SYDONIA Plus schemas
class SYDONIAPlusBase(BaseModel):
    numero_dossier: str
    bureau_douane: str
    type_operation: str
    regime: str


class SYDONIAPlusCreate(SYDONIAPlusBase):
    numero_declaration: str = ""
    date_declaration: date = None


class SYDONIAPlusUpdate(BaseModel):
    numero_declaration: Optional[str] = None
    date_declaration: Optional[date] = None
    statut_douane: Optional[str] = None
    date_statut: Optional[date] = None
    valeur_douane: Optional[float] = None
    droits_taxes: Optional[float] = None
    numero_tva: Optional[str] = None
    montant_tva: Optional[float] = None
    date_validation: Optional[date] = None
    numero_bad: Optional[str] = None
    date_bad: Optional[date] = None
    observateur_douane: Optional[str] = None


class SYDONIAPlusResponse(SYDONIAPlusBase):
    id: int
    numero_declaration: Optional[str] = None
    date_declaration: Optional[date] = None
    statut_douane: Optional[str] = None
    date_statut: Optional[date] = None
    valeur_douane: Optional[float] = None
    droits_taxes: Optional[float] = None
    numero_tva: Optional[str] = None
    montant_tva: Optional[float] = None
    date_validation: Optional[date] = None
    numero_bad: Optional[str] = None
    date_bad: Optional[date] = None
    observateur_douane: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Guichet Unique schemas
class GuichetUniqueBase(BaseModel):
    numero_transaction: str
    service: str
    type_service: str
    utilisateur: str


class GuichetUniqueCreate(GuichetUniqueBase):
    reference_externe: str = ""


class GuichetUniqueUpdate(BaseModel):
    reference_externe: Optional[str] = None
    statut: Optional[str] = None
    resultat: Optional[str] = None
    date_resultat: Optional[datetime] = None
    erreur: Optional[str] = None
    ip_origine: Optional[str] = None


class GuichetUniqueResponse(GuichetUniqueBase):
    id: int
    reference_externe: Optional[str] = None
    statut: str
    date_transaction: datetime
    resultat: Optional[str] = None
    date_resultat: Optional[datetime] = None
    erreur: Optional[str] = None
    ip_origine: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# PCS schemas
class PCSBase(BaseModel):
    reference_pcs: str
    type_operation: str
    navire: str
    port: str


class PCSCreate(PCSBase):
    voyage: str = ""
    date_operation: date = None
    numero_equipement: str = ""
    type_equipement: str = ""
    poids: float = 0.0
    unite_poids: str = ""
    nombre_conteneurs: int = 0
    observateur: str = ""


class PCSUpdate(BaseModel):
    voyage: Optional[str] = None
    date_operation: Optional[date] = None
    numero_equipement: Optional[str] = None
    type_equipement: Optional[str] = None
    statut_pcs: Optional[str] = None
    date_statut: Optional[date] = None
    poids: Optional[float] = None
    unite_poids: Optional[str] = None
    nombre_conteneurs: Optional[int] = None
    observateur: Optional[str] = None


class PCSResponse(PCSBase):
    id: int
    voyage: Optional[str] = None
    date_operation: date
    numero_equipement: Optional[str] = None
    type_equipement: Optional[str] = None
    statut_pcs: str
    date_statut: Optional[date] = None
    poids: float
    unite_poids: Optional[str] = None
    nombre_conteneurs: int
    observateur: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Integration Banque schemas
class IntegrationBanqueBase(BaseModel):
    banque_id: int
    code_banque: str
    nom_banque: str
    bic: str
    iban: str


class IntegrationBanqueCreate(IntegrationBanqueBase):
    api_endpoint: str = ""
    api_key: str = ""
    type_service: str = ""


class IntegrationBanqueUpdate(BaseModel):
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    type_service: Optional[str] = None
    statut: Optional[str] = None
    date_activation: Optional[date] = None
    derniere_synchronisation: Optional[datetime] = None
    solde: Optional[float] = None


class IntegrationBanqueResponse(IntegrationBanqueBase):
    id: int
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    type_service: Optional[str] = None
    statut: str
    date_activation: Optional[date] = None
    derniere_synchronisation: Optional[datetime] = None
    solde: Optional[float] = None
    devise: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Integration Assureur schemas
class IntegrationAssureurBase(BaseModel):
    assureur_id: int
    code_assureur: str
    nom_assureur: str
    type_assurance: str


class IntegrationAssureurCreate(IntegrationAssureurBase):
    numero_police: str = ""
    date_debut: date = None
    date_fin: date = None
    montant_assure: float = 0.0
    franchise: float = 0.0
    prime: float = 0.0


class IntegrationAssureurUpdate(BaseModel):
    numero_police: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    montant_assure: Optional[float] = None
    franchise: Optional[float] = None
    prime: Optional[float] = None
    statut: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None


class IntegrationAssureurResponse(IntegrationAssureurBase):
    id: int
    numero_police: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    montant_assure: float
    franchise: float
    prime: float
    devise: str
    statut: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Integration Transitaire schemas
class IntegrationTransitaireBase(BaseModel):
    transitaire_id: int
    code_transitaire: str
    nom_transitaire: str
    type_service: str


class IntegrationTransitaireCreate(IntegrationTransitaireBase):
    numero_agrement: str = ""
    bureau: str = ""


class IntegrationTransitaireUpdate(BaseModel):
    numero_agrement: Optional[str] = None
    bureau: Optional[str] = None
    statut: Optional[str] = None
    date_activation: Optional[date] = None
    derniere_synchronisation: Optional[datetime] = None
    numero_dossiers: Optional[int] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None


class IntegrationTransitaireResponse(IntegrationTransitaireBase):
    id: int
    numero_agrement: Optional[str] = None
    bureau: Optional[str] = None
    statut: str
    date_activation: Optional[date] = None
    derniere_synchronisation: Optional[datetime] = None
    numero_dossiers: int
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Synchronisation schemas
class SynchronisationBase(BaseModel):
    integration_id: int
    type_synchronisation: str
    lance_par: str


class SynchronisationCreate(SynchronisationBase):
    pass


class SynchronisationUpdate(BaseModel):
    statut: Optional[str] = None
    enregistrements_traites: Optional[int] = None
    enregistrements_echoues: Optional[int] = None
    duree_secondes: Optional[int] = None
    details: Optional[str] = None
    erreur: Optional[str] = None


class SynchronisationResponse(SynchronisationBase):
    id: int
    date_debut: datetime
    date_fin: Optional[datetime] = None
    statut: str
    enregistrements_traites: int
    enregistrements_echoues: int
    duree_secondes: Optional[int] = None
    details: Optional[str] = None
    erreur: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Rapport Integration
class RapportIntegrationResponse(BaseModel):
    integration: dict
    requetes: dict
    synchronisations: dict

"""Integration models - External integrations for Cameroon/CEMAC (SYDONIA+, GUICHET UNIQUE, PCS, Banks, Insurers, Forwarders)"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeIntegration(str, enum.Enum):
    """Integration type enumeration"""
    SYDONIA = "sydonia"
    GUICHET_UNIQUE = "guichet_unique"
    PCS = "pcs"
    BANQUE = "banque"
    ASSUREUR = "assureur"
    TRANSITAIRE = "transitaire"
    AUTRE = "autre"


class StatutIntegration(str, enum.Enum):
    """Integration status enumeration"""
    ACTIF = "actif"
    INACTIF = "inactif"
    ERREUR = "erreur"
    SYNCHRONISATION = "synchronisation"
    BLOQUE = "bloque"


class TypeRequete(str, enum.Enum):
    """Request type enumeration"""
    DECLARATION = "declaration"
    VALIDATION = "validation"
    CONSULTATION = "consultation"
    ANNULATION = "annulation"
    PAYEMENT = "paiement"
    TRANSFERT = "transfert"
    AUTRE = "autre"


class StatutRequete(str, enum.Enum):
    """Request status enumeration"""
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    SUCCES = "succes"
    ECHEC = "echec"
    ANNULE = "annule"
    EXPIRE = "expire"


class Integration(Base):
    """External integration configuration"""
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    code_integration = Column(String(50), unique=True, nullable=False, index=True)
    type_integration = Column(Enum(TypeIntegration))
    nom = Column(String(200), nullable=False)
    description = Column(Text)
    url_api = Column(String(500))
    api_key = Column(String(255))
    api_secret = Column(String(255))
    cert_path = Column(String(255))
    timeout = Column(Integer, default=30)
    retry_attempts = Column(Integer, default=3)
    statut = Column(Enum(StatutIntegration), default=StatutIntegration.ACTIF)
    date_activation = Column(Date)
    date_desactivation = Column(Date)
    derniere_synchronisation = Column(DateTime(timezone=True))
    frequence_synchronisation = Column(String(50))  # "continu", "quotidien", "hebdomadaire"
    configuration = Column(Text)  # JSON
    parametres = Column(Text)  # JSON
    logs_retention_jours = Column(Integer, default=30)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    requetes = relationship("RequeteIntegration", back_populates="integration")
    webhooks = relationship("WebhookIntegration", back_populates="integration")


class RequeteIntegration(Base):
    """Integration request log"""
    __tablename__ = "requetes_integration"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey('integrations.id'))
    numero_requete = Column(String(50), unique=True, nullable=False, index=True)
    type_requete = Column(Enum(TypeRequete))
    direction = Column(String(20))  # "entrant", "sortant"
    donnees_envoyees = Column(Text)  # JSON
    donnees_recues = Column(Text)  # JSON
    headers = Column(Text)  # JSON
    statut = Column(Enum(StatutRequete), default=StatutRequete.EN_ATTENTE)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_envoi = Column(DateTime(timezone=True))
    date_reponse = Column(DateTime(timezone=True))
    duree_ms = Column(Integer)
    code_reponse = Column(Integer)
    message_erreur = Column(Text)
    reference_externe = Column(String(100))
    correlation_id = Column(String(100))
    
    # Relationships
    integration = relationship("Integration", back_populates="requetes")


class WebhookIntegration(Base):
    """Webhook configuration"""
    __tablename__ = "webhooks_integration"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey('integrations.id'))
    nom = Column(String(200), nullable=False)
    url_webhook = Column(String(500), nullable=False)
    evenements = Column(Text)  # JSON array
    secret = Column(String(255))
    statut = Column(String(20), default="actif")  # actif, inactif
    derniere_utilisation = Column(DateTime(timezone=True))
    nombre_reussites = Column(Integer, default=0)
    nombre_echecs = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration", back_populates="webhooks")


class SYDONIAPlus(Base):
    """SYDONIA+ integration"""
    __tablename__ = "sydonia_plus"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_dossier = Column(String(50), unique=True, nullable=False, index=True)
    bureau_douane = Column(String(100), nullable=False)
    type_operation = Column(String(50))  # "import", "export", "transit"
    regime = Column(String(50))
    numero_declaration = Column(String(50))
    date_declaration = Column(Date)
    statut_douane = Column(String(50))
    date_statut = Column(Date)
    valeur_douane = Column(Numeric(15, 2))
    droits_taxes = Column(Numeric(15, 2))
    numero_tva = Column(String(50))
    montant_tva = Column(Numeric(15, 2))
    date_validation = Column(Date)
    numero_bad = Column(String(50))
    date_bad = Column(Date)
    observateur_douane = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GuichetUnique(Base):
    """GUICHET UNIQUE integration"""
    __tablename__ = "guichet_unique"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_transaction = Column(String(50), unique=True, nullable=False, index=True)
    service = Column(String(100), nullable=False)
    type_service = Column(String(50))
    date_transaction = Column(DateTime(timezone=True), nullable=False)
    utilisateur = Column(String(100))
    reference_externe = Column(String(100))
    statut = Column(String(20), default="en_cours")
    resultat = Column(Text)  # JSON
    date_resultat = Column(DateTime(timezone=True))
    erreur = Column(Text)
    ip_origine = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PCS(Base):
    """PCS (Port Community System) integration"""
    __tablename__ = "pcs"
    
    id = Column(Integer, primary_key=True, index=True)
    reference_pcs = Column(String(50), unique=True, nullable=False, index=True)
    type_operation = Column(String(50))
    navire = Column(String(200))
    voyage = Column(String(50))
    port = Column(String(100))
    date_operation = Column(Date)
    numero_equipement = Column(String(50))
    type_equipement = Column(String(50))
    statut_pcs = Column(String(20))
    date_statut = Column(Date)
    poids = Column(Numeric)
    unite_poids = Column(String(20))
    nombre_conteneurs = Column(Integer)
    observateur = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IntegrationBanque(Base):
    """Bank integration"""
    __tablename__ = "integrations_banque"
    
    id = Column(Integer, primary_key=True, index=True)
    banque_id = Column(Integer, ForeignKey('tiers.id'))
    code_banque = Column(String(50), unique=True, nullable=False, index=True)
    nom_banque = Column(String(200), nullable=False)
    bic = Column(String(11))
    iban = Column(String(34))
    api_endpoint = Column(String(500))
    api_key = Column(String(255))
    type_service = Column(String(50))  # "virement", "releve", "prelevement"
    statut = Column(String(20), default="actif")
    date_activation = Column(Date)
    derniere_synchronisation = Column(DateTime(timezone=True))
    solde = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IntegrationAssureur(Base):
    """Insurer integration"""
    __tablename__ = "integrations_assureur"
    
    id = Column(Integer, primary_key=True, index=True)
    assureur_id = Column(Integer, ForeignKey('tiers.id'))
    code_assureur = Column(String(50), unique=True, nullable=False, index=True)
    nom_assureur = Column(String(200), nullable=False)
    numero_police = Column(String(50))
    type_assurance = Column(String(50))  # "fap", "transport", "responsabilite"
    date_debut = Column(Date)
    date_fin = Column(Date)
    montant_assure = Column(Numeric(15, 2))
    franchise = Column(Numeric(15, 2))
    prime = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    statut = Column(String(20), default="actif")
    api_endpoint = Column(String(500))
    api_key = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IntegrationTransitaire(Base):
    """Forwarder integration"""
    __tablename__ = "integrations_transitaire"
    
    id = Column(Integer, primary_key=True, index=True)
    transitaire_id = Column(Integer, ForeignKey('tiers.id'))
    code_transitaire = Column(String(50), unique=True, nullable=False, index=True)
    nom_transitaire = Column(String(200), nullable=False)
    numero_agrement = Column(String(50))
    bureau = Column(String(100))
    type_service = Column(String(50))  # "transit", "courtage", "consignation"
    api_endpoint = Column(String(500))
    api_key = Column(String(255))
    statut = Column(String(20), default="actif")
    date_activation = Column(Date)
    derniere_synchronisation = Column(DateTime(timezone=True))
    numero_dossiers = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Synchronisation(Base):
    """Synchronization record"""
    __tablename__ = "synchronisations"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey('integrations.id'))
    type_synchronisation = Column(String(50))  # "full", "incremental", "on_demand"
    date_debut = Column(DateTime(timezone=True), nullable=False)
    date_fin = Column(DateTime(timezone=True))
    statut = Column(String(20), default="en_cours")  # en_cours, succes, echec, annule
    enregistrements_traites = Column(Integer, default=0)
    enregistrements_echoues = Column(Integer, default=0)
    duree_secondes = Column(Integer)
    details = Column(Text)  # JSON
    erreur = Column(Text)
    lance_par = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

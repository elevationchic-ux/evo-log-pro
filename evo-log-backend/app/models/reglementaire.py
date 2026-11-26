"""Regulatory and Documentation Models - Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeReglementation(str, enum.Enum):
    """Regulation type enumeration"""
    LOI = "loi"
    DECRET = "decret"
    ARRETE = "arrete"
    CIRCULAIRE = "circulaire"
    NORME = "norme"
    DIRECTIVE = "directive"


class TypeDocument(str, enum.Enum):
    """Document type enumeration"""
    MANUEL = "manuel"
    GUIDE = "guide"
    PROCEDURE = "procedure"
    FAQ = "faq"
    TUTORIEL = "tutoriel"
    VIDEO = "video"
    CHECKLIST = "checklist"


class Reglementation(Base):
    """Réglementation Cameroun/CEMAC"""
    __tablename__ = "reglementations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    titre = Column(String(200), nullable=False)
    type_reglement = Column(Enum(TypeReglementation), nullable=False)
    numero = Column(String(50))  # Numéro officiel
    date_promulgation = Column(Date, nullable=False)
    date_application = Column(Date, nullable=False)
    ministere = Column(String(100))
    description = Column(Text, nullable=False)
    resume = Column(Text)
    url_officielle = Column(String(255))
    fichier_pdf = Column(String(255))
    est_actif = Column(Boolean, default=True)
    version = Column(String(20))
    date_maj = Column(Date)
    categorie = Column(String(50))  # DOUANE, TRANSPORT, FISCALITE, ENVIRONNEMENT
    mots_cles = Column(Text)  # JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AlerteReglementaire(Base):
    """Alerte réglementaire - Changements de lois"""
    __tablename__ = "alertes_reglementaires"
    
    id = Column(Integer, primary_key=True, index=True)
    reglementation_id = Column(Integer, ForeignKey('reglementations.id'))
    type_alerte = Column(String(20), nullable=False)  # NOUVEAU, MODIFICATION, ABROGATION
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    date_publication = Column(Date, nullable=False)
    date_application = Column(Date)
    severite = Column(String(20), default="moyenne")  # faible, moyenne, critique
    impact_operationnel = Column(Text)
    actions_requises = Column(Text)  # JSON
    est_resolue = Column(Boolean, default=False)
    date_resolution = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DocumentUtilisateur(Base):
    """Document utilisateur - Manuels, guides, tutoriels"""
    __tablename__ = "documents_utilisateur"
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200), nullable=False)
    type_document = Column(Enum(TypeDocument), nullable=False)
    categorie = Column(String(50), nullable=False)  # DOUANE, TRANSPORT, FINANCE, GENERAL
    sous_categorie = Column(String(50))
    contenu = Column(Text, nullable=False)  # Markdown
    contenu_html = Column(Text)
    video_url = Column(String(255))
    duree_minutes = Column(Integer)
    langue = Column(String(10), default="fr")
    niveau = Column(String(20), default="debutant")  # debutant, intermediaire, avance
    date_publication = Column(Date, nullable=False)
    auteur = Column(String(100))
    version = Column(String(20))
    fichier_pdf = Column(String(255))
    est_publie = Column(Boolean, default=True)
    nombre_vues = Column(Integer, default=0)
    nombre_telechargements = Column(Integer, default=0)
    note = Column(Numeric)  # Rating 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProcedureOperationnelle(Base):
    """Procédure opérationnelle - Guide étape par étape"""
    __tablename__ = "procedures_operationnelles"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    categorie = Column(String(50), nullable=False)  # IMPORT, EXPORT, TRANSIT, ACCESSION
    duree_estimee_minutes = Column(Integer)
    difficulte = Column(String(20), default="moyenne")  # facile, moyenne, difficile
    documents_requis = Column(Text)  # JSON array
    preconditions = Column(Text)  # JSON array
    etapes = Column(Text, nullable=False)  # JSON array
    risques = Column(Text)  # JSON array
    alternatives = Column(Text)  # JSON array
    est_actif = Column(Boolean, default=True)
    date_creation = Column(Date, nullable=False)
    date_maj = Column(Date)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FAQ(Base):
    """FAQ - Questions Fréquentes"""
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500), nullable=False)
    reponse = Column(Text, nullable=False)
    categorie = Column(String(50), nullable=False)
    sous_categorie = Column(String(50))
    mots_cles = Column(Text)  # JSON array
    ordre = Column(Integer, default=0)
    langue = Column(String(10), default="fr")
    nombre_vues = Column(Integer, default=0)
    est_utile = Column(Integer, default=0)
    est_publie = Column(Boolean, default=True)
    date_creation = Column(Date, nullable=False)
    date_maj = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

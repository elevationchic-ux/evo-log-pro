"""Documents models - Electronic document management for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, LargeBinary, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeDocument(str, enum.Enum):
    """Document type enumeration"""
    FACTURE = "facture"
    CONNAISSEMENT = "connaissement"
    CERTIFICAT = "certificat"
    CONTRAT = "contrat"
    RAPPORT = "rapport"
    COURRIER = "courrier"
    IMAGE = "image"
    PLAN = "plan"
    AUTRE = "autre"


class StatutDocument(str, enum.Enum):
    """Document status enumeration"""
    BROUILLON = "brouillon"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    REJETE = "rejete"
    EXPIRE = "expire"
    ANNULE = "annule"
    ARCHIVE = "archive"


class EtapeWorkflow(str, enum.Enum):
    """Workflow step enumeration"""
    CREATION = "creation"
    VALIDATION = "validation"
    APPROBATION = "approbation"
    SIGNATURE = "signature"
    FINALISATION = "finalisation"
    ARCHIVAGE = "archivage"


class StatutWorkflow(str, enum.Enum):
    """Workflow status enumeration"""
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    REJETE = "rejete"
    TERMINE = "termine"


class Document(Base):
    """Document entity"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_document = Column(String(50), unique=True, nullable=False, index=True)
    type_document = Column(Enum(TypeDocument))
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    proprietaire_id = Column(Integer, ForeignKey('users.id'))
    dossier_id = Column(Integer, ForeignKey('dossiers.id'))
    fichier = Column(LargeBinary)
    nom_fichier = Column(String(255))
    type_mime = Column(String(100))
    taille_octets = Column(Integer)
    emplacement_stockage = Column(String(500))
    checksum = Column(String(64))  # SHA-256
    statut = Column(Enum(StatutDocument), default=StatutDocument.BROUILLON)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    date_expiration = Column(Date)
    confidential = Column(Boolean, default=False)
    mots_cles = Column(Text)  # JSON array
    version = Column(Integer, default=1)
    version_active = Column(Boolean, default=True)
    cree_par = Column(String(100))
    modifie_par = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dossier = relationship("Dossier", back_populates="documents")
    versions = relationship("VersionDocument", back_populates="document")
    signatures = relationship("SignatureDocument", back_populates="document")
    workflows = relationship("WorkflowDocument", back_populates="document")


class Dossier(Base):
    """Folder/Directory"""
    __tablename__ = "dossiers"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False)
    dossier_parent_id = Column(Integer, ForeignKey('dossiers.id'))
    proprietaire_id = Column(Integer, ForeignKey('users.id'))
    description = Column(Text)
    chemin = Column(String(500))
    statut = Column(String(20), default="actif")  # actif, archive
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    cree_par = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="dossier")
    dossiers_enfants = relationship("Dossier")


class VersionDocument(Base):
    """Document version"""
    __tablename__ = "versions_document"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    numero_version = Column(Integer, nullable=False)
    fichier = Column(LargeBinary)
    nom_fichier = Column(String(255))
    type_mime = Column(String(100))
    taille_octets = Column(Integer)
    emplacement_stockage = Column(String(500))
    checksum = Column(String(64))
    modifications = Column(Text)
    modifie_par = Column(String(100))
    date_version = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="versions")


class SignatureDocument(Base):
    """Electronic signature"""
    __tablename__ = "signatures_document"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    signataire_id = Column(Integer, ForeignKey('users.id'))
    type_signature = Column(String(50))  # "electronique", "numerique", "manuscrite"
    date_signature = Column(DateTime(timezone=True), nullable=False)
    certificat_id = Column(String(100))
    empreinte = Column(String(255))
    raison = Column(String(200))
    statut = Column(String(20), default="valide")  # valide, expire, revoque
    date_expiration = Column(Date)
    ip_adresse = Column(String(50))
    user_agent = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="signatures")


class WorkflowDocument(Base):
    """Document workflow"""
    __tablename__ = "workflows_document"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    nom_workflow = Column(String(100), nullable=False)
    etape_actuelle = Column(Enum(EtapeWorkflow))
    statut = Column(Enum(StatutWorkflow), default=StatutWorkflow.EN_ATTENTE)
    date_debut = Column(DateTime(timezone=True), server_default=func.now())
    date_fin = Column(DateTime(timezone=True))
    initiateur_id = Column(Integer, ForeignKey('users.id'))
    approbateur_id = Column(Integer, ForeignKey('users.id'))
    commentaires = Column(Text)
    historique = Column(Text)  # JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="workflows")


class SceauNumerique(Base):
    """Digital seal"""
    __tablename__ = "sceaux_numeriques"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    numero_sceau = Column(String(100), unique=True, nullable=False, index=True)
    type_sceau = Column(String(50))  # "temporel", "permanent", "officiel"
    createur_id = Column(Integer, ForeignKey('users.id'))
    date_creation = Column(DateTime(timezone=True), nullable=False)
    date_expiration = Column(Date)
    contenu_sceau = Column(Text)
    url_sceau = Column(String(500))
    statut = Column(String(20), default="actif")  # actif, expire, revoque
    public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalyseOCR(Base):
    """OCR analysis"""
    __tablename__ = "analyses_ocr"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    date_analyse = Column(DateTime(timezone=True), server_default=func.now())
    langue = Column(String(10), default="fra")
    texte_extrait = Column(Text)
    confidence = Column(Numeric)
    donnees_structurees = Column(Text)  # JSON
    mots_cles = Column(Text)  # JSON array
    tableaux = Column(Text)  # JSON array
    statut = Column(String(20), default="traite")  # traite, succes, echec
    duree_traitement = Column(Integer)  # en secondes
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ArchivageLegal(Base):
    """Legal archiving"""
    __tablename__ = "archivages_legal"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    type_archivage = Column(String(50))  # "fiscal", "juridique", "comptable", "autre"
    duree_conservation = Column(Integer)  # en mois
    date_archivage = Column(DateTime(timezone=True), server_default=func.now())
    date_expiration = Column(Date)
    numero_archivage = Column(String(50), unique=True, nullable=False, index=True)
    autorite_archivage = Column(String(100))
    reference_archivage = Column(String(100))
    classification = Column(String(50))  # "confidentiel", "prive", "public"
    conformite = Column(Boolean, default=True)
    verification_conformite = Column(Text)
    certificat_conformite = Column(String(255))
    statut = Column(String(20), default="archive")  # archive, restaure, detruit
    date_restauration = Column(Date)
    motif_restauration = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TemplateDocument(Base):
    """Document template"""
    __tablename__ = "templates_document"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False)
    type_document = Column(Enum(TypeDocument))
    categorie = Column(String(50))
    description = Column(Text)
    contenu = Column(Text)  # HTML/Markdown template
    variables = Column(Text)  # JSON array of variables
    proprietaire_id = Column(Integer, ForeignKey('users.id'))
    statut = Column(String(20), default="actif")  # actif, inactif
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    cree_par = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PartageDocument(Base):
    """Document sharing"""
    __tablename__ = "partages_document"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    partage_par = Column(Integer, ForeignKey('users.id'))
    partage_avec = Column(Integer, ForeignKey('users.id'))
    type_partage = Column(String(20))  # "lecture", "ecriture", "complet"
    date_partage = Column(DateTime(timezone=True), server_default=func.now())
    date_expiration = Column(Date)
    mot_debut = Column(String(200))
    statut = Column(String(20), default="actif")  # actif, expire, revoque
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HistoriqueDocument(Base):
    """Document history"""
    __tablename__ = "historique_document"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    date_action = Column(DateTime(timezone=True), server_default=func.now())
    action = Column(String(100), nullable=False)  # "creation", "modification", "suppression", "visionnage", "telechargement"
    utilisateur_id = Column(Integer, ForeignKey('users.id'))
    details = Column(Text)
    adresse_ip = Column(String(50))
    user_agent = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

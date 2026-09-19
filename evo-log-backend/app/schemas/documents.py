"""Pydantic schemas for Documents module - Electronic document management"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Document schemas
class DocumentBase(BaseModel):
    numero_document: str
    type_document: str
    titre: str
    proprietaire_id: int


class DocumentCreate(DocumentBase):
    dossier_id: int = None
    description: str = ""
    date_expiration: date = None
    confidential: bool = False
    mots_cles: str = ""


class DocumentUpdate(BaseModel):
    description: Optional[str] = None
    statut: Optional[str] = None
    date_expiration: Optional[date] = None
    confidential: Optional[bool] = None
    mots_cles: Optional[str] = None
    modifie_par: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    dossier_id: Optional[int] = None
    description: Optional[str] = None
    nom_fichier: Optional[str] = None
    type_mime: Optional[str] = None
    taille_octets: Optional[int] = None
    emplacement_stockage: Optional[str] = None
    checksum: Optional[str] = None
    statut: str
    date_creation: datetime
    date_modification: Optional[datetime] = None
    date_expiration: Optional[date] = None
    confidential: bool
    mots_cles: Optional[str] = None
    version: int
    version_active: bool
    cree_par: str
    modifie_par: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Dossier schemas
class DossierBase(BaseModel):
    nom: str
    proprietaire_id: int


class DossierCreate(DossierBase):
    dossier_parent_id: int = None
    description: str = ""


class DossierUpdate(BaseModel):
    description: Optional[str] = None
    statut: Optional[str] = None


class DossierResponse(DossierBase):
    id: int
    dossier_parent_id: Optional[int] = None
    description: Optional[str] = None
    chemin: Optional[str] = None
    statut: str
    date_creation: datetime
    cree_par: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Version Document schemas
class VersionDocumentBase(BaseModel):
    document_id: int
    numero_version: int
    nom_fichier: str
    type_mime: str


class VersionDocumentCreate(VersionDocumentBase):
    modifications: str = ""


class VersionDocumentResponse(VersionDocumentBase):
    id: int
    taille_octets: Optional[int] = None
    emplacement_stockage: Optional[str] = None
    checksum: Optional[str] = None
    modifications: Optional[str] = None
    modifie_par: str
    date_version: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Signature Document schemas
class SignatureDocumentBase(BaseModel):
    document_id: int
    signataire_id: int
    type_signature: str
    certificat_id: str
    raison: str


class SignatureDocumentCreate(SignatureDocumentBase):
    pass


class SignatureDocumentUpdate(BaseModel):
    statut: Optional[str] = None
    date_expiration: Optional[date] = None


class SignatureDocumentResponse(SignatureDocumentBase):
    id: int
    date_signature: datetime
    empreinte: Optional[str] = None
    statut: str
    date_expiration: Optional[date] = None
    ip_adresse: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Workflow Document schemas
class WorkflowDocumentBase(BaseModel):
    document_id: int
    nom_workflow: str


class WorkflowDocumentCreate(WorkflowDocumentBase):
    initiateur_id: int
    approbateur_id: int = None
    commentaires: str = ""


class WorkflowDocumentUpdate(BaseModel):
    etape_actuelle: Optional[str] = None
    statut: Optional[str] = None
    approbateur_id: Optional[int] = None
    commentaires: Optional[str] = None
    date_fin: Optional[datetime] = None


class WorkflowDocumentResponse(WorkflowDocumentBase):
    id: int
    etape_actuelle: str
    statut: str
    date_debut: datetime
    date_fin: Optional[datetime] = None
    initiateur_id: int
    approbateur_id: Optional[int] = None
    commentaires: Optional[str] = None
    historique: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Sceau Numerique schemas
class SceauNumeriqueBase(BaseModel):
    document_id: int
    numero_sceau: str
    type_sceau: str
    createur_id: int


class SceauNumeriqueCreate(SceauNumeriqueBase):
    date_expiration: date = None
    contenu_sceau: str = ""
    url_sceau: str = ""
    public: bool = False


class SceauNumeriqueUpdate(BaseModel):
    contenu_sceau: Optional[str] = None
    url_sceau: Optional[str] = None
    public: Optional[bool] = None
    statut: Optional[str] = None


class SceauNumeriqueResponse(SceauNumeriqueBase):
    id: int
    date_creation: datetime
    date_expiration: Optional[date] = None
    contenu_sceau: Optional[str] = None
    url_sceau: Optional[str] = None
    statut: str
    public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Analyse OCR schemas
class AnalyseOCRBase(BaseModel):
    document_id: int
    langue: str
    texte_extrait: str
    confidence: float


class AnalyseOCRCreate(AnalyseOCRBase):
    donnees_structurees: str = ""
    mots_cles: str = ""
    tableaux: str = ""


class AnalyseOCRResponse(AnalyseOCRBase):
    id: int
    donnees_structurees: Optional[str] = None
    mots_cles: Optional[str] = None
    tableaux: Optional[str] = None
    statut: str
    duree_traitement: int
    date_analyse: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Archivage Legal schemas
class ArchivageLegalBase(BaseModel):
    document_id: int
    type_archivage: str
    duree_conservation: int
    autorite_archivage: str


class ArchivageLegalCreate(ArchivageLegalBase):
    classification: str = "prive"
    verification_conformite: str = ""
    certificat_conformite: str = ""


class ArchivageLegalUpdate(BaseModel):
    classification: Optional[str] = None
    conformite: Optional[bool] = None
    verification_conformite: Optional[str] = None
    certificat_conformite: Optional[str] = None
    statut: Optional[str] = None
    date_restauration: Optional[date] = None
    motif_restauration: Optional[str] = None


class ArchivageLegalResponse(ArchivageLegalBase):
    id: int
    date_archivage: datetime
    date_expiration: date
    numero_archivage: str
    reference_archivage: Optional[str] = None
    classification: str
    conformite: bool
    verification_conformite: Optional[str] = None
    certificat_conformite: Optional[str] = None
    statut: str
    date_restauration: Optional[date] = None
    motif_restauration: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Template Document schemas
class TemplateDocumentBase(BaseModel):
    nom: str
    type_document: str
    categorie: str
    contenu: str
    variables: str
    proprietaire_id: int


class TemplateDocumentCreate(TemplateDocumentBase):
    description: str = ""


class TemplateDocumentUpdate(BaseModel):
    description: Optional[str] = None
    statut: Optional[str] = None


class TemplateDocumentResponse(TemplateDocumentBase):
    id: int
    description: Optional[str] = None
    statut: str
    date_creation: datetime
    cree_par: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Partage Document schemas
class PartageDocumentBase(BaseModel):
    document_id: int
    partage_par: int
    partage_avec: int
    type_partage: str


class PartageDocumentCreate(PartageDocumentBase):
    date_expiration: date = None
    mot_debut: str = ""


class PartageDocumentUpdate(BaseModel):
    date_expiration: Optional[date] = None
    statut: Optional[str] = None


class PartageDocumentResponse(PartageDocumentBase):
    id: int
    date_partage: datetime
    date_expiration: Optional[date] = None
    mot_debut: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Historique Document schemas
class HistoriqueDocumentBase(BaseModel):
    document_id: int
    action: str
    utilisateur_id: int
    details: str


class HistoriqueDocumentCreate(HistoriqueDocumentBase):
    adresse_ip: str = ""
    user_agent: str = ""


class HistoriqueDocumentResponse(HistoriqueDocumentBase):
    id: int
    date_action: datetime
    adresse_ip: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Rapport Documents
class RapportDocumentsResponse(BaseModel):
    dossier_id: int
    total_documents: int
    par_type: dict
    par_statut: dict
    taille_totale: int

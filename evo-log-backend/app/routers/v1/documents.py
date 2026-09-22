"""Documents router - Electronic document management"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.documents import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DossierCreate, DossierUpdate, DossierResponse,
    VersionDocumentCreate, VersionDocumentResponse,
    SignatureDocumentCreate, SignatureDocumentUpdate, SignatureDocumentResponse,
    WorkflowDocumentCreate, WorkflowDocumentUpdate, WorkflowDocumentResponse,
    SceauNumeriqueCreate, SceauNumeriqueUpdate, SceauNumeriqueResponse,
    AnalyseOCRCreate, AnalyseOCRResponse,
    ArchivageLegalCreate, ArchivageLegalUpdate, ArchivageLegalResponse,
    TemplateDocumentCreate, TemplateDocumentUpdate, TemplateDocumentResponse,
    PartageDocumentCreate, PartageDocumentUpdate, PartageDocumentResponse,
    HistoriqueDocumentCreate, HistoriqueDocumentResponse,
    RapportDocumentsResponse
)
from app.services.documents_service import (
    DocumentService, DossierService, VersionDocumentService, SignatureDocumentService,
    WorkflowDocumentService, SceauNumeriqueService, AnalyseOCRService, ArchivageLegalService,
    TemplateDocumentService, PartageDocumentService, HistoriqueDocumentService,
    DocumentsReportingService
)
from app.models.documents import Document, Dossier, TemplateDocument

router = APIRouter(prefix="/documents", tags=["Documents"])


# ============ DOCUMENTS ============
@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def creer_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create document"""
    return DocumentService.creer_document(
        db, document.numero_document, document.type_document, document.titre,
        document.proprietaire_id, document.dossier_id, None,
        "placeholder.pdf", "application/pdf"
    )


@router.post("/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def uploader_document(
    dossier_id: int,
    type_document: str,
    titre: str,
    fichier: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload document file"""
    contenu = fichier.file.read()
    type_mime = fichier.content_type
    nom_fichier = fichier.filename
    
    from app.models.documents import TypeDocument
    numero_doc = f"DOC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return DocumentService.creer_document(
        db, numero_doc, TypeDocument(type_document), titre,
        current_user.id, dossier_id, contenu, nom_fichier, type_mime
    )


@router.put("/documents/{document_id}/valider", response_model=DocumentResponse)
def valider_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate document"""
    return DocumentService.valider_document(db, document_id)


@router.put("/documents/{document_id}", response_model=DocumentResponse)
def mettre_a_jour_document(
    document_id: int,
    document: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update document"""
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    for field, value in document.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ DOSSIERS ============
@router.post("/dossiers", response_model=DossierResponse, status_code=status.HTTP_201_CREATED)
def creer_dossier(
    dossier: DossierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create folder"""
    return DossierService.creer_dossier(
        db, dossier.nom, dossier.proprietaire_id,
        dossier.dossier_parent_id, dossier.description
    )


@router.put("/dossiers/{dossier_id}", response_model=DossierResponse)
def mettre_a_jour_dossier(
    dossier_id: int,
    dossier: DossierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update folder"""
    d = db.query(Dossier).filter(Dossier.id == dossier_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    for field, value in dossier.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ VERSIONS DOCUMENT ============
@router.post("/versions", response_model=VersionDocumentResponse, status_code=status.HTTP_201_CREATED)
def creer_version(
    version: VersionDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create document version"""
    return VersionDocumentService.creer_version(
        db, version.document_id, version.numero_version, None,
        version.nom_fichier, version.type_mime, version.modifications
    )


# ============ SIGNATURES ============
@router.post("/signatures", response_model=SignatureDocumentResponse, status_code=status.HTTP_201_CREATED)
def signer_document(
    signature: SignatureDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sign document electronically"""
    return SignatureDocumentService.signer_document(
        db, signature.document_id, signature.signataire_id,
        signature.type_signature, signature.certificat_id, signature.raison
    )


@router.put("/signatures/{signature_id}", response_model=SignatureDocumentResponse)
def mettre_a_jour_signature(
    signature_id: int,
    signature: SignatureDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update electronic signature"""
    s = db.query(SignatureDocument).filter(SignatureDocument.id == signature_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Signature non trouvée")
    
    for field, value in signature.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    
    db.commit()
    db.refresh(s)
    return s


# ============ WORKFLOWS ============
@router.post("/workflows", response_model=WorkflowDocumentResponse, status_code=status.HTTP_201_CREATED)
def creer_workflow(
    workflow: WorkflowDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create document workflow"""
    return WorkflowDocumentService.creer_workflow(
        db, workflow.document_id, workflow.nom_workflow, workflow.initiateur_id
    )


@router.put("/workflows/{workflow_id}/avancer", response_model=WorkflowDocumentResponse)
def avancer_etape(
    workflow_id: int,
    etape_suivante: str,
    approbateur_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Advance workflow step"""
    from app.models.documents import EtapeWorkflow
    return WorkflowDocumentService.avancer_etape(
        db, workflow_id, EtapeWorkflow(etape_suivante), approbateur_id
    )


@router.put("/workflows/{workflow_id}", response_model=WorkflowDocumentResponse)
def mettre_a_jour_workflow(
    workflow_id: int,
    workflow: WorkflowDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update workflow"""
    w = db.query(WorkflowDocument).filter(WorkflowDocument.id == workflow_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Workflow non trouvé")
    
    for field, value in workflow.model_dump(exclude_unset=True).items():
        setattr(w, field, value)
    
    db.commit()
    db.refresh(w)
    return w


# ============ SCEAUX NUMERIQUES ============
@router.post("/sceaux", response_model=SceauNumeriqueResponse, status_code=status.HTTP_201_CREATED)
def creer_sceau(
    sceau: SceauNumeriqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create digital seal"""
    return SceauNumeriqueService.creer_sceau(
        db, sceau.document_id, sceau.numero_sceau, sceau.type_sceau,
        sceau.createur_id, sceau.date_expiration
    )


@router.put("/sceaux/{sceau_id}", response_model=SceauNumeriqueResponse)
def mettre_a_jour_sceau(
    sceau_id: int,
    sceau: SceauNumeriqueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update digital seal"""
    s = db.query(SceauNumerique).filter(SceauNumerique.id == sceau_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sceau non trouvé")
    
    for field, value in sceau.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    
    db.commit()
    db.refresh(s)
    return s


# ============ ANALYSES OCR ============
@router.post("/analyses-ocr", response_model=AnalyseOCRResponse, status_code=status.HTTP_201_CREATED)
def creer_analyse_ocr(
    analyse: AnalyseOCRCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create OCR analysis"""
    return AnalyseOCRService.creer_analyse_ocr(
        db, analyse.document_id, analyse.langue, analyse.texte_extrait, analyse.confidence
    )


# ============ ARCHIVAGE LEGAL ============
@router.post("/archivages-legal", response_model=ArchivageLegalResponse, status_code=status.HTTP_201_CREATED)
def archiver_document(
    archivage: ArchivageLegalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive document legally"""
    return ArchivageLegalService.archiver_document(
        db, archivage.document_id, archivage.type_archivage,
        archivage.duree_conservation, archivage.autorite_archivage
    )


@router.put("/archivages-legal/{archivage_id}", response_model=ArchivageLegalResponse)
def mettre_a_jour_archivage(
    archivage_id: int,
    archivage: ArchivageLegalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update legal archiving"""
    a = db.query(ArchivageLegal).filter(ArchivageLegal.id == archivage_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Archivage non trouvé")
    
    for field, value in archivage.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ TEMPLATES ============
@router.post("/templates", response_model=TemplateDocumentResponse, status_code=status.HTTP_201_CREATED)
def creer_template(
    template: TemplateDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create document template"""
    return TemplateDocumentService.creer_template(
        db, template.nom, template.type_document, template.categorie,
        template.contenu, template.variables, template.proprietaire_id
    )


@router.put("/templates/{template_id}", response_model=TemplateDocumentResponse)
def mettre_a_jour_template(
    template_id: int,
    template: TemplateDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update document template"""
    t = db.query(TemplateDocument).filter(TemplateDocument.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    
    for field, value in template.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    
    db.commit()
    db.refresh(t)
    return t


# ============ PARTAGES ============
@router.post("/partages", response_model=PartageDocumentResponse, status_code=status.HTTP_201_CREATED)
def partager_document(
    partage: PartageDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Share document"""
    return PartageDocumentService.partager_document(
        db, partage.document_id, partage.partage_par, partage.partage_avec,
        partage.type_partage, partage.date_expiration
    )


@router.put("/partages/{partage_id}", response_model=PartageDocumentResponse)
def mettre_a_jour_partage(
    partage_id: int,
    partage: PartageDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update document sharing"""
    p = db.query(PartageDocument).filter(PartageDocument.id == partage_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Partage non trouvé")
    
    for field, value in partage.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ HISTORIQUE ============
@router.post("/historique", response_model=HistoriqueDocumentResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_action(
    historique: HistoriqueDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record document action"""
    return HistoriqueDocumentService.enregistrer_action(
        db, historique.document_id, historique.action, historique.utilisateur_id,
        historique.details, historique.adresse_ip, historique.user_agent
    )


@router.get("/dossiers/{dossier_id}/rapport", response_model=RapportDocumentsResponse)
def rapport_documents(
    dossier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate documents report"""
    return DocumentsReportingService.rapport_documents(db, dossier_id)

"""Documents service - Electronic document management for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.documents import (
    Document, Dossier, VersionDocument, SignatureDocument, WorkflowDocument,
    SceauNumerique, AnalyseOCR, ArchivageLegal, TemplateDocument, PartageDocument, HistoriqueDocument,
    TypeDocument, StatutDocument, EtapeWorkflow, StatutWorkflow
)


class DocumentService:
    """Document service"""
    
    @staticmethod
    def creer_document(
        db: Session,
        numero_document: str,
        type_document: TypeDocument,
        titre: str,
        proprietaire_id: int,
        dossier_id: int,
        fichier: bytes,
        nom_fichier: str,
        type_mime: str
    ) -> Document:
        """Create document"""
        document = Document(
            numero_document=numero_document,
            type_document=type_document,
            titre=titre,
            proprietaire_id=proprietaire_id,
            dossier_id=dossier_id,
            fichier=fichier,
            nom_fichier=nom_fichier,
            type_mime=type_mime,
            taille_octets=len(fichier),
            statut=StatutDocument.BROUILLON,
            version=1,
            version_active=True,
            cree_par="system"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    @staticmethod
    def valider_document(db: Session, document_id: int) -> Document:
        """Validate document"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document non trouvé")
        
        document.statut = StatutDocument.VALIDE
        document.date_modification = datetime.utcnow()
        db.commit()
        db.refresh(document)
        return document


class DossierService:
    """Folder service"""
    
    @staticmethod
    def creer_dossier(
        db: Session,
        nom: str,
        proprietaire_id: int,
        dossier_parent_id: int = None,
        description: str = ""
    ) -> Dossier:
        """Create folder"""
        dossier = Dossier(
            nom=nom,
            proprietaire_id=proprietaire_id,
            dossier_parent_id=dossier_parent_id,
            description=description,
            statut="actif",
            cree_par="system"
        )
        db.add(dossier)
        db.commit()
        db.refresh(dossier)
        return dossier


class VersionDocumentService:
    """Document version service"""
    
    @staticmethod
    def creer_version(
        db: Session,
        document_id: int,
        numero_version: int,
        fichier: bytes,
        nom_fichier: str,
        type_mime: str,
        modifications: str
    ) -> VersionDocument:
        """Create document version"""
        version = VersionDocument(
            document_id=document_id,
            numero_version=numero_version,
            fichier=fichier,
            nom_fichier=nom_fichier,
            type_mime=type_mime,
            taille_octets=len(fichier),
            modifications=modifications,
            modifie_par="system"
        )
        db.add(version)
        
        # Update document version
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.version = numero_version
            document.date_modification = datetime.utcnow()
        
        db.commit()
        db.refresh(version)
        return version


class SignatureDocumentService:
    """Electronic signature service"""
    
    @staticmethod
    def signer_document(
        db: Session,
        document_id: int,
        signataire_id: int,
        type_signature: str,
        certificat_id: str,
        raison: str
    ) -> SignatureDocument:
        """Sign document electronically"""
        signature = SignatureDocument(
            document_id=document_id,
            signataire_id=signataire_id,
            type_signature=type_signature,
            date_signature=datetime.utcnow(),
            certificat_id=certificat_id,
            raison=raison,
            statut="valide"
        )
        db.add(signature)
        db.commit()
        db.refresh(signature)
        return signature


class WorkflowDocumentService:
    """Document workflow service"""
    
    @staticmethod
    def creer_workflow(
        db: Session,
        document_id: int,
        nom_workflow: str,
        initiateur_id: int
    ) -> WorkflowDocument:
        """Create document workflow"""
        workflow = WorkflowDocument(
            document_id=document_id,
            nom_workflow=nom_workflow,
            etape_actuelle=EtapeWorkflow.CREATION,
            statut=StatutWorkflow.EN_ATTENTE,
            initiateur_id=initiateur_id
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        return workflow
    
    @staticmethod
    def avancer_etape(
        db: Session,
        workflow_id: int,
        etape_suivante: EtapeWorkflow,
        approbateur_id: int
    ) -> WorkflowDocument:
        """Advance workflow step"""
        workflow = db.query(WorkflowDocument).filter(WorkflowDocument.id == workflow_id).first()
        if not workflow:
            raise ValueError("Workflow non trouvé")
        
        workflow.etape_actuelle = etape_suivante
        workflow.approbateur_id = approbateur_id
        workflow.statut = StatutWorkflow.EN_COURS
        workflow.updated_at = datetime.utcnow()
        
        if etape_suivante == EtapeWorkflow.ARCHIVAGE:
            workflow.statut = StatutWorkflow.TERMINE
            workflow.date_fin = datetime.utcnow()
        
        db.commit()
        db.refresh(workflow)
        return workflow


class SceauNumeriqueService:
    """Digital seal service"""
    
    @staticmethod
    def creer_sceau(
        db: Session,
        document_id: int,
        numero_sceau: str,
        type_sceau: str,
        createur_id: int,
        date_expiration: date = None
    ) -> SceauNumerique:
        """Create digital seal"""
        sceau = SceauNumerique(
            document_id=document_id,
            numero_sceau=numero_sceau,
            type_sceau=type_sceau,
            createur_id=createur_id,
            date_creation=datetime.utcnow(),
            date_expiration=date_expiration,
            statut="actif"
        )
        db.add(sceau)
        db.commit()
        db.refresh(sceau)
        return sceau


class AnalyseOCRService:
    """OCR analysis service"""
    
    @staticmethod
    def creer_analyse_ocr(
        db: Session,
        document_id: int,
        langue: str,
        texte_extrait: str,
        confidence: float
    ) -> AnalyseOCR:
        """Create OCR analysis"""
        analyse = AnalyseOCR(
            document_id=document_id,
            langue=langue,
            texte_extrait=texte_extrait,
            confidence=confidence,
            statut="traite"
        )
        db.add(analyse)
        db.commit()
        db.refresh(analyse)
        return analyse


class ArchivageLegalService:
    """Legal archiving service"""
    
    @staticmethod
    def archiver_document(
        db: Session,
        document_id: int,
        type_archivage: str,
        duree_conservation: int,
        autorite_archivage: str
    ) -> ArchivageLegal:
        """Archive document legally"""
        date_expiration = date.today() + timedelta(days=duree_conservation * 30)
        
        archivage = ArchivageLegal(
            document_id=document_id,
            type_archivage=type_archivage,
            duree_conservation=duree_conservation,
            date_archivage=datetime.utcnow(),
            date_expiration=date_expiration,
            numero_archivage=f"ARCH-{datetime.utcnow().strftime('%Y%m%d')}-{document_id}",
            autorite_archivage=autorite_archivage,
            classification="prive",
            conformite=True,
            statut="archive"
        )
        db.add(archivage)
        db.commit()
        db.refresh(archivage)
        return archivage


class TemplateDocumentService:
    """Document template service"""
    
    @staticmethod
    def creer_template(
        db: Session,
        nom: str,
        type_document: TypeDocument,
        categorie: str,
        contenu: str,
        variables: str,
        proprietaire_id: int
    ) -> TemplateDocument:
        """Create document template"""
        template = TemplateDocument(
            nom=nom,
            type_document=type_document,
            categorie=categorie,
            contenu=contenu,
            variables=variables,
            proprietaire_id=proprietaire_id,
            statut="actif",
            cree_par="system"
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template


class PartageDocumentService:
    """Document sharing service"""
    
    @staticmethod
    def partager_document(
        db: Session,
        document_id: int,
        partage_par: int,
        partage_avec: int,
        type_partage: str,
        date_expiration: date = None
    ) -> PartageDocument:
        """Share document"""
        partage = PartageDocument(
            document_id=document_id,
            partage_par=partage_par,
            partage_avec=partage_avec,
            type_partage=type_partage,
            date_expiration=date_expiration,
            statut="actif"
        )
        db.add(partage)
        db.commit()
        db.refresh(partage)
        return partage


class HistoriqueDocumentService:
    """Document history service"""
    
    @staticmethod
    def enregistrer_action(
        db: Session,
        document_id: int,
        action: str,
        utilisateur_id: int,
        details: str,
        adresse_ip: str = "",
        user_agent: str = ""
    ) -> HistoriqueDocument:
        """Record document action"""
        historique = HistoriqueDocument(
            document_id=document_id,
            action=action,
            utilisateur_id=utilisateur_id,
            details=details,
            adresse_ip=adresse_ip,
            user_agent=user_agent
        )
        db.add(historique)
        db.commit()
        db.refresh(historique)
        return historique


class DocumentsReportingService:
    """Documents reporting service"""
    
    @staticmethod
    def rapport_documents(db: Session, dossier_id: int) -> Dict[str, Any]:
        """Generate documents report"""
        documents = db.query(Document).filter(
            Document.dossier_id == dossier_id
        ).all()
        
        return {
            "dossier_id": dossier_id,
            "total_documents": len(documents),
            "par_type": {doc.type_document.value: 1 for doc in documents},
            "par_statut": {doc.statut.value: 1 for doc in documents},
            "taille_totale": sum(doc.taille_octets or 0 for doc in documents)
        }

"""Unit tests for Documents module - Electronic Document Management"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.documents import (
    Document, Dossier, VersionDocument, SignatureDocument,
    WorkflowDocument, SceauNumerique, AnalyseOCR
)
from app.services.documents_service import (
    DocumentsService, DossierService, VersionDocumentService,
    SignatureDocumentService, WorkflowDocumentService
)


class TestDocumentsService:
    """Test Documents service"""
    
    def test_creer_document(self, db: Session):
        """Test creating document"""
        document = DocumentsService.creer_document(
            db=db,
            titre="Facture F-2026-001",
            type_document="FACTURE",
            reference="F-2026-001",
            chemin="/documents/factures/F-2026-001.pdf",
            taille_octets=245760,
            mime_type="application/pdf"
        )
        assert document.titre == "Facture F-2026-001"
        assert document.type_document == "FACTURE"
        assert document.statut == "actif"
    
    def test_classer_document(self, db: Session):
        """Test classifying document"""
        document = DocumentsService.creer_document(
            db=db,
            titre="Facture F-2026-001",
            type_document="FACTURE",
            reference="F-2026-001",
            chemin="/documents/factures/F-2026-001.pdf",
            taille_octets=245760,
            mime_type="application/pdf"
        )
        
        document_classifie = DocumentsService.classer_document(
            db=db,
            document_id=document.id,
            categorie="FINANCE",
            tags=["facture", "client"]
        )
        assert document_classifie.categorie == "FINANCE"
        assert "facture" in document_classifie.tags


class TestDossierService:
    """Test Dossier service"""
    
    def test_creer_dossier(self, db: Session):
        """Test creating folder"""
        dossier = DossierService.creer_dossier(
            db=db,
            nom="Factures 2026",
            description="Dossier des factures de l'année 2026",
            chemin="/documents/factures/2026"
        )
        assert dossier.nom == "Factures 2026"
        assert dossier.type_dossier == "PRINCIPAL"
        assert dossier.statut == "actif"
    
    def test_ajouter_document_dossier(self, db: Session):
        """Test adding document to folder"""
        dossier = DossierService.creer_dossier(
            db=db,
            nom="Factures 2026",
            description="Dossier des factures de l'année 2026",
            chemin="/documents/factures/2026"
        )
        
        document = DocumentsService.creer_document(
            db=db,
            titre="Facture F-2026-001",
            type_document="FACTURE",
            reference="F-2026-001",
            chemin="/documents/factures/F-2026-001.pdf",
            taille_octets=245760,
            mime_type="application/pdf"
        )
        
        dossier_maj = DossierService.ajouter_document_dossier(
            db=db,
            dossier_id=dossier.id,
            document_id=document.id
        )
        assert len(dossier_maj.documents) == 1


class TestVersionDocumentService:
    """Test Version Document service"""
    
    def test_creer_version(self, db: Session):
        """Test creating document version"""
        document = DocumentsService.creer_document(
            db=db,
            titre="Facture F-2026-001",
            type_document="FACTURE",
            reference="F-2026-001",
            chemin="/documents/factures/F-2026-001.pdf",
            taille_octets=245760,
            mime_type="application/pdf"
        )
        
        version = VersionDocumentService.creer_version(
            db=db,
            document_id=document.id,
            numero_version="2.0",
            chemin="/documents/factures/F-2026-001_v2.pdf",
            modifie_par=1
        )
        assert version.numero_version == "2.0"
        assert version.document_id == document.id


class TestSignatureDocumentService:
    """Test Signature Document service"""
    
    def test_signer_document(self, db: Session):
        """Test signing document"""
        document = DocumentsService.creer_document(
            db=db,
            titre="Facture F-2026-001",
            type_document="FACTURE",
            reference="F-2026-001",
            chemin="/documents/factures/F-2026-001.pdf",
            taille_octets=245760,
            mime_type="application/pdf"
        )
        
        signature = SignatureDocumentService.signer_document(
            db=db,
            document_id=document.id,
            signataire_id=1,
            methode="ELECTRONIQUE",
            certificat_id="CERT-001"
        )
        assert signature.document_id == document.id
        assert signature.statut == "valide"


class TestWorkflowDocumentService:
    """Test Workflow Document service"""
    
    def test_creer_workflow(self, db: Session):
        """Test creating document workflow"""
        workflow = WorkflowDocumentService.creer_workflow(
            db=db,
            nom="Validation Facture",
            type_workflow="VALIDATION",
            etapes=[{"etape": "validation_comptable", "role": "FINANCIER"}]
        )
        assert workflow.nom == "Validation Facture"
        assert workflow.type_workflow == "VALIDATION"
        assert workflow.statut == "actif"

"""Unit tests for Documents module - Electronic Document Management

Tests alignes sur l'API REELLE de app.services.documents_service et du modele
app.models.documents (enums TypeDocument/StatutDocument en valeurs minuscules).
"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.documents import (
    Document, Dossier, VersionDocument, SignatureDocument,
    WorkflowDocument, SceauNumerique, AnalyseOCR,
    TypeDocument, StatutDocument
)
from app.services.documents_service import (
    DocumentsService, DossierService, VersionDocumentService,
    SignatureDocumentService, WorkflowDocumentService
)


def _make_document(db: Session, titre: str = "Facture F-2026-001") -> Document:
    """Helper : cree un document via le vrai service."""
    return DocumentsService.creer_document(
        db=db,
        numero_document="F-2026-001",
        type_document=TypeDocument.FACTURE,
        titre=titre,
        proprietaire_id=None,
        dossier_id=None,
        fichier=None,
        nom_fichier="F-2026-001.pdf",
        type_mime="application/pdf",
    )


class TestDocumentsService:
    """Test Documents service"""

    def test_creer_document(self, db: Session):
        """Test creating document"""
        document = _make_document(db)
        assert document.titre == "Facture F-2026-001"
        assert document.type_document == TypeDocument.FACTURE
        assert document.statut == StatutDocument.BROUILLON

    def test_valider_document(self, db: Session):
        """Test validating document (remplace l'ancien 'classer_document' inexistant)"""
        document = _make_document(db)
        valide = DocumentsService.valider_document(db=db, document_id=document.id)
        assert valide.statut == StatutDocument.VALIDE


class TestDossierService:
    """Test Dossier service"""

    def test_creer_dossier(self, db: Session):
        """Test creating folder"""
        dossier = DossierService.creer_dossier(
            db=db,
            nom="Factures 2026",
            proprietaire_id=None,
            description="Dossier des factures de l'année 2026"
        )
        assert dossier.nom == "Factures 2026"
        assert dossier.statut == "actif"

    def test_ajouter_document_dossier(self, db: Session):
        """Test linking a document to a folder via dossier_id"""
        dossier = DossierService.creer_dossier(
            db=db,
            nom="Factures 2026",
            proprietaire_id=None,
            description="Dossier des factures de l'année 2026"
        )
        document = DocumentsService.creer_document(
            db=db,
            numero_document="F-2026-002",
            type_document=TypeDocument.FACTURE,
            titre="Facture F-2026-002",
            dossier_id=dossier.id,
        )
        assert document.dossier_id == dossier.id


class TestVersionDocumentService:
    """Test Version Document service"""

    def test_creer_version(self, db: Session):
        """Test creating document version"""
        document = _make_document(db)
        version = VersionDocumentService.creer_version(
            db=db,
            document_id=document.id,
            numero_version=2,
            fichier=b"%PDF-1.4 fake",
            nom_fichier="F-2026-001_v2.pdf",
            type_mime="application/pdf",
            modifications="Seconde version"
        )
        assert version.numero_version == 2
        assert version.document_id == document.id


class TestSignatureDocumentService:
    """Test Signature Document service"""

    def test_signer_document(self, db: Session):
        """Test signing document"""
        document = _make_document(db)
        signature = SignatureDocumentService.signer_document(
            db=db,
            document_id=document.id,
            signataire_id=1,
            type_signature="electronique",
            certificat_id="CERT-001",
            raison="Validation"
        )
        assert signature.document_id == document.id
        assert signature.id is not None


class TestWorkflowDocumentService:
    """Test Workflow Document service"""

    def test_creer_workflow(self, db: Session):
        """Test creating document workflow"""
        document = _make_document(db)
        workflow = WorkflowDocumentService.creer_workflow(
            db=db,
            document_id=document.id,
            nom_workflow="Validation Facture",
            initiateur_id=1
        )
        assert workflow.nom_workflow == "Validation Facture"
        assert workflow.document_id == document.id
        assert workflow.statut.value == "en_attente"

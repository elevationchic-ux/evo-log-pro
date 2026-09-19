"""Unit tests for Integration module - External system integrations"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.integration import (
    Integration, RequeteIntegration, SYDONIAPlus, GuichetUnique, PCS
)
from app.services.integration_service import (
    IntegrationService, RequeteIntegrationService, SYDONIAPlusService,
    GuichetUniqueService, PCSService
)


class TestIntegrationService:
    """Test Integration service"""
    
    def test_creer_integration(self, db: Session):
        """Test creating integration"""
        integration = IntegrationService.creer_integration(
            db=db,
            code_integration="SYDONIA",
            type_integration="SYDONIA_PLUS",
            nom="SYDONIA+ Customs",
            url_api="https://sydonia.douane.cm/api",
            statut="actif"
        )
        assert integration.code_integration == "SYDONIA"
        assert integration.type_integration == "SYDONIA_PLUS"
        assert integration.statut == "actif"
    
    def test_activer_integration(self, db: Session):
        """Test activating integration"""
        integration = IntegrationService.creer_integration(
            db=db,
            code_integration="SYDONIA",
            type_integration="SYDONIA_PLUS",
            nom="SYDONIA+ Customs",
            url_api="https://sydonia.douane.cm/api",
            statut="inactif"
        )
        
        integration_active = IntegrationService.activer_integration(
            db=db,
            integration_id=integration.id
        )
        assert integration_active.statut == "actif"
        assert integration_active.date_activation is not None


class TestRequeteIntegrationService:
    """Test Requete Integration service"""
    
    def test_creer_requete(self, db: Session):
        """Test creating integration request"""
        requete = RequeteIntegrationService.creer_requete(
            db=db,
            numero_requete="REQ-2026-001",
            integration_id=1,
            type_requete="DECLARATION",
            direction="SORTANT",
            donnees_envoyees={"declaration": "DEC-2026-001"}
        )
        assert requete.numero_requete == "REQ-2026-001"
        assert requete.type_requete == "DECLARATION"
        assert requete.statut == "en_attente"
    
    def test_traiter_reponse(self, db: Session):
        """Test processing response"""
        requete = RequeteIntegrationService.creer_requete(
            db=db,
            numero_requete="REQ-2026-001",
            integration_id=1,
            type_requete="DECLARATION",
            direction="SORTANT",
            donnees_envoyees={"declaration": "DEC-2026-001"}
        )
        
        requete_traitee = RequeteIntegrationService.traiter_reponse(
            db=db,
            requete_id=requete.id,
            code_reponse=200,
            donnees_recues={"statut": "accepte"}
        )
        assert requete_traitee.code_reponse == 200
        assert requete_traitee.statut == "livre"


class TestSYDONIAPlusService:
    """Test SYDONIA+ service"""
    
    def test_creer_dossier_sydonia(self, db: Session):
        """Test creating SYDONIA+ dossier"""
        dossier = SYDONIAPlusService.creer_dossier_sydonia(
            db=db,
            numero_dossier="SYD-2026-001",
            bureau_douane="Douane Douala",
            type_operation="IMPORT",
            regime="T1",
            numero_declaration="DEC-2026-001"
        )
        assert dossier.numero_dossier == "SYD-2026-001"
        assert dossier.type_operation == "IMPORT"
        assert dossier.statut_douane == "en_cours"


class TestGuichetUniqueService:
    """Test Guichet Unique service"""
    
    def test_creer_transaction_guichet(self, db: Session):
        """Test creating Guichet Unique transaction"""
        transaction = GuichetUniqueService.creer_transaction_guichet(
            db=db,
            numero_transaction="GU-2026-001",
            service="PCS",
            type_service="DECLARATION",
            reference_externe="REF-001"
        )
        assert transaction.numero_transaction == "GU-2026-001"
        assert transaction.service == "PCS"
        assert transaction.statut == "en_cours"


class TestPCSService:
    """Test PCS service"""
    
    def test_creer_operation_pcs(self, db: Session):
        """Test creating PCS operation"""
        operation = PCSService.creer_operation_pcs(
            db=db,
            reference_pcs="PCS-2026-001",
            type_operation="DECHARGEMENT",
            navire="MV EVER GIVEN",
            voyage="V-2026-001",
            port="Kribi"
        )
        assert operation.reference_pcs == "PCS-2026-001"
        assert operation.type_operation == "DECHARGEMENT"
        assert operation.statut_pcs == "en_cours"

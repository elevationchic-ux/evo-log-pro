"""Unit tests for Integration module - External system integrations

Tests alignes sur l'API REELLE de app.services.integration_service et les enums
de app.models.integration (valeurs minuscules).
"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.integration import (
    Integration, RequeteIntegration, SYDONIAPlus, GuichetUnique, PCS,
    TypeIntegration, TypeRequete, StatutIntegration
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
            type_integration=TypeIntegration.SYDONIA,
            nom="SYDONIA+ Customs",
            url_api="https://sydonia.douane.cm/api",
            api_key="test-key"
        )
        assert integration.code_integration == "SYDONIA"
        assert integration.type_integration == TypeIntegration.SYDONIA
        assert integration.statut is not None

    def test_activer_integration(self, db: Session):
        """Test activating integration"""
        integration = IntegrationService.creer_integration(
            db=db,
            code_integration="SYDONIA-ACT",
            type_integration=TypeIntegration.SYDONIA,
            nom="SYDONIA+ Customs",
            url_api="https://sydonia.douane.cm/api",
            api_key="test-key"
        )

        integration_active = IntegrationService.activer_integration(
            db=db,
            integration_id=integration.id
        )
        assert integration_active.statut == StatutIntegration.ACTIF
        assert integration_active.date_activation is not None


class TestRequeteIntegrationService:
    """Test Requete Integration service"""

    @staticmethod
    def _integration(db: Session) -> Integration:
        return IntegrationService.creer_integration(
            db=db,
            code_integration="SYDONIA-REQ",
            type_integration=TypeIntegration.SYDONIA,
            nom="SYDONIA+ Customs",
            url_api="https://sydonia.douane.cm/api",
            api_key="test-key"
        )

    def test_creer_requete(self, db: Session):
        """Test creating integration request"""
        integration = self._integration(db)
        requete = RequeteIntegrationService.creer_requete(
            db=db,
            integration_id=integration.id,
            numero_requete="REQ-2026-001",
            type_requete=TypeRequete.DECLARATION,
            direction="SORTANT",
            donnees_envoyees='{"declaration": "DEC-2026-001"}'
        )
        assert requete.numero_requete == "REQ-2026-001"
        assert requete.type_requete == TypeRequete.DECLARATION
        assert requete.statut is not None

    def test_traiter_reponse(self, db: Session):
        """Test processing response (mettre_a_jour_reponse dans l'API reelle)"""
        integration = self._integration(db)
        requete = RequeteIntegrationService.creer_requete(
            db=db,
            integration_id=integration.id,
            numero_requete="REQ-2026-002",
            type_requete=TypeRequete.DECLARATION,
            direction="SORTANT",
            donnees_envoyees='{"declaration": "DEC-2026-002"}'
        )

        requete_traitee = RequeteIntegrationService.mettre_a_jour_reponse(
            db=db,
            requete_id=requete.id,
            donnees_recues='{"statut": "accepte"}',
            code_reponse=200,
            duree_ms=120
        )
        assert requete_traitee.code_reponse == 200


class TestSYDONIAPlusService:
    """Test SYDONIA+ service"""

    def test_creer_dossier_sydonia(self, db: Session):
        """Test creating SYDONIA+ dossier"""
        dossier = SYDONIAPlusService.creer_dossier_sydonia(
            db=db,
            numero_dossier="SYD-2026-001",
            bureau_douane="Douane Douala",
            type_operation="IMPORT",
            regime="T1"
        )
        assert dossier.numero_dossier == "SYD-2026-001"
        assert dossier.type_operation == "IMPORT"
        assert dossier.id is not None


class TestGuichetUniqueService:
    """Test Guichet Unique service"""

    def test_creer_transaction_guichet(self, db: Session):
        """Test creating Guichet Unique transaction"""
        transaction = GuichetUniqueService.creer_transaction(
            db=db,
            numero_transaction="GU-2026-001",
            service="PCS",
            type_service="DECLARATION",
            utilisateur="test-user"
        )
        assert transaction.numero_transaction == "GU-2026-001"
        assert transaction.service == "PCS"
        assert transaction.statut is not None


class TestPCSService:
    """Test PCS service"""

    def test_creer_operation_pcs(self, db: Session):
        """Test creating PCS operation"""
        operation = PCSService.creer_operation_pcs(
            db=db,
            reference_pcs="PCS-2026-001",
            type_operation="DECHARGEMENT",
            navire="MV EVER GIVEN",
            port="Kribi"
        )
        assert operation.reference_pcs == "PCS-2026-001"
        assert operation.type_operation == "DECHARGEMENT"
        assert operation.id is not None

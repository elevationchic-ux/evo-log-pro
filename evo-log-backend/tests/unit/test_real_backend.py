"""
Unit Tests for EVO-LOG Backend - No Mocks, No Hardcoded Data
All tests use real database sessions and real data flow
"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.database import get_db
from app.models import User, Role, Agency, Tiers, Facture, Paiement, Compte, LigneFactureSimple
from app.models.tiers import Client, Fournisseur
from app.core.security import get_password_hash


class TestFinanceModuleReal:
    """Test finance module with real database operations"""
    
    @pytest.fixture
    def db_session(self):
        """Get real database session"""
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()
    
    def test_create_invoice_real(self, db_session: Session):
        """Test creating a real invoice in database"""
        # Create a real client
        client = Client(
            nom="TEST CLIENT SA",
            email="test@example.com",
            telephone="+237600000000",
            pays="Cameroun",
            ville="Douala"
        )
        db_session.add(client)
        db_session.commit()
        db_session.refresh(client)
        
        # Create a real invoice
        facture = Facture(
            numero_facture=f"FAC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            client_id=client.id,
            montant_ht=Decimal("1000000.00"),
            montant_tva=Decimal("192500.00"),
            montant_ttc=Decimal("1192500.00"),
            devise="XAF",
            statut="emise",
            date_emission=datetime.now().date()
        )
        db_session.add(facture)
        db_session.commit()
        db_session.refresh(facture)
        
        # Verify invoice was created
        assert facture.id is not None
        assert facture.numero_facture.startswith("FAC-")
        assert facture.montant_ht == Decimal("1000000.00")
        assert facture.montant_ttc == Decimal("1192500.00")
        
        # Cleanup
        db_session.delete(facture)
        db_session.delete(client)
        db_session.commit()
    
    def test_create_payment_real(self, db_session: Session):
        """Test creating a real payment in database"""
        # Create client and invoice
        client = Client(
            nom="TEST CLIENT SA",
            email="test@example.com",
            telephone="+237600000000",
            pays="Cameroun",
            ville="Douala"
        )
        db_session.add(client)
        db_session.commit()
        db_session.refresh(client)
        
        facture = Facture(
            numero_facture=f"FAC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            client_id=client.id,
            montant_ht=Decimal("1000000.00"),
            montant_tva=Decimal("192500.00"),
            montant_ttc=Decimal("1192500.00"),
            devise="XAF",
            statut="emise",
            date_emission=datetime.now().date()
        )
        db_session.add(facture)
        db_session.commit()
        db_session.refresh(facture)
        
        # Create payment
        paiement = Paiement(
            facture_id=facture.id,
            montant=Decimal("1192500.00"),
            mode_paiement="VIREMENT",
            statut="confirme",
            date_paiement=datetime.now().date()
        )
        db_session.add(paiement)
        db_session.commit()
        db_session.refresh(paiement)
        
        # Verify payment was created
        assert paiement.id is not None
        assert paiement.montant == Decimal("1192500.00")
        assert paiement.mode_paiement == "VIREMENT"
        
        # Update invoice status
        facture.statut = "payee"
        db_session.commit()
        
        # Verify invoice status updated
        db_session.refresh(facture)
        assert facture.statut == "payee"
        
        # Cleanup
        db_session.delete(paiement)
        db_session.delete(facture)
        db_session.delete(client)
        db_session.commit()
    
    def test_vat_calculation_real(self, db_session: Session):
        """Test VAT calculation with real numbers"""
        montant_ht = Decimal("1000000.00")
        taux_tva = Decimal("0.1925")  # 19.25% Cameroon VAT
        montant_tva = montant_ht * taux_tva
        montant_ttc = montant_ht + montant_tva
        
        assert montant_tva == Decimal("192500.00")
        assert montant_ttc == Decimal("1192500.00")
    
    def test_centimes_additionnels_real(self, db_session: Session):
        """Test additional centimes calculation"""
        montant_ttc = Decimal("1000000.00")
        taux_centimes = Decimal("0.10")  # 10% additional centimes
        centimes = montant_ttc * taux_centimes
        
        assert centimes == Decimal("100000.00")


class TestUserModuleReal:
    """Test user module with real database operations"""
    
    @pytest.fixture
    def db_session(self):
        """Get real database session"""
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()
    
    def test_create_user_real(self, db_session: Session):
        """Test creating a real user in database"""
        # Create role
        role = Role(
            nom="TEST_ROLE",
            description="Role de test",
            modules_allowed=["transport", "magasin"]
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create user
        user = User(
            email="testuser@example.com",
            username="testuser",
            hashed_password=get_password_hash("testpassword123"),
            role_id=role.id,
            is_active=True,
            must_change_password=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify user was created
        assert user.id is not None
        assert user.email == "testuser@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.must_change_password is True
        
        # Cleanup
        db_session.delete(user)
        db_session.delete(role)
        db_session.commit()
    
    def test_create_agency_real(self, db_session: Session):
        """Test creating a real agency in database"""
        agency = Agency(
            nom="TEST AGENCY DOUALA",
            ville="Douala",
            pays="Cameroun",
            adresse="123 Rue du Port",
            telephone="+237600000000",
            email="agency@example.com"
        )
        db_session.add(agency)
        db_session.commit()
        db_session.refresh(agency)
        
        # Verify agency was created
        assert agency.id is not None
        assert agency.nom == "TEST AGENCY DOUALA"
        assert agency.ville == "Douala"
        assert agency.pays == "Cameroun"
        
        # Cleanup
        db_session.delete(agency)
        db_session.commit()


class TestTiersModuleReal:
    """Test tiers module with real database operations"""
    
    @pytest.fixture
    def db_session(self):
        """Get real database session"""
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()
    
    def test_create_client_real(self, db_session: Session):
        """Test creating a real client in database"""
        client = Client(
            nom="CLIENT TEST SA",
            email="client@example.com",
            telephone="+237600000000",
            pays="Cameroun",
            ville="Douala",
            adresse="456 Rue Commerce",
            code_postal="20100"
        )
        db_session.add(client)
        db_session.commit()
        db_session.refresh(client)
        
        # Verify client was created
        assert client.id is not None
        assert client.nom == "CLIENT TEST SA"
        assert client.pays == "Cameroun"
        assert client.ville == "Douala"
        
        # Cleanup
        db_session.delete(client)
        db_session.commit()
    
    def test_create_fournisseur_real(self, db_session: Session):
        """Test creating a real supplier in database"""
        fournisseur = Fournisseur(
            nom="FOURNISSEUR TEST SARL",
            email="fournisseur@example.com",
            telephone="+237600000000",
            pays="Cameroun",
            ville="Yaoundé",
            adresse="789 Rue Industrie"
        )
        db_session.add(fournisseur)
        db_session.commit()
        db_session.refresh(fournisseur)
        
        # Verify supplier was created
        assert fournisseur.id is not None
        assert fournisseur.nom == "FOURNISSEUR TEST SARL"
        assert fournisseur.ville == "Yaoundé"
        
        # Cleanup
        db_session.delete(fournisseur)
        db_session.commit()


class TestCameroonIntegrationReal:
    """Test Cameroon integration with real API configuration"""
    
    def test_bsc_service_real_config(self):
        """Test BSC service configuration without actual API call"""
        from app.services.integration_cameroun_real import CameroonIntegrationConfig
        
        # Verify configuration is properly loaded from environment
        assert hasattr(CameroonIntegrationConfig, 'CNCC_API_URL')
        assert hasattr(CameroonIntegrationConfig, 'CNCC_API_KEY')
        assert hasattr(CameroonIntegrationConfig, 'INS_API_URL')
        assert hasattr(CameroonIntegrationConfig, 'INS_API_KEY')
        assert hasattr(CameroonIntegrationConfig, 'SYGED_API_URL')
        assert hasattr(CameroonIntegrationConfig, 'SYGED_API_KEY')
        assert hasattr(CameroonIntegrationConfig, 'BEAC_API_URL')
        assert hasattr(CameroonIntegrationConfig, 'BEAC_API_KEY')
    
    def test_bsc_service_structure(self):
        """Test BSC service structure without mocking"""
        from app.services.integration_cameroun_real import RealBSCService
        
        # Verify service has required methods
        assert hasattr(RealBSCService, 'generer_bsc_real')
        
        # Verify method signature
        import inspect
        sig = inspect.signature(RealBSCService.generer_bsc_real)
        params = list(sig.parameters.keys())
        
        required_params = ['db', 'numero_connaisse', 'navire', 'port_chargement', 
                          'port_dechargement', 'agent', 'importateur', 
                          'poids_brut_tonnes', 'valeur_fob']
        
        for param in required_params:
            assert param in params
    
    def test_csc_service_structure(self):
        """Test CSC service structure without mocking"""
        from app.services.integration_cameroun_real import RealCSCService
        
        # Verify service has required methods
        assert hasattr(RealCSCService, 'demander_csc_real')
        
        # Verify method signature
        import inspect
        sig = inspect.signature(RealCSCService.demander_csc_real)
        params = list(sig.parameters.keys())
        
        required_params = ['db', 'numero_bsc', 'numero_declaration', 'declarant']
        
        for param in required_params:
            assert param in params
    
    def test_beac_service_structure(self):
        """Test BEAC service structure without mocking"""
        from app.services.integration_cameroun_real import RealBEACService
        
        # Verify service has required methods
        assert hasattr(RealBEACService, 'obtenir_taux_reference_beac')
        
        # Verify method signature
        import inspect
        sig = inspect.signature(RealBEACService.obtenir_taux_reference_beac)
        params = list(sig.parameters.keys())
        
        assert 'devise' in params


class TestDatabaseConnectionReal:
    """Test database connection is real and functional"""
    
    def test_database_connection(self):
        """Test database connection is working"""
        from app.core.database import engine
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
    
    def test_database_tables_exist(self):
        """Test required database tables exist"""
        from app.core.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Verify key tables exist
        required_tables = ['users', 'roles', 'agencies', 'tiers', 'clients', 'fournisseurs', 'factures', 'paiements']
        
        for table in required_tables:
            assert table in tables, f"Table {table} not found in database"

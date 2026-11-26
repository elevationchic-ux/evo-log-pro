"""Unit tests for Acquisition module - Procurement and supplier management"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.acquisition import (
    AppelOffre, CahierCharges, Offre, Comparatif, ContratCadre,
    BonCommande, Reception, Litige
)
from app.services.acquisition_service import (
    AcquisitionService, AppelOffreService, ContratCadreService,
    BonCommandeService, ReceptionService
)


class TestAppelOffreService:
    """Test Appel Offre service"""
    
    def test_creer_appel_offre(self, db: Session):
        """Test creating tender"""
        appel = AppelOffreService.creer_appel_offre(
            db=db,
            numero_appel="AO-2026-001",
            titre="Fourniture équipements de manutention",
            type_appel="NATIONAL",
            date_limite=date(2026, 2, 15),
            budget_estime=50000000.0
        )
        assert appel.numero_appel == "AO-2026-001"
        assert appel.type_appel == "NATIONAL"
        assert appel.statut == "publie"
    
    def test_lancer_selection(self, db: Session):
        """Test launching selection"""
        appel = AppelOffreService.creer_appel_offre(
            db=db,
            numero_appel="AO-2026-001",
            titre="Fourniture équipements de manutention",
            type_appel="NATIONAL",
            date_limite=date(2026, 2, 15),
            budget_estime=50000000.0
        )
        
        appel_selection = AppelOffreService.lancer_selection(
            db=db,
            appel_id=appel.id
        )
        assert appel_selection.statut == "en_selection"


class TestContratCadreService:
    """Test Contrat Cadre service"""
    
    def test_creer_contrat_cadre(self, db: Session):
        """Test creating framework contract"""
        contrat = ContratCadreService.creer_contrat_cadre(
            db=db,
            numero_contrat="CC-2026-001",
            fournisseur_id=1,
            type_contrat="FOURNITURE",
            date_debut=date(2026, 1, 15),
            date_fin=date(2026, 12, 31),
            montant_max=100000000.0
        )
        assert contrat.numero_contrat == "CC-2026-001"
        assert contrat.type_contrat == "FOURNITURE"
        assert contrat.statut == "actif"


class TestBonCommandeService:
    """Test Bon Commande service"""
    
    def test_creer_bon_commande(self, db: Session):
        """Test creating purchase order"""
        bc = BonCommandeService.creer_bon_commande(
            db=db,
            numero_bc="BC-2026-001",
            fournisseur_id=1,
            contrat_cadre_id=1,
            date_commande=date(2026, 1, 15),
            montant_ht=25000000.0
        )
        assert bc.numero_bc == "BC-2026-001"
        assert bc.statut == "envoye"


class TestReceptionService:
    """Test Reception service"""
    
    def test_creer_reception(self, db: Session):
        """Test creating reception"""
        reception = ReceptionService.creer_reception(
            db=db,
            numero_reception="REC-2026-001",
            bon_commande_id=1,
            date_reception=date(2026, 1, 20),
            quantite_recue=100,
            quantite_commandee=100
        )
        assert reception.numero_reception == "REC-2026-001"
        assert reception.statut == "conforme"

"""Unit tests for Finance module - OHADA accounting for Cameroon/CEMAC"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.finance import (
    PlanComptableOHADA, EcritureComptable, ExerciceComptable,
    Facture, LigneFacture, Paiement, TVA, RetenueSource,
    MinimumCorporateTax, CentimesAdditionnels, Patente
)
from app.services.finance_service import (
    FinanceService, PlanComptableService, EcritureComptableService,
    FactureService, PaiementService, TaxeService
)


class TestPlanComptableService:
    """Test Plan Comptable OHADA service"""
    
    def test_creer_compte(self, db: Session):
        """Test creating OHADA account"""
        compte = PlanComptableService.creer_compte(
            db=db,
            numero="401000",
            libelle="Fournisseurs",
            classe=4,
            categorie="PASSIF_CIRCULANT",
            solde_debit=0.0,
            solde_credit=100000.0
        )
        assert compte.numero == "401000"
        assert compte.libelle == "Fournisseurs"
        assert compte.classe == 4
        assert compte.actif is True
    
    def test_mettre_a_jour_solde(self, db: Session):
        """Test updating account balance"""
        compte = PlanComptableService.creer_compte(
            db=db,
            numero="401000",
            libelle="Fournisseurs",
            classe=4,
            categorie="PASSIF_CIRCULANT",
            solde_debit=0.0,
            solde_credit=100000.0
        )
        
        compte_maj = PlanComptableService.mettre_a_jour_solde(
            db=db,
            compte_id=compte.id,
            debit=50000.0,
            credit=0.0
        )
        assert compte_maj.solde_debit == 50000.0


class TestEcritureComptableService:
    """Test Ecriture Comptable service"""
    
    def test_creer_ecriture(self, db: Session):
        """Test creating accounting entry"""
        ecriture = EcritureComptableService.creer_ecriture(
            db=db,
            numero_ecriture="EC-2026-001",
            date_ecriture=date(2026, 1, 15),
            reference="FACT-2026-001",
            libelle="Achat fournisseur",
            montant_debit=100000.0,
            montant_credit=100000.0
        )
        assert ecriture.numero_ecriture == "EC-2026-001"
        assert ecriture.montant_debit == 100000.0
        assert ecriture.statut == "validee"


class TestFactureService:
    """Test Facture service"""
    
    def test_creer_facture(self, db: Session):
        """Test creating invoice"""
        facture = FactureService.creer_facture(
            db=db,
            numero_facture="F-2026-001",
            client_id=1,
            date_facture=date(2026, 1, 15),
            date_echeance=date(2026, 2, 15),
            montant_ht=100000.0,
            taux_tva=19.25,
            montant_tva=19250.0,
            montant_ttc=119250.0
        )
        assert facture.numero_facture == "F-2026-001"
        assert facture.montant_ht == 100000.0
        assert facture.montant_ttc == 119250.0
        assert facture.statut == "non_payee"
    
    def test_ajouter_ligne_facture(self, db: Session):
        """Test adding invoice line"""
        facture = FactureService.creer_facture(
            db=db,
            numero_facture="F-2026-001",
            client_id=1,
            date_facture=date(2026, 1, 15),
            date_echeance=date(2026, 2, 15),
            montant_ht=100000.0,
            taux_tva=19.25,
            montant_tva=19250.0,
            montant_ttc=119250.0
        )
        
        ligne = FactureService.ajouter_ligne_facture(
            db=db,
            facture_id=facture.id,
            article="Services logistiques",
            quantite=10,
            prix_unitaire=10000.0,
            montant_ht=100000.0
        )
        assert ligne.article == "Services logistiques"
        assert ligne.quantite == 10
        assert ligne.montant_ht == 100000.0


class TestPaiementService:
    """Test Paiement service"""
    
    def test_creer_paiement(self, db: Session):
        """Test creating payment"""
        paiement = PaiementService.creer_paiement(
            db=db,
            numero_paiement="P-2026-001",
            facture_id=1,
            date_paiement=date(2026, 1, 20),
            montant=119250.0,
            mode_paiement="virement",
            reference_bancaire="BGFI-001"
        )
        assert paiement.numero_paiement == "P-2026-001"
        assert paiement.montant == 119250.0
        assert paiement.mode_paiement == "virement"


class TestTaxeService:
    """Test Taxe service"""
    
    def test_calculer_tva(self, db: Session):
        """Test VAT calculation"""
        tva = TaxeService.calculer_tva(
            db=db,
            numero_tva="TVA-2026-001",
            base_imposable=100000.0,
            taux=19.25,
            date=date(2026, 1, 15)
        )
        assert tva.base_imposable == 100000.0
        assert tva.taux == 19.25
        assert tva.montant_tva == 19250.0
    
    def test_calculer_retenu_source(self, db: Session):
        """Test withholding tax calculation"""
        retenu = TaxeService.calculer_retenu_source(
            db=db,
            numero_retenu="RS-2026-001",
            base_imposable=100000.0,
            taux=5.0,
            date=date(2026, 1, 15)
        )
        assert retenu.base_imposable == 100000.0
        assert retenu.taux == 5.0
        assert retenu.montant_retenu == 5000.0

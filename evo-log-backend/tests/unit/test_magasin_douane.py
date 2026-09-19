"""Unit tests for Magasin Douane module - Customs warehouse management"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.magasin_douane import (
    EntrepotDouane, DeclarationEntrepot, FicheMagasin,
    InventaireDouanier, SurveillanceEntrepot
)
from app.services.magasin_douane_service import (
    MagasinDouaneService, EntrepotDouaneService, DeclarationEntrepotService,
    FicheMagasinService, SurveillanceService
)


class TestEntrepotDouaneService:
    """Test Entrepot Douane service"""
    
    def test_creer_entrepot(self, db: Session):
        """Test creating customs warehouse"""
        entrepot = EntrepotDouaneService.creer_entrepot(
            db=db,
            code_entrepot="MAG1",
            nom="Entrepôt Douane MAG1",
            type_entrepot="ZONE_FRANCHE",
            capacite=10000.0,
            unite="TONNES"
        )
        assert entrepot.code_entrepot == "MAG1"
        assert entrepot.type_entrepot == "ZONE_FRANCHE"
        assert entrepot.statut == "actif"


class TestDeclarationEntrepotService:
    """Test Declaration Entrepot service"""
    
    def test_creer_declaration(self, db: Session):
        """Test creating warehouse declaration"""
        declaration = DeclarationEntrepotService.creer_declaration(
            db=db,
            numero_declaration="DE-2026-001",
            entrepot_id=1,
            type_declaration="ENTREE",
            date_declaration=date(2026, 1, 15)
        )
        assert declaration.numero_declaration == "DE-2026-001"
        assert declaration.type_declaration == "ENTREE"
        assert declaration.statut == "en_cours"


class TestFicheMagasinService:
    """Test Fiche Magasin service"""
    
    def test_creer_fiche(self, db: Session):
        """Test creating warehouse record"""
        fiche = FicheMagasinService.creer_fiche(
            db=db,
            numero_fiche="FM-2026-001",
            entrepot_id=1,
            article="Ciment ZLECAF",
            quantite=400.0,
            unite="TONNES"
        )
        assert fiche.numero_fiche == "FM-2026-001"
        assert fiche.article == "Ciment ZLECAF"
        assert fiche.statut == "actif"


class TestSurveillanceService:
    """Test Surveillance service"""
    
    def test_creer_surveillance(self, db: Session):
        """Test creating surveillance record"""
        surveillance = SurveillanceService.creer_surveillance(
            db=db,
            numero_surveillance="SURV-2026-001",
            entrepot_id=1,
            type_surveillance="VIDEO",
            date_debut=date(2026, 1, 15)
        )
        assert surveillance.numero_surveillance == "SURV-2026-001"
        assert surveillance.type_surveillance == "VIDEO"
        assert surveillance.statut == "actif"

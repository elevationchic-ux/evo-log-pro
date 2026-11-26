"""Unit tests for Magasin Douane module - Customs warehouse management

Tests alignes sur l'API REELLE de app.services.magasin_douane_service et sur
les enums de app.models.magasin_douane (TypeEntrepotDouane, RegimeEntrepot).
"""
import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.models.magasin_douane import (
    EntrepotDouane, DeclarationEntrepot, FicheMagasin,
    InventaireDouanier, SurveillanceEntrepot,
    TypeEntrepotDouane, RegimeEntrepot
)
from app.services.magasin_douane_service import (
    MagasinDouaneService, EntrepotDouaneService, DeclarationEntrepotService,
    FicheMagasinService, SurveillanceService
)


def _make_entrepot(db: Session, code: str = "MAG1") -> EntrepotDouane:
    """Helper : cree un entrepot douanier via le vrai service."""
    today = date.today()
    return EntrepotDouaneService.creer_entrepot_douane(
        db=db,
        code=code,
        nom=f"Entrepot Douane {code}",
        type_entrepot=TypeEntrepotDouane.MAGASIN_SOUS_DOUANE,
        regime=RegimeEntrepot.SUSPENDU,
        adresse="Zone Portuaire, Douala",
        surface_m2=5000.0,
        capacite_tonnage=10000.0,
        numero_agrement=f"AGR-{code}",
        date_agrement=today,
        date_expiration_agrement=today + timedelta(days=365)
    )


class TestEntrepotDouaneService:
    """Test Entrepot Douane service"""

    def test_creer_entrepot(self, db: Session):
        """Test creating customs warehouse"""
        entrepot = _make_entrepot(db)
        assert entrepot.code == "MAG1"
        assert entrepot.type_entrepot == TypeEntrepotDouane.MAGASIN_SOUS_DOUANE
        assert entrepot.statut == "actif"


class TestDeclarationEntrepotService:
    """Test Declaration Entrepot service"""

    def test_creer_declaration(self, db: Session):
        """Test creating warehouse declaration"""
        entrepot = _make_entrepot(db, code="MAG2")
        declaration = DeclarationEntrepotService.creer_declaration_entrepot(
            db=db,
            numero_declaration="DE-2026-001",
            entrepot_id=entrepot.id,
            dossier_transit_id=None,
            regime=RegimeEntrepot.SUSPENDU,
            valeur_marchandise=1000000.0
        )
        assert declaration.numero_declaration == "DE-2026-001"
        assert declaration.entrepot_id == entrepot.id
        assert declaration.statut == "en_attente"


class TestFicheMagasinService:
    """Test Fiche Magasin service"""

    def test_creer_fiche(self, db: Session):
        """Test creating warehouse record"""
        entrepot = _make_entrepot(db, code="MAG3")
        fiche = FicheMagasinService.creer_fiche_magasin(
            db=db,
            numero_fiche="FM-2026-001",
            entrepot_id=entrepot.id,
            article_id=None,
            designation="Ciment ZLECAF",
            numero_lot="LOT-001",
            stock_initial=400.0,
            unite="TONNES",
            emplacement="A-01",
            valeur_unitaire=25000.0
        )
        assert fiche.numero_fiche == "FM-2026-001"
        assert fiche.designation == "Ciment ZLECAF"
        assert fiche.statut == "actif"


class TestSurveillanceService:
    """Test Surveillance service"""

    def test_creer_surveillance(self, db: Session):
        """Test creating surveillance patrol record"""
        entrepot = _make_entrepot(db, code="MAG4")
        surveillance = SurveillanceService.enregistrer_patrouille(
            db=db,
            entrepot_id=entrepot.id,
            gardien="Gardien Test",
            type_controle="VIDEO",
            zones_controlees="Quai A, Quai B"
        )
        assert surveillance.entrepot_id == entrepot.id
        assert surveillance.gardien == "Gardien Test"
        assert surveillance.statut == "normal"

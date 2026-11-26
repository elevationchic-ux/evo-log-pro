"""Unit tests for Acconage module - Port operations"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.acconage import (
    StowagePlan, Grue, Remorqueur, ConteneurAcconage,
    Connaissement, Surestaries, THCAcconage, ScelleAcconage
)
from app.services.acconage_service import (
    AcconageService, StowagePlanService, GrueService,
    ConnaissementService, SurestariesService
)


class TestStowagePlanService:
    """Test Stowage Plan service"""
    
    def test_creer_stowage_plan(self, db: Session):
        """Test creating stowage plan"""
        plan = StowagePlanService.creer_stowage_plan(
            db=db,
            numero_plan="SP-2026-001",
            navire="MV EVER GIVEN",
            voyage="V-2026-001",
            date_arrivee=date(2026, 1, 15),
            position_actuelle="Quai Nord"
        )
        assert plan.numero_plan == "SP-2026-001"
        assert plan.navire == "MV EVER GIVEN"
        assert plan.statut == "planifie"


class TestGrueService:
    """Test Grue service"""
    
    def test_creer_grue(self, db: Session):
        """Test creating crane"""
        grue = GrueService.creer_grue(
            db=db,
            code_grue="GR-001",
            nom="Grue Portique G1",
            type_grue="PORTIQUE",
            capacite_max=50.0,
            fabricant="Liebherr"
        )
        assert grue.code_grue == "GR-001"
        assert grue.type_grue == "PORTIQUE"
        assert grue.statut == "actif"


class TestConnaissementService:
    """Test Connaissement service"""
    
    def test_creer_connaissement(self, db: Session):
        """Test creating bill of lading"""
        bl = ConnaissementService.creer_connaissement(
            db=db,
            numero_bl="BL-2026-001",
            navire="MV EVER GIVEN",
            voyage="V-2026-001",
            port_chargement="Shanghai",
            port_dechargement="Douala",
            nombre_conteneurs=50
        )
        assert bl.numero_bl == "BL-2026-001"
        assert bl.port_chargement == "Shanghai"
        assert bl.statut == "emis"


class TestSurestariesService:
    """Test Surestaries service"""
    
    def test_calculer_surestaries(self, db: Session):
        """Test calculating demurrage"""
        surestaries = SurestariesService.calculer_surestaries(
            db=db,
            numero_surestaries="SST-2026-001",
            connaissement_id=1,
            date_arrivee=date(2026, 1, 15),
            date_depart=date(2026, 1, 20),
            taux_journalier=50000.0
        )
        assert surestaries.numero_surestaries == "SST-2026-001"
        assert surestaries.nombre_jours == 5
        assert surestaries.montant_total == 250000.0

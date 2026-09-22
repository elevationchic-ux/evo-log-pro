"""Unit tests for Maintenance GMAO module - Computerized Maintenance Management"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.maintenance_gmao import (
    OrdreMaintenance, EquipementGMAO, PlanMaintenance,
    PieceRechangeGMAO, Calibration, PerformanceEquipement
)
from app.services.maintenance_gmao_service import (
    MaintenanceGMAOService, OrdreMaintenanceService, EquipementGMAOService,
    PlanMaintenanceService, CalibrationService
)


class TestOrdreMaintenanceService:
    """Test Ordre Maintenance service"""
    
    def test_creer_ordre_maintenance(self, db: Session):
        """Test creating maintenance order"""
        ordre = OrdreMaintenanceService.creer_ordre_maintenance(
            db=db,
            numero_ordre="OM-2026-001",
            equipement_id=1,
            type_maintenance="CORRECTIVE",
            priorite="HAUTE",
            description="Remplacement alternateur",
            planifie_le=date(2026, 1, 20)
        )
        assert ordre.numero_ordre == "OM-2026-001"
        assert ordre.type_maintenance == "CORRECTIVE"
        assert ordre.priorite == "HAUTE"
        assert ordre.statut == "planifie"
    
    def test_demarrer_maintenance(self, db: Session):
        """Test starting maintenance"""
        ordre = OrdreMaintenanceService.creer_ordre_maintenance(
            db=db,
            numero_ordre="OM-2026-001",
            equipement_id=1,
            type_maintenance="CORRECTIVE",
            priorite="HAUTE",
            description="Remplacement alternateur",
            planifie_le=date(2026, 1, 20)
        )
        
        ordre_en_cours = OrdreMaintenanceService.demarrer_maintenance(
            db=db,
            ordre_id=ordre.id,
            technicien_id=1
        )
        assert ordre_en_cours.statut == "en_cours"
        assert ordre_en_cours.date_debut is not None


class TestEquipementGMAOService:
    """Test Equipement GMAO service"""
    
    def test_creer_equipement(self, db: Session):
        """Test creating equipment"""
        equipement = EquipementGMAOService.creer_equipement(
            db=db,
            code_equipement="EQ-001",
            nom="Grue Portique G1",
            type_equipement="GRUE",
            fabricant="Liebherr",
            modele="LHM 550",
            date_mise_service=date(2020, 1, 15)
        )
        assert equipement.code_equipement == "EQ-001"
        assert equipement.type_equipement == "GRUE"
        assert equipement.statut == "actif"
    
    def test_calculer_mtbf(self, db: Session):
        """Test calculating MTBF"""
        equipement = EquipementGMAOService.creer_equipement(
            db=db,
            code_equipement="EQ-001",
            nom="Grue Portique G1",
            type_equipement="GRUE",
            fabricant="Liebherr",
            modele="LHM 550",
            date_mise_service=date(2020, 1, 15)
        )
        
        equipement_maj = EquipementGMAOService.calculer_mtbf(
            db=db,
            equipement_id=equipement.id,
            mtbf=720.0
        )
        assert equipement_maj.mtbf == 720.0


class TestPlanMaintenanceService:
    """Test Plan Maintenance service"""
    
    def test_creer_plan_maintenance(self, db: Session):
        """Test creating maintenance plan"""
        plan = PlanMaintenanceService.creer_plan_maintenance(
            db=db,
            code_plan="PM-001",
            nom="Plan Grue G1",
            equipement_id=1,
            frequence="MENSUEL",
            description="Maintenance préventive mensuelle"
        )
        assert plan.code_plan == "PM-001"
        assert plan.frequence == "MENSUEL"
        assert plan.actif is True


class TestCalibrationService:
    """Test Calibration service"""
    
    def test_creer_calibration(self, db: Session):
        """Test creating calibration"""
        calibration = CalibrationService.creer_calibration(
            db=db,
            numero_calibration="CAL-2026-001",
            equipement_id=1,
            type_calibration="POIDS",
            date_calibration=date(2026, 1, 15),
            resultat="CONFORME"
        )
        assert calibration.numero_calibration == "CAL-2026-001"
        assert calibration.resultat == "CONFORME"
        assert calibration.statut == "valide"

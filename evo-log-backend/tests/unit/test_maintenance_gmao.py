"""Unit tests for Maintenance GMAO module - Computerized Maintenance Management

Tests alignes sur l'API REELLE de app.services.maintenance_gmao_service et sur
les enums de app.models.maintenance_gmao.
"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.maintenance_gmao import (
    OrdreMaintenance, EquipementGMAO, PlanMaintenance,
    PieceRechangeGMAO, Calibration, PerformanceEquipement,
    TypeMaintenance, PrioriteMaintenance, TypeEquipement, StatutMaintenance
)
from app.services.maintenance_gmao_service import (
    MaintenanceGMAOService, OrdreMaintenanceService, EquipementGMAOService,
    PlanMaintenanceService, CalibrationService
)


def _make_equipement(db: Session, numero_serie: str = "SN-EQ-001") -> EquipementGMAO:
    """Helper : cree un equipement via le vrai service."""
    return EquipementGMAOService.creer_equipement(
        db=db,
        numero_serie=numero_serie,
        designation="Grue Portique G1",
        type_equipement=TypeEquipement.GRUE,
        marque="Liebherr",
        modele="LHM 550",
        localisation="Terminal a quai"
    )


class TestOrdreMaintenanceService:
    """Test Ordre Maintenance service"""

    def test_creer_ordre_maintenance(self, db: Session):
        """Test creating maintenance order"""
        equipement = _make_equipement(db)
        ordre = OrdreMaintenanceService.creer_ordre(
            db=db,
            numero_ordre="OM-2026-001",
            equipement_id=equipement.id,
            type_maintenance=TypeMaintenance.CORRECTIVE,
            priorite=PrioriteMaintenance.HAUTE,
            description="Remplacement alternateur",
            date_planifiee=date(2026, 1, 20),
            technicien_id=None
        )
        assert ordre.numero_ordre == "OM-2026-001"
        assert ordre.type_maintenance == TypeMaintenance.CORRECTIVE
        assert ordre.priorite == PrioriteMaintenance.HAUTE
        assert ordre.statut == StatutMaintenance.PLANIFIEE

    def test_completer_ordre(self, db: Session):
        """Test completing maintenance (remplace l'ancien 'demarrer_maintenance' inexistant)"""
        equipement = _make_equipement(db, numero_serie="SN-EQ-002")
        ordre = OrdreMaintenanceService.creer_ordre(
            db=db,
            numero_ordre="OM-2026-002",
            equipement_id=equipement.id,
            type_maintenance=TypeMaintenance.CORRECTIVE,
            priorite=PrioriteMaintenance.HAUTE,
            description="Remplacement alternateur",
            date_planifiee=date(2026, 1, 20),
            technicien_id=None
        )

        ordre_termine = OrdreMaintenanceService.completer_ordre(
            db=db,
            ordre_id=ordre.id,
            date_fin=datetime(2026, 1, 21, 14, 0),
            duree_reelle=3,
            observations="Alternateur remplace"
        )
        assert ordre_termine.statut != StatutMaintenance.PLANIFIEE
        assert ordre_termine.date_fin is not None


class TestEquipementGMAOService:
    """Test Equipement GMAO service"""

    def test_creer_equipement(self, db: Session):
        """Test creating equipment"""
        equipement = _make_equipement(db, numero_serie="SN-EQ-003")
        assert equipement.numero_serie == "SN-EQ-003"
        assert equipement.designation == "Grue Portique G1"
        assert equipement.type_equipement == TypeEquipement.GRUE
        assert equipement.statut is not None

    def test_calculer_mtbf_nexiste_pas(self, db: Session):
        """L'API reelle n'expose pas de calcul MTBF : la methode doit rester absente
        plutot que d'etre un faux succes."""
        assert not hasattr(EquipementGMAOService, "calculer_mtbf")


class TestPlanMaintenanceService:
    """Test Plan Maintenance service"""

    def test_creer_plan_maintenance(self, db: Session):
        """Test creating maintenance plan"""
        equipement = _make_equipement(db, numero_serie="SN-EQ-004")
        plan = PlanMaintenanceService.creer_plan(
            db=db,
            numero_plan="PM-001",
            equipement_id=equipement.id,
            type_maintenance=TypeMaintenance.PREVENTIVE,
            frequence="MENSUEL",
            intervalle_jours=30,
            date_debut=date(2026, 1, 15)
        )
        assert plan.numero_plan == "PM-001"
        assert plan.frequence == "MENSUEL"
        assert plan.statut == "actif"


class TestCalibrationService:
    """Test Calibration service"""

    def test_creer_calibration(self, db: Session):
        """Test creating calibration"""
        equipement = _make_equipement(db, numero_serie="SN-EQ-005")
        calibration = CalibrationService.creer_calibration(
            db=db,
            numero_calibration="CAL-2026-001",
            equipement_id=equipement.id,
            instrument="Balances",
            date_calibration=date(2026, 1, 15),
            intervalle_mois=12
        )
        assert calibration.numero_calibration == "CAL-2026-001"
        assert calibration.equipement_id == equipement.id
        assert calibration.statut == "valide"

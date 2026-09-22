"""Unit tests for QHSE module - Quality, Health, Safety, Environment"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.qhse import (
    AnalyseRisque, ActionPrevention, PlanPrevention, EPI,
    AccidentTravail, Investigation, CertificationISO, Audit
)
from app.services.qhse_service import (
    QHSEService, AnalyseRisqueService, ActionPreventionService,
    AccidentTravailService, AuditService
)


class TestAnalyseRisqueService:
    """Test Analyse Risque service"""
    
    def test_creer_analyse_risque(self, db: Session):
        """Test creating risk analysis"""
        analyse = AnalyseRisqueService.creer_analyse_risque(
            db=db,
            numero_analyse="AR-2026-001",
            type_risque="ERGONOMIQUE",
            zone="Entrepôt MAG1",
            description="Risque de manutention manuelle",
            probabilite=3,
            gravite=4,
            niveau_risque="MOYEN"
        )
        assert analyse.numero_analyse == "AR-2026-001"
        assert analyse.type_risque == "ERGONOMIQUE"
        assert analyse.niveau_risque == "MOYEN"
    
    def test_evaluer_risque(self, db: Session):
        """Test risk evaluation"""
        analyse = AnalyseRisqueService.creer_analyse_risque(
            db=db,
            numero_analyse="AR-2026-001",
            type_risque="ERGONOMIQUE",
            zone="Entrepôt MAG1",
            description="Risque de manutention manuelle",
            probabilite=3,
            gravite=4,
            niveau_risque="MOYEN"
        )
        
        analyse_maj = AnalyseRisqueService.evaluer_risque(
            db=db,
            analyse_id=analyse.id,
            nouvelles_mesures="Formation ergonomique"
        )
        assert analyse_maj.statut == "traite"


class TestActionPreventionService:
    """Test Action Prevention service"""
    
    def test_creer_action_prevention(self, db: Session):
        """Test creating prevention action"""
        action = ActionPreventionService.creer_action_prevention(
            db=db,
            numero_action="AP-2026-001",
            type_action="FORMATION",
            description="Formation manutention",
            responsable_id=1,
            date_echeance=date(2026, 2, 15)
        )
        assert action.numero_action == "AP-2026-001"
        assert action.type_action == "FORMATION"
        assert action.statut == "planifie"


class TestAccidentTravailService:
    """Test Accident Travail service"""
    
    def test_declarer_accident(self, db: Session):
        """Test declaring work accident"""
        accident = AccidentTravailService.declarer_accident(
            db=db,
            numero_accident="AT-2026-001",
            employe_id=1,
            date_accident=datetime(2026, 1, 15, 10, 30),
            lieu="Entrepôt MAG1",
            description="Chute sur sol glissant",
            gravite="LEGERE"
        )
        assert accident.numero_accident == "AT-2026-001"
        assert accident.gravite == "LEGERE"
        assert accident.statut == "declare"
    
    def test_lancer_investigation(self, db: Session):
        """Test launching investigation"""
        accident = AccidentTravailService.declarer_accident(
            db=db,
            numero_accident="AT-2026-001",
            employe_id=1,
            date_accident=datetime(2026, 1, 15, 10, 30),
            lieu="Entrepôt MAG1",
            description="Chute sur sol glissant",
            gravite="LEGERE"
        )
        
        investigation = AccidentTravailService.lancer_investigation(
            db=db,
            accident_id=accident.id,
            investigateur_id=2
        )
        assert investigation.accident_id == accident.id
        assert investigation.statut == "en_cours"


class TestAuditService:
    """Test Audit service"""
    
    def test_creer_audit(self, db: Session):
        """Test creating audit"""
        audit = AuditService.creer_audit(
            db=db,
            numero_audit="AUD-2026-001",
            type_audit="ISO_9001",
            date_debut=date(2026, 3, 1),
            date_fin=date(2026, 3, 5),
            scope="Entrepôts MAG1-MAG3"
        )
        assert audit.numero_audit == "AUD-2026-001"
        assert audit.type_audit == "ISO_9001"
        assert audit.statut == "planifie"

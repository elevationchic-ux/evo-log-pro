"""Unit tests for Transit module - Customs operations for CEMAC"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.transit_avance import (
    BureauDouane, DossierTransitAvance, VisitePhysique,
    Valorisation, NomenclatureCEMAC, BAD, AMC
)
from app.services.transit_avance_service import (
    TransitAvanceService, DossierTransitService, VisitePhysiqueService,
    ValorisationService, BADService
)


class TestDossierTransitService:
    """Test Dossier Transit service"""
    
    def test_creer_dossier_transit(self, db: Session):
        """Test creating transit dossier"""
        dossier = DossierTransitService.creer_dossier_transit(
            db=db,
            numero_dossier="TR-2026-001",
            bureau_entree_id=1,
            bureau_sortie_id=2,
            type_transit="ORDINAIRE",
            reference_externe="REF-001"
        )
        assert dossier.numero_dossier == "TR-2026-001"
        assert dossier.type_transit == "ORDINAIRE"
        assert dossier.statut == "en_cours"


class TestVisitePhysiqueService:
    """Test Visite Physique service"""
    
    def test_planifier_visite(self, db: Session):
        """Test scheduling physical inspection"""
        visite = VisitePhysiqueService.planifier_visite(
            db=db,
            numero_visite="VP-2026-001",
            dossier_transit_id=1,
            date_visite=date(2026, 1, 20),
            inspecteur_id=1
        )
        assert visite.numero_visite == "VP-2026-001"
        assert visite.statut == "planifie"


class TestValorisationService:
    """Test Valorisation service"""
    
    def test_creer_valorisation(self, db: Session):
        """Test creating valuation"""
        valorisation = ValorisationService.creer_valorisation(
            db=db,
            numero_valorisation="VAL-2026-001",
            dossier_transit_id=1,
            valeur_cif=100000.0,
            valeur_douane=110000.0,
            taux_change=650.0
        )
        assert valorisation.numero_valorisation == "VAL-2026-001"
        assert valorisation.valeur_cif == 100000.0
        assert valorisation.statut == "valide"


class TestBADService:
    """Test BAD service"""
    
    def test_emettre_bad(self, db: Session):
        """Test issuing BAD"""
        bad = BADService.emettre_bad(
            db=db,
            numero_bad="BAD-2026-001",
            dossier_transit_id=1,
            date_emission=date(2026, 1, 20),
            date_validite=date(2026, 2, 20)
        )
        assert bad.numero_bad == "BAD-2026-001"
        assert bad.statut == "emis"

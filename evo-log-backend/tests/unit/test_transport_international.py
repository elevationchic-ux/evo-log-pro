"""Unit tests for Transport International module - International road transport"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.transport_international import (
    OrdreTransport, CarnetTIR, CMR, ScelleRoutier,
    PositionGPS, CET, AssuranceFAP
)
from app.services.transport_international_service import (
    TransportInternationalService, OrdreTransportService, CarnetTIRService,
    CMRService, ScelleRoutierService, PositionGPSService
)


class TestOrdreTransportService:
    """Test Ordre Transport service"""
    
    def test_creer_ordre_transport(self, db: Session):
        """Test creating transport order"""
        ordre = OrdreTransportService.creer_ordre_transport(
            db=db,
            numero_ot="OT-2026-001",
            client_id=1,
            origine="Douala",
            destination="Yaoundé",
            date_depart=date(2026, 1, 15),
            distance_km=200.0
        )
        assert ordre.numero_ot == "OT-2026-001"
        assert ordre.origine == "Douala"
        assert ordre.statut == "planifie"


class TestCarnetTIRService:
    """Test Carnet TIR service"""
    
    def test_creer_carnet_tir(self, db: Session):
        """Test creating TIR carnet"""
        carnet = CarnetTIRService.creer_carnet_tir(
            db=db,
            numero_carnet="TIR-2026-001",
            vehicule_id=1,
            date_emission=date(2026, 1, 15),
            date_validite=date(2026, 12, 31),
            nombre_virements=5
        )
        assert carnet.numero_carnet == "TIR-2026-001"
        assert carnet.nombre_virements == 5
        assert carnet.statut == "actif"


class TestCMRService:
    """Test CMR service"""
    
    def test_emettre_cmr(self, db: Session):
        """Test issuing CMR"""
        cmr = CMRService.emettre_cmr(
            db=db,
            numero_cmr="CMR-2026-001",
            ordre_transport_id=1,
            expediteur="SARL LOGISTIQUE",
            destinataire="CAMEROON BREWERIES",
            date_emission=date(2026, 1, 15)
        )
        assert cmr.numero_cmr == "CMR-2026-001"
        assert cmr.expediteur == "SARL LOGISTIQUE"
        assert cmr.statut == "emis"


class TestScelleRoutierService:
    """Test Scelle Routier service"""
    
    def test_appliquer_scelle(self, db: Session):
        """Test applying road seal"""
        scelle = ScelleRoutierService.appliquer_scelle(
            db=db,
            numero_scelle="SCL-2026-001",
            vehicule_id=1,
            type_scelle="METALLIQUE",
            date_application=date(2026, 1, 15)
        )
        assert scelle.numero_scelle == "SCL-2026-001"
        assert scelle.type_scelle == "METALLIQUE"
        assert scelle.statut == "actif"


class TestPositionGPSService:
    """Test Position GPS service"""
    
    def test_enregistrer_position(self, db: Session):
        """Test recording GPS position"""
        position = PositionGPSService.enregistrer_position(
            db=db,
            vehicule_id=1,
            latitude=4.0581,
            longitude=9.7043,
            date_position=datetime(2026, 1, 15, 10, 30),
            vitesse=60.0
        )
        assert position.vehicule_id == 1
        assert position.latitude == 4.0581
        assert position.longitude == 9.7043

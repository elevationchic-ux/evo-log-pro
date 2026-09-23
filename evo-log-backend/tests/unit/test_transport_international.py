"""Unit tests for Transport International module - International road transport

Tests ecrits contre l'API reelle de transport_international_service :
signatures statiques (db, numero_ot, client_id, ...), enums reels
(TypeTransitRoutier, StatutTransport) et statuts en chaine tels que poses
par les services ("actif", "emis", "pose").
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.transport_international import (
    OrdreTransport, CarnetTIR, CMR, ScelleRoutier, PositionTransport,
    TypeTransitRoutier, StatutTransport,
)
from app.services.transport_international_service import (
    OrdreTransportService, CarnetTIRService, CMRService,
    ScelleRoutierService, PositionTransportService,
)


@pytest.fixture
def ordre_transport(db: Session) -> OrdreTransport:
    """OT Douala -> Yaounde cree via le service (base des documents TIR/CMR/scelle)"""
    return OrdreTransportService.creer_ordre_transport(
        db=db,
        numero_ot="OT-2026-001",
        client_id=1,
        transporteur_id=2,
        camion_id=3,
        conducteur_id=4,
        type_transit=TypeTransitRoutier.TIR,
        lieu_chargement="Douala",
        lieu_livraison="Yaounde",
        pays_destination="Cameroun",
        code_pays_destination="CM",
        marchandise="Sac de ciment",
        poids_net=24.0,
        poids_brut=26.0,
        nombre_colis=1200,
        valeur_marchandise=12000000.0,
        montant_freight=850000.0,
    )


class TestOrdreTransportService:
    """Test Ordre Transport service"""

    def test_creer_ordre_transport(self, db: Session, ordre_transport):
        """Test creating transport order"""
        assert ordre_transport.numero_ot == "OT-2026-001"
        assert ordre_transport.lieu_chargement == "Douala"
        assert ordre_transport.statut == StatutTransport.PLANIFIE
        assert ordre_transport.type_transit == TypeTransitRoutier.TIR

    def test_mettre_en_transit(self, db: Session, ordre_transport):
        """Test moving order to in-transit"""
        ot = OrdreTransportService.mettre_en_transit(db=db, ot_id=ordre_transport.id)
        assert ot.statut == StatutTransport.EN_TRANSIT
        assert ot.date_chargement_reelle is not None

    def test_marquer_livre(self, db: Session, ordre_transport):
        """Test marking order as delivered"""
        ot = OrdreTransportService.marquer_livre(db=db, ot_id=ordre_transport.id)
        assert ot.statut == StatutTransport.LIVRE
        assert ot.date_livraison_reelle is not None


class TestCarnetTIRService:
    """Test Carnet TIR service"""

    def test_creer_carnet_tir(self, db: Session, ordre_transport):
        """Test creating TIR carnet"""
        carnet = CarnetTIRService.creer_carnet_tir(
            db=db,
            numero_carnet="TIR-2026-001",
            ordre_transport_id=ordre_transport.id,
            pays_emission="Cameroun",
            code_pays_emission="CM",
            bureau_depart="Douala",
            bureau_arrivee="Lagos",
            montant_garantie=10000000.0,
        )
        assert carnet.numero_carnet == "TIR-2026-001"
        assert carnet.ordre_transport_id == ordre_transport.id
        assert carnet.statut == "actif"
        # Validite d'un an pose par le service
        assert carnet.date_validite > carnet.date_emission


class TestCMRService:
    """Test CMR service"""

    def test_emettre_cmr(self, db: Session, ordre_transport):
        """Test issuing CMR"""
        cmr = CMRService.emettre_cmr(
            db=db,
            numero_cmr="CMR-2026-001",
            ordre_transport_id=ordre_transport.id,
            expediteur="SARL LOGISTIQUE",
            destinataire="CAMEROON BREWERIES",
            transporteur="TRANS CM",
            lieu_chargement="Douala",
            lieu_livraison="Yaounde",
            marchandise="Boissons",
            poids_net=24.0,
            poids_brut=26.0,
            nombre_colis=1200,
            type_emballage="Palettes",
            valeur_marchandise=12000000.0,
        )
        assert cmr.numero_cmr == "CMR-2026-001"
        assert cmr.expediteur == "SARL LOGISTIQUE"
        assert cmr.statut == "emis"

    def test_signer_cmr(self, db: Session, ordre_transport):
        """Test the three-party CMR signature chain"""
        cmr = CMRService.emettre_cmr(
            db=db,
            numero_cmr="CMR-2026-002",
            ordre_transport_id=ordre_transport.id,
            expediteur="Expediteur SA",
            destinataire="Destinataire SARL",
            transporteur="Transitaire",
            lieu_chargement="Douala",
            lieu_livraison="Bafoussam",
            marchandise="Fer",
            poids_net=20.0,
            poids_brut=21.0,
            nombre_colis=10,
            type_emballage="Sacs",
            valeur_marchandise=5000000.0,
        )
        cmr = CMRService.signer_cmr(db=db, cmr_id=cmr.id, type_signature="expediteur")
        assert cmr.signature_expediteur is True
        assert cmr.statut == "emis"
        cmr = CMRService.signer_cmr(db=db, cmr_id=cmr.id, type_signature="destinataire")
        assert cmr.signature_destinataire is True
        assert cmr.statut == "livre"


class TestScelleRoutierService:
    """Test Scelle Routier service"""

    def test_poser_scelle(self, db: Session, ordre_transport):
        """Test applying road seal"""
        scelle = ScelleRoutierService.poser_scelle(
            db=db,
            numero_scelle="SCL-2026-001",
            ordre_transport_id=ordre_transport.id,
            type_scelle="douane",
            emplacement="Porte arriere",
            pose_par="Brigade de Douala",
        )
        assert scelle.numero_scelle == "SCL-2026-001"
        assert scelle.type_scelle == "douane"
        assert scelle.statut == "pose"

    def test_verifier_scelle(self, db: Session, ordre_transport):
        """Test verifying an intact seal"""
        scelle = ScelleRoutierService.poser_scelle(
            db=db,
            numero_scelle="SCL-2026-002",
            ordre_transport_id=ordre_transport.id,
            type_scelle="transporteur",
            emplacement="Conteneur",
            pose_par="Transporteur",
        )
        scelle = ScelleRoutierService.verifier_scelle(
            db=db, scelle_id=scelle.id, verifie_par="Poste de Edéa", intact=True
        )
        assert scelle.statut == "verifie"
        assert scelle.intact is True
        assert scelle.date_verification is not None


class TestPositionGPSService:
    """Test Position GPS service"""

    def test_enregistrer_position(self, db: Session, ordre_transport):
        """Test recording GPS position"""
        position = PositionTransportService.enregistrer_position(
            db=db,
            ordre_transport_id=ordre_transport.id,
            latitude=4.0581,
            longitude=9.7043,
            vitesse_kmh=60.0,
            direction=45.0,
        )
        assert position.ordre_transport_id == ordre_transport.id
        assert float(position.latitude) == pytest.approx(4.0581)
        assert float(position.longitude) == pytest.approx(9.7043)
        assert position.statut == "en_mouvement"

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
    CorridorCEMACService, TransportInternationalReportingService,
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

    def test_lister_retourne_les_ot_crees(self, db: Session, ordre_transport):
        """Batch 12 : GET /ordres-transport branché sur lister(). Vérifie que
        la route frontend (transport-international/page.tsx) recevra bien les
        lignes stockées au lieu d'une liste vide."""
        rows = OrdreTransportService.lister(db)
        assert any(r.id == ordre_transport.id for r in rows)

    def test_lister_filtre_par_statut(self, db: Session, ordre_transport):
        """Batch 12 : le filtre `statut=` est exploitable côté écran (onglet
        'En transit' / 'Livrés')."""
        OrdreTransportService.marquer_livre(db=db, ot_id=ordre_transport.id)
        livres = OrdreTransportService.lister(db, statut=StatutTransport.LIVRE.value)
        planifies = OrdreTransportService.lister(db, statut=StatutTransport.PLANIFIE.value)
        assert any(r.id == ordre_transport.id for r in livres)
        assert not any(r.id == ordre_transport.id for r in planifies)

    def test_lister_pagination_bornee(self, db: Session, ordre_transport):
        """Batch 12 : `limit` est borné à 500 côté service pour éviter un
        abuse. offset/limit doivent être appliqués sans crash."""
        # limit <= 0 ou > 500 est clampé, jamais de SQL négatif
        rows_small = OrdreTransportService.lister(db, limit=1)
        assert len(rows_small) <= 1
        rows_overflow = OrdreTransportService.lister(db, limit=10_000)
        assert len(rows_overflow) <= 500


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

    def test_lister_carnets(self, db: Session, ordre_transport):
        """Batch 12 : GET /carnets-tir branché sur lister() côté frontend."""
        CarnetTIRService.creer_carnet_tir(
            db=db,
            numero_carnet="TIR-LIST-01",
            ordre_transport_id=ordre_transport.id,
            pays_emission="Cameroun",
            code_pays_emission="CM",
            bureau_depart="Douala",
            bureau_arrivee="N'Djamena",
            montant_garantie=5000000.0,
        )
        rows = CarnetTIRService.lister(db)
        assert any(r.numero_carnet == "TIR-LIST-01" for r in rows)


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


class TestPreuvesLivraisonListEndpoint:
    """GET /api/v1/transport-international/preuves-livraison (endpoint ajoute session 2026-09-27)."""

    def test_liste_vide_retourne_items_et_total(self, client: TestClient):
        r = client.get("/api/v1/transport-international/preuves-livraison")
        assert r.status_code == 200, r.text
        body = r.json()
        assert "items" in body and isinstance(body["items"], list)
        assert body["total"] == len(body["items"])

    def test_endpoint_exige_auth(self, unauthenticated):
        """Sans JWT, la route ne doit pas repondre (protegee par get_current_user).

        `unauthenticated` retire uniquement l'override get_current_user de la
        fixture client ; get_db reste surcharge sur la base memoire de test.
        (L'ancien pattern create()ait un TestClient nu apres un
        dependency_overrides.clear() : sans override get_db, la requete
        partait sur l'engine reel de l'application.)
        """
        r = unauthenticated.get("/api/v1/transport-international/preuves-livraison")
        assert r.status_code in (401, 403)


class TestConducteurResponseFields:
    """ConducteurResponse exposes optional fields that exist in the model."""

    def test_champs_optionnels_exposes(self):
        from app.schemas.transport import ConducteurResponse

        fields = ConducteurResponse.model_fields
        # Fields added this session (were missing before)
        assert "categorie_permis" in fields, "categorie_permis absent du schema"
        assert "expiration_visite_medicale" in fields, "expiration_visite_medicale absent"
        assert "date_naissance" in fields, "date_naissance absent"
        assert "numero_cnps" in fields, "numero_cnps absent"

    def test_champs_sont_optionnels(self):
        """All added fields default to None so existing JSON without them still validates."""
        from app.schemas.transport import ConducteurResponse
        from datetime import datetime

        minimal = ConducteurResponse(
            id=1, nom="Mballa", prenom="Jean",
            numero_permis="AB-99-2024", date_expiration_permis=datetime(2027, 1, 1),
            telephone="+2376000011", email="t@t.cm", adresse="Douala",
            is_active=True, created_at=datetime(2026, 1, 1),
        )
        assert minimal.categorie_permis is None
        assert minimal.expiration_visite_medicale is None
        assert minimal.date_naissance is None
        assert minimal.numero_cnps is None


class TestStatutEnumCoercion:
    """Le filtre `?statut=` comparait la colonne Enum au NOM stocké ('LIVRE')
    alors que l'API fournit la valeur ('livre') : il ne renvoyait jamais rien.
    Apres coercion valeur->membre, la valeur valide filtre reellement et une
    valeur inconnue renvoie une liste vide honnete (pas d'erreur 500)."""

    def test_valeur_retrouve_lebon_enregistrement(self, db: Session, ordre_transport):
        planifies = OrdreTransportService.lister(db, statut=StatutTransport.PLANIFIE.value)
        assert any(r.id == ordre_transport.id for r in planifies)

    def test_valeur_inconnue_renvoie_liste_vide(self, db: Session, ordre_transport):
        assert OrdreTransportService.lister(db, statut="statut_fantome") == []

    def test_nom_enum_nest_pas_une_valeur_valide(self, db: Session, ordre_transport):
        # 'PLANIFIE' (NOM stocké) n'est pas une valeur d'enum -> vide honnete.
        assert OrdreTransportService.lister(db, statut="PLANIFIE") == []


class TestCMRLister:
    """CMR etait write-only (POST sans GET) : CMRService.lister rend la
    liste reellement consultable."""

    def _emmet(self, db, ordre_transport, numero):
        return CMRService.emettre_cmr(
            db=db, numero_cmr=numero, ordre_transport_id=ordre_transport.id,
            expediteur="Expediteur", destinataire="Destinataire", transporteur="Trans",
            lieu_chargement="Douala", lieu_livraison="Yaounde", marchandise="Fer",
            poids_net=10.0, poids_brut=11.0, nombre_colis=5,
            type_emballage="Sacs", valeur_marchandise=1000000.0,
        )

    def test_lister_retourne_les_cmr_emises(self, db: Session, ordre_transport):
        self._emmet(db, ordre_transport, "CMR-LIST-01")
        rows = CMRService.lister(db)
        assert any(r.numero_cmr == "CMR-LIST-01" for r in rows)

    def test_lister_filtre_par_statut_chaine(self, db: Session, ordre_transport):
        self._emmet(db, ordre_transport, "CMR-LIST-02")
        emis = CMRService.lister(db, statut="emis")
        assert any(r.numero_cmr == "CMR-LIST-02" for r in emis)
        assert CMRService.lister(db, statut="livre") == []


class TestCorridorCEMACService:
    def test_creer_puis_lister_corridor(self, db: Session):
        CorridorCEMACService.creer_corridor(
            db=db, nom="Douala-Yaounde", pays_depart="Cameroun", code_pays_depart="CM",
            pays_arrivee="Cameroun", code_pays_arrivee="CM",
            distance_km=250.0, duree_estimee_heures=4.0,
        )
        rows = CorridorCEMACService.lister(db)
        assert any(r.nom == "Douala-Yaounde" for r in rows)

    def test_lister_filtre_par_statut(self, db: Session):
        CorridorCEMACService.creer_corridor(
            db=db, nom="Douala-Bangui", pays_depart="Cameroun", code_pays_depart="CM",
            pays_arrivee="RCA", code_pays_arrivee="CF",
            distance_km=780.0, duree_estimee_heures=12.0,
        )
        assert any(r.nom == "Douala-Bangui" for r in CorridorCEMACService.lister(db, statut="actif"))
        assert CorridorCEMACService.lister(db, statut="ferme") == []


class TestStatistiques:
    """Les KPI venaient d'un `Array.length` tronque a 50 lignes. statistiques()
    doit renvoyer des comptes/sommes SQL exacts, quelles que soient la
    volumetrie et la tranche affichee."""

    def test_vide_tous_compteurs_a_zero(self, db: Session):
        stats = TransportInternationalReportingService.statistiques(db)
        assert stats["ordres_transport"]["total"] == 0
        assert stats["ordres_transport"]["par_statut"] == {}
        assert stats["ordres_transport"]["tonnage_net"] == 0.0
        assert stats["carnets_tir"] == 0
        assert stats["cmr"] == 0
        assert stats["corridors_cemac"] == 0

    def test_compte_par_statut_et_tonnage(self, db: Session, ordre_transport):
        # ordre_transport fixture : poids_net=24.0, statut planifie.
        second = OrdreTransportService.creer_ordre_transport(
            db=db, numero_ot="OT-2026-002", client_id=1, transporteur_id=2,
            camion_id=3, conducteur_id=4, type_transit=TypeTransitRoutier.TIR,
            lieu_chargement="Douala", lieu_livraison="Bafoussam",
            pays_destination="Cameroun", code_pays_destination="CM",
            marchandise="Riz", poids_net=10.0, poids_brut=11.0, nombre_colis=100,
            valeur_marchandise=500000.0, montant_freight=100000.0,
        )
        OrdreTransportService.marquer_livre(db=db, ot_id=second.id)
        stats = TransportInternationalReportingService.statistiques(db)
        assert stats["ordres_transport"]["total"] == 2
        assert stats["ordres_transport"]["par_statut"]["planifie"] == 1
        assert stats["ordres_transport"]["par_statut"]["livre"] == 1
        assert stats["ordres_transport"]["tonnage_net"] == pytest.approx(34.0)


class TestNouveauxEndpointsLecture:
    """GET /statistiques, /cmr, /corridors-cemac : routes ajoutees pour sortir
    les donnees write-only et fournir des KPI exacts a l'ecran."""

    def test_statistiques_200_structure(self, client):
        r = client.get("/api/v1/transport-international/statistiques")
        assert r.status_code == 200, r.text
        body = r.json()
        assert "ordres_transport" in body
        assert body["ordres_transport"]["total"] == 0
        for key in ("carnets_tir", "cmr", "corridors_cemac"):
            assert key in body

    def test_cmr_liste_vide(self, client):
        r = client.get("/api/v1/transport-international/cmr")
        assert r.status_code == 200, r.text
        assert r.json() == []

    def test_corridors_liste_vide(self, client):
        r = client.get("/api/v1/transport-international/corridors-cemac")
        assert r.status_code == 200, r.text
        assert r.json() == []

    def test_statistiques_exige_auth(self, unauthenticated):
        r = unauthenticated.get("/api/v1/transport-international/statistiques")
        assert r.status_code in (401, 403)

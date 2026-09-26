"""Tests d22 — aggregats corridor CEMAC / TCO flotte : politique zero-mock.

Le service renvoyait des dicts 100% codés en dur (23 camions en transit,
convois 14/9, TCO 1240 XAF/km, immatriculations LT-TR-4021...). Ces tests
verrouillent les deux proprietes de la reecriture :

1. base vide -> vides HONNETES (None + note explicite), jamais de chiffres
   decoratifs ;
2. base peuplee -> valeurs recalculees exactement depuis les modeles reels
   (corridors_cemac_transit, procedures_tir, missions, frais_missions,
   camions, transport_pannes).
"""
from datetime import datetime, timedelta

import pytest

from app.models.transport import Camion, Mission, MissionStatus, Panne
from app.models.transit_cemac import (
    CorridorCEMACTransit, PosteFrontalier, ProcedureTIR,
    TypePosteFrontalier,
)
from app.models.frais_mission import FraisMission
from app.services.transport_international_service import TMSAdvancedOptimizerService


class TestCorridorVideHonnete:
    def test_base_vide_ne_retourne_aucun_chiffre_decoratif(self, db):
        r = TMSAdvancedOptimizerService.get_corridor_cemac_status(db)
        assert r["corridors"] == []
        # L'ancienne implementation renvoyait 23 : le nil est la preuve du recal.
        assert r["total_camions_en_transit"] is None
        assert "source" in r

    def test_plus_faux_dict_corridor(self, db):
        r = TMSAdvancedOptimizerService.get_corridor_cemac_status(db)
        assert "systeme_tracking" not in r, "la mention decorative doit disparaitre"


class TestTCOBaseVide:
    def test_cout_km_non_calculable_n_est_pas_invente(self, db):
        r = TMSAdvancedOptimizerService.get_tco_fleet_analytics(db)
        assert r["cout_global_moyen_km_xaf"] is None
        assert r["repartition_tco"] == []
        assert r["alertes_maintenance_predictive"] == []
        assert r["note"], "le nil doit etre explique, pas seulement vide"

    def test_plus_de_fLOTTE_fictive_48(self, db):
        r = TMSAdvancedOptimizerService.get_tco_fleet_analytics(db)
        assert r["flotte_totale_vehicules"] == 0


class TestCorridorRecalcule:
    @pytest.fixture
    def corridor_seed(self, db):
        cor = CorridorCEMACTransit(
            code="DOU-NDJ", nom="Corridor Douala - N'Djamena",
            origine="Douala", destination="N'Djamena",
            distance_km=1850, duree_estimee_heures=168,
            pays_origine="CM", pays_destination="TD",
            points_dangers=None, risques='["barrieres"]',
            est_actif=True,
        )
        db.add(cor)
        db.flush()
        db.add(PosteFrontalier(
            corridor_id=cor.id, code="KOU", nom="Kousseri",
            pays="Cameroun", ville="Kousseri",
            type_poste=TypePosteFrontalier.DOUANE,
            coordonnees="12.0833, 15.0333", est_actif=True,
        ))
        for i in range(2):
            db.add(ProcedureTIR(
                numero_carnet=f"TIR-2026-{i:03d}",
                date_delivrance=datetime.now().date(),
                date_validite=(datetime.now() + timedelta(days=90)).date(),
                numero_assurance="ASS-001", assureur="AXA",
                montant_garantie=10_000_000,
                bureau_depart="Douala", bureau_arrivee="N'Djamena",
                corridor="DOU-NDJ", statut="en_cours",
            ))
        # Un carnet clos ne doit pas etre compte comme convoi actif.
        db.add(ProcedureTIR(
            numero_carnet="TIR-2026-999",
            date_delivrance=datetime.now().date() - timedelta(days=200),
            date_validite=datetime.now().date(),
            numero_assurance="ASS-002", assureur="AXA",
            montant_garantie=5_000_000,
            bureau_depart="Douala", bureau_arrivee="N'Djamena",
            corridor="DOU-NDJ", statut="cloture",
        ))
        db.commit()
        return cor

    def test_convois_actifs_comptes_reellement(self, db, corridor_seed):
        r = TMSAdvancedOptimizerService.get_corridor_cemac_status(db)
        assert r["total_camions_en_transit"] == 2
        cor = r["corridors"][0]
        assert cor["code"] == "DOU-NDJ"
        assert cor["distance_km"] == 1850
        assert cor["duree_moyenne_jours"] == 7
        assert cor["convois_actifs"] == 2

    def test_points_passage_depuis_postes_reels(self, db, corridor_seed):
        r = TMSAdvancedOptimizerService.get_corridor_cemac_status(db)
        points = r["corridors"][0]["points_passage"]
        assert len(points) == 1
        assert points[0]["ville"] == "Kousseri"
        assert points[0]["lat"] == pytest.approx(12.0833)
        assert points[0]["lng"] == pytest.approx(15.0333)


class TestTCORecalcule:
    @pytest.fixture
    def tco_seed(self, db):
        camion = Camion(
            immatriculation="AB-123-CM", marque="Mercedes", modele="Actros",
            kilometrage=150_000, is_active=True,
            prochaine_maintenance=datetime.now() - timedelta(days=10),
        )
        camion_ok = Camion(
            immatriculation="CD-456-CM", marque="MAN", modele="TGX",
            kilometrage=80_000, is_active=True,
            prochaine_maintenance=datetime.now() + timedelta(days=20),
        )
        hors_fenetre = Camion(
            immatriculation="EF-789-CM", marque="Renault", modele="T",
            kilometrage=10_000, is_active=True,
            prochaine_maintenance=datetime.now() + timedelta(days=200),
        )
        db.add_all([camion, camion_ok, hors_fenetre])
        db.flush()

        mission = Mission(
            reference="MSN-001", camion_id=camion.id,
            statut=MissionStatus.TERMINEE, distance_km=1000,
        )
        mission_sans_distance = Mission(
            reference="MSN-002", camion_id=camion_ok.id,
            statut=MissionStatus.TERMINEE, distance_km=None,
        )
        db.add_all([mission, mission_sans_distance])
        db.flush()

        db.add_all([
            FraisMission(mission_id=mission.id, type_frais="CARBURANT",
                         montant=400_000, statut="VALIDE"),
            FraisMission(mission_id=mission.id, type_frais="PEAGE",
                         montant=100_000, statut="REMBOURSE"),
            # Jamais compte : non valide.
            FraisMission(mission_id=mission.id, type_frais="DIVERS",
                         montant=999_999, statut="BROUILLON"),
            # Jamais compte : mission non terminee (id inexistante côté terminé).
            FraisMission(mission_id=mission_sans_distance.id, type_frais="CARBURANT",
                         montant=500_000, statut="VALIDE"),
        ])

        db.add(Panne(
            reference="PAN-001", camion_id=camion.id, type_panne="freinage",
            gravite="bloquante", description="Freins HS", statut="immobilisee",
        ))
        db.commit()
        return camion, camion_ok

    def test_cout_km_calcule_sur_frais_valide_de_mission_terminee(self, db, tco_seed):
        r = TMSAdvancedOptimizerService.get_tco_fleet_analytics(db)
        # 500 000 XAF justifies / 1000 km prouves = 500 XAF/km.
        assert r["cout_global_moyen_km_xaf"] == pytest.approx(500.0)
        assert r["distance_totale_km_prouvee"] == 1000
        assert r["total_frais_justifies_xaf"] == pytest.approx(500_000)
        assert r["note"] is None

    def test_repartition_reflete_la_base_reelle(self, db, tco_seed):
        r = TMSAdvancedOptimizerService.get_tco_fleet_analytics(db)
        posts = {b["poste"]: b for b in r["repartition_tco"]}
        assert set(posts) == {"CARBURANT", "PEAGE"}
        assert posts["CARBURANT"]["pourcentage"] == pytest.approx(80.0)
        assert posts["CARBURANT"]["cout_km_xaf"] == pytest.approx(400.0)
        assert posts["PEAGE"]["cout_km_xaf"] == pytest.approx(100.0)

    def test_alertes_sur_echeances_reelles_jamais_immatriculation_inventee(self, db, tco_seed):
        r = TMSAdvancedOptimizerService.get_tco_fleet_analytics(db)
        plaques = [a["immatriculation"] for a in r["alertes_maintenance_predictive"]]
        # Hors fenetre (j+200) jamais remonte ; les deux autres camions oui.
        assert "EF-789-CM" not in plaques
        assert plaques.count("AB-123-CM") == 2  # echeance depassee + panne bloquante
        assert "CD-456-CM" in plaques
        by_camion = {a["immatriculation"]: a for a in r["alertes_maintenance_predictive"]}
        assert by_camion["AB-123-CM"]["priorite"] in ("CRITIQUE", "HAUTE")
        assert all(a["immatriculation"] != "LT-TR-4021" for a in r["alertes_maintenance_predictive"])
        panne_alerts = [
            a for a in r["alertes_maintenance_predictive"] if a["alerte"].startswith("PANNE_")
        ]
        assert panne_alerts[0]["panne_reference"] == "PAN-001"

    def test_flotte_totale_compte_camions_actifs(self, db, tco_seed):
        r = TMSAdvancedOptimizerService.get_tco_fleet_analytics(db)
        assert r["flotte_totale_vehicules"] == 3

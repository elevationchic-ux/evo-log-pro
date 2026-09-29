"""Tests d23  services WMS avancé : politique zero-mock.

Le service `magasin_wms_avance_service.py` fabriquait :
- des lignes de vague inventees (ART-1000x, LOT-2026-x, quantite 12.5,
  distances simulees 45+i*8) sans lire la moindre commande ;
- une valorisation d'ecarts d'inventaire a un prix moyen arbitraire de
  15 000 XAF, avec un PV de « regularisation » qui n'ecrivait rien ;
- des recus cross-dock « XDOCK-<timestamp » et un « gain_temps_heures »
  de 18.5 sans aucune persistance ;
- des scans RF « certifies conformes » pour tout code d'au moins 4
  caracteres, avec l'emplacement invente A01-R04-N02.

Chaque comportement est verrouille ici : either la valeur vient de la base,
either elle est null et expliquee  jamais inventee.
"""
from datetime import datetime

import pytest

from app.models.magasin import (
    Article, Commande, CommandeStatut, LigneCommande, Stock,
)
from app.schemas.magasin_wms_avance import VaguePickingResponse, InventaireRegularisationResponse
from app.services.magasin_wms_avance_service import (
    CrossDockingService, InventaireCompletService, PickingAvanceService,
    RadioFrequencePDAService,
)


class TestVaguePickingSurBaseVide:
    def test_aucune_commande_aucune_ligne_inventee(self, db):
        r = PickingAvanceService.generer_vague_picking(db, [9999], "FIFO")
        assert r["nb_lignes"] == 0
        assert r["lignes"] == []
        # L'ancienne version renvoyait 5 lignes "ART-10000..." pour n'importe quelle id.
        VaguePickingResponse.model_validate(r)


class TestVaguePickingReel:
    @pytest.fixture
    def commande_semee(self, db):
        art = Article(code="ART-CIMENT-50", designation="Ciment CPA 50kg",
                      prix_unitaire=5000, is_active=True)
        db.add(art)
        db.flush()
        stock = Stock(code_article=art.code, designation=art.designation,
                      quantite_disponible=1000, prix_unitaire=5000,
                      emplacement="A-02-01", date_derniere_entree=datetime(2026, 1, 5),
                      is_active=True)
        db.add(stock)
        cmd = Commande(reference="CMD-2026-001", statut=CommandeStatut.VALIDEE,
                       type_commande="sortie")
        db.add(cmd)
        db.flush()
        db.add(LigneCommande(commande_id=cmd.id, article_id=art.id,
                             designation=art.designation, quantite=40))
        db.commit()
        return cmd, art, stock

    def test_ligne_produit_de_la_commande_reelle(self, db, commande_semee):
        cmd, art, stock = commande_semee
        r = PickingAvanceService.generer_vague_picking(db, [cmd.id], "FIFO")
        assert r["nb_lignes"] == 1
        ligne = r["lignes"][0]
        assert ligne["article_code"] == art.code
        assert ligne["emplacement"] == "A-02-01"
        assert ligne["quantite"] == 40.0
        # Lot/expiration et distances : jamais fabriques.
        assert ligne["lot_numero"] is None
        assert ligne["distance_parcours_m"] is None
        assert r["distance_totale_m"] is None
        assert "note" in r and r["note"]
        VaguePickingResponse.model_validate(r)


class TestEcartInventaireValorise:
    def test_prix_reel_de_la_ligne_de_stock_utilise(self, db):
        art = Article(code="ART-FER", designation="Fer a beton", is_active=True)
        db.add(art)
        stock = Stock(code_article="ART-FER", designation="Fer a beton",
                      quantite_disponible=100, prix_unitaire=750,
                      emplacement="B-01-02", is_active=True)
        db.add(stock)
        db.commit()
        r = InventaireCompletService.calculer_ecarts_et_regulariser(
            db, campagne_id=7,
            lignes_comptage=[{
                "article_code": "ART-FER", "emplacement": "B-01-02",
                "quantite_physique": 90, "quantite_theorique": 100,
            }],
        )
        # 10 u d'ecart x 750 F (prix reel), au lieu du 15 000 F arbitraire.
        assert r["nb_ecarts_detectes"] == 1
        assert r["valeur_totale_ecarts_xaf"] == pytest.approx(7500)
        assert r["statut"] == "non_persiste", "le PV ne doit pas pretendre regulariser"
        assert "AUCUNE ecriture" in r["note"]
        InventaireRegularisationResponse.model_validate(r)

    def test_prix_inconnu_signale_non_simule(self, db):
        r = InventaireCompletService.calculer_ecarts_et_regulariser(
            db, campagne_id=8,
            lignes_comptage=[{
                "article_code": "ART-INCONNU", "emplacement": "X",
                "quantite_physique": 5, "quantite_theorique": 2,
            }],
        )
        assert r["valeur_totale_ecarts_xaf"] == 0
        assert "ART-INCONNU" in r["note"]


class TestCrossDockingSansFauxRecu:
    def test_consolidation_fidele_et_receipt_null(self, db):
        r = CrossDockingService.executer_cross_docking(
            db, manifeste_ref="MAN-REV-123", camion_immat="BC-456-CM",
            colis_items=[
                {"colis_ref": "C1", "poids_kg": 800},
                {"colis_ref": "C2", "poids_kg": 250},
                {"colis_ref": "C3"},
            ],
        )
        assert r["nb_colis"] == 3
        assert r["poids_total_kg"] == pytest.approx(1050)
        assert r["poids_non_renseignes"] == 1
        # L'ancienne version renvoyait "XDOCK-<timestamp>" et gain 18.5 h.
        assert r["cross_dock_ref"] is None
        assert r["gain_temps_heures"] is None
        assert r["statut"] == "non_persiste"
        assert all(i.get("quai_chargement") is None for i in r["items"])


class TestScanRFResolutionReelle:
    def test_code_inconnu_n_est_plus_valide_par_longueur(self, db):
        r = RadioFrequencePDAService.scanner_code_barres(db, "NIMP-2026-TROPHONGUE")
        assert r["valide"] is False
        assert r["type_identifie"] == "INCONNU"
        # Plus d'emplacement invente quand rien ne correspond.
        assert r["emplacement_attribue"] is None

    def test_code_barres_article_resolu_avec_emplacement_reel(self, db):
        art = Article(code="ART-RIS", designation="Riz local 25kg",
                      code_barres="6091234500011", is_active=True)
        db.add(art)
        db.flush()
        db.add(Stock(code_article="ART-RIS", designation=art.designation,
                     quantite_disponible=300, emplacement="C-05-03", is_active=True))
        db.commit()
        r = RadioFrequencePDAService.scanner_code_barres(db, "6091234500011")
        assert r["valide"] is True
        assert r["article_code"] == "ART-RIS"
        assert r["emplacement_attribue"] == "C-05-03"

    def test_code_de_ligne_de_stock_resolu_sans_article(self, db):
        db.add(Stock(code_article="ART-SANS-FICHE", designation="Vrac",
                     quantite_disponible=10, emplacement="D-01-01", is_active=True))
        db.commit()
        r = RadioFrequencePDAService.scanner_code_barres(db, "ART-SANS-FICHE")
        assert r["valide"] is True
        assert r["article_code"] == "ART-SANS-FICHE"
        assert r["emplacement_attribue"] == "D-01-01"

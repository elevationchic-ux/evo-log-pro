"""Tests WMS avance : ecarts d'inventaire valorises et cross-docking
honnete (aggregation reelle, rien de fabrique)."""
from decimal import Decimal

from app.models.magasin import Stock
from app.services.magasin_wms_avance_service import (
    InventaireCompletService, CrossDockingService,)


def _stock(db, code, pu, qte=100):
    s = Stock(company_id=None, code_article=code, designation=f"Art {code}",
              quantite_disponible=qte, quantite_reservee=0,
              prix_unitaire=Decimal(str(pu)), is_active=True)
    db.add(s)
    db.commit()
    return s


def test_ecarts_valorises_au_prix_reel(db):
    """Ecart -5 sur un article a 8 500 XAF = 42 500 XAF ; ecart nul ignore."""
    _stock(db, "WMS-1", 8500)

    res = InventaireCompletService.calculer_ecarts_et_regulariser(
        db, campagne_id=7, lignes_comptage=[
            {"article_code": "WMS-1", "quantite_theorique": 100,
             "quantite_physique": 95, "emplacement": "A1"},
            {"article_code": "WMS-1", "quantite_theorique": 100,
             "quantite_physique": 100},
        ])

    assert res["nb_articles_controles"] == 2
    assert res["nb_ecarts_detectes"] == 1
    assert res["ecarts"][0]["ecart_quantite"] == -5
    assert res["ecarts"][0]["valeur_ecart_xaf"] == 42_500
    assert res["statut"] == "non_persiste"


def test_ecart_prix_inconnu_signale_honnetement(db):
    """Article sans prix unitaire : valorisation 0 + signalement explicite."""
    res = InventaireCompletService.calculer_ecarts_et_regulariser(
        db, campagne_id=8, lignes_comptage=[
            {"article_code": "INCONNU-1", "quantite_theorique": 10,
             "quantite_physique": 8},
        ])

    assert res["valeur_totale_ecarts_xaf"] == 0.0
    assert "INCONNU-1" in res["note"]


def test_cross_docking_agrege_reel_sans_fabriquer(db):
    """Les colis soumis sont agreges tels quels ; aucun recu invente."""
    res = CrossDockingService.executer_cross_docking(
        db, manifeste_ref="MAN-2026-01", camion_immat="LT-1234-AB",
        colis_items=[
            {"colis_ref": "C1", "poids_kg": 500},
            {"colis_ref": "C2", "poids_kg": 300},
        ])

    assert res["statut"] == "non_persiste"
    assert res["cross_dock_ref"] is None
    assert res["nb_colis"] == 2
    assert res["poids_total_kg"] == 800

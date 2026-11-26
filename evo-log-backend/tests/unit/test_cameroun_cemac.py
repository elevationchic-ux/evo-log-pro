"""Tests fiscalite/paie Cameroun : CNPS (plafond), IRPP progressif, TVA."""
from app.services.cameroun_cemac_service import (
    CamerounConfig, PaieCamerounService, OHADAComptabiliteService,)

CONFIG = CamerounConfig()


def test_cnps_sous_plafond():
    """Brut 500 000 (< plafond 750 000) : employe 7 %, employeur 11,5 %."""
    r = PaieCamerounService.calculer_cnps(500_000, CONFIG)
    assert r["base_assujettie"] == 500_000
    assert r["cnps_employe"] == 35_000
    assert r["cnps_employeur"] == 57_500
    assert r["total_cnps"] == 92_500


def test_cnps_plafond_applique():
    """Brut 1 000 000 : base plafonnee a 750 000."""
    r = PaieCamerounService.calculer_cnps(1_000_000, CONFIG)
    assert r["base_assujettie"] == 750_000
    assert r["cnps_employe"] == 52_500
    assert r["cnps_employeur"] == 86_250


def test_irpp_premiere_tranche():
    """Salaire imposable 40 000 : tranche 0-53 000 a 10 % -> 4 000."""
    r = PaieCamerounService.calculer_irpp(40_000, CONFIG)
    assert r["irpp"] == 4_000


def test_irpp_progressif_croissant():
    """L'IRPP croit avec le salaire imposable."""
    bas = PaieCamerounService.calculer_irpp(50_000, CONFIG)["irpp"]
    haut = PaieCamerounService.calculer_irpp(500_000, CONFIG)["irpp"]
    assert haut > bas > 0


def test_tva_ohada_montants():
    """HT 200 000 a 19,25 % -> TVA 38 500, TTC 238 500."""
    r = OHADAComptabiliteService.calculer_tva_ohada(200_000, 0.1925, CONFIG)
    assert r["tva"] == 38_500
    assert r["montant_ttc"] == 238_500
    assert r["devise"] == "XAF"

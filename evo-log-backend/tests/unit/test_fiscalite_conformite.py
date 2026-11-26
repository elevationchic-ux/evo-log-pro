"""Tests fiscalite Cameroun (TVA OHADA, centimes, IS minimum) et
conformite (duree de retention des donnees)."""
from datetime import date, timedelta

from app.services.fiscalite_cameroun_service import OHADAService
from app.services.compliance_service import RGPDComplianceService


def test_tva_ohada_19_25_pourcent():
    """HT 1 000 000 -> TVA 192 500 -> TTC 1 192 500."""
    r = OHADAService.calculer_tva_ohada(1_000_000)
    assert r["montant_tva"] == 192_500
    assert r["montant_ttc"] == 1_192_500
    assert r["taux_tva"] == 19.25


def test_centimes_additionnels_10_pourcent():
    r = OHADAService.calculer_centimes_additionnels(500_000)
    assert r["montant_centimes"] == 50_000


def test_is_minimum_paliers(db):
    """Paliers IS minimum camerounais : <10M -> 300K ; 50-100M -> 1M."""
    assert OHADAService.calculer_is_minimum(db, 5_000_000)["is_minimum"] == 300_000
    assert OHADAService.calculer_is_minimum(db, 75_000_000)["is_minimum"] == 1_000_000
    assert OHADAService.calculer_is_minimum(db, 500_000_000)["is_minimum"] == 2_000_000


def test_duree_retention_selon_type():
    """Donnees fiscales/comptables : 10 ans ; employe : 5 ans ; inconnu : 5."""
    f = RGPDComplianceService.calculer_duree_retention("donnees_fiscales")
    assert f["duree_retention_annees"] == 10
    assert f["date_expiration"].year == date.today().year + 10

    e = RGPDComplianceService.calculer_duree_retention("donnees_employe")
    assert e["duree_retention_annees"] == 5

    d = RGPDComplianceService.calculer_duree_retention("type_inconnu")
    assert d["duree_retention_annees"] == 5
    assert d["base_legale"]

"""Tests des moteurs normatifs profonds : liquidation douaniere CEMAC
et bilan accidentologie QHSE (TF/TG)."""
from datetime import date, datetime

import pytest

from app.services.taxation_douaniere import (
    calculer_liquidation, resoudre_taux_dd, _normaliser_taux,
    TAUX_REDEVANCE_INFORMATIQUE, TAUX_CCI_COMMUNAUTAIRE,
    TAUX_PRELEVEMENT_OHADA, TAUX_TVA_CMR, TAUX_PRECOMPTE_IS,)
from app.models.qhse import AccidentTravail, HeuresExposition
from app.services.qhse_service import WorkPermitsIMDGService


# --------------------------------------------------------------------------- #
# Liquidation douaniere CEMAC
# --------------------------------------------------------------------------- #
def test_normalisation_taux_pourcentage_vers_fraction():
    assert _normaliser_taux(20.0) == 0.20
    assert _normaliser_taux(0.20) == 0.20
    assert _normaliser_taux(1.0) == 1.0


def test_liquidation_mise_consomption_complete():
    """IM4 hors-zone : DD + redevances + TVA sur (assiette + DD + redevances)
    + prelevement OHADA + precompte IS."""
    res = calculer_liquidation(
        valeur_en_douane=1_000_000, taux_dd_explicite=20.0, origine="HORS_ZONE")

    dd = 1_000_000 * 0.20
    redev = 1_000_000 * TAUX_REDEVANCE_INFORMATIQUE
    cci = 1_000_000 * TAUX_CCI_COMMUNAUTAIRE
    ohada = 1_000_000 * TAUX_PRELEVEMENT_OHADA
    base_tva = 1_000_000 + dd + redev + cci
    tva = base_tva * TAUX_TVA_CMR
    pre_is = 1_000_000 * TAUX_PRECOMPTE_IS

    assert res["droit_douane_dd"] == round(dd, 2)
    assert res["redevance_informatique"] == round(redev, 2)
    assert res["cci_cemac"] == round(cci, 2)
    assert res["prelevement_ohada"] == round(ohada, 2)
    assert res["tva_1925"] == round(tva, 2)
    assert res["precompte_is"] == round(pre_is, 2)
    assert res["total_a_liquider_xaf"] == round(dd + redev + cci + ohada + tva + pre_is, 2)


def test_origine_cemac_exonere_le_dd():
    """Origine CEMAC : droit de douane exonere, TVA et redevances dues."""
    res = calculer_liquidation(
        valeur_en_douane=1_000_000, taux_dd_explicite=20.0, origine="CEMAC")
    assert res["droit_douane_dd"] == 0
    assert res["tva_1925"] > 0


def test_regime_hors_mise_consomption_pas_de_dd_ni_tva():
    res = calculer_liquidation(
        valeur_en_douane=1_000_000, taux_dd_explicite=20.0,
        origine="HORS_ZONE", regime="TR90")
    assert res["droit_douane_dd"] == 0
    assert res["tva_1925"] == 0


def test_sans_taux_refuse_honnetement():
    with pytest.raises(ValueError):
        resoudre_taux_dd(None, None, None, None, None)
    with pytest.raises(ValueError):
        calculer_liquidation(valeur_en_douane=-100, taux_dd_explicite=20)


# --------------------------------------------------------------------------- #
# Bilan accidentologie QHSE
# --------------------------------------------------------------------------- #
def _accident(db, numero, annee=2026, arret=0, gravite="leger", hosp=False):
    a = AccidentTravail(
        numero_accident=numero, employe_id=None, lieu="Site",
        type_accident="chute", description="Test", gravite=gravite,
        arret_travail=arret, hospitalisation=hosp,
        date_accident=datetime(annee, 6, 15), statut="cloture")
    db.add(a)
    return a


def test_bilan_qhse_taux_reels_avec_denominateur(db):
    _accident(db, "ACC-1", arret=10)
    _accident(db, "ACC-2", arret=5, gravite="grave", hosp=True)
    _accident(db, "ACC-3", arret=0)  # sans arret : compte quand meme
    db.add(HeuresExposition(annee=2026, heures_travaillees=500_000, nb_employes=50))
    db.commit()

    bilan = WorkPermitsIMDGService.bilan_annuel_csst_cnps(db, 2026)

    assert bilan["accidents_declares"] == 3
    assert bilan["accidents_hospitalises"] == 1
    assert bilan["jours_arret_total"] == 15
    assert bilan["taux_frequence_TF_par_million_h"] == 6.0   # 3 * 1M / 500k
    assert bilan["taux_gravite_TG_par_million_h"] == 30.0   # 15 * 1M / 500k
    assert bilan["heures_non_saisies"] is False


def test_bilan_qhse_sans_heures_aucun_taux_invente(db):
    _accident(db, "ACC-1")
    db.commit()

    bilan = WorkPermitsIMDGService.bilan_annuel_csst_cnps(db, 2026)

    assert bilan["accidents_declares"] == 1
    assert bilan["taux_frequence_TF_par_million_h"] is None
    assert bilan["taux_gravite_TG_par_million_h"] is None
    assert bilan["heures_non_saisies"] is True
    assert bilan["avertissement"]

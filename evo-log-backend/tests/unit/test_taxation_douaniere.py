"""Tests du moteur UNIQUE de liquidation douaniere CEMAC (P1 #2 + P1 #5).

Contrairement aux anciens tests "tautologiques" qui recodaient la formule du
service, ceux-ci verifient des MONTANTS DE REFERENCE calcules a la main et
prouvent qu'un MEME conteneur donne le MEME montant quel que soit l'ecran
(ancienne cause de divergence : TVA basee differemment, taux en % vs fraction,
composantes differentes selon le module).
"""
import pytest
from sqlalchemy.orm import Session

from app.services.taxation_douaniere import (
    TEC_CATEGORIES,
    calculer_liquidation,
)


# --------------------------------------------------------------------------- #
# 1. Valeurs de reference calculees a la main (non re-derives du code)
# --------------------------------------------------------------------------- #
def test_liquidation_reference_categorie_3():
    """10 000 000 XAF, TEC cat.3 (20%), HORS_ZONE, IM4 -> montants exacts."""
    r = calculer_liquidation(
        valeur_en_douane=10_000_000, categorie_tec=3, origine="HORS_ZONE"
    )
    assert r["droit_douane_dd"] == pytest.approx(2_000_000.0)
    assert r["redevance_informatique"] == pytest.approx(45_000.0)   # 0.45%
    assert r["cci_cemac"] == pytest.approx(100_000.0)               # 1%
    assert r["prelevement_ohada"] == pytest.approx(5_000.0)         # 0.05%
    # Base TVA = 10M + 2M + 45k + 100k = 12 145 000
    assert r["base_tva"] == pytest.approx(12_145_000.0)
    assert r["tva_1925"] == pytest.approx(2_337_912.5)              # *19.25%
    assert r["precompte_is"] == pytest.approx(220_000.0)            # 2.2%
    assert r["total_a_liquider_xaf"] == pytest.approx(4_707_912.5)
    assert r["simulation"] is True          # categorie TEC = estimation
    assert r["source_taux"] == "categorie_tec"


def test_categorie_0_exoneree_biens_essentiels():
    r = calculer_liquidation(valeur_en_douane=8_000_000, categorie_tec=0)
    assert r["droit_douane_dd"] == 0.0
    # TVA malgre tout du sur (valeur + 0 + redevance + CCI)
    assert r["base_tva"] == pytest.approx(8_000_000 + 36_000 + 80_000)


# --------------------------------------------------------------------------- #
# 2. Coherence TEC : une seule table de taux
# --------------------------------------------------------------------------- #
def test_table_tec_unique():
    assert TEC_CATEGORIES == {0: 0.00, 1: 0.05, 2: 0.10, 3: 0.20}


def test_categorie_tec_inconnue_refuse_honnetement():
    with pytest.raises(ValueError):
        calculer_liquidation(valeur_en_douane=1_000_000, categorie_tec=9)


def test_valeur_negative_refusee():
    with pytest.raises(ValueError):
        calculer_liquidation(valeur_en_douane=-100)


def test_aucune_source_de_taux_refusee_honnetement():
    """Sans SH en nomenclature, sans taux et sans categorie : on ne devine pas."""
    with pytest.raises(ValueError):
        calculer_liquidation(valeur_en_douane=5_000_000, code_sh="00000000")


# --------------------------------------------------------------------------- #
# 3. Nomenclature CEMAC en base = source de verite (simulation -> False)
# --------------------------------------------------------------------------- #
def test_taux_issus_de_la_nomenclature(db: Session):
    from app.models.transit_avance import NomenclatureCEMAC

    db.add(NomenclatureCEMAC(
        code_hs="84713000", description="Ordinateurs portables",
        taux_dd=10, taux_tva=19.25, statut="actif",
    ))
    db.commit()

    r = calculer_liquidation(
        valeur_en_douane=10_000_000, db=db, code_sh="84713000"
    )
    assert r["source_taux"] == "nomenclature_cemac"
    assert r["simulation"] is False
    assert r["taux_dd"] == pytest.approx(0.10)
    assert r["droit_douane_dd"] == pytest.approx(1_000_000.0)
    assert r["total_a_liquider_xaf"] == pytest.approx(3_515_412.5)


# --------------------------------------------------------------------------- #
# 4. Exoneration a l'origine (CEMAC / ZLECAF) : DD nul, reste du
# --------------------------------------------------------------------------- #
def test_exoneration_origine_cemac():
    r = calculer_liquidation(
        valeur_en_douane=10_000_000, categorie_tec=3, origine="CEMAC"
    )
    assert r["droit_douane_dd"] == 0.0
    assert r["source_taux"] == "exoneration_origine"
    # TVA et redevances toujours dues
    assert r["tva_1925"] > 0
    assert r["redevance_informatique"] == pytest.approx(45_000.0)


# --------------------------------------------------------------------------- #
# 5. Non-regression de la DIVERGENCE : tous les ecrans donnent le meme total
# --------------------------------------------------------------------------- #
def test_les_modules_divergents_convergent():
    """L'ancien bug : 10M @20% produisait des totaux differents selon l'ecran.

    On rejoue les entrees des 3 modules desormais debranchés sur le moteur :
    le resultat doit etre identique a la source.
    """
    from app.services.transit_douane_avance_service import TaxationDouaniereService
    from app.services.cameroun_cemac_service import SydoniaPlusIntegrationService

    # Ecran "transit douane avance" (defaut simulation 20%)
    via_taxation = TaxationDouaniereService.calculer_droits_et_taxes(
        valeur_cif_xaf=10_000_000, code_sh="85176290", regime="IM4"
    )
    # Ecran "comptabilite/fiscalite cameroun" (taux explicites en fractions)
    via_douane = SydoniaPlusIntegrationService.calculer_droits_douane(
        valeur_caf=10_000_000, taux_dd=0.20, taux_tva=0.1925,
    )

    assert via_taxation["total_a_liquider_xaf"] == pytest.approx(4_707_912.5)
    assert via_douane["detail"]["total_a_liquider_xaf"] == pytest.approx(4_707_912.5)
    assert via_taxation["tva_1925"] == via_douane["detail"]["tva_1925"]

"""Tests paie : cumuls annuels par salarie."""
from datetime import date
import pytest
from decimal import Decimal

from app.models.rh import Salaire
from app.services.paie_service import PaieService


def _sal(db, employe_id, annee, mois, brut, impot, net, statut="paye"):
    s = Salaire(employe_id=employe_id, annee=annee, mois=mois,
                salaire_brut=Decimal(str(brut)),
                deductions_impot=Decimal(str(impot)),
                salaire_net=Decimal(str(net)),
                periode_debut=date(annee, mois, 1),
                periode_fin=date(annee, mois, 28),
                salaire_base=Decimal(str(brut)),
                statut=statut)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_cumuls_annuels(db):
    """Employe 1 : 2 mois (brut 500k+600k, impot 50k+60k)."""
    _sal(db, 1, 2026, 1, 500_000, 50_000, 450_000)
    _sal(db, 1, 2026, 2, 600_000, 60_000, 540_000)
    _sal(db, 2, 2026, 1, 300_000, 30_000, 270_000)
    _sal(db, 1, 2025, 12, 500_000, 50_000, 450_000)  # autre annee
    r = PaieService.cumuls_annuels(db, annee=2026)
    assert r["bulletins_total"] == 3
    assert r["employes"] == 2
    assert r["masse_brute_xaf"] == 1_400_000
    assert r["masse_impot_xaf"] == 140_000
    assert r["par_employe"][1]["brut"] == 1_100_000
    assert r["par_employe"][1]["mois"] == 2


def test_vide_honnete(db):
    r = PaieService.cumuls_annuels(db, annee=2030)
    assert r["salaires"] == 0


def test_cumuls_progressifs(db):
    """2 mois : brut 600k/mois, cnps 0 -> base 600k, IRGM barème."""
    _sal(db, 5, 2026, 1, 600_000, 0, 600_000)
    _sal(db, 5, 2026, 2, 600_000, 0, 600_000)
    r = PaieService.cumuls_progressifs(db, annee=2026, employe_id=5)
    assert len(r["mois"]) == 2
    assert r["mois"][0]["base_imposable"] == 600_000
    # barème: 80000 + (600k-500k)*0.25 = 105000/mois
    assert r["impot_annuel_calcule"] == pytest.approx(210_000, abs=1)
    assert r["impot_annuel_retenu"] == 0  # deductions_impot = 0 dans la fixture
    assert r["ecart_annuel"] == pytest.approx(-210_000, abs=1)


def test_bulletin(db):
    """Bulletin detaille : brut 500k, cnps 4.7%, IRGM calcule."""
    _sal(db, 7, 2026, 3, 500_000, 95_000, 405_000)
    b = PaieService.bulletin(db, employe_id=7, annee=2026, mois=3)
    assert "note" not in b
    assert b["salaire_brut"] == 500_000
    assert b["total_cnps"] == pytest.approx(500_000 * 0.047, abs=1)
    assert b["base_imposable"] == pytest.approx(500_000 * 0.953, abs=1)
    assert b["salaire_net"] == 405_000
    assert b["devise"] == "XAF"


def test_bulletin_absent_honnete(db):
    b = PaieService.bulletin(db, employe_id=99, annee=2026, mois=1)
    assert "note" in b

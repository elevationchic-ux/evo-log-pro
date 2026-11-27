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

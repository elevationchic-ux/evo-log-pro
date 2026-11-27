"""Tests QHSE B : quasi-accidents et etalonnage en retard."""
from datetime import date, timedelta
import pytest

from app.models.qhse_b_deep import QhseNearMiss, QhseCalibration
from app.services.qhse_b_service import QhseBService


def _nm(db, site, gravite, reference):
    e = QhseNearMiss(company_id=1, reference=reference, site=site,
                     gravite_potentielle=gravite, is_active=True)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def _cal(db, numero, prochaine, reference):
    c = QhseCalibration(company_id=1, numero_instrument=numero,
                        date_prochaine=prochaine, is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_quasi_accidents_par_site(db):
    """2 sur site A, 1 sur site B ; gravites reparties."""
    _nm(db, "Usine-A", "majeure", "NM1")
    _nm(db, "Usine-A", "moderee", "NM2")
    _nm(db, "Usine-B", "majeure", "NM3")
    r = QhseBService.analyse_quasi_accidents(db)
    assert r["evenements_total"] == 3
    assert r["par_site"]["Usine-A"] == 2
    assert r["par_gravite_potentielle"]["majeure"] == 2


def test_instruments_en_retard(db):
    """1 en retard, 1 a jour."""
    _cal(db, "INST-1", date.today() - timedelta(days=10), "CAL1")
    _cal(db, "INST-2", date.today() + timedelta(days=30), "CAL2")
    r = QhseBService.instruments_en_retard(db)
    assert r["en_retard_etalonage"] == 1
    assert r["details_retard"][0]["numero"] == "INST-1"


def test_vide_honnete(db):
    r = QhseBService.analyse_quasi_accidents(db, site="SiteVide")
    assert r["evenements"] == 0

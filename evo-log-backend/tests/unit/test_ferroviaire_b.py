"""Tests ferroviaire B : verification gabarit et analyse convoi."""
import pytest
from fastapi import HTTPException

from app.models.ferroviaire_b_deep import RailLoadingGauge, RailTrainConsist
from app.services.ferroviaire_b_service import RailGaugeService


def _gauge(db, code="GAB-A", masse=2000, ligne="Ligne Nord"):
    g = RailLoadingGauge(company_id=1, code_gabarit=code, ligne=ligne,
                         masse_max_t=masse, is_active=True)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def _consist(db, masse=1800, nb=20, reference="CONV-1"):
    c = RailTrainConsist(company_id=1, reference=reference, masse_total_t=masse,
                         nb_wagons=nb, is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_convoi_conforme(db):
    """1800 t < 2000 t -> conforme, marge 200 t."""
    _gauge(db)
    c = _consist(db)
    r = RailGaugeService.verifier_gabarit(db, c.id, "GAB-A")
    assert r["conforme"] is True
    assert r["marge_t"] == 200.0


def test_convoi_depasse_gabarit(db):
    """2500 t > 2000 t -> non conforme."""
    _gauge(db)
    c = _consist(db, masse=2500, reference="CONV-2")
    r = RailGaugeService.verifier_gabarit(db, c.id, "GAB-A")
    assert r["conforme"] is False


def test_analyse_convoi(db):
    c = _consist(db, masse=2000, nb=25, reference="CONV-3")
    r = RailGaugeService.analyse_convoi(db, c.id)
    assert r["masse_par_wagon_t"] == 80.0


def test_gabarit_inconnu_404(db):
    c = _consist(db)
    with pytest.raises(HTTPException):
        RailGaugeService.verifier_gabarit(db, c.id, "INCONNU")

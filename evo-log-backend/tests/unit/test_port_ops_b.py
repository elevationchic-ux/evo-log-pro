"""Tests ops portuaires B : occupation des postes a quai."""
from datetime import datetime, timedelta
import pytest

from app.models.port_ops_b_deep import PortbBerthSchedule
from app.services.port_ops_b_service import PortOpsBService


def _escale(db, poste="Q-1", navire="MV-A", heures=24, reference="ESC-1",
            sans_fenetre=False):
    t0 = datetime(2026, 1, 10, 6, 0)
    kw = dict(navire=navire, poste_amarrage=poste, is_active=True)
    if not sans_fenetre:
        kw["date_arrivee_prevue"] = t0
        kw["date_depart_prevu"] = t0 + timedelta(hours=heures)
    s = PortbBerthSchedule(company_id=1, reference=reference, **kw)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_occupation_quai(db):
    """2 escales de 24 h = 48 h d'occupation."""
    _escale(db, reference="E1", navire="MV-A")
    _escale(db, reference="E2", navire="MV-B", heures=12)
    r = PortOpsBService.occupation_quai(db, "Q-1")
    assert r["escales_total"] == 2
    assert r["heures_occupation"] == 36.0
    assert len(r["navires"]) == 2


def test_escalade_sans_fenetre_honnete(db):
    """Escale sans dates comptee mais pas dans les heures."""
    _escale(db, reference="E3")
    _escale(db, reference="E4", sans_fenetre=True)
    r = PortOpsBService.occupation_quai(db, "Q-1")
    assert r["escales_total"] == 2
    assert r["escales_horodatees"] == 1
    assert r["escales_sans_fenetre"] == 1
    assert r["heures_occupation"] == 24.0


def test_quai_vide_honnete(db):
    r = PortOpsBService.occupation_quai(db, "Q-INEXISTANT")
    assert r["escales"] == 0
    assert "Aucune escale" in r["note"]

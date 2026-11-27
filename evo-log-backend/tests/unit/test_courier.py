"""Tests SLA coursier : mesure d'engagement et penalites honnetes."""
from datetime import date, timedelta
import pytest
from fastapi import HTTPException

from app.models.courier_deep import CourierWaybill, CourierSla
from app.services.courier_service import CourierSlaService


def _sla(db, code="SLA-A", engagement=95, delai=48, penalite=None, client="CLI-1"):
    s = CourierSla(company_id=1, code_sla=code, client=client,
                   engagement_pct=engagement, delai_h=delai,
                   penalite_xaf=penalite, is_active=True,
                   date_debut=date.today() - timedelta(days=30),
                   date_fin=date.today() + timedelta(days=30))
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


_seq = [0]


def _wb(db, client, prevue, reelle=None, numero=None):
    _seq[0] += 1
    numero = numero or f"LSE-{_seq[0]}"
    w = CourierWaybill(company_id=1, numero_lse=numero, client=client,
                       date_emission=date.today(),
                       date_livraison_prevue=prevue,
                       date_livraison_reelle=reelle, is_active=True)
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def test_sans_livraison_reelle_honnete(db):
    sla = _sla(db)
    _wb(db, "CLI-1", date.today() + timedelta(days=1))
    r = CourierSlaService.controler_livraison(db, _wb(db, "CLI-1", date.today()).id, sla.id)
    assert r["mesure_pct"] is None
    assert r["penalite_appliquee_xaf"] is None


def test_engagement_dans_les_temps(db):
    """Livraison 24 h apres prevue (< delai 48 h) : mesure 100 %."""
    sla = _sla(db)
    prevue = date.today() + timedelta(days=1)
    w1 = _wb(db, "CLI-1", prevue, prevue + timedelta(hours=24), "LSE-A")
    w2 = _wb(db, "CLI-1", prevue, prevue + timedelta(hours=10), "LSE-B")
    r = CourierSlaService.controler_livraison(db, w1.id, sla.id)
    assert r["mesure_pct"] == 100.0
    assert r["dans_les_temps"] == 2


def test_hors_delai_et_penalite_honnete(db):
    """Livraison 72 h > delai 48 h : hors delai ; penalite seulement si SLA la definit."""
    sla = _sla(db, engagement=100, penalite=None)
    prevue = date.today() + timedelta(days=1)
    w = _wb(db, "CLI-1", prevue, prevue + timedelta(hours=72), "LSE-C")
    r = CourierSlaService.controler_livraison(db, w.id, sla.id)
    assert r["mesure_pct"] == 0.0
    assert r["penalite_appliquee_xaf"] is None  # pas de penalite definie au SLA


def test_penalite_appliquee_si_definie(db):
    sla = _sla(db, code="SLA-P", engagement=100, penalite=500000)
    prevue = date.today() + timedelta(days=1)
    w = _wb(db, "CLI-1", prevue, prevue + timedelta(hours=72), "LSE-D")
    r = CourierSlaService.controler_livraison(db, w.id, sla.id)
    assert r["mesure_pct"] == 0.0
    assert r["penalite_appliquee_xaf"] == 500000


def test_waybill_inconnu_404(db):
    sla = _sla(db)
    with pytest.raises(HTTPException):
        CourierSlaService.controler_livraison(db, 999999, sla.id)

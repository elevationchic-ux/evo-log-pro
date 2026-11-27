"""Tests superadmin deep : incidents et licences."""
from datetime import date, timedelta
import pytest
from decimal import Decimal

from app.models.superadmin_deep import PlatformIncident, SoftwareLicense
from app.services.superadmin_deep_service import SuperadminDeepService


def _inc(db, reference, priorite="P1", statut="ouvert"):
    i = PlatformIncident(company_id=1, reference=reference, titre="Incident",
                         priorite=priorite, statut=statut, is_active=True)
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


def _lic(db, reference, module, date_fin, statut="active", cotisation=100_000):
    l = SoftwareLicense(company_id=1, reference=reference, module=module,
                        nb_sieges=10, date_fin=date_fin, statut=statut,
                        cotisation_xaf=Decimal(str(cotisation)), is_active=True)
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


def test_incidents_ouverts(db):
    """2 ouverts (P1, P2), 1 resolu."""
    _inc(db, "INC-1", "p1", "ouvert")
    _inc(db, "INC-2", "p2", "contenu")
    _inc(db, "INC-3", "p3", "resolu")
    r = SuperadminDeepService.incidents(db)
    assert r["incidents_total"] == 3
    assert r["ouverts"] == 2
    assert r["par_priorite"]["p1"] == 1


def test_licences_expirees(db):
    """1 expiree (fin -10j, statut active), 1 valide."""
    _lic(db, "LIC-1", "ERP", date.today() - timedelta(days=10), "active")
    _lic(db, "LIC-2", "CRM", date.today() + timedelta(days=90), "active")
    r = SuperadminDeepService.licences(db)
    assert r["licences_total"] == 2
    assert r["expirees"] == 1
    assert r["details_expirees"][0]["reference"] == "LIC-1"
    assert r["cotisation_totale_xaf"] == 200_000


def test_vide_honnete(db):
    r = SuperadminDeepService.incidents(db)
    assert r["incidents"] == 0

"""Tests dashboard deep : sante modules et alertes."""
import pytest

from app.models.dashboard_deep import ModuleHealth, OperationalAlert
from app.services.dashboard_deep_service import DashboardDeepService


def _mod(db, code, etat, erreur=None, latence=None):
    m = ModuleHealth(company_id=1, code_module=code, etat=etat,
                     taux_erreur_pct=erreur, latence_p95_ms=latence, is_active=True)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def _alert(db, reference, niveau, statut="ouvert"):
    a = OperationalAlert(company_id=1, reference=reference, description="Alerte",
                         niveau=niveau, statut=statut, is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_sante_modules(db):
    """2 operationnels, 1 degrade (erreur 5%)."""
    _mod(db, "transport", "operationnel")
    _mod(db, "magasin", "operationnel")
    _mod(db, "douane", "degrade", erreur=5.0, latence=1200)
    r = DashboardDeepService.sante_modules(db)
    assert r["modules_total"] == 3
    assert r["degradees"] == 1
    assert r["details_degradees"][0]["code_module"] == "douane"


def test_alertes(db):
    _alert(db, "AL-1", "critique", "ouverte")
    _alert(db, "AL-2", "warning", "resolue")
    _alert(db, "AL-3", "info", "prise_en_charge")
    r = DashboardDeepService.alertes(db)
    assert r["alertes_total"] == 3
    assert r["ouvertes"] == 2
    assert r["par_niveau"]["critique"] == 1


def test_vide_honnete(db):
    r = DashboardDeepService.sante_modules(db)
    assert r["modules"] == 0

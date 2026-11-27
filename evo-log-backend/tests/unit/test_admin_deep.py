"""Tests admin deep : quotas API et tickets."""
import pytest

from app.models.admin_deep import ApiQuota, PlatformTicket
from app.services.admin_deep_service import AdminDeepService


def _quota(db, reference, conso, limite_jour, api="api.logistique"):
    q = ApiQuota(company_id=1, reference=reference, tenant_id=1,
                 api_group=api, limite_jour=limite_jour, limite_minute=None,
                 consommation_actuelle=conso, is_active=True)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def _ticket(db, reference, priorite, statut="ouvert"):
    t = PlatformTicket(company_id=1, reference=reference, titre="Ticket",
                       priorite=priorite, statut=statut, is_active=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_quotas_depassement(db):
    """1 quota a 120 % (depass), 1 a 90 % (alerte)."""
    _quota(db, "Q-1", 1200, 1000)
    _quota(db, "Q-2", 900, 1000)
    r = AdminDeepService.quotas(db)
    assert r["quotas_total"] == 2
    assert r["depassements"] == 1
    assert r["alertes_80pct"] == 1


def test_quotas_ok(db):
    _quota(db, "Q-3", 500, 1000)
    r = AdminDeepService.quotas(db)
    assert r["depassements"] == 0
    assert r["alertes_80pct"] == 0


def test_tickets(db):
    _ticket(db, "T-1", "haute")
    _ticket(db, "T-2", "basse", statut="resolu")
    r = AdminDeepService.tickets(db)
    assert r["tickets_total"] == 2
    assert r["ouvertes"] == 1
    assert r["par_priorite"]["haute"] == 1


def test_vide_honnete(db):
    r = AdminDeepService.quotas(db)
    assert r["quotas"] == 0

"""Tests admin tenant : quotas, sauvegardes, impersonations."""
import pytest

from app.models.admin_tenant_c_deep import (
    AdmtUsageQuota, AdmtTenantBackup, AdmtImpersonationLog)
from app.services.admin_tenant_service import AdminTenantService


def _quota(db, reference, ressource, consomme, autorise, periode="2026-03"):
    u = AdmtUsageQuota(company_id=1, reference=reference, ressource=ressource,
                       consomme=consomme, quota_autorise=autorise,
                       periode=periode, is_active=True)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _backup(db, reference, tenant, statut="succes"):
    b = AdmtTenantBackup(company_id=1, reference=reference, tenant=tenant,
                         statut=statut, is_active=True)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def _imp(db, reference, statut="en_cours"):
    l = AdmtImpersonationLog(company_id=1, reference=reference, admin="admin@x",
                             cible_tenant="T-1", statut=statut, is_active=True)
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


def test_quotas(db):
    """1 depasse (1200/1000), 1 alerte (850/1000), 1 ok (500/1000)."""
    _quota(db, "Q-1", "api_calls", 1200, 1000)
    _quota(db, "Q-2", "stockage", 850, 1000)
    _quota(db, "Q-3", "utilisateurs", 500, 1000)
    r = AdminTenantService.quotas(db)
    assert r["quotas_total"] == 3
    assert r["depassements"] == 1
    assert r["alertes_80pct"] == 1


def test_sauvegardes(db):
    _backup(db, "BK-1", "T-1", "succes")
    _backup(db, "BK-2", "T-1", "echec")
    r = AdminTenantService.sauvegardes(db, tenant="T-1")
    assert r["sauvegardes_total"] == 2
    assert r["par_statut"]["echec"] == 1


def test_impersonations(db):
    _imp(db, "IM-1", "en_cours")
    _imp(db, "IM-2", "clos")
    r = AdminTenantService.impersonations(db)
    assert r["impersonations_total"] == 2
    assert r["ouvertes"] == 1

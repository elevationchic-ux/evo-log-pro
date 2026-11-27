"""Tests organisation : abonnements et expiration."""
from datetime import datetime, timedelta
import pytest

from app.models.organization import Organization
from app.services.organization_service import OrganizationService


def _org(db, code, plan, status="ACTIVE", expire_in_days=None):
    o = Organization(code=code, name=f"Org {code}", slug=code.lower(),
                     plan=plan, status=status, max_users=10,
                     subscription_expires_at=(
                         datetime.utcnow() + timedelta(days=expire_in_days)
                         if expire_in_days is not None else None))
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


def test_abonnements(db):
    """1 BUSINESS expire dans 10j, 1 ENTERPRISE expire dans 1 an, 1 suspendu."""
    _org(db, "ORG-1", "BUSINESS", expire_in_days=10)
    _org(db, "ORG-2", "ENTERPRISE", expire_in_days=365)
    _org(db, "ORG-3", "STARTER", status="SUSPENDED")
    r = OrganizationService.abonnements(db)
    assert r["organisations_total"] == 3
    assert r["expirant_30j"] == 1
    assert r["details_expiration"][0]["code"] == "ORG-1"
    assert r["par_plan"]["ENTERPRISE"] == 1


def test_vide_honnete(db):
    r = OrganizationService.abonnements(db)
    assert r["organisations"] == 0

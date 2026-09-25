"""Integration tests for the centralized RBAC layer and the tenant console.

Covers the Super Admin / Admin Entreprise separation requested in the spec:
  * Super Admin (level 0, no company) manages every company but belongs to none.
  * Admin Entreprise (level 1) acts only inside its own company.
  * Nobody else can even see the Super Admin console (403).
"""
import pytest

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.tenant import Company, Department
from app.models.user import User


@pytest.fixture
def superadmin(db):
    u = User(
        username="supadmin", email="supadmin@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=True, role_level=0, company_id=None,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def company(db):
    c = Company(
        code="ACME", nom="ACME SA", is_active=True,
        max_users=3, max_storage_mb=1000, current_storage_mb=950,
        modules_actives='["transport","magasin"]',
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def company_admin(db, company):
    u = User(
        username="acme-admin", email="acme.admin@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=False, role_level=1, company_id=company.id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def plain_user(db, company):
    u = User(
        username="worker", email="worker@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=False, role_level=3, company_id=company.id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _as(client, user):
    """Force the authenticated identity for the next requests."""
    app.dependency_overrides[get_current_user] = lambda: user


def _clear(client):
    app.dependency_overrides.clear()


# --------------------------------------------------------------------------- #
# Super Admin console isolation
# --------------------------------------------------------------------------- #
def test_console_invisible_to_non_superadmin(client, db, company_admin, plain_user, company):
    _as(client, company_admin)
    assert client.get("/api/v1/tenant/companies/detailed").status_code == 403
    _as(client, plain_user)
    assert client.get("/api/v1/tenant/companies/detailed").status_code == 403
    _clear(client)


def test_superadmin_sees_company_detail_with_live_counts(client, db, superadmin, company, company_admin, plain_user):
    # two employees attached to the company
    _as(client, superadmin)
    resp = client.get(f"/api/v1/tenant/companies/{company.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["employees_count"] == 2  # company_admin + plain_user
    assert data["storage"]["allocated_mb"] == 1000
    assert data["storage"]["remaining_mb"] == 50
    assert data["modules_actives"] == ["transport", "magasin"]
    assert data["admin_entreprise"]["id"] == company_admin.id
    _clear(client)


def test_platform_alerts_flag_quota_and_storage(client, db, superadmin, company, company_admin, plain_user):
    # third user pushes employees to the max_users quota (3)
    extra = User(
        username="third", email="third@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, role_level=3, company_id=company.id,
    )
    db.add(extra)
    db.commit()
    _as(client, superadmin)
    resp = client.get("/api/v1/tenant/alerts/platform")
    assert resp.status_code == 200
    kinds = {a["type"] for a in resp.json()["alerts"]}
    assert "quota_utilisateurs" in kinds
    assert "stockage" in kinds
    _clear(client)


# --------------------------------------------------------------------------- #
# Create EXACTLY one admin-entreprise
# --------------------------------------------------------------------------- #
def test_create_one_admin_entreprise_and_second_rejected(client, db, superadmin):
    c = Company(code="BETA", nom="Beta SARL", is_active=True, max_users=5, max_storage_mb=100)
    db.add(c)
    db.commit()
    db.refresh(c)
    _as(client, superadmin)
    resp = client.post(
        f"/api/v1/tenant/companies/{c.id}/admin-entreprise",
        json={"email": "beta.admin@example.com", "password": "Str0ngPass1", "full_name": "Beta Admin"},
    )
    assert resp.status_code == 201
    created = resp.json()["admin"]
    assert created["role_level"] == 1
    # a second admin-entreprise for the same company must be rejected
    resp2 = client.post(
        f"/api/v1/tenant/companies/{c.id}/admin-entreprise",
        json={"email": "second@example.com", "password": "Str0ngPass1"},
    )
    assert resp2.status_code == 409
    _clear(client)


def test_admin_entreprise_cannot_create_another_admin(client, db, company_admin, company):
    _as(client, company_admin)
    resp = client.post(
        f"/api/v1/tenant/companies/{company.id}/admin-entreprise",
        json={"email": "x@example.com", "password": "Str0ngPass1"},
    )
    assert resp.status_code == 403
    _clear(client)


# --------------------------------------------------------------------------- #
# Company delete guard
# --------------------------------------------------------------------------- #
def test_delete_company_guarded(client, db, superadmin, company, company_admin):
    _as(client, superadmin)
    # refuses while users are attached
    assert client.delete(f"/api/v1/tenant/companies/{company.id}").status_code == 409
    # force detaches users then deletes
    resp = client.delete(f"/api/v1/tenant/companies/{company.id}", params={"force": True})
    assert resp.status_code == 200
    assert db.query(Company).filter(Company.id == company.id).first() is None
    _clear(client)


# --------------------------------------------------------------------------- #
# Admin Entreprise company scoping
# --------------------------------------------------------------------------- #
def test_company_dashboard_scoped_to_own_company(client, db, company_admin, company, superadmin):
    _as(client, company_admin)
    resp = client.get("/api/v1/tenant/company/dashboard")
    assert resp.status_code == 200
    assert resp.json()["company"]["id"] == company.id
    # a regular user cannot access the admin dashboard
    _as(client, superadmin)
    # super admin has no own company -> honest 400 (must pass explicit company elsewhere)
    assert client.get("/api/v1/tenant/company/dashboard").status_code == 400
    _clear(client)


def test_department_crud_company_scoped(client, db, company_admin, company):
    # another company's department must be invisible / untouchable
    other = Company(code="OTHER", nom="Other SA", is_active=True, max_users=2, max_storage_mb=10)
    db.add(other)
    db.commit()
    db.refresh(other)
    foreign_dept = Department(company_id=other.id, code="F1", nom="Foreign")
    db.add(foreign_dept)
    db.commit()
    db.refresh(foreign_dept)

    _as(client, company_admin)
    lst = client.get("/api/v1/tenant/departments")
    assert lst.status_code == 200
    assert all(d["company_id"] != other.id for d in lst.json()) if lst.json() else True
    # cannot delete a department belonging to another company
    assert client.delete(f"/api/v1/tenant/departments/{foreign_dept.id}").status_code == 404
    _clear(client)


# --------------------------------------------------------------------------- #
# admin.py user endpoints: RBAC + anti privilege escalation
# --------------------------------------------------------------------------- #
def test_regular_user_cannot_create_users(client, db, plain_user):
    _as(client, plain_user)
    resp = client.post(
        "/api/v1/admin/users",
        json={"email": "n@example.com", "password": "Str0ngPass1", "role": "OPERATEUR"},
    )
    assert resp.status_code == 403
    _clear(client)


def test_company_admin_cannot_mint_superuser(client, db, company_admin):
    _as(client, company_admin)
    resp = client.post(
        "/api/v1/admin/users",
        json={"email": "esc@example.com", "password": "Str0ngPass1", "role": "SUPER_ADMIN"},
    )
    assert resp.status_code == 403
    _clear(client)


def test_company_admin_cannot_touch_foreign_user(client, db, company_admin):
    other = Company(code="FOE", nom="Foe SA", is_active=True, max_users=2, max_storage_mb=10)
    db.add(other)
    db.commit()
    db.refresh(other)
    foe_user = User(
        username="foe", email="foe@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, role_level=3, company_id=other.id,
    )
    db.add(foe_user)
    db.commit()
    db.refresh(foe_user)
    _as(client, company_admin)
    resp = client.patch(f"/api/v1/admin/users/{foe_user.id}/status", json={"is_active": False})
    assert resp.status_code == 403
    _clear(client)


def test_company_admin_can_create_operator_in_own_company(client, db, company_admin, company):
    _as(client, company_admin)
    resp = client.post(
        "/api/v1/admin/users",
        json={"email": "op@example.com", "password": "Str0ngPass1", "role": "OPERATEUR"},
    )
    assert resp.status_code == 201
    created = db.query(User).filter(User.email == "op@example.com").first()
    assert created.company_id == company.id
    assert created.role_level == 3 and created.is_superuser is False
    _clear(client)

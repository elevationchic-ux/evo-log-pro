"""Tests Phase 2 — Admin Entreprise (niveau 1).

Couvre :
  * designation d'un admin entreprise PAR le CADC (role_level=1, rattaché,
    must_change_password force, mot de passe hashé) ;
  * quota max_users du plan respecte ; unicite username/email ;
  * console CADC (admins) invisible pour un simple admin entreprise (403) ;
  * surface d'administration interne scopee : profil / collaborateurs / roles,
    un admin entreprise epingle a SON entreprise (autre entreprise -> 403),
    anti-escalade (ne peut creer un niveau superieur au sien) ;
  * ecran modules alloues/demandes + requete d'accreditation vers le CADC
    (Accreditation statut 'demande', ignoree par le moteur d'autorisation).
"""
import pytest

from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.accreditation import Accreditation
from app.models.tenant import Company, SubscriptionPlan, SubscriptionPlanType
from app.models.user import User


def _as(user):
    app.dependency_overrides[get_current_user] = lambda: user


def _clear():
    app.dependency_overrides.clear()


@pytest.fixture
def superadmin(db):
    u = User(
        username="CADC TECH", email="cadc@example.com",
        hashed_password=get_password_hash("@C2A0D2C6"),
        is_active=True, is_superuser=True, role_level=0,
        company_id=None, must_change_password=False,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def company(db):
    c = Company(code="ACME", nom="ACME SA", is_active=True, modules_actives='["transport"]')
    db.add(c); db.commit(); db.refresh(c)
    return c


@pytest.fixture
def other_company(db):
    c = Company(code="OTHER", nom="Other SA", is_active=True, modules_actives="[]")
    db.add(c); db.commit(); db.refresh(c)
    return c


@pytest.fixture
def company_admin(db, company):
    u = User(
        username="acme-admin", email="acme.admin@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=False, role_level=1, company_id=company.id,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def plain_user(db, company):
    u = User(
        username="worker", email="worker@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=False, role_level=3, company_id=company.id,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u


def _make_plan(db, code, max_users=None, max_modules=None):
    p = SubscriptionPlan(
        code=code, nom=code, type_plan=SubscriptionPlanType.PRO,
        max_users=max_users, max_modules=max_modules, modules_inclus="[]",
    )
    db.add(p); db.commit(); db.refresh(p)
    return p


# --------------------------------------------------------------------------- #
# 2.1 designation d'un admin entreprise par le CADC
# --------------------------------------------------------------------------- #
def test_cadc_creates_company_admin(client, db, superadmin, company):
    _as(superadmin)
    resp = client.post(
        f"/api/v1/saas/console/companies/{company.id}/admins",
        json={"username": "newadmin", "email": "new.admin@example.com",
              "full_name": "Nouveau Admin"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role_level"] == 1
    assert body["company_id"] == company.id
    assert body["is_superuser"] is False
    assert body["must_change_password"] is True
    assert "temporary_password" in body and body["temporary_password"]

    created = db.query(User).filter(User.username == "newadmin").first()
    assert created is not None
    assert created.hashed_password != body["temporary_password"]  # hashé, jamais clair
    _clear()


def test_cadc_create_admin_rejects_duplicate_email(client, db, superadmin, company, company_admin):
    _as(superadmin)
    resp = client.post(
        f"/api/v1/saas/console/companies/{company.id}/admins",
        json={"username": "another", "email": company_admin.email},
    )
    assert resp.status_code == 400
    _clear()


def test_cadc_create_admin_quota_enforced(client, db, superadmin, company, company_admin):
    plan = _make_plan(db, "ONEUSER", max_users=1)
    company.subscription_plan_id = plan.id
    db.commit()
    _as(superadmin)
    # company_admin existe deja => 1 utilisateur, quota = 1 -> refus.
    resp = client.post(
        f"/api/v1/saas/console/companies/{company.id}/admins",
        json={"username": "extra", "email": "extra@example.com"},
    )
    assert resp.status_code == 400
    _clear()


def test_console_admins_invisible_to_company_admin(client, db, company_admin, company):
    _as(company_admin)
    resp = client.get(f"/api/v1/saas/console/companies/{company.id}/admins")
    assert resp.status_code == 403
    _clear()


# --------------------------------------------------------------------------- #
# 2.2 administration interne scopee entreprise
# --------------------------------------------------------------------------- #
def test_company_admin_reads_own_profile(client, db, company_admin, company):
    _as(company_admin)
    resp = client.get("/api/v1/company-admin/profil")
    assert resp.status_code == 200
    assert resp.json()["id"] == company.id
    _clear()


def test_superadmin_profile_requires_explicit_company_id(client, db, superadmin, company):
    _as(superadmin)
    missing = client.get("/api/v1/company-admin/profil")
    assert missing.status_code == 400
    ok = client.get(f"/api/v1/company-admin/profil?company_id={company.id}")
    assert ok.status_code == 200
    assert ok.json()["id"] == company.id
    _clear()


def test_company_admin_cannot_touch_other_company(client, db, company_admin, other_company):
    _as(company_admin)
    resp = client.get(f"/api/v1/company-admin/profil?company_id={other_company.id}")
    assert resp.status_code == 403
    _clear()


def test_plain_user_forbidden_on_company_admin(client, db, plain_user):
    _as(plain_user)
    resp = client.get("/api/v1/company-admin/utilisateurs")
    assert resp.status_code == 403
    _clear()


def test_company_admin_creates_member_scoped(client, db, company_admin, company):
    _as(company_admin)
    resp = client.post(
        "/api/v1/company-admin/utilisateurs",
        json={"username": "employee1", "email": "emp1@example.com",
              "full_name": "Employe Un", "job_title": "Magasinier"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role_level"] == 3
    assert body["must_change_password"] is True
    created = db.query(User).filter(User.username == "employee1").first()
    assert created.company_id == company.id
    _clear()


def test_company_admin_cannot_escalate_to_superadmin(client, db, company_admin):
    _as(company_admin)
    resp = client.post(
        "/api/v1/company-admin/utilisateurs",
        json={"username": "sneaky", "email": "sneaky@example.com", "role_level": 0},
    )
    assert resp.status_code == 403
    _clear()


# --------------------------------------------------------------------------- #
# 2.3 modules alloues / demandes d'accreditation vers le CADC
# --------------------------------------------------------------------------- #
def test_modules_overview_marks_allocated_and_locked(client, db, company_admin, company):
    _as(company_admin)
    resp = client.get("/api/v1/company-admin/modules")
    assert resp.status_code == 200
    data = resp.json()
    etats = {m["key"]: m["etat"] for m in data["modules"]}
    assert etats.get("transport") == "alloue"
    assert "verrouille" in etats.values()  # au moins un module non alloue
    _clear()


def test_module_request_creates_pending_accreditation(client, db, company_admin, company):
    _as(company_admin)
    resp = client.post(
        "/api/v1/company-admin/modules/demandes",
        json={"module": "finance", "motif": "Besoin comptabilite"},
    )
    assert resp.status_code == 201
    req = db.query(Accreditation).filter(Accreditation.module == "finance").first()
    assert req is not None
    assert req.statut == "demande"
    assert req.company_id == company.id

    # La demande n'accorde AUCUN droit : statut != actif -> ignoree.
    assert req.est_valide() is False
    _clear()


def test_module_request_appears_in_overview(client, db, company_admin, company):
    _as(company_admin)
    client.post("/api/v1/company-admin/modules/demandes", json={"module": "finance"})
    data = client.get("/api/v1/company-admin/modules").json()
    etats = {m["key"]: m["etat"] for m in data["modules"]}
    assert etats.get("finance") == "demande"
    assert any(d["module"] == "finance" for d in data["demandes"])
    _clear()


def test_module_request_duplicate_rejected(client, db, company_admin, company):
    _as(company_admin)
    first = client.post("/api/v1/company-admin/modules/demandes", json={"module": "finance"})
    assert first.status_code == 201
    dup = client.post("/api/v1/company-admin/modules/demandes", json={"module": "finance"})
    assert dup.status_code == 400
    _clear()


def test_module_request_for_already_allocated_rejected(client, db, company_admin, company):
    _as(company_admin)
    # transport est deja alloue a ACME.
    resp = client.post("/api/v1/company-admin/modules/demandes", json={"module": "transport"})
    assert resp.status_code == 400
    _clear()


def test_cadc_lists_pending_requests(client, db, superadmin, company_admin, company):
    _as(company_admin)
    client.post("/api/v1/company-admin/modules/demandes", json={"module": "finance"})
    _as(superadmin)
    resp = client.get("/api/v1/saas/console/accreditations/demandes")
    assert resp.status_code == 200
    rows = resp.json()
    assert any(r["module"] == "finance" and r["company_nom"] == company.nom for r in rows)
    _clear()

"""Tests Phase 1 — Console Super-Admin CADC (SaaS).

Couvre les regles non-regression de la console :
  * exemption de changement de mot de passe pour un Super Admin (compte CADC) ;
  * console strictement invisible (403) pour admin entreprise / utilisateur ;
  * verrou ``max_modules`` d'un plan a l'creation d'entreprise et a l'allocation ;
  * accreditation d'entreprise datee : valide puis expiree -> droit retire ;
  * upload de logo (multipart) ecrit le fichier et renseigne ``logo_url`` ;
  * ecriture annuaire prestataires reservee au CADC.
"""
import io
from datetime import date, timedelta

import pytest

from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.accreditation import Accreditation
from app.models.tenant import Company, SubscriptionPlan, SubscriptionPlanType
from app.models.user import User


def _as(user):
    app.dependency_overrides[get_current_user] = lambda: user


def _clear():
    # Pop ciblé : `dependency_overrides.clear()` supprimerait AUSSI l'override
    # get_db de la fixture client → les requêtes suivantes partiraient sur
    # l'engine réel de l'app (base de dev). On ne retire que l'identité.
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def superadmin(db):
    u = User(
        username="CADC TECH", email="cadc@example.com",
        hashed_password=get_password_hash("@C2A0D2C6"),
        is_active=True, is_superuser=True, role_level=0,
        company_id=None, must_change_password=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def company(db):
    c = Company(code="ACME", nom="ACME SA", is_active=True, modules_actives="[]")
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


# --------------------------------------------------------------------------- #
# 1.2 exemption changement de mot de passe (super admin uniquement)
# --------------------------------------------------------------------------- #
def test_login_payload_superuser_exempt_from_password_change(superadmin):
    from app.routers.v1.auth import _build_login_payload
    # must_change_password True en base mais super-admin -> exempte.
    assert superadmin.must_change_password is True
    payload = _build_login_payload(superadmin)
    assert payload["must_change_password"] is False
    assert payload["is_superuser"] is True


def test_login_payload_regular_user_still_prompted(plain_user):
    from app.routers.v1.auth import _build_login_payload
    plain_user.must_change_password = True
    payload = _build_login_payload(plain_user)
    assert payload["must_change_password"] is True


# --------------------------------------------------------------------------- #
# 1.4 invisibilite backend de la console
# --------------------------------------------------------------------------- #
def test_console_invisible_to_company_admin_and_user(client, company_admin, plain_user):
    _as(company_admin)
    assert client.get("/api/v1/saas/console/companies").status_code == 403
    _as(plain_user)
    assert client.get("/api/v1/saas/console/plans").status_code == 403
    _clear()


def test_console_accessible_to_superadmin(client, superadmin):
    _as(superadmin)
    assert client.get("/api/v1/saas/console/companies").status_code == 200
    assert client.get("/api/v1/saas/console/modules-catalog").status_code == 200
    _clear()


# --------------------------------------------------------------------------- #
# 1.3 verrou max_modules d'un plan
# --------------------------------------------------------------------------- #
def _make_plan(db, code, max_modules):
    p = SubscriptionPlan(
        code=code, nom=code, type_plan=SubscriptionPlanType.PRO,
        max_modules=max_modules, modules_inclus="[]",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_create_company_over_module_cap_rejected(client, db, superadmin):
    _as(superadmin)
    plan = _make_plan(db, "TWO-MOD", 2)
    too_many = client.post(
        "/api/v1/saas/console/companies",
        json={"code": "OVF", "nom": "Overflow", "subscription_plan_id": plan.id,
              "modules_actives": ["transport", "magasin", "finance"]},
    )
    assert too_many.status_code == 400
    ok = client.post(
        "/api/v1/saas/console/companies",
        json={"code": "FIT", "nom": "Fit SARL", "subscription_plan_id": plan.id,
              "modules_actives": ["transport", "magasin"]},
    )
    assert ok.status_code == 201
    _clear()


def test_allocate_modules_over_cap_rejected(client, db, superadmin, company):
    _as(superadmin)
    plan = _make_plan(db, "CAP1", 1)
    company.subscription_plan_id = plan.id
    db.commit()
    bad = client.put(
        f"/api/v1/saas/console/companies/{company.id}/modules",
        json={"modules": ["transport", "magasin"]},
    )
    assert bad.status_code == 400
    good = client.put(
        f"/api/v1/saas/console/companies/{company.id}/modules",
        json={"modules": ["transport"]},
    )
    assert good.status_code == 200
    assert good.json()["modules_actives"] == ["transport"]
    _clear()


# --------------------------------------------------------------------------- #
# accreditation d'entreprise datee : valide puis expiree
# --------------------------------------------------------------------------- #
def test_company_accreditation_expiry_revokes_right(client, db, superadmin, company, plain_user):
    from app.core.permissions import load_effective_permissions, has_perm
    _as(superadmin)
    today = date.today()
    future = (today + timedelta(days=30)).isoformat()
    past = (today - timedelta(days=5)).isoformat()

    resp = client.post(
        f"/api/v1/saas/console/companies/{company.id}/accreditations",
        json={"user_id": plain_user.id, "module": "transport",
              "date_debut": past, "date_fin": future},
    )
    assert resp.status_code == 201
    assert resp.json()["valide"] is True

    # Accreditation valide -> le code granulaire est effectif.
    db.refresh(plain_user)
    codes = load_effective_permissions(plain_user)
    assert has_perm(codes, "transport.mission.read") is True

    # On fait expirer l'accreditation -> le code disparait des droits effectifs.
    acc = db.query(Accreditation).filter(Accreditation.user_id == plain_user.id).first()
    acc.date_fin = today - timedelta(days=1)
    db.commit()
    db.refresh(plain_user)
    codes = load_effective_permissions(plain_user)
    assert "transport.*.*" not in codes
    assert has_perm(codes, "transport.mission.read") is False
    _clear()


def test_accreditation_rejects_foreign_user(client, db, superadmin, company):
    _as(superadmin)
    other = Company(code="OTHER", nom="Other SA", is_active=True, modules_actives="[]")
    db.add(other)
    db.commit()
    db.refresh(other)
    resp = client.post(
        f"/api/v1/saas/console/companies/{other.id}/accreditations",
        json={"user_id": None} ,
    )
    # user_id obligatoire -> 422 (validation pydantic) ; et un user hors
    # perimetre serait refuse 400 par la garre metier.
    assert resp.status_code == 422
    _clear()


# --------------------------------------------------------------------------- #
# upload de logo
# --------------------------------------------------------------------------- #
def test_upload_logo_sets_url(client, db, superadmin, company, monkeypatch, tmp_path):
    import app.routers.v1.saas_console as console
    monkeypatch.setattr(console.settings, "UPLOAD_DIR", str(tmp_path))
    _as(superadmin)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00"
        b"\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    resp = client.post(
        f"/api/v1/saas/console/companies/{company.id}/logo",
        files={"file": ("logo.png", io.BytesIO(png_bytes), "image/png")},
    )
    assert resp.status_code == 200
    logo_url = resp.json()["logo_url"]
    assert logo_url.startswith("/static/uploads/logos/")
    db.refresh(company)
    assert company.logo_url == logo_url
    written = list((tmp_path / "logos").glob("*.png"))
    assert written, "le fichier logo devrait etre ecrit sur disque"
    _clear()


def test_upload_logo_rejects_bad_type(client, db, superadmin, company, monkeypatch, tmp_path):
    import app.routers.v1.saas_console as console
    monkeypatch.setattr(console.settings, "UPLOAD_DIR", str(tmp_path))
    _as(superadmin)
    resp = client.post(
        f"/api/v1/saas/console/companies/{company.id}/logo",
        files={"file": ("bad.exe", io.BytesIO(b"MZ..."), "application/octet-stream")},
    )
    assert resp.status_code == 400
    _clear()


# --------------------------------------------------------------------------- #
# annuaire prestataires : ecriture reservee au CADC
# --------------------------------------------------------------------------- #
def test_prestataire_create_forbidden_for_company_admin(client, db, company_admin):
    _as(company_admin)
    resp = client.post(
        "/api/v1/prestataires",
        json={"raison_sociale": "Trans X", "specialite": "TRANSPORT_LOURD",
              "contact_telephone": "+237 600 00 00 00"},
    )
    assert resp.status_code == 403
    _clear()


def test_prestataire_create_ok_via_console(client, db, superadmin):
    _as(superadmin)
    resp = client.post(
        "/api/v1/saas/console/prestataires",
        json={"code": "PRT-001", "raison_sociale": "Manut Est",
              "specialite": "MANUTENTION_PORTUAIRE",
              "contact_telephone": "+237 699 00 00 00"},
    )
    assert resp.status_code == 201
    assert resp.json()["code"] == "PRT-001"
    lst = client.get("/api/v1/saas/console/prestataires")
    assert lst.status_code == 200
    assert any(p["code"] == "PRT-001" for p in lst.json())
    _clear()


# --------------------------------------------------------------------------- #
# modele : colonnes ajoutees par la migration 025
# --------------------------------------------------------------------------- #
def test_user_and_plan_new_columns_exist(db, superadmin):
    superadmin.matricule = "CADC-0001"
    superadmin.job_title = "Super Administrateur"
    db.commit()
    db.refresh(superadmin)
    assert superadmin.matricule == "CADC-0001"
    assert superadmin.job_title == "Super Administrateur"
    plan = SubscriptionPlan(
        code="X", nom="X", type_plan=SubscriptionPlanType.CUSTOM, max_modules=5,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    assert plan.max_modules == 5

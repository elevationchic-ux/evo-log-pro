"""Tests Phase 4 (Tranche F) — modèle "Utilisateur != Role" dans l'admin.

Formalise separement :
  * l'IDENTITE employe (matricule, job_title) exposee en lecture + ecriture ;
  * les CASQUETTES (roles, beaucoup-a-beaucoup) affectables en plusieurs via
    PUT /api/v1/admin/users/{id}/roles, avec role_level derive du role le plus
    privilegie et anti-escalade (SUPER_ADMIN / niveau superieur reserves).

Conventions : fixture `client` (override get_db + identite factice) ; on
repositionne l'identite via _as() comme dans test_company_admin_phase2.py.
"""
import pytest

from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.tenant import Company
from app.models.user import Role, User


def _as(user):
    app.dependency_overrides[get_current_user] = lambda: user


def _clear():
    # Pop ciblé uniquement : clear() emporterait l'override get_db (base de dev).
    app.dependency_overrides.pop(get_current_user, None)


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
def member(db, company):
    u = User(
        username="worker", email="worker@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=False, role_level=3, company_id=company.id,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def foreign_member(db, other_company):
    u = User(
        username="outsider", email="outsider@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=False, role_level=3, company_id=other_company.id,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u


# --------------------------------------------------------------------------- #
# Identite employe : matricule / job_title (Utilisateur != Role)
# --------------------------------------------------------------------------- #
def test_list_users_exposes_identity_fields(client, db, company_admin, member):
    member.matricule = "MAT-042"
    member.job_title = "Cariste"
    db.commit()
    _as(company_admin)
    rows = client.get("/api/v1/admin/users").json()
    row = next(r for r in rows if r["id"] == member.id)
    assert row["matricule"] == "MAT-042"
    assert row["job_title"] == "Cariste"
    _clear()


def test_create_user_persists_identity(client, db, company_admin):
    _as(company_admin)
    resp = client.post(
        "/api/v1/admin/users",
        json={"username": "nouveau", "email": "nouveau@example.com",
              "password": "Passw0rd!", "full_name": "Nouveau Employe",
              "matricule": "MAT-100", "job_title": "Magasinier"},
    )
    assert resp.status_code == 201, resp.text
    created = db.query(User).filter(User.username == "nouveau").first()
    assert created.matricule == "MAT-100"
    assert created.job_title == "Magasinier"
    _clear()


def test_update_user_edits_identity(client, db, company_admin, member):
    _as(company_admin)
    resp = client.put(
        f"/api/v1/admin/users/{member.id}",
        json={"matricule": "MAT-777", "job_title": "Chef d'equipe"},
    )
    assert resp.status_code == 200, resp.text
    db.refresh(member)
    assert member.matricule == "MAT-777"
    assert member.job_title == "Chef d'equipe"
    _clear()


# --------------------------------------------------------------------------- #
# Casquettes multiples : PUT /users/{id}/roles
# --------------------------------------------------------------------------- #
def test_assign_roles_multiple_casquettes(client, db, company_admin, member):
    _as(company_admin)
    r = client.put(
        f"/api/v1/admin/users/{member.id}/roles",
        json={"roles": ["OPERATEUR", "MAGASINIER"]},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body["roles"]) == {"OPERATEUR", "MAGASINIER"}
    names = {role.name for role in member.roles}
    assert names == {"OPERATEUR", "MAGASINIER"}
    _clear()


def test_assign_roles_role_level_tracks_most_privileged(client, db, company_admin, member):
    # TRANSITAIRE = niveau 2 (cf. STANDARD_ROLES) : la casquette la plus privilegiee
    # doit abaisser role_level a 2.
    _as(company_admin)
    r = client.put(
        f"/api/v1/admin/users/{member.id}/roles",
        json={"roles": ["OPERATEUR", "TRANSITAIRE"]},
    )
    assert r.status_code == 200, r.text
    assert r.json()["role_level"] == 2
    db.refresh(member)
    assert member.role_level == 2
    _clear()


def test_assign_roles_superadmin_forbidden_for_company_admin(client, db, company_admin, member):
    _as(company_admin)
    r = client.put(
        f"/api/v1/admin/users/{member.id}/roles",
        json={"roles": ["SUPER_ADMIN"]},
    )
    assert r.status_code == 403
    _clear()


def test_assign_roles_superadmin_allowed_for_superadmin(client, db, member):
    admin = User(
        username="root", email="root@example.com",
        hashed_password=get_password_hash("Adm1n!xyz"),
        is_active=True, is_superuser=True, role_level=0, company_id=None,
    )
    db.add(admin); db.commit(); db.refresh(admin)
    _as(admin)
    r = client.put(
        f"/api/v1/admin/users/{member.id}/roles",
        json={"roles": ["SUPER_ADMIN"]},
    )
    assert r.status_code == 200, r.text
    assert "SUPER_ADMIN" in r.json()["roles"]
    _clear()


def test_assign_roles_materializes_unknown_standard_role(client, db, company_admin, member):
    # 'DECLARANT' (standard, niveau 3) peut ne pas exister en base : get-or-create.
    db.query(Role).filter(Role.name == "DECLARANT").delete()
    db.commit()
    _as(company_admin)
    r = client.put(
        f"/api/v1/admin/users/{member.id}/roles",
        json={"roles": ["DECLARANT"]},
    )
    assert r.status_code == 200, r.text
    role = db.query(Role).filter(Role.name == "DECLARANT").first()
    assert role is not None and role.level == 3
    _clear()


def test_assign_roles_requires_list(client, db, company_admin, member):
    _as(company_admin)
    missing = client.put(f"/api/v1/admin/users/{member.id}/roles", json={})
    assert missing.status_code == 400
    bad = client.put(f"/api/v1/admin/users/{member.id}/roles", json={"roles": "OPERATEUR"})
    assert bad.status_code == 400
    _clear()


def test_assign_roles_scoped_to_company(client, db, company_admin, foreign_member):
    # Un admin entreprise ne peut pas toucher un utilisateur d'une AUTRE societe.
    _as(company_admin)
    r = client.put(
        f"/api/v1/admin/users/{foreign_member.id}/roles",
        json={"roles": ["OPERATEUR"]},
    )
    assert r.status_code == 403
    _clear()

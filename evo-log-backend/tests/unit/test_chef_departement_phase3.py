"""Phase 3 Tranche A — Espace departement (niveau 2, chef de departement).

Ferme le maillon "chef de departement" du roadmap (plan PHASE 3) : un niveau 2
ne voit et ne pilote QUE son propre departement. Trois maillons couverts :

  1. GARDE ``require_department_head`` (utils/rbac.py) : niveau 3 refuse ; un
     niveau 2 sans department_id refuse (scope vide silencieux interdit) ;
     niveau 2 avec departement, niveau 1 et Super Admin passent.

  2. RESOLUTION DE PERIMETRE ``_scoped_department`` : un chef est epingle a son
     departement (403 s'il tente d'en telecharger un autre) ; un admin entreprise
     cible n'importe quel departement de SON entreprise mais 403 des qu'il change
     d'entreprise ; un Super Admin doit passer un department_id explicite.

  3. BOUT-EN-BOUT HTTP : deux departements d'une meme entreprise, chacun avec son
     chef. Le chef de Operations ne recoit que les membres de Operations via
     l'API reelle (middleware + JWT reels, aucun dependency_overrides d'auth) ;
     tenter department_id=Finance -> 403 ; et la liste ne fuite jamais un id de
     l'autre departement.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import app.main  # noqa: F401 - enregistre tous les modeles + monte le middleware
from app.core.database import Base, SessionLocal, engine
from app.core.security import create_access_token, get_password_hash
from app.core.tenant_context import clear_current_tenant
from app.models.tenant import Company, Department
from app.models.user import User
from app.routers.v1.chef_departement import _scoped_department
from app.utils.rbac import require_department_head


def _mk_user(level: int, *, company_id=None, department_id=None, username="u"):
    return User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True,
        is_superuser=(level == 0),
        role_level=level,
        company_id=company_id,
        department_id=department_id,
    )


# --------------------------------------------------------------------------- #
# 1. Garde require_department_head
# --------------------------------------------------------------------------- #
def test_guard_rejects_plain_user_level3():
    u = _mk_user(3, company_id=1, department_id=1, username="op")
    with pytest.raises(HTTPException) as exc:
        require_department_head(u)
    assert exc.value.status_code == 403


def test_guard_rejects_chef_without_department():
    # Niveau 2 mais non rattache a un departement -> refus explicite (pas de
    # scope vide silencieux qui afficherait une liste trompeuse).
    u = _mk_user(2, company_id=1, department_id=None, username="orphan-chef")
    with pytest.raises(HTTPException) as exc:
        require_department_head(u)
    assert exc.value.status_code == 403


def test_guard_allows_chef_with_department():
    u = _mk_user(2, company_id=1, department_id=7, username="chef")
    assert require_department_head(u) is u


def test_guard_allows_company_admin():
    u = _mk_user(1, company_id=1, department_id=None, username="admin")
    assert require_department_head(u) is u


def test_guard_allows_superadmin():
    u = _mk_user(0, company_id=None, department_id=None, username="cad")
    assert require_department_head(u) is u


# --------------------------------------------------------------------------- #
# 2. _scoped_department (perimetre), sur la base ORM isolee de conftest
# --------------------------------------------------------------------------- #
def _seed_company_and_depts(db):
    co = Company(nom="SARL Perimetre", code="PERI", is_active=True, modules_actives="[]")
    db.add(co)
    db.commit()
    db.refresh(co)
    ops = Department(company_id=co.id, code="OPS", nom="Operations")
    fin = Department(company_id=co.id, code="FIN", nom="Finance")
    other = Company(nom="Autre SA", code="OTHER", is_active=True, modules_actives="[]")
    db.add_all([ops, fin, other])
    db.commit()
    db.refresh(other)
    foreign = Department(company_id=other.id, code="X", nom="Foreign")
    db.add(foreign)
    db.commit()
    db.refresh(ops); db.refresh(fin); db.refresh(foreign)
    return co, ops, fin, foreign


def test_scoped_department_chef_pinned_to_own(db):
    co, ops, fin, _foreign = _seed_company_and_depts(db)
    chef = _mk_user(2, company_id=co.id, department_id=ops.id, username="chef-ops")
    db.add(chef)
    db.commit()

    # Sans request explicite -> son departement.
    resolved = _scoped_department(db, chef, None)
    assert resolved.id == ops.id
    # Tentative de telecharger Finance -> 403.
    with pytest.raises(HTTPException) as exc:
        _scoped_department(db, chef, fin.id)
    assert exc.value.status_code == 403


def test_scoped_department_admin_same_company_ok_other_company_403(db):
    co, ops, _fin, foreign = _seed_company_and_depts(db)
    admin = _mk_user(1, company_id=co.id, department_id=None, username="admin-1")
    db.add(admin)
    db.commit()

    # Departement de son entreprise -> OK.
    assert _scoped_department(db, admin, ops.id).id == ops.id
    # Departement d'une AUTRE entreprise -> 403.
    with pytest.raises(HTTPException) as exc:
        _scoped_department(db, admin, foreign.id)
    assert exc.value.status_code == 403
    # Aucun department_id -> 400 (choix explicite requis).
    with pytest.raises(HTTPException) as exc:
        _scoped_department(db, admin, None)
    assert exc.value.status_code == 400


def test_scoped_department_superadmin_requires_explicit(db):
    _co, ops, _fin, _foreign = _seed_company_and_depts(db)
    cad = _mk_user(0, company_id=None, department_id=None, username="cad")
    db.add(cad)
    db.commit()
    with pytest.raises(HTTPException) as exc:
        _scoped_department(db, cad, None)
    assert exc.value.status_code == 400
    assert _scoped_department(db, cad, ops.id).id == ops.id


# --------------------------------------------------------------------------- #
# 3. Bout-en-bout HTTP : middleware + JWT reels, deux departements cloisonnes
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module", autouse=True)
def _ensure_app_schema():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    yield
    clear_current_tenant()


@pytest.fixture(scope="module")
def dept_http_client():
    """TestClient sans override d'auth : middleware + get_current_user reels sur
    la base en memoire partagee de l'app (StaticPool)."""
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    with TestClient(app.main.app) as c:
        yield c
    clear_current_tenant()


@pytest.fixture(scope="module")
def two_departments(dept_http_client):
    """Une entreprise, deux departements (OPS/FIN), un chef + 2 membres chacun."""
    db = SessionLocal()
    try:
        co = Company(nom="Transports Reunis", code="TR", is_active=True, modules_actives="[]")
        db.add(co)
        db.commit()
        db.refresh(co)

        ops = Department(company_id=co.id, code="OPS", nom="Operations", modules_allowed='["transport"]')
        fin = Department(company_id=co.id, code="FIN", nom="Finance", modules_allowed='["finance"]')
        db.add_all([ops, fin])
        db.commit()
        db.refresh(ops); db.refresh(fin)

        chef_ops = _mk_user(2, company_id=co.id, department_id=ops.id, username="chef-ops")
        chef_fin = _mk_user(2, company_id=co.id, department_id=fin.id, username="chef-fin")
        op_a = _mk_user(3, company_id=co.id, department_id=ops.id, username="ops-a")
        op_b = _mk_user(3, company_id=co.id, department_id=ops.id, username="ops-b")
        fin_a = _mk_user(3, company_id=co.id, department_id=fin.id, username="fin-a")
        db.add_all([chef_ops, chef_fin, op_a, op_b, fin_a])
        db.commit()
        db.refresh(chef_ops); db.refresh(chef_fin)

        return {
            "company_id": co.id,
            "ops_id": ops.id,
            "fin_id": fin.id,
            "chef_ops_token": create_access_token({"sub": str(chef_ops.id)}),
            "chef_fin_token": create_access_token({"sub": str(chef_fin.id)}),
        }
    finally:
        db.close()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_membres_requires_auth(dept_http_client):
    resp = dept_http_client.get("/api/v1/departement/membres")
    assert resp.status_code in (401, 403)


def test_chef_sees_only_own_department_members(dept_http_client, two_departments):
    resp = dept_http_client.get(
        "/api/v1/departement/membres", headers=_auth(two_departments["chef_ops_token"])
    )
    assert resp.status_code == 200, resp.text
    usernames = sorted(m["username"] for m in resp.json())
    # Operations : les 2 membres + le chef lui-meme (tous rattachés au dept).
    assert usernames == ["chef-ops", "ops-a", "ops-b"]
    # Aucun membre de Finance ne fuite.
    assert "fin-a" not in usernames
    assert "chef-fin" not in usernames
    # Et la cloison inverse tient.
    resp_fin = dept_http_client.get(
        "/api/v1/departement/membres", headers=_auth(two_departments["chef_fin_token"])
    )
    assert sorted(m["username"] for m in resp_fin.json()) == ["chef-fin", "fin-a"]


def test_chef_cannot_download_other_department(dept_http_client, two_departments):
    resp = dept_http_client.get(
        "/api/v1/departement/membres",
        headers=_auth(two_departments["chef_ops_token"]),
        params={"department_id": two_departments["fin_id"]},
    )
    assert resp.status_code == 403


def test_overview_scoped_to_own_department(dept_http_client, two_departments):
    resp = dept_http_client.get(
        "/api/v1/departement/overview", headers=_auth(two_departments["chef_ops_token"])
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] == two_departments["ops_id"]
    assert data["nom"] == "Operations"
    assert data["modules_allowed"] == ["transport"]
    assert data["effectif"] == 3

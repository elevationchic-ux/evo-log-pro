"""Phase 3 Tranche B  Espace departement : ECRITURES scopees (niveau 2 / 1 / 0).

Complete la Tranche A (lecture) par les operations d'ecriture, toujours sous
``_scoped_department`` + ``require_department_head`` :

  - AFFECTER / RETIRER un collaborateur du departement :
      * un chef (2) ne pilote QUE des collaborateurs (niveau 3) de SON entreprise
        et dans SON departement ;
      * un niveau 1/2 (pair/superieur) et un Super Admin sont refuses ;
      * un compte d'une autre entreprise ne fuite jamais (403/404).
  - ALLOCATION DES MODULES d'un departement :
      * un chef (2) ne se auto-grantit pas -> 403 ;
      * un admin entreprise (1) / CADC (0) alloue, STRICTEMENT sous-ensemble des
        modules de l'entreprise (Company.modules_actives), sinon 400.

Bout-en-bout HTTP reel : middleware + JWT reels (create_access_token), AUCUN
dependency_overrides d'auth, base en memoire partagee de l'app (StaticPool).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.main  # noqa: F401 - enregistre les modeles + monte le middleware
from app.core.database import Base, SessionLocal, engine
from app.core.security import create_access_token, get_password_hash
from app.core.tenant_context import clear_current_tenant
from app.models.tenant import Company, Department
from app.models.user import User


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
# Fixtures module : schema reel + client + sandbox d'ecriture independant
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module", autouse=True)
def _ensure_app_schema():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    yield
    clear_current_tenant()


@pytest.fixture(scope="module")
def write_client():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    with TestClient(app.main.app) as c:
        yield c
    clear_current_tenant()


@pytest.fixture(scope="module")
def sandbox(write_client):
    """Entreprise W (modules transport+magasin), 2 departements, chef + admin,
    2 collaborateurs niveau 3 (dont un sans departement), 1 chef voisin, et une
    entreprise F etrangere avec un niveau 3."""
    db = SessionLocal()
    try:
        co = Company(nom="Logistique W", code="W", is_active=True, modules_actives='["transport","magasin"]')
        db.add(co)
        db.commit()
        db.refresh(co)

        ops = Department(company_id=co.id, code="OPS", nom="Operations", modules_allowed='[]')
        fin = Department(company_id=co.id, code="FIN", nom="Finance", modules_allowed='[]')
        db.add_all([ops, fin])
        db.commit()
        db.refresh(ops)
        db.refresh(fin)

        chef = _mk_user(2, company_id=co.id, department_id=ops.id, username="chef-w")
        chef_fin = _mk_user(2, company_id=co.id, department_id=fin.id, username="chef-w2")
        admin = _mk_user(1, company_id=co.id, department_id=None, username="admin-w")
        float_a = _mk_user(3, company_id=co.id, department_id=None, username="float-a")
        float_b = _mk_user(3, company_id=co.id, department_id=None, username="float-b")
        membre_ops = _mk_user(3, company_id=co.id, department_id=ops.id, username="membre-ops")
        db.add_all([chef, chef_fin, admin, float_a, float_b, membre_ops])
        db.commit()
        db.refresh(chef)
        db.refresh(float_a)
        db.refresh(float_b)
        db.refresh(membre_ops)
        db.refresh(chef_fin)

        # Entreprise etrangere + son niveau 3 (tentation de cross-tenant).
        foreign = Company(nom="Autre SA", code="F", is_active=True, modules_actives='["transport"]')
        db.add(foreign)
        db.commit()
        db.refresh(foreign)
        fdept = Department(company_id=foreign.id, code="X", nom="Foreign Dept")
        db.add(fdept)
        db.commit()
        db.refresh(fdept)
        outsider = _mk_user(3, company_id=foreign.id, department_id=fdept.id, username="outsider")
        db.add(outsider)
        db.commit()
        db.refresh(outsider)

        return {
            "ops_id": ops.id,
            "fin_id": fin.id,
            "chef_token": create_access_token({"sub": str(chef.id)}),
            "admin_token": create_access_token({"sub": str(admin.id)}),
            "float_a_id": int(float_a.id),
            "float_b_id": int(float_b.id),
            "membre_ops_id": int(membre_ops.id),
            "chef_fin_id": int(chef_fin.id),
            "outsider_id": int(outsider.id),
        }
    finally:
        db.close()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------- #
# Affecter / retirer des membres
# --------------------------------------------------------------------------- #
def test_writes_require_auth(write_client):
    resp = write_client.post("/api/v1/departement/membres/1/affecter")
    assert resp.status_code in (401, 403)


def test_candidats_requires_auth(write_client):
    resp = write_client.get("/api/v1/departement/candidats")
    assert resp.status_code in (401, 403)


def test_chef_candidates_are_level3_outside_own_dept(write_client, sandbox):
    # Invariants stables quelle que soit l'ordre d'execution des tests precedents :
    # seuls des niveaux 3 de l'entreprise, jamais deja dans le departement du chef.
    resp = write_client.get(
        "/api/v1/departement/candidats", headers=_auth(sandbox["chef_token"])
    )
    assert resp.status_code == 200, resp.text
    for c in resp.json():
        assert c["role_level"] == 3
        assert c["department_id"] != sandbox["ops_id"]


def test_chef_affects_collaborator_into_own_department(write_client, sandbox):
    resp = write_client.post(
        f"/api/v1/departement/membres/{sandbox['float_b_id']}/affecter",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["department_id"] == sandbox["ops_id"]
    assert body["previous_department_id"] is None
    # Le roster du chef contient desormais le collaborateur affecte.
    roster = write_client.get(
        "/api/v1/departement/membres", headers=_auth(sandbox["chef_token"])
    ).json()
    assert "float-b" in {m["username"] for m in roster}


def test_chef_cannot_affect_a_fellow_department_head(write_client, sandbox):
    # chef-w2 est niveau 2 : un chef ne pilote que des niveaux 3.
    resp = write_client.post(
        f"/api/v1/departement/membres/{sandbox['chef_fin_id']}/affecter",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 403, resp.text


def test_chef_cannot_touch_other_company_member(write_client, sandbox):
    # outsider appartient a une autre entreprise : 403 (garde) ou 404
    # (cloisonnement ORM par contexte tenant)  les deux prouvent la non-fuite.
    resp = write_client.post(
        f"/api/v1/departement/membres/{sandbox['outsider_id']}/affecter",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code in (403, 404), resp.text


def test_chef_retires_member_from_own_department(write_client, sandbox):
    resp = write_client.post(
        f"/api/v1/departement/membres/{sandbox['membre_ops_id']}/retirer",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["department_id"] is None
    roster = write_client.get(
        "/api/v1/departement/membres", headers=_auth(sandbox["chef_token"])
    ).json()
    assert "membre-ops" not in {m["username"] for m in roster}


def test_retire_rejects_member_not_in_department(write_client, sandbox):
    # float-a n'est pas (encore) dans le departement du chef -> retrait refuse.
    resp = write_client.post(
        f"/api/v1/departement/membres/{sandbox['float_a_id']}/retirer",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 400, resp.text


def test_admin_can_move_member_across_departments_same_company(write_client, sandbox):
    # Un admin entreprise (1) n'est pas epingle : il place float-a dans FIN.
    resp = write_client.post(
        f"/api/v1/departement/membres/{sandbox['float_a_id']}/affecter",
        headers=_auth(sandbox["admin_token"]),
        params={"department_id": sandbox["fin_id"]},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["department_id"] == sandbox["fin_id"]


# --------------------------------------------------------------------------- #
# Allocation des modules du departement
# --------------------------------------------------------------------------- #
def test_chef_cannot_self_grant_modules(write_client, sandbox):
    resp = write_client.put(
        "/api/v1/departement/modules",
        headers=_auth(sandbox["chef_token"]),
        json={"modules": ["transport"]},
    )
    assert resp.status_code == 403, resp.text


def test_admin_allocates_subset_of_company_modules(write_client, sandbox):
    resp = write_client.put(
        "/api/v1/departement/modules",
        headers=_auth(sandbox["admin_token"]),
        params={"department_id": sandbox["ops_id"]},
        json={"modules": ["Transport", "transport", "magasin"]},
    )
    assert resp.status_code == 200, resp.text
    # Normalise + dedupfine : ["transport","magasin"].
    assert resp.json()["modules_allowed"] == ["transport", "magasin"]
    # La fiche du departement reflet l'allocation.
    overview = write_client.get(
        "/api/v1/departement/overview",
        headers=_auth(sandbox["admin_token"]),
        params={"department_id": sandbox["ops_id"]},
    ).json()
    assert overview["modules_allowed"] == ["transport", "magasin"]


def test_admin_cannot_exceed_company_allocated_modules(write_client, sandbox):
    # "finance" n'est pas alloue a l'entreprise (transport+magasin seulement).
    resp = write_client.put(
        "/api/v1/departement/modules",
        headers=_auth(sandbox["admin_token"]),
        params={"department_id": sandbox["fin_id"]},
        json={"modules": ["finance"]},
    )
    assert resp.status_code == 400, resp.text

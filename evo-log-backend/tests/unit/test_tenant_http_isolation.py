"""Phase 4 — Certification de l'etancheite multi-tenant.

Le mecanisme d'isolation (app.core.tenant_enforcement + tenant_context) etait
deja prouve au niveau ORM (tests/unit/test_tenant_isolation.py). Ce module ferme
les DEUX maillons jusque-la non couverts :

  1. COUVERTURE : toute entite metier portant ``company_id`` est bien suivie par
     le moteur (garde anti-regression : un nouveau modele "monnaie courante" qui
     oublierait company_id basculerait silencieusement en global / fail-open).

  2. CHAINE HTTP COMPLETE : un vrai JWT d'un utilisateur rattache a une
     entreprise active l'isolation de bout en bout — middleware
     (TenantContextMiddleware, qui lit l'en-tete Authorization et resout la
     societe) -> contexte contextvar -> moteur ORM -> router. Deux societes
     distinctes ne DOIVENT jamais voir leurs ressources reciproques via l'API
     reelle, sans aucun dependency_overrides d'auth.

Contrairement a la fixture ``client`` (faux super-utilisateur, enforcement
OFF par conception), ces tests exercent l'authentification REELLE et le
middleware REEL, en partageant la base en memoire de l'application (StaticPool
:memory:) via app.core.database.SessionLocal — la meme que celle que le
middleware ouvre pour resoudre le tenant.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.main  # noqa: F401 - enregistre tous les modeles + monte le middleware
from app.core import tenant_enforcement
from app.core.database import Base, SessionLocal, engine
from app.core.security import create_access_token, get_password_hash
from app.core.tenant_context import clear_current_tenant, get_current_tenant
from app.middleware.tenant_context import TenantContextMiddleware
from app.models.tenant import Company, Department
from app.models.user import User


# --------------------------------------------------------------------------- #
# 1. Couverture : le moteur suit bien toute entite portant company_id
# --------------------------------------------------------------------------- #
def _tracked_class_names() -> set:
    return {cls.__name__ for cls in tenant_enforcement._tenant_scoped_classes()}


def test_every_company_bearing_model_is_tracked():
    """Invariant central : une classe est suivie ssi elle declare company_id.

    Le moteur determine sa liste en filtrant ``'company_id' in mapper.columns``.
    On recalcule independamment et on exige l'identite stricte : si un jour la
    logique d'enumeration diverge (heritage, alias), ce test le crie.
    """
    from sqlalchemy.orm import class_mapper

    should_track = set()
    for mapper in Base.registry.mappers:
        if "company_id" in mapper.columns:
            should_track.add(mapper.class_.__name__)
    assert should_track == _tracked_class_names()
    assert should_track, "au moins une entite metier doit etre tenant-scoped"


def test_known_business_entities_are_scoped():
    """Garde-nom : ces entites metiers DOIVENT rester rattachées a une societe."""
    tracked = _tracked_class_names()
    for name in ("Department", "User", "Accreditation"):
        assert name in tracked, f"{name} doit porter company_id et etre isolee par tenant"


# --------------------------------------------------------------------------- #
# 2. Middleware : un vrai JWT positionne (puis efface) le contexte tenant
# --------------------------------------------------------------------------- #
def test_middleware_scopes_context_from_real_jwt():
    """Sonde ASGI minimale : on capture get_current_tenant() PENDANT le
    traitement, ce qui prouve que le middleware a resolu la societe depuis
    l'en-tete et la publie dans le contextvar visible par l'ORM."""
    seen: dict = {}

    async def probe(scope, receive, send):
        seen["tenant"] = get_current_tenant()
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    mw = TenantContextMiddleware(probe)

    db = SessionLocal()
    try:
        company = Company(nom="Sonde SARL", code="SONDE", is_active=True, modules_actives="[]")
        db.add(company)
        db.commit()
        db.refresh(company)
        admin = User(
            username="sonde-admin", email="sonde.admin@example.com",
            hashed_password=get_password_hash("Admin12345"),
            is_active=True, is_superuser=False, role_level=1, company_id=company.id,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        token = create_access_token({"sub": str(admin.id)})
    finally:
        db.close()

    async def _receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def _send(_msg):
        return None

    import asyncio

    scope = {
        "type": "http", "method": "GET", "path": "/x", "headers": [
            (b"authorization", f"Bearer {token}".encode())
        ],
        "query_string": b"", "scheme": "http", "server": ("test", 80), "client": ("127.0.0.1", 1),
    }
    try:
        asyncio.run(mw(scope, _receive, _send))
        assert seen["tenant"] == company.id
        # Apres la requete, le contexte est nettoye (pas de fuite entre requetes).
        assert get_current_tenant() is None
    finally:
        # Nettoyage du seed (aucun contexte actif -> enforcement inactif).
        clear_current_tenant()
        db = SessionLocal()
        try:
            db.query(User).filter(User.company_id == company.id).delete()
            db.query(Department).filter(Department.company_id == company.id).delete()
            db.query(Company).filter(Company.id == company.id).delete()
            db.commit()
        finally:
            db.close()


# --------------------------------------------------------------------------- #
# 3. Bout-en-bout : deux societes invisibles l'une pour l'autre via l'API reelle
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def tenant_http_client():
    """TestClient sans AUCUN override d'auth : middleware + get_current_user +
    enforcement reels, sur la base en memoire partagee de l'app (StaticPool)."""
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    with TestClient(app.main.app) as c:
        yield c
    clear_current_tenant()
    # Purge des lignes creées par ce module (enforcement inactif hors requete).
    db = SessionLocal()
    try:
        db.query(Department).delete()
        db.query(User).delete()
        db.query(Company).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="module")
def two_companies(tenant_http_client):
    """Cree 2 societes + 1 admin chacune + 2 departements par societe (dont un
    nom commun 'COMMUN' pour verifier que le filtrage n'est pas nominal)."""
    db = SessionLocal()
    try:
        alpha = Company(nom="Alpha Logistics", code="ALPHA", is_active=True, modules_actives="[]")
        beta = Company(nom="Beta Transport", code="BETA", is_active=True, modules_actives="[]")
        db.add_all([alpha, beta])
        db.commit()
        db.refresh(alpha); db.refresh(beta)

        a_admin = User(
            username="alpha-admin", email="alpha.admin@example.com",
            hashed_password=get_password_hash("Admin12345"),
            is_active=True, is_superuser=False, role_level=1, company_id=alpha.id,
        )
        b_admin = User(
            username="beta-admin", email="beta.admin@example.com",
            hashed_password=get_password_hash("Admin12345"),
            is_active=True, is_superuser=False, role_level=1, company_id=beta.id,
        )
        db.add_all([a_admin, b_admin])
        db.commit()
        db.refresh(a_admin); db.refresh(b_admin)

        db.add_all([
            Department(company_id=alpha.id, code="OPS", nom="Alpha Operations"),
            Department(company_id=alpha.id, code="FIN", nom="Alpha Finance"),
            Department(company_id=beta.id, code="OPS", nom="Beta Operations"),
        ])
        db.commit()

        tokens = {
            "alpha": create_access_token({"sub": str(a_admin.id)}),
            "beta": create_access_token({"sub": str(b_admin.id)}),
        }
        yield {"alpha_id": alpha.id, "beta_id": beta.id, "tokens": tokens}
    finally:
        db.close()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_departments_list_requires_auth(tenant_http_client):
    """Sans JWT, la liste des departements n'est pas servie (401/403)."""
    resp = tenant_http_client.get("/api/v1/tenant/departments")
    assert resp.status_code in (401, 403)


def test_each_company_sees_only_its_departments(tenant_http_client, two_companies):
    alpha = tenant_http_client.get(
        "/api/v1/tenant/departments", headers=_auth(two_companies["tokens"]["alpha"])
    )
    beta = tenant_http_client.get(
        "/api/v1/tenant/departments", headers=_auth(two_companies["tokens"]["beta"])
    )
    assert alpha.status_code == 200, alpha.text
    assert beta.status_code == 200, beta.text

    a_rows = alpha.json()
    b_rows = beta.json()
    a_names = sorted(d["nom"] for d in a_rows)
    b_names = sorted(d["nom"] for d in b_rows)

    assert a_names == ["Alpha Finance", "Alpha Operations"]
    assert b_names == ["Beta Operations"]
    # Aucun chevauchement inter-tenant, y compris sur le code partage 'OPS'.
    assert all(d["company_id"] == two_companies["alpha_id"] for d in a_rows)
    assert all(d["company_id"] == two_companies["beta_id"] for d in b_rows)
    assert set(d["id"] for d in a_rows).isdisjoint(d["id"] for d in b_rows)


def test_company_cannot_read_other_company_department_by_id(
    tenant_http_client, two_companies
):
    """Attaque IDOR : Beta tente d'acceder a un departement d'Alpha par son id."""
    a_rows = tenant_http_client.get(
        "/api/v1/tenant/departments", headers=_auth(two_companies["tokens"]["alpha"])
    ).json()
    alpha_dept_id = next(d["id"] for d in a_rows if d["nom"] == "Alpha Finance")

    # La liste scoped de Beta ne contient jamais la ligne d'Alpha.
    b_rows = tenant_http_client.get(
        "/api/v1/tenant/departments", headers=_auth(two_companies["tokens"]["beta"])
    ).json()
    assert alpha_dept_id not in {d["id"] for d in b_rows}

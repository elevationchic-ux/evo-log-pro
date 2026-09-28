"""Phase 4 Tranche A — Planning + Presence du departement (espace chef, niveau 2).

Reutilise les modeles RH ``PlanningGarde`` (tours de garde) et ``PointageVacation``
(emargements) mais les EXPOSE sous le perimetre departemental strict deja en place :
``require_department_head`` + ``_scoped_department``. Le module RH global
``chef_personnel`` ne donne PAS cette cloison par departement ; c'est ici qu'un
chef de departement ne voit que le planning / la presence de SES collaborateurs.

Couvert :
  - helpers ``_week_bounds`` (semaine ISO) et ``_parse_date`` (rejets 400) ;
  - /departement/planning : lignes limitees aux membres du departement resolu,
    un membre d'un autre departement ne fuite pas ; cross-dept -> 403 ; semaine
    invalide -> 400 ; un admin (1) cible un departement explicite de son entreprise ;
  - /departement/presence : statut DEDUIT des lignes reelles (PRESENT / ATTENDU /
    NON_PLANIFIE), perimetre departemental, date invalide -> 400.

Bout-en-bout HTTP reel : middleware + JWT reels, aucun dependency_overrides d'auth.
"""
from __future__ import annotations

from datetime import date as _date

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import app.main  # noqa: F401 - enregistre tous les modeles + monte le middleware
from app.core.database import Base, SessionLocal, engine
from app.core.security import create_access_token, get_password_hash
from app.core.tenant_context import clear_current_tenant
from app.models.chef_personnel import PlanningGarde, PointageVacation
from app.models.tenant import Company, Department
from app.models.user import User
from app.routers.v1.chef_departement import _parse_date, _week_bounds


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
# 1. Helpers de perimetre temporel (unites pures)
# --------------------------------------------------------------------------- #
def test_week_bounds_known_iso_week():
    # 2026-W09 : lundi 23 fevrier 2026 -> dimanche 1 mars 2026 (calendrier ISO).
    start, end = _week_bounds("2026-W09")
    assert start == _date(2026, 2, 23)
    assert end == _date(2026, 3, 1)
    assert (end - start).days == 6


def test_week_bounds_default_is_current_week():
    start, _end = _week_bounds(None)
    iso = _date.today().isocalendar()
    assert start == _date.fromisocalendar(iso[0], iso[1], 1)  # lundi courant


def test_week_bounds_rejects_garbage():
    with pytest.raises(HTTPException) as exc:
        _week_bounds("not-a-week")
    assert exc.value.status_code == 400


def test_parse_date_valid_and_default():
    assert _parse_date("2026-05-04") == _date(2026, 5, 4)
    assert _parse_date(None) == _date.today()
    with pytest.raises(HTTPException) as exc:
        _parse_date("04/05/2026")
    assert exc.value.status_code == 400


# --------------------------------------------------------------------------- #
# 2. Fixtures HTTP module + sandbox a deux departements
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module", autouse=True)
def _ensure_app_schema():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    yield
    clear_current_tenant()


@pytest.fixture(scope="module")
def pp_client():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    with TestClient(app.main.app) as c:
        yield c
    clear_current_tenant()


@pytest.fixture(scope="module")
def sandbox(pp_client):
    """Une entreprise, deux departements OPS/FIN.

    Aujourd'hui (dans la semaine courante) :
      - ops-a : planifie + pointe  -> PRESENT
      - ops-b : planifie, non pointe -> ATTENDU
      - ops-c : ni planifie ni pointe -> NON_PLANIFIE
      - fin-a (autre departement) : planifie + pointe -> ne doit JAMAIS fuite
        vers le chef de OPS ; visible seulement si on cible FIN (admin).
    """
    today = _date.today()
    db = SessionLocal()
    try:
        co = Company(nom="Manutention SA", code="MS", is_active=True, modules_actives='["port","transport"]')
        db.add(co)
        db.commit()
        db.refresh(co)

        ops = Department(company_id=co.id, code="OPS", nom="Operations")
        fin = Department(company_id=co.id, code="FIN", nom="Finance")
        db.add_all([ops, fin])
        db.commit()
        db.refresh(ops)
        db.refresh(fin)

        chef_ops = _mk_user(2, company_id=co.id, department_id=ops.id, username="chef-ops")
        admin = _mk_user(1, company_id=co.id, department_id=None, username="admin-ms")
        ops_a = _mk_user(3, company_id=co.id, department_id=ops.id, username="ops-a")
        ops_b = _mk_user(3, company_id=co.id, department_id=ops.id, username="ops-b")
        ops_c = _mk_user(3, company_id=co.id, department_id=ops.id, username="ops-c")
        fin_a = _mk_user(3, company_id=co.id, department_id=fin.id, username="fin-a")
        db.add_all([chef_ops, admin, ops_a, ops_b, ops_c, fin_a])
        db.commit()
        db.refresh(chef_ops)
        db.refresh(admin)
        db.refresh(ops_a)
        db.refresh(ops_b)
        db.refresh(fin_a)

        # Planning (tours de garde) du jour.
        db.add_all([
            PlanningGarde(company_id=co.id, employe_id=ops_a.id, date_jour=today, quart="MATIN",
                          poste_assigne="Quai 14", statut="CONFIRME"),
            PlanningGarde(company_id=co.id, employe_id=ops_b.id, date_jour=today, quart="SOIR",
                          poste_assigne="Entrepot Central", statut="PLANIFIE"),
            PlanningGarde(company_id=co.id, employe_id=fin_a.id, date_jour=today, quart="STANDARD",
                          poste_assigne="Bureau Finance", statut="CONFIRME"),
        ])
        db.commit()

        # Emargements du jour (ops-a et fin-a pointent ; ops-b non).
        db.add_all([
            PointageVacation(company_id=co.id, employe_id=ops_a.id, date_pointage=today,
                             heure_arrivee="06:58", est_valide=True),
            PointageVacation(company_id=co.id, employe_id=fin_a.id, date_pointage=today,
                             heure_arrivee="08:02", est_valide=True),
        ])
        db.commit()

        return {
            "ops_id": ops.id,
            "fin_id": fin.id,
            "chef_ops_token": create_access_token({"sub": str(chef_ops.id)}),
            "admin_token": create_access_token({"sub": str(admin.id)}),
            "today": today.isoformat(),
        }
    finally:
        db.close()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------- #
# 3. Planning scope
# --------------------------------------------------------------------------- #
def test_planning_requires_auth(pp_client):
    resp = pp_client.get("/api/v1/departement/planning")
    assert resp.status_code in (401, 403)


def test_chef_planning_only_own_department_members(pp_client, sandbox):
    resp = pp_client.get("/api/v1/departement/planning", headers=_auth(sandbox["chef_ops_token"]))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["departement_nom"] == "Operations"
    usernames = {l["employe_username"] for l in data["lignes"]}
    assert usernames == {"ops-a", "ops-b"}
    # Un membre d'un autre departement ne fuite jamais.
    assert "fin-a" not in usernames
    assert "ops-c" not in usernames  # non planifie ce jour -> aucune ligne


def test_chef_planning_cross_department_is_403(pp_client, sandbox):
    resp = pp_client.get(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["chef_ops_token"]),
        params={"department_id": sandbox["fin_id"]},
    )
    assert resp.status_code == 403


def test_planning_invalid_week_is_400(pp_client, sandbox):
    resp = pp_client.get(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["chef_ops_token"]),
        params={"semaine": "invalide"},
    )
    assert resp.status_code == 400


def test_admin_can_target_other_department_of_company(pp_client, sandbox):
    resp = pp_client.get(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["admin_token"]),
        params={"department_id": sandbox["fin_id"]},
    )
    assert resp.status_code == 200, resp.text
    usernames = {l["employe_username"] for l in resp.json()["lignes"]}
    assert usernames == {"fin-a"}


# --------------------------------------------------------------------------- #
# 4. Presence scope
# --------------------------------------------------------------------------- #
def test_presence_requires_auth(pp_client):
    resp = pp_client.get("/api/v1/departement/presence")
    assert resp.status_code in (401, 403)


def test_chef_presence_statuts_are_deduced(pp_client, sandbox):
    resp = pp_client.get(
        "/api/v1/departement/presence",
        headers=_auth(sandbox["chef_ops_token"]),
        params={"date": sandbox["today"]},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    by_user = {c["username"]: c["presence"] for c in data["collaborateurs"]}
    assert by_user == {"chef-ops": "NON_PLANIFIE", "ops-a": "PRESENT", "ops-b": "ATTENDU", "ops-c": "NON_PLANIFIE"}
    # Aucun membre de Finance ne fuite.
    assert "fin-a" not in by_user
    assert data["synthese"]["presents"] == 1
    assert data["synthese"]["attendus"] == 1


def test_presence_invalid_date_is_400(pp_client, sandbox):
    resp = pp_client.get(
        "/api/v1/departement/presence",
        headers=_auth(sandbox["chef_ops_token"]),
        params={"date": "2026-13-40"},
    )
    assert resp.status_code == 400

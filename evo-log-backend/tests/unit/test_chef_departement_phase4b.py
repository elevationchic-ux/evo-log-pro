"""Phase 4 Tranche B  Ecriture Planning + Validation Presence (espace chef, niveau 2).

Couvert :
  - POST /departement/planning (creation tour de garde, deadline "au mercredi") ;
  - PUT /departement/planning/{id} (modification, idem deadline) ;
  - DELETE /departement/planning/{id} (suppression scopee) ;
  - POST /departement/presence/{id}/valider (validation emargement) ;
  - isolation departement (403 cross-dept) ;
  - validation des enumerations (quart, statut) ;
  - contrainte publication : CONFIRME refuse apres le mercredi precedent.

Bout-en-bout HTTP reel : middleware + JWT reels, aucun dependency_overrides d'auth.
"""
from __future__ import annotations

from datetime import date as _date
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import app.main  # noqa: F401 - enregistre tous les modeles + monte le middleware
from app.core.database import Base, SessionLocal, engine
from app.core.security import create_access_token, get_password_hash
from app.core.tenant_context import clear_current_tenant
from app.models.chef_personnel import PlanningGarde, PointageVacation
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
# Helpers
# --------------------------------------------------------------------------- #
def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------- #
# Module-scoped fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module", autouse=True)
def _ensure_app_schema():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    yield
    clear_current_tenant()


@pytest.fixture(scope="module")
def wb_client():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    with TestClient(app.main.app) as c:
        yield c
    clear_current_tenant()


@pytest.fixture(scope="module")
def sandbox(wb_client):
    """Une entreprise, deux departements OPS/FIN.

    Users : chef-ops (2), admin-1 (1), ops-a/b/c (3), fin-a (3).
    Planning : ops-a a un tour CONFIRME (id retourné).
    Pointage : ops-a a un emargement non-valide (id retourné).
    """
    today = _date.today()
    # Date en semaine suivante pour les tests de deadline.
    iso = today.isocalendar()
    next_week_monday = _date.fromisocalendar(iso[0], iso[1] + 1 if iso[1] < 52 else 1, 1)

    db = SessionLocal()
    try:
        co = Company(nom="Manutention SA", code="MS-WB", is_active=True, modules_actives='["port","transport"]')
        db.add(co)
        db.commit()
        db.refresh(co)

        ops = Department(company_id=co.id, code="OPS-WB", nom="Operations WB")
        fin = Department(company_id=co.id, code="FIN-WB", nom="Finance WB")
        db.add_all([ops, fin])
        db.commit()
        db.refresh(ops)
        db.refresh(fin)

        chef_ops = _mk_user(2, company_id=co.id, department_id=ops.id, username="chef-ops-wb")
        admin_1 = _mk_user(1, company_id=co.id, department_id=None, username="admin-wb")
        ops_a = _mk_user(3, company_id=co.id, department_id=ops.id, username="ops-a-wb")
        ops_b = _mk_user(3, company_id=co.id, department_id=ops.id, username="ops-b-wb")
        ops_c = _mk_user(3, company_id=co.id, department_id=ops.id, username="ops-c-wb")
        fin_a = _mk_user(3, company_id=co.id, department_id=fin.id, username="fin-a-wb")
        db.add_all([chef_ops, admin_1, ops_a, ops_b, ops_c, fin_a])
        db.commit()
        for u in (chef_ops, admin_1, ops_a, ops_b, fin_a):
            db.refresh(u)

        # Planning existant pour ops-a (tour CONFIRME aujourdhui).
        pg = PlanningGarde(
            company_id=co.id, employe_id=ops_a.id, date_jour=today,
            quart="MATIN", poste_assigne="Quai 14", statut="CONFIRME",
        )
        db.add(pg)
        db.commit()
        db.refresh(pg)

        # Pointage NON VALIDE pour ops-a.
        pv = PointageVacation(
            company_id=co.id, employe_id=ops_a.id, date_pointage=today,
            heure_arrivee="06:50", est_valide=False,
        )
        db.add(pv)
        db.commit()
        db.refresh(pv)

        return {
            "ops_id": ops.id,
            "fin_id": fin.id,
            "chef_token": create_access_token({"sub": str(chef_ops.id)}),
            "admin_token": create_access_token({"sub": str(admin_1.id)}),
            "ops_a_id": ops_a.id,
            "ops_b_id": ops_b.id,
            "fin_a_id": fin_a.id,
            "planning_id": pg.id,
            "pointage_id": pv.id,
            "today": today,
            "next_week_monday": next_week_monday,
        }
    finally:
        db.close()


# --------------------------------------------------------------------------- #
# 1. Auth requirement (all endpoints)
# --------------------------------------------------------------------------- #
def test_create_planning_requires_auth(wb_client):
    resp = wb_client.post("/api/v1/departement/planning", json={
        "employe_id": 1, "date_jour": "2026-10-01", "quart": "JOUR", "poste_assigne": "X",
    })
    assert resp.status_code in (401, 403)


def test_update_planning_requires_auth(wb_client):
    resp = wb_client.put("/api/v1/departement/planning/1", json={"quart": "NUIT"})
    assert resp.status_code in (401, 403)


def test_delete_planning_requires_auth(wb_client):
    resp = wb_client.delete("/api/v1/departement/planning/1")
    assert resp.status_code in (401, 403)


def test_validate_presence_requires_auth(wb_client):
    resp = wb_client.post("/api/v1/departement/presence/1/valider")
    assert resp.status_code in (401, 403)


# --------------------------------------------------------------------------- #
# 2. POST /planning  creation
# --------------------------------------------------------------------------- #
def test_chef_creates_planning_for_own_member(wb_client, sandbox):
    resp = wb_client.post(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["chef_token"]),
        json={
            "employe_id": sandbox["ops_b_id"],
            "date_jour": sandbox["today"].isoformat(),
            "quart": "SOIR",
            "poste_assigne": "Entrepot Central",
            "statut": "PLANIFIE",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["employe_id"] == sandbox["ops_b_id"]
    assert data["quart"] == "SOIR"
    assert data["statut"] == "PLANIFIE"


def test_create_planning_employe_not_in_dept_is_403(wb_client, sandbox):
    resp = wb_client.post(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["chef_token"]),
        json={
            "employe_id": sandbox["fin_a_id"],
            "date_jour": sandbox["today"].isoformat(),
            "quart": "JOUR",
            "poste_assigne": "Bureau",
        },
    )
    assert resp.status_code == 403


def test_create_planning_invalid_quart_is_400(wb_client, sandbox):
    resp = wb_client.post(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["chef_token"]),
        json={
            "employe_id": sandbox["ops_a_id"],
            "date_jour": sandbox["today"].isoformat(),
            "quart": "WEEKEND",
            "poste_assigne": "Test",
        },
    )
    assert resp.status_code == 400


def test_create_planning_invalid_date_is_400(wb_client, sandbox):
    resp = wb_client.post(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["chef_token"]),
        json={
            "employe_id": sandbox["ops_a_id"],
            "date_jour": "13/45/2026",
            "quart": "JOUR",
            "poste_assigne": "Test",
        },
    )
    assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# 3. Contrainte publication "au mercredi"
# --------------------------------------------------------------------------- #
def test_create_planning_confirme_future_week_ok_before_deadline(wb_client, sandbox):
    """CONFIRME pour la semaine suivante est OK si today <= mercredi precedent.

    Date FIGEE au lundi de la semaine courante : sinon l'assertion dependrait
    du jour reel d'execution (jeudi > mercredi precedent -> 400 legitime). On
    rend le test deterministe, a l'image du test "after deadline" sibling.
    """
    real_iso = _date.today().isocalendar()
    fake_today = _date.fromisocalendar(real_iso[0], real_iso[1], 1)  # lundi
    with patch("app.routers.v1.chef_departement._date") as mock_date:
        mock_date.today.return_value = fake_today
        mock_date.fromisocalendar = _date.fromisocalendar
        mock_date.fromisoformat = _date.fromisoformat
        mock_date.resolution = _date.resolution
        fake_iso = fake_today.isocalendar()
        target_monday = _date.fromisocalendar(fake_iso[0], fake_iso[1] + 1, 1)
        resp = wb_client.post(
            "/api/v1/departement/planning",
            headers=_auth(sandbox["chef_token"]),
            json={
                "employe_id": sandbox["ops_a_id"],
                "date_jour": target_monday.isoformat(),
                "quart": "NUIT",
                "poste_assigne": "Poste Nuit",
                "statut": "CONFIRME",
            },
        )
    # Lundi <= mercredi precedent de la semaine cible -> publication ouverte.
    assert resp.status_code == 201, resp.text


def test_create_planning_confirme_future_week_rejected_after_deadline(wb_client, sandbox):
    """CONFIRME refuse si today > mercredi de la semaine precedente."""
    # Simulate today being a Thursday AFTER the Wednesday deadline.
    today = sandbox["today"]
    iso = today.isocalendar()
    # Use a date_jour in the CURRENT week to keep it simple, then mock today as
    # Friday of the week BEFORE the target.
    # Simpler: target next week, mock today = next Thursday (= past this Wednesday).
    # Wednesday of current week:
    wednesday_current = _date.fromisocalendar(iso[0], iso[1], 3)
    fake_today = wednesday_current + _date.resolution * 3  # Thursday of W
    # Actually we need a clean approach: patch _date.today().
    with patch("app.routers.v1.chef_departement._date") as mock_date:
        # The function uses _date.today(), _date.fromisocalendar(), _date.fromisoformat()
        mock_date.today.return_value = fake_today
        mock_date.fromisocalendar = _date.fromisocalendar
        mock_date.fromisoformat = _date.fromisoformat
        mock_date.resolution = _date.resolution
        # Target date in the week following fake_today's week
        fake_iso = fake_today.isocalendar()
        target_monday = _date.fromisocalendar(fake_iso[0], fake_iso[1] + 1, 1)
        resp = wb_client.post(
            "/api/v1/departement/planning",
            headers=_auth(sandbox["chef_token"]),
            json={
                "employe_id": sandbox["ops_a_id"],
                "date_jour": target_monday.isoformat(),
                "quart": "STANDARD",
                "poste_assigne": "Permanence",
                "statut": "CONFIRME",
            },
        )
    assert resp.status_code == 400
    assert "Publication fermee" in resp.json()["detail"]


# --------------------------------------------------------------------------- #
# 4. PUT /planning/{id}  modification
# --------------------------------------------------------------------------- #
def test_chef_updates_planning(wb_client, sandbox):
    resp = wb_client.put(
        f"/api/v1/departement/planning/{sandbox['planning_id']}",
        headers=_auth(sandbox["chef_token"]),
        json={"poste_assigne": "Quai 7", "observations": "Change de poste"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["poste_assigne"] == "Quai 7"


def test_update_planning_cross_dept_is_403(wb_client, sandbox):
    # Create a planning for fin_a via admin, then try to update as chef.
    admin_resp = wb_client.post(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["admin_token"]),
        params={"department_id": sandbox["fin_id"]},
        json={
            "employe_id": sandbox["fin_a_id"],
            "date_jour": sandbox["today"].isoformat(),
            "quart": "JOUR",
            "poste_assigne": "Bureau Finance",
        },
    )
    assert admin_resp.status_code == 201, admin_resp.text
    fin_pg_id = admin_resp.json()["id"]
    # Chef-ops tries to update it -> 403 (not in his dept).
    resp = wb_client.put(
        f"/api/v1/departement/planning/{fin_pg_id}",
        headers=_auth(sandbox["chef_token"]),
        json={"quart": "NUIT"},
    )
    assert resp.status_code == 403


def test_update_planning_invalid_statut_is_400(wb_client, sandbox):
    resp = wb_client.put(
        f"/api/v1/departement/planning/{sandbox['planning_id']}",
        headers=_auth(sandbox["chef_token"]),
        json={"statut": "MARCHÉ"},
    )
    assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# 5. DELETE /planning/{id}  suppression
# --------------------------------------------------------------------------- #
def test_chef_deletes_planning(wb_client, sandbox):
    # First create one to delete (avoid deleting the module-scoped fixture row).
    create = wb_client.post(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["chef_token"]),
        json={
            "employe_id": sandbox["ops_c_id"] if "ops_c_id" in sandbox else sandbox["ops_b_id"],
            "date_jour": sandbox["today"].isoformat(),
            "quart": "JOUR",
            "poste_assigne": "Temporary",
        },
    )
    assert create.status_code == 201, create.text
    pg_id = create.json()["id"]
    resp = wb_client.delete(
        f"/api/v1/departement/planning/{pg_id}",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["deleted"] == pg_id


def test_delete_planning_cross_dept_is_403(wb_client, sandbox):
    # Create for fin_a via admin, delete as chef -> 403.
    admin_resp = wb_client.post(
        "/api/v1/departement/planning",
        headers=_auth(sandbox["admin_token"]),
        params={"department_id": sandbox["fin_id"]},
        json={
            "employe_id": sandbox["fin_a_id"],
            "date_jour": sandbox["today"].isoformat(),
            "quart": "STANDARD",
            "poste_assigne": "Delete test",
        },
    )
    assert admin_resp.status_code == 201
    fin_pg_id = admin_resp.json()["id"]
    resp = wb_client.delete(
        f"/api/v1/departement/planning/{fin_pg_id}",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# 6. POST /presence/{id}/valider  validation emargement
# --------------------------------------------------------------------------- #
def test_chef_validates_presence(wb_client, sandbox):
    resp = wb_client.post(
        f"/api/v1/departement/presence/{sandbox['pointage_id']}/valider",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["est_valide"] is True
    assert data["valide_par_id"] is not None


def test_validate_presence_cross_dept_is_403(wb_client, sandbox):
    # Create a pointage for fin_a via direct DB, then try to validate as chef-ops.
    db = SessionLocal()
    try:
        pv = PointageVacation(
            company_id=db.query(Company).filter(Company.code == "MS-WB").first().id,
            employe_id=sandbox["fin_a_id"],
            date_pointage=sandbox["today"],
            heure_arrivee="08:00",
            est_valide=False,
        )
        db.add(pv)
        db.commit()
        db.refresh(pv)
        pv_id = pv.id
    finally:
        db.close()
    resp = wb_client.post(
        f"/api/v1/departement/presence/{pv_id}/valider",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 403


def test_validate_presence_not_found(wb_client, sandbox):
    resp = wb_client.post(
        "/api/v1/departement/presence/999999/valider",
        headers=_auth(sandbox["chef_token"]),
    )
    assert resp.status_code == 404

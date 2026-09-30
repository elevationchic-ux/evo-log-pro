"""Phase 4 Tranche C — Pointage automatique a la connexion + depart.

Couvre les utilitaires ``app.utils.pointage`` ET le bout-en-bout HTTP reel :
  - ``auto_pointage_arrivee`` : cree une PointageVacation a l'arrivee (niveau 3
    rattache a un departement), idempotent (pas de doublon le meme jour),
    calcule l'ecart/retard par rapport au quart planifie ;
  - ``pointer_depart`` : enregistre l'heure de depart + heures_effectives,
    400 si aucune arrivee le meme jour, idempotent si deja parti ;
  - POST /auth/login : greffe ``pointage_info`` sur la reponse de session ;
  - POST /auth/pointer-depart : exige l'authentification (401/403 sinon).

Aucun mock d'authorisation : JWT reels + middleware, conformement au reste du
plan. Les scenarios temporels (retard, duree) gellent ``datetime.now`` UNIQUEMENT
(le ``date.today()`` reste reel, aligne sur les lignes PlanningGarde/Pointage).
"""
from __future__ import annotations

from datetime import date as _date, datetime
from unittest.mock import patch

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
from app.utils.pointage import auto_pointage_arrivee, pointer_depart


# --------------------------------------------------------------------------- #
# Fixtures schema + session (fail-open : aucun contexte tenant pendant l'ecriture)
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module", autouse=True)
def _ensure_app_schema():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    yield
    clear_current_tenant()


@pytest.fixture
def db():
    clear_current_tenant()
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
        clear_current_tenant()


def _mk_user(db, level, *, company_id, department_id=None, username="u",
             password="Admin12345"):
    u = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=get_password_hash(password),
        is_active=True,
        is_superuser=(level == 0),
        role_level=level,
        company_id=company_id,
        department_id=department_id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _mk_company_dept(db, code):
    co = Company(nom=f"Co {code}", code=code, is_active=True,
                 modules_actives='["transport"]')
    db.add(co)
    db.commit()
    db.refresh(co)
    dep = Department(company_id=co.id, code=f"{code}-OPS", nom="Operations")
    db.add(dep)
    db.commit()
    db.refresh(dep)
    return co, dep


# --------------------------------------------------------------------------- #
# 1. auto_pointage_arrivee (unites pures, temps gelle)
# --------------------------------------------------------------------------- #
def test_auto_arrivee_creates_pointage_for_level3(db):
    co, dep = _mk_company_dept(db, "PA1")
    emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id, username="pa1-emp")
    with patch("app.utils.pointage.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 9, 29, 8, 0)
        info = auto_pointage_arrivee(db, emp)
    assert info is not None
    assert info["pointe"] is True
    assert info["deja_pointe"] is False
    assert info["heure_arrivee"] == "08:00"
    # Une seule ligne en base ce jour.
    rows = db.query(PointageVacation).filter(
        PointageVacation.employe_id == emp.id,
        PointageVacation.date_pointage == _date.today()).all()
    assert len(rows) == 1
    assert rows[0].company_id == co.id


def test_auto_arrivee_skips_non_level3_or_without_department(db):
    co, dep = _mk_company_dept(db, "PA2")
    chef = _mk_user(db, 2, company_id=co.id, department_id=dep.id, username="pa2-chef")
    float_user = _mk_user(db, 3, company_id=co.id, department_id=None, username="pa2-float")
    assert auto_pointage_arrivee(db, chef) is None         # niveau 2 -> non concerne
    assert auto_pointage_arrivee(db, float_user) is None    # pas de departement
    assert db.query(PointageVacation).filter(
        PointageVacation.employe_id.in_([chef.id, float_user.id])).count() == 0


def test_auto_arrivee_is_idempotent_same_day(db):
    co, dep = _mk_company_dept(db, "PA3")
    emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id, username="pa3-emp")
    with patch("app.utils.pointage.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 9, 29, 7, 30)
        first = auto_pointage_arrivee(db, emp)
        mock_dt.now.return_value = datetime(2026, 9, 29, 9, 15)
        second = auto_pointage_arrivee(db, emp)
    assert first["deja_pointe"] is False
    assert second["deja_pointe"] is True
    # L'heure de la premiere arrivee est conservee (pas d'ecrasement).
    assert second["heure_arrivee"] == "07:30"
    assert db.query(PointageVacation).filter(
        PointageVacation.employe_id == emp.id).count() == 1


def test_auto_arrivee_computes_retard_from_quart(db):
    co, dep = _mk_company_dept(db, "PA4")
    emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id, username="pa4-emp")
    # Quart MATIN (06:00). Arrivee 07:45 -> ecart 105 min, retard.
    db.add(PlanningGarde(company_id=co.id, employe_id=emp.id,
                         date_jour=_date.today(), quart="MATIN",
                         poste_assigne="Quai", statut="CONFIRME"))
    db.commit()
    with patch("app.utils.pointage.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 9, 29, 7, 45)
        info = auto_pointage_arrivee(db, emp)
    assert info["ecart_minutes"] == 105
    assert info["retard"] is True


def test_auto_arrivee_toelerance_retard_5_min(db):
    co, dep = _mk_company_dept(db, "PA5")
    emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id, username="pa5-emp")
    db.add(PlanningGarde(company_id=co.id, employe_id=emp.id,
                         date_jour=_date.today(), quart="STANDARD",  # 08:00
                         poste_assigne="Bureau", statut="CONFIRME"))
    db.commit()
    with patch("app.utils.pointage.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 9, 29, 8, 4)  # +4 min
        info = auto_pointage_arrivee(db, emp)
    assert info["ecart_minutes"] == 4
    assert info["retard"] is False


# --------------------------------------------------------------------------- #
# 2. pointer_depart
# --------------------------------------------------------------------------- #
def test_depart_computes_heures_effectives(db):
    co, dep = _mk_company_dept(db, "PD1")
    emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id, username="pd1-emp")
    with patch("app.utils.pointage.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 9, 29, 8, 0)
        auto_pointage_arrivee(db, emp)
        mock_dt.now.return_value = datetime(2026, 9, 29, 16, 30)
        res = pointer_depart(db, emp)
    assert res["heure_arrivee"] == "08:00"
    assert res["heure_depart"] == "16:30"
    assert res["heures_effectives"] == 8.5


def test_depart_nuit_passe_minuit(db):
    co, dep = _mk_company_dept(db, "PD2")
    emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id, username="pd2-emp")
    with patch("app.utils.pointage.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 9, 29, 22, 0)
        auto_pointage_arrivee(db, emp)
        mock_dt.now.return_value = datetime(2026, 9, 29, 6, 0)  # lendemain (heuristique)
        res = pointer_depart(db, emp)
    # 06:00 - 22:00 = -16h -> +24h = 8h.
    assert res["heures_effectives"] == 8.0


def test_depart_without_arrivee_is_400(db):
    co, dep = _mk_company_dept(db, "PD3")
    emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id, username="pd3-emp")
    with pytest.raises(HTTPException) as exc:
        pointer_depart(db, emp)
    assert exc.value.status_code == 400


def test_depart_is_idempotent(db):
    co, dep = _mk_company_dept(db, "PD4")
    emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id, username="pd4-emp")
    with patch("app.utils.pointage.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 9, 29, 8, 0)
        auto_pointage_arrivee(db, emp)
        mock_dt.now.return_value = datetime(2026, 9, 29, 15, 0)
        first = pointer_depart(db, emp)
        mock_dt.now.return_value = datetime(2026, 9, 29, 20, 0)  # ignore
        second = pointer_depart(db, emp)
    assert first["heure_depart"] == "15:00"
    assert second["heure_depart"] == "15:00"  # non ecrase
    assert second["heures_effectives"] == 7.0


# --------------------------------------------------------------------------- #
# 3. Bout-en-bout HTTP reel (login + pointer-depart)
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def http_client():
    Base.metadata.create_all(bind=engine)
    clear_current_tenant()
    with TestClient(app.main.app) as c:
        yield c
    clear_current_tenant()


def test_login_attaches_pointage_info(http_client):
    db = SessionLocal()
    try:
        co, dep = _mk_company_dept(db, "HL1")
        _mk_user(db, 3, company_id=co.id, department_id=dep.id,
                 username="hl1-emp", password="Admin12345")
    finally:
        db.close()
    resp = http_client.post("/api/v1/auth/login",
                            json={"username": "hl1-emp", "password": "Admin12345"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "pointage_info" in data
    assert data["pointage_info"]["pointe"] is True
    # La pointe existe reellement en base.
    db = SessionLocal()
    try:
        assert db.query(PointageVacation).join(User).filter(
            User.username == "hl1-emp",
            PointageVacation.date_pointage == _date.today()).count() == 1
    finally:
        db.close()


def test_pointer_depart_requires_auth(http_client):
    resp = http_client.post("/api/v1/auth/pointer-depart")
    assert resp.status_code in (401, 403)


def test_pointer_depart_records_for_authenticated_user(http_client):
    # On amorce la journee via login (arrivee auto), puis on pointe le depart.
    db = SessionLocal()
    try:
        co, dep = _mk_company_dept(db, "HL2")
        emp = _mk_user(db, 3, company_id=co.id, department_id=dep.id,
                       username="hl2-emp", password="Admin12345")
        emp_id = emp.id
    finally:
        db.close()
    login = http_client.post("/api/v1/auth/login",
                             json={"username": "hl2-emp", "password": "Admin12345"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    resp = http_client.post("/api/v1/auth/pointer-depart",
                            headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["heure_depart"] is not None
    assert body["id"] is not None

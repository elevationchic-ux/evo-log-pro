"""Tests Phase 3  Arbitrage CADC des demandes d'accreditation.

Boucle fermee sur la Phase 2 : l'admin entreprise emet une demande
(Accreditation statut 'demande'), le Super Admin CADC l'arbitre :

  * APPROUVER : conversion EN PLACE (pas de doublon), statut actif, dates
    tamponnees, octroye_par = arbitre, droit effectif immediat pour le porteur
    de la demande, et l'ecran entreprise bascule le module en 'accredite' ;
  * REFUSER : statut 'refuse' (trace preservee), retire de la file CADC et de
    la liste des demandes de l'entreprise, et libere le droit de redemander ;
  * invisibilite totale de la file et des decisions pour un admin entreprise
    ou un simple utilisateur (403, garde require_superadmin du routeur) ;
  * idempotence : une demande traitee ne peut pas etre re-arbitree (400).
"""
from datetime import date, timedelta

import pytest

from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.accreditation import Accreditation
from app.models.tenant import Company
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


def _emit_demande(client, company_admin, module="comptabilite"):
    """Phase 2 : l'admin entreprise emet une demande, retourne son id."""
    _as(company_admin)
    resp = client.post("/api/v1/company-admin/modules/demandes", json={"module": module})
    assert resp.status_code == 201
    return resp.json()["id"]


# --------------------------------------------------------------------------- #
# 3.1 approbation : conversion en place, droit effectif
# --------------------------------------------------------------------------- #
def test_approve_converts_demande_in_place(client, db, superadmin, company_admin, company):
    req_id = _emit_demande(client, company_admin)
    _as(superadmin)
    fin = (date.today() + timedelta(days=90)).isoformat()
    resp = client.post(
        f"/api/v1/saas/console/accreditations/demandes/{req_id}/approuver",
        json={"date_debut": date.today().isoformat(), "date_fin": fin},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == req_id          # MEME ligne : conversion en place
    assert body["statut"] == "actif"
    assert body["valide"] is True
    assert body["octroye_par"] == superadmin.id
    assert str(body["date_fin"]) == fin

    # Pas de doublon : une seule ligne pour ce module dans cette entreprise.
    rows = (
        db.query(Accreditation)
        .filter(Accreditation.company_id == company.id, Accreditation.module == "comptabilite")
        .all()
    )
    assert len(rows) == 1

    # La file CADC ne contient plus la demande arbitree.
    queue = client.get("/api/v1/saas/console/accreditations/demandes").json()
    assert not any(r["id"] == req_id for r in queue)
    _clear()


def test_approve_grants_effective_permission_to_requester(client, db, superadmin, company_admin):
    from app.core.permissions import load_effective_permissions, has_perm
    req_id = _emit_demande(client, company_admin)
    _as(superadmin)
    assert client.post(
        f"/api/v1/saas/console/accreditations/demandes/{req_id}/approuver", json={}
    ).status_code == 200

    db.refresh(company_admin)
    codes = load_effective_permissions(company_admin)
    assert has_perm(codes, "comptabilite.journal.read") is True
    _clear()


def test_approve_flips_company_overview_to_accredite(client, db, superadmin, company_admin):
    req_id = _emit_demande(client, company_admin)
    _as(superadmin)
    client.post(f"/api/v1/saas/console/accreditations/demandes/{req_id}/approuver", json={})

    _as(company_admin)
    data = client.get("/api/v1/company-admin/modules").json()
    etats = {m["key"]: m["etat"] for m in data["modules"]}
    assert etats.get("comptabilite") == "accredite"
    assert data["demandes"] == []
    _clear()


def test_approve_rejects_inverted_dates(client, db, superadmin, company_admin):
    req_id = _emit_demande(client, company_admin)
    _as(superadmin)
    resp = client.post(
        f"/api/v1/saas/console/accreditations/demandes/{req_id}/approuver",
        json={"date_debut": "2026-09-25", "date_fin": "2026-09-01"},
    )
    assert resp.status_code == 400
    _clear()


def test_approve_unknown_or_processed_request(client, db, superadmin, company_admin):
    req_id = _emit_demande(client, company_admin)
    _as(superadmin)
    assert client.post(
        "/api/v1/saas/console/accreditations/demandes/999999/approuver", json={}
    ).status_code == 404
    assert client.post(
        f"/api/v1/saas/console/accreditations/demandes/{req_id}/approuver", json={}
    ).status_code == 200
    # Idempotence : re-arbitrer une demande traitee est refusé.
    again = client.post(f"/api/v1/saas/console/accreditations/demandes/{req_id}/approuver", json={})
    assert again.status_code == 400
    _clear()


# --------------------------------------------------------------------------- #
# 3.2 refus : trace preservee, file vide, redemande possible
# --------------------------------------------------------------------------- #
def test_reject_marks_refuse_and_clears_queue(client, db, superadmin, company_admin, company):
    req_id = _emit_demande(client, company_admin)
    _as(superadmin)
    resp = client.post(
        f"/api/v1/saas/console/accreditations/demandes/{req_id}/refuser",
        json={"motif": "Hors forfait du plan en cours"},
    )
    assert resp.status_code == 200
    assert resp.json()["statut"] == "refuse"
    assert resp.json()["valide"] is False

    # Trace preservee (pas de suppression) avec le motif de l'arbitre.
    row = db.query(Accreditation).filter(Accreditation.id == req_id).first()
    assert row is not None and row.statut == "refuse"
    assert row.motif == "Hors forfait du plan en cours"

    queue = client.get("/api/v1/saas/console/accreditations/demandes").json()
    assert not any(r["id"] == req_id for r in queue)
    _clear()


def test_reject_returns_module_to_locked_and_allows_rerequest(client, db, superadmin, company_admin):
    req_id = _emit_demande(client, company_admin)
    _as(superadmin)
    client.post(f"/api/v1/saas/console/accreditations/demandes/{req_id}/refuser", json={})

    _as(company_admin)
    data = client.get("/api/v1/company-admin/modules").json()
    etats = {m["key"]: m["etat"] for m in data["modules"]}
    assert etats.get("comptabilite") == "verrouille"
    assert data["demandes"] == []

    # Le refus libere le verrou anti-doublon : l'admin peut redemander.
    again = client.post("/api/v1/company-admin/modules/demandes", json={"module": "comptabilite"})
    assert again.status_code == 201
    _clear()


def test_refused_accreditation_grants_nothing(client, db, superadmin, company_admin):
    from app.core.permissions import load_effective_permissions, has_perm
    req_id = _emit_demande(client, company_admin)
    _as(superadmin)
    client.post(f"/api/v1/saas/console/accreditations/demandes/{req_id}/refuser", json={})
    db.refresh(company_admin)
    codes = load_effective_permissions(company_admin)
    assert has_perm(codes, "comptabilite.journal.read") is False
    _clear()


# --------------------------------------------------------------------------- #
# 3.3 invisibilite : file et decisions reservees au Super Admin CADC
# --------------------------------------------------------------------------- #
def test_demande_queue_invisible_to_company_admin(client, db, company_admin):
    _as(company_admin)
    assert client.get("/api/v1/saas/console/accreditations/demandes").status_code == 403
    _clear()


def test_decisions_forbidden_for_company_admin_and_plain_user(
    client, db, superadmin, company_admin, plain_user
):
    req_id = _emit_demande(client, company_admin)
    _as(company_admin)
    assert client.post(
        f"/api/v1/saas/console/accreditations/demandes/{req_id}/approuver", json={}
    ).status_code == 403
    assert client.post(
        f"/api/v1/saas/console/accreditations/demandes/{req_id}/refuser", json={}
    ).status_code == 403
    _as(plain_user)
    assert client.post(
        f"/api/v1/saas/console/accreditations/demandes/{req_id}/approuver", json={}
    ).status_code == 403
    # Rien n'a bouge : la demande est toujours en attente.
    _as(superadmin)
    queue = client.get("/api/v1/saas/console/accreditations/demandes").json()
    assert any(r["id"] == req_id for r in queue)
    _clear()

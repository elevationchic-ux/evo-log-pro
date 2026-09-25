"""Integration tests Tranche B : parc (zones/emplacements/gate) + purchase
(requisitions avec workflow d'approbation).

Anti-regression : ces routes repondent pending=False (donnees reelles) au lieu
du fallback pending-modules.
"""
import pytest

from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.user import User


@pytest.fixture
def user(db):
    u = User(
        username="acheteur", email="acheteur@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=False, role_level=2, company_id=None,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def authed(client, user):
    app.dependency_overrides[get_current_user] = lambda: user
    yield client
    app.dependency_overrides.clear()


# --------------------------------------------------------------------------- #
# Zones / emplacements
# --------------------------------------------------------------------------- #

def test_zone_crud_cycle(client):
    created = client.post(
        "/api/v1/parc/zones",
        json={"code": "Z1", "nom": "Zone chaude", "type_zone": "refrigerie", "capacite": 40},
    )
    assert created.status_code == 201
    zone = created.json()
    assert zone["statut"] == "active"

    lst = client.get("/api/v1/parc/zones").json()
    assert lst["pending"] is False
    assert lst["total"] == 1

    assert client.get(f"/api/v1/parc/zones/{zone['id']}").status_code == 200
    upd = client.put(f"/api/v1/parc/zones/{zone['id']}", json={"statut": "maintenance"})
    assert upd.json()["statut"] == "maintenance"
    assert client.delete(f"/api/v1/parc/zones/{zone['id']}").status_code == 204
    assert client.get("/api/v1/parc/zones/9999").status_code == 404


def test_emplacement_crud_and_zone_filter(client):
    zone = client.post("/api/v1/parc/zones", json={"code": "Z2", "nom": "Zone quai"}).json()
    e1 = client.post(
        "/api/v1/parc/emplacements",
        json={"code": "E-01", "zone_id": zone["id"], "type_emplacement": "sol"},
    )
    assert e1.status_code == 201
    assert e1.json()["statut"] == "libre"
    client.post("/api/v1/parc/emplacements", json={"code": "E-02"})  # sans zone

    all_e = client.get("/api/v1/parc/emplacements").json()
    assert all_e["total"] == 2
    by_zone = client.get("/api/v1/parc/emplacements", params={"zone_id": zone["id"]}).json()
    assert by_zone["total"] == 1

    # zone inexistante au create -> 400
    bad = client.post("/api/v1/parc/emplacements", json={"code": "E-X", "zone_id": 9999})
    assert bad.status_code == 400


# --------------------------------------------------------------------------- #
# Gate in / gate out
# --------------------------------------------------------------------------- #

def test_gate_in_out_marks_emplacement(client):
    empl = client.post("/api/v1/parc/emplacements", json={"code": "E-G"}).json()

    gin = client.post(
        "/api/v1/parc/gate-in",
        json={
            "numero_conteneur": "MSKU1234567",
            "type_conteneur": "20DRY",
            "etat": "BON_ETAT",
            "poids_tare_kg": 2200,
            "emplacement_id": empl["id"],
        },
    )
    assert gin.status_code == 201
    assert gin.json()["sens"] == "entree"
    assert client.get(f"/api/v1/parc/emplacements/{empl['id']}").json()["statut"] == "occupe"

    gout = client.post(
        "/api/v1/parc/gate-out",
        json={"numero_conteneur": "MSKU1234567", "emplacement_id": empl["id"]},
    )
    assert gout.status_code == 201
    assert gout.json()["sens"] == "sortie"
    after = client.get(f"/api/v1/parc/emplacements/{empl['id']}").json()
    assert after["statut"] == "libre"

    mvts = client.get("/api/v1/parc/mouvements").json()
    assert mvts["total"] == 2
    entrees = client.get("/api/v1/parc/mouvements", params={"sens": "entree"}).json()
    assert entrees["total"] == 1

    # emplacement inconnu -> 400
    bad = client.post("/api/v1/parc/gate-in", json={"emplacement_id": 9999})
    assert bad.status_code == 400


# --------------------------------------------------------------------------- #
# Requisitions (workflow, protegees par auth comme le routeur purchase)
# --------------------------------------------------------------------------- #

def _create_requisition(authed, **over):
    return authed.post(
        "/api/v1/purchase/requisitions/",
        json={"designation": "Palettes bois", "quantite": 50, "prix_estime": 12500.0, **over},
    )


def test_requisition_requires_auth(client):
    assert client.get("/api/v1/purchase/requisitions").status_code in (401, 403)


def test_requisition_workflow(authed):
    created = _create_requisition(authed)
    assert created.status_code == 201
    req = created.json()
    assert req["statut"] == "brouillon"
    assert req["reference"].startswith("DA-")
    assert req["demandeur"] == "acheteur"  # herite de l'utilisateur connecté

    rid = req["id"]
    # modification possible seulement en brouillon
    upd = authed.put(f"/api/v1/purchase/requisitions/{rid}", json={"quantite": 60})
    assert upd.status_code == 200
    assert upd.json()["quantite"] == 60

    # soumission
    sub = authed.post(f"/api/v1/purchase/requisitions/{rid}/submit")
    assert sub.status_code == 200
    assert sub.json()["statut"] == "soumise"
    # plus modifiable une fois soumise
    assert authed.put(f"/api/v1/purchase/requisitions/{rid}", json={"quantite": 7}).status_code == 400
    # double soumission refusee
    assert authed.post(f"/api/v1/purchase/requisitions/{rid}/submit").status_code == 400

    # approbation avec notes
    ok = authed.post(
        f"/api/v1/purchase/requisitions/{rid}/approve",
        json={"notes_approbation": "Budget OK"},
    )
    assert ok.status_code == 200
    body = ok.json()
    assert body["statut"] == "approuvee"
    assert body["notes_approbation"] == "Budget OK"
    assert body["approuve_par"] is not None
    # decision deja prise -> refusee
    assert authed.post(f"/api/v1/purchase/requisitions/{rid}/reject").status_code == 400


def test_requisition_reject_and_filters(authed):
    req = _create_requisition(authed).json()
    rid = req["id"]
    authed.post(f"/api/v1/purchase/requisitions/{rid}/submit")
    rej = authed.post(
        f"/api/v1/purchase/requisitions/{rid}/reject",
        json={"notes_approbation": "Trop cher"},
    )
    assert rej.json()["statut"] == "rejetee"

    # une rejetee est supprimable (logique), pas une approuvee engagee
    assert authed.delete(f"/api/v1/purchase/requisitions/{rid}").status_code == 204

    lst = authed.get("/api/v1/purchase/requisitions/", params={"statut": "soumise"}).json()
    assert lst["pending"] is False
    assert lst["total"] == 0

    assert authed.get("/api/v1/purchase/requisitions/9999").status_code == 404


# --------------------------------------------------------------------------- #
# Anti-regression catch-all
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("path", [
    "/api/v1/parc/zones",
    "/api/v1/parc/emplacements",
])
def test_b_parc_routes_real_not_pending(client, path):
    body = client.get(path).json()
    assert body.get("pending") is False, f"{path} sert encore le fallback pending"


def test_b_requisition_route_real_not_pending(authed):
    body = authed.get("/api/v1/purchase/requisitions").json()
    assert body.get("pending") is False

"""Integration tests Tranche C : fleet, customers CRM, support."""
import pytest


# --------------------------------------------------------------------------- #
# Fleet (proxy Vehicule + carburant + documents)
# --------------------------------------------------------------------------- #

def test_fleet_vehicle_crud(client):
    created = client.post(
        "/api/v1/fleet/vehicles",
        json={"immatriculation": "LT-TR-8945", "marque": "Mercedes", "modele": "Actros", "type_vehicule": "camion"},
    )
    assert created.status_code == 201
    veh = created.json()
    assert veh["status"] == "disponible"

    # immatriculation unique
    dup = client.post("/api/v1/fleet/vehicles", json={"immatriculation": "LT-TR-8945", "marque": "X"})
    assert dup.status_code == 400

    lst = client.get("/api/v1/fleet/vehicles").json()
    assert lst["pending"] is False
    assert lst["total"] == 1

    search = client.get("/api/v1/fleet/vehicles", params={"search": "8945"}).json()
    assert search["total"] == 1

    upd = client.put(f"/api/v1/fleet/vehicles/{veh['id']}", json={"status": "en_maintenance", "kilometrage": 120000})
    assert upd.status_code == 200
    assert upd.json()["status"] == "en_maintenance"

    assert client.get("/api/v1/fleet/vehicles/9999").status_code == 404
    assert client.delete(f"/api/v1/fleet/vehicles/{veh['id']}").status_code == 204


def test_fleet_fuel_records(client):
    veh = client.post("/api/v1/fleet/vehicles", json={"immatriculation": "FU-0001", "marque": "Iveco"}).json()
    rec = client.post(
        "/api/v1/fleet/fuel-records",
        json={"vehicule_id": veh["id"], "litres": 120.5, "cout": 115000, "station": "Total Kribi"},
    )
    assert rec.status_code == 201
    body = rec.json()
    assert body["immatriculation"] == "FU-0001"  # enrichi depuis le vehicule

    # vehicule inconnu -> 400
    bad = client.post("/api/v1/fleet/fuel-records", json={"vehicule_id": 9999, "litres": 10})
    assert bad.status_code == 400

    lst = client.get("/api/v1/fleet/fuel-records", params={"vehicule_id": veh["id"]}).json()
    assert lst["pending"] is False
    assert lst["total"] == 1


def test_fleet_documents_form_upload(client):
    veh = client.post("/api/v1/fleet/vehicles", json={"immatriculation": "DOC-0001", "marque": "Renault"}).json()
    uploaded = client.post(
        "/api/v1/fleet/documents",
        data={"vehicule_id": veh["id"], "type_document": "carte_grise", "date_expiration": "2027-01-15T00:00:00"},
        files={"file": ("carte_grise.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert uploaded.status_code == 201
    doc = uploaded.json()
    assert doc["nom_fichier"] == "carte_grise.pdf"
    assert doc["date_expiration"].startswith("2027-01-15")

    lst = client.get("/api/v1/fleet/documents", params={"vehicle_id": veh["id"]}).json()
    assert lst["total"] == 1


# --------------------------------------------------------------------------- #
# Customers CRM
# --------------------------------------------------------------------------- #

def test_customer_crud_cycle(client):
    created = client.post(
        "/api/v1/customers",
        json={"name": "Geocam SARL", "city": "Douala", "segment": "pme"},
    )
    assert created.status_code == 201
    cust = created.json()
    assert cust["code"].startswith("CUS-")
    assert cust["country"] == "Cameroun"

    lst = client.get("/api/v1/customers").json()
    assert lst["pending"] is False
    assert lst["total"] == 1

    upd = client.put(f"/api/v1/customers/{cust['id']}", json={"segment": "grand_compte"})
    assert upd.json()["segment"] == "grand_compte"
    assert client.get("/api/v1/customers/9999").status_code == 404
    assert client.delete(f"/api/v1/customers/{cust['id']}").status_code == 204


def test_customer_contracts(client):
    # /contracts n'est jamais capture par /{customer_id}
    empty = client.get("/api/v1/customers/contracts").json()
    assert empty["pending"] is False
    assert empty["items"] == []

    cust = client.post("/api/v1/customers", json={"name": "HCB"}).json()
    c1 = client.post(
        "/api/v1/customers/contracts",
        json={"customer_id": cust["id"], "objet": "Acconage 2026", "type_contrat": "cadre", "montant": 5000000},
    )
    assert c1.status_code == 201
    assert c1.json()["reference"].startswith("CTR-")
    assert c1.json()["statut"] == "actif"

    # client inexistant -> 400
    bad = client.post("/api/v1/customers/contracts", json={"customer_id": 9999, "objet": "x"})
    assert bad.status_code == 400

    lst = client.get("/api/v1/customers/contracts", params={"customer_id": cust["id"]}).json()
    assert lst["total"] == 1


# --------------------------------------------------------------------------- #
# Support
# --------------------------------------------------------------------------- #

def test_support_ticket_cycle(client):
    created = client.post(
        "/api/v1/support/tickets",
        json={
            "sujet": "Erreur lors de l'edition du B/L TR-2026-0042",
            "categorie": "douane",
            "priorite": "haute",
            "description": "Le bouton enregistrer renvoie une erreur 500",
        },
    )
    assert created.status_code == 201
    tkt = created.json()
    assert tkt["reference"].startswith("TKT-")
    assert tkt["statut"] == "ouvert"

    lst = client.get("/api/v1/support/tickets").json()
    assert lst["pending"] is False
    assert lst["total"] == 1

    # sujet requis
    assert client.post("/api/v1/support/tickets", json={"priorite": "basse"}).status_code == 422


def test_support_incident_cycle(client):
    created = client.post(
        "/api/v1/support/incidents",
        json={"titre": "Panne portique 3", "type": "materiel", "priorite": "urgente"},
    )
    assert created.status_code == 201
    inc = created.json()
    assert inc["reference"].startswith("INC-")

    upd = client.put(f"/api/v1/support/incidents/{inc['id']}", json={"statut": "resolu"})
    assert upd.status_code == 200
    assert upd.json()["statut"] == "resolu"
    assert upd.json()["resolved_at"] is not None  # horodatage automatique

    filtres = client.get("/api/v1/support/incidents", params={"statut": "resolu"}).json()
    assert filtres["total"] == 1
    assert client.put("/api/v1/support/incidents/9999", json={"statut": "ferme"}).status_code == 404


# --------------------------------------------------------------------------- #
# Anti-regression catch-all + rewrite legacy /api/
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("path", [
    "/api/v1/fleet/vehicles",
    "/api/v1/fleet/fuel-records",
    "/api/v1/fleet/documents",
    "/api/v1/customers",
    "/api/v1/customers/contracts",
    "/api/v1/support/tickets",
    "/api/v1/support/incidents",
])
def test_c_routes_real_not_pending(client, path):
    body = client.get(path).json()
    assert body.get("pending") is False, f"{path} sert encore le fallback pending"


def test_c_legacy_prefix_rewrite_hits_real_route(client):
    """Les pages appellent /api/v1/... ; d'anciennes /api/... sont reecrites
    vers /api/v1/... par le middleware et touchent bien la route reelle."""
    body = client.get("/api/support/tickets").json()
    assert body.get("pending") is False

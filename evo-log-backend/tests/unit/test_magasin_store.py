"""Integration tests for the Magasin store domain (Tranche A).

Covers the real DB-backed endpoints mounted on /api/v1/magasin :
  * articles            (CRUD + code unique + suppression logique)
  * clients             (proxy sur le modele Tiers/Client)
  * commandes           (+ lignes imbriquees, machine a etats, annulation)
  * ordres-transfert    (machine a etats complete)
  * bandes-livraison    (CRUD + derivation depuis un ordre de transfert)

Regle anti-regression : ces routes reponnent avec pending=False ( vraies donnees )
et non plus via le fallback pending-modules.
"""
import pytest


# --------------------------------------------------------------------------- #
# Articles
# --------------------------------------------------------------------------- #

def _create_article(client, code="ART-001", **overrides):
    payload = {
        "code": code,
        "designation": "Ciment CP 50kg",
        "categorie": "materiaux",
        "prix_unitaire": 4500.0,
        "unite_mesure": "SAC",
        **overrides,
    }
    return client.post("/api/v1/magasin/articles", json=payload)


def test_article_crud_cycle(client):
    created = _create_article(client)
    assert created.status_code == 201
    art = created.json()
    assert art["code"] == "ART-001"
    assert art["prix_unitaire"] == 4500.0

    # code en double -> 400
    dup = _create_article(client)
    assert dup.status_code == 400

    # liste reelle (pending=False), pas le fallback
    lst = client.get("/api/v1/magasin/articles").json()
    assert lst["pending"] is False
    assert lst["total"] == 1

    # recherche
    found = client.get("/api/v1/magasin/articles", params={"search": "ciment"}).json()
    assert found["total"] == 1
    missing = client.get("/api/v1/magasin/articles", params={"search": "acier"}).json()
    assert missing["total"] == 0

    # by-code / by-id
    by_code = client.get("/api/v1/magasin/articles/by-code/ART-001")
    assert by_code.status_code == 200
    assert by_code.json()["id"] == art["id"]
    assert client.get(f"/api/v1/magasin/articles/{art['id']}").status_code == 200

    # update
    upd = client.put(
        f"/api/v1/magasin/articles/{art['id']}",
        json={"designation": "Ciment CPA 45", "prix_unitaire": 4800.0},
    )
    assert upd.status_code == 200
    assert upd.json()["designation"] == "Ciment CPA 45"
    assert upd.json()["prix_unitaire"] == 4800.0

    # suppression logique : 204, l'article reste actif en base mais inerte
    assert client.delete(f"/api/v1/magasin/articles/{art['id']}").status_code == 204


def test_article_404(client):
    assert client.get("/api/v1/magasin/articles/9999").status_code == 404
    assert client.get("/api/v1/magasin/articles/by-code/NOPE").status_code == 404


# --------------------------------------------------------------------------- #
# Clients (proxy Tiers)
# --------------------------------------------------------------------------- #

def test_client_crud_cycle(client):
    created = client.post(
        "/api/v1/magasin/clients",
        json={"name": "EBM Douala", "email": "contact@ebm.cm", "city": "Douala"},
    )
    assert created.status_code == 201
    cli = created.json()
    assert cli["name"] == "EBM Douala"
    assert cli["code"].startswith("CLI-")  # code auto-genere

    lst = client.get("/api/v1/magasin/clients").json()
    assert lst["pending"] is False
    assert lst["total"] == 1

    upd = client.put(f"/api/v1/magasin/clients/{cli['id']}", json={"city": "Yaounde"})
    assert upd.status_code == 200
    assert upd.json()["city"] == "Yaounde"

    assert client.delete(f"/api/v1/magasin/clients/{cli['id']}").status_code == 204
    assert client.get("/api/v1/magasin/clients/9999").status_code == 404


# --------------------------------------------------------------------------- #
# Commandes + machine a etats
# --------------------------------------------------------------------------- #

def _create_commande(client):
    return client.post(
        "/api/v1/magasin/commandes",
        json={
            "type_commande": "sortie",
            "montant_total": 9000.0,
            "lignes": [
                {"designation": "Ciment CP 50kg", "quantite": 2, "prix_unitaire": 4500.0, "montant": 9000.0},
            ],
        },
    )


def test_commande_lifecycle(client):
    created = _create_commande(client)
    assert created.status_code == 201
    cmd = created.json()
    assert cmd["statut"] == "brouillon"
    assert cmd["reference"].startswith("CMD-")
    assert len(cmd["lignes"]) == 1
    assert cmd["lignes"][0]["quantite"] == 2

    cid = cmd["id"]
    steps = [
        ("/valider", "validee"),
        ("/preparer", "en_preparation"),
        ("/valider-paiement", "prete"),
    ]
    for action, expected in steps:
        r = client.post(f"/api/v1/magasin/commandes/{cid}{action}")
        assert r.status_code == 200, action
        assert r.json()["statut"] == expected

    # annulation, puis transition refusee
    ann = client.post(f"/api/v1/magasin/commandes/{cid}/annuler")
    assert ann.status_code == 200
    assert ann.json()["statut"] == "annulee"
    blocked = client.post(f"/api/v1/magasin/commandes/{cid}/valider")
    assert blocked.status_code == 400


def test_commande_filtrage_statut(client):
    _create_commande(client)
    ok_brouillon = client.get("/api/v1/magasin/commandes", params={"statut": "brouillon"}).json()
    assert ok_brouillon["total"] == 1
    ok_validee = client.get("/api/v1/magasin/commandes", params={"statut": "validee"}).json()
    assert ok_validee["total"] == 0
    assert client.get("/api/v1/magasin/commandes/9999").status_code == 404


# --------------------------------------------------------------------------- #
# Ordres de transfert + machine a etats
# --------------------------------------------------------------------------- #

def _create_ot(client):
    return client.post(
        "/api/v1/magasin/ordres-transfert",
        json={"quantite": 50, "motif": "Reappro Magasin 2", "montant_paiement": 25000.0},
    )


def test_ordre_transfert_lifecycle(client):
    created = _create_ot(client)
    assert created.status_code == 201
    ot = created.json()
    assert ot["statut"] == "brouillon"
    assert ot["reference"].startswith("OT-")

    otid = ot["id"]
    for action, expected in [
        ("/valider", "valide"),
        ("/valider-paiement", "paye"),
        ("/expedier", "expedie"),
        ("/receptionner", "receptionne"),
    ]:
        r = client.post(f"/api/v1/magasin/ordres-transfert/{otid}{action}")
        assert r.status_code == 200, action
        assert r.json()["statut"] == expected

    lst = client.get("/api/v1/magasin/ordres-transfert").json()
    assert lst["pending"] is False
    assert lst["total"] == 1


def test_ordre_transfert_annule_blocking(client):
    ot = _create_ot(client).json()
    ann = client.post(f"/api/v1/magasin/ordres-transfert/{ot['id']}/annuler")
    assert ann.json()["statut"] == "annule"
    blocked = client.post(f"/api/v1/magasin/ordres-transfert/{ot['id']}/valider")
    assert blocked.status_code == 400


# --------------------------------------------------------------------------- #
# Bandes de livraison
# --------------------------------------------------------------------------- #

def test_bande_livraison_cycle(client):
    created = client.post(
        "/api/v1/magasin/bandes-livraison",
        json={"nb_colis": 12, "poids_total": 500.0, "notes": "Fragile"},
    )
    assert created.status_code == 201
    bl = created.json()
    assert bl["reference"].startswith("BL-")
    assert bl["statut"] == "en_preparation"
    assert bl["date_preparation"] is not None

    upd = client.put(
        f"/api/v1/magasin/bandes-livraison/{bl['id']}",
        json={"statut": "livree", "nb_colis": 11},
    )
    assert upd.status_code == 200
    assert upd.json()["statut"] == "livree"
    assert upd.json()["nb_colis"] == 11


def test_bande_livraison_depuis_ordre_transfert(client):
    ot = _create_ot(client).json()
    derived = client.post(f"/api/v1/magasin/bandes-livraison/from-ordre-transfert/{ot['id']}")
    assert derived.status_code == 201
    bl = derived.json()
    assert bl["ordre_transfert_id"] == ot["id"]
    assert bl["poids_total"] == ot["quantite"]

    by_ot = client.get(f"/api/v1/magasin/bandes-livraison/ordre-transfert/{ot['id']}")
    assert by_ot.status_code == 200
    assert len(by_ot.json()) == 1

    # OT inexistant -> 404 (et non le fallback pending)
    assert client.post("/api/v1/magasin/bandes-livraison/from-ordre-transfert/9999").status_code == 404


# --------------------------------------------------------------------------- #
# Anti-regression : les routes reelles ne tombent plus dans le catch-all
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("path", [
    "articles",
    "clients",
    "commandes",
    "ordres-transfert",
    "bandes-livraison",
])
def test_store_routes_are_real_not_pending(client, path):
    resp = client.get(f"/api/v1/magasin/{path}")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("pending") is False, f"/api/v1/magasin/{path} sert encore le fallback pending"

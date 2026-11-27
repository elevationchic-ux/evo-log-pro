"""Tests des endpoints /api/v1/metier : forme de reponse et refus honnete."""
import pytest


@pytest.mark.parametrize("path", [
    "/api/v1/metier/paie/cumuls",
    "/api/v1/metier/rentabilite",
    "/api/v1/metier/indicateurs-financiers",
    "/api/v1/metier/qhse/depassements",
    "/api/v1/metier/compta/controle-budgetaire",
    "/api/v1/metier/finance/previsions",
    "/api/v1/metier/finance/affacturage",
    "/api/v1/metier/magasin/ecarts",
    "/api/v1/metier/transport/tournees",
    "/api/v1/metier/dashboard/sante",
    "/api/v1/metier/organisation/abonnements",
    "/api/v1/metier/rh/formation",
    "/api/v1/metier/frais/tva-recuperable",
    "/api/v1/metier/frais/avances",
    "/api/v1/metier/commercial/pipeline",
    "/api/v1/metier/support/stats",
    "/api/v1/metier/qhse/quasi-accidents",
    "/api/v1/metier/parc/pneus-a-remplacer",
    "/api/v1/metier/transit/conformite",
])
def test_endpoint_metier_200(client, path):
    """Chaque endpoint de lecture repond 200 avec un dict JSON."""
    resp = client.get(path)
    assert resp.status_code == 200, f"{path}: {resp.status_code} {resp.text[:200]}"
    body = resp.json()
    assert isinstance(body, dict)


def test_paie_bulletin_absent_honnete(client):
    """Bulletin inexistant : note honnete, pas de crash."""
    resp = client.get("/api/v1/metier/paie/bulletin",
                      params={"employe_id": 999999, "annee": 2030, "mois": 1})
    assert resp.status_code == 200
    assert "note" in resp.json()


def test_paie_progressifs_absent_honnete(client):
    resp = client.get("/api/v1/metier/paie/cumuls-progressifs",
                      params={"annee": 2030, "employe_id": 999999})
    assert resp.status_code == 200
    assert "note" in resp.json()


def test_cuves_alerte(client):
    resp = client.get("/api/v1/metier/cuves-en-alerte")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)

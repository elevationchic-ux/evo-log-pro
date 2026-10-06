"""Contrat d'honnetete du module Reporting (/api/v1/reporting).

Regles verifiees ici, conformement a la politique zero-mock du projet :
  - les listes sans enregistrement repondent vides ([]), jamais avec des
    lignes inventees ;
  - la "generation" d'un rapport horodate et change le statut, mais NE
    FABRIQUE PLUS nombre_lignes (l'ancien code ecrivait 1000 lignes
    fictives + un time.sleep() de simulation) ;
  - le rapport executif agrege reellement la table KPI : sans KPI
    enregistre, kpis/poles restent vides et nombre_kpis = 0 ;
  - un modele POSTe est restitue avec ses valeurs reelles, et le 404 est
    honnete sur un id inexistant.

Bout-en-bout HTTP reel via le fixture client de conftest (override
get_current_user superuser), sans dependency_overrides.clear().
"""
from __future__ import annotations

import pytest

BASE = "/api/v1/reporting"


# ── 1. Listes : etat vide honnete ────────────────────────────────────────────

@pytest.mark.parametrize("path", [
    "/rapports",
    "/dashboards",
    "/kpis",
    "/exports",
    "/tableaux-bord",
])
def test_listes_vides_sans_lignes_inventees(client, path):
    r = client.get(f"{BASE}{path}")
    assert r.status_code == 200, r.text
    assert r.json() == [], f"{path} doit etre vide, pas fabrique"


# ── 2. Génération : plus de compteur fabrique ────────────────────────────────

def _creer_rapport(client, numero="RP-HONNETETE-001", titre="Mod test"):
    payload = {
        "numero_rapport": numero,
        "titre": titre,
        "type_rapport": "TRANSIT",
        "frequence": "MENSUEL",
        "requetes": {},
        "colonnes": {},
    }
    return client.post(f"{BASE}/rapports", json=payload)


def test_generer_rapport_n_invente_plus_nombre_lignes(client, db):
    """L'ancien service ecrivait nombre_lignes = 1000 apres un sleep(1)
    de simulation. Interdit desormais : rien n'est calcule, le compteur
    reste NULL et l'ecran doit l'afficher comme « non calcule »."""
    from app.models.reporting import Rapport

    r = _creer_rapport(client)
    assert r.status_code == 201, r.text
    rid = r.json()["id"]

    g = client.put(f"{BASE}/rapports/{rid}/generer")
    assert g.status_code == 200, g.text

    rapport = db.query(Rapport).filter(Rapport.id == rid).first()
    assert str(getattr(rapport.statut, "value", rapport.statut)) == "disponible"
    assert rapport.nombre_lignes is None, (
        "aucune ligne n'a reellement ete calculee : le compteur doit "
        "rester NULL au lieu d'inventer 1000")


def test_modele_persiste_restitue_valeurs_reelles(client):
    r = _creer_rapport(client, numero="RP-HONNETETE-002", titre="Encours douane")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["numero_rapport"] == "RP-HONNETETE-002"
    assert body["titre"] == "Encours douane"
    assert body["type_rapport"] == "TRANSIT"
    # Statut initial reel : en preparation, jamais « disponible ».
    assert body["statut"] == "en_preparation"

    liste = client.get(f"{BASE}/rapports")
    assert liste.status_code == 200
    numeros = [x["numero_rapport"] for x in liste.json()]
    assert "RP-HONNETETE-002" in numeros


# ── 3. Rapport executif : agregation reelle de la table KPI ─────────────────

def test_rapport_executif_sans_kpi_reste_vide(client):
    r = client.get(f"{BASE}/rapports/executif")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kpis"] == [], "aucun KPI enregistre => liste vide"
    assert body["nombre_kpis"] == 0
    assert body["poles"] == [], "regroupement par pôle calcule sur du reel"


def test_rapport_executif_agrege_kpi_reels(client, db):
    from app.services.reporting_service import KPIService

    KPIService.creer_kpi(
        db, code="CA_MOIS", nom="Chiffre d'affaires", type_rapport="FINANCE",
        categorie="ventes", formule="sum(factures)", unite="XAF", objectif=100000,
    )
    KPIService.creer_kpi(
        db, code="MISSIONS", nom="Missions livrees", type_rapport="TRANSPORT",
        categorie="exploitation", formule="count(missions)", unite="nb", objectif=50,
    )
    KPIService.creer_kpi(
        db, code="CA_TOT", nom="CA cumule", type_rapport="FINANCE",
        categorie="ventes", formule="sum(factures)", unite="XAF", objectif=1000000,
    )

    r = client.get(f"{BASE}/rapports/executif")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["nombre_kpis"] == 3
    codes = {k["code"] for k in body["kpis"]}
    assert codes == {"CA_MOIS", "MISSIONS", "CA_TOT"}
    poles = {p["pole"]: p["nb_indicateurs"] for p in body["poles"]}
    assert poles == {"FINANCE": 2, "TRANSPORT": 1}
    # Regression : k_par_type etait force a {cle: 1}. Doit compter reellement.
    assert body["k_par_type"] == {"FINANCE": 2, "TRANSPORT": 1}


# ── 4. 404 honnetes ──────────────────────────────────────────────────────────

def test_rapport_inexistant_404(client):
    assert client.get(f"{BASE}/rapports/999999").status_code == 404
    assert client.put(f"{BASE}/rapports/999999/generer").status_code == 404
    assert client.delete(f"{BASE}/rapports/999999").status_code == 404

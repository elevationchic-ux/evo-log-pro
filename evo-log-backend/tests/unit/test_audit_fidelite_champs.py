# -*- coding: utf-8 -*-
"""Tests de l'audit de fidelite des champs (scripts/audit_fidelite_champs.py).

Cet outil juge des ecrans, pas des routes : il affirme qu'une propriete lue par
le frontend n'existe pas dans le schema emis par le backend. Chacune des regles
ci-dessous a ete ecrite APRES avoir produit un resultat faux sur un fichier
reel de ce depot, et figure ici comme verrou :

  * la proximite de chaine designait `kpis` (dictionnaire brut, sans contrat)
    comme porteur des champs de CamionResponse -> faux positif ;
  * une cle fabriquee par un view-model local (`brand: c.marque`) etait signalee
    comme champ invente -> faux positif sur `transport/flotte` ;
  * les variables d'etat alimentees sans iteration (`mission.origine`)
    n'etaient jamais verifiees -> faux negatif sur `transport/epod` ;
  * le nom du champ se verifiait, jamais sa VALEUR -> les 'ACTIVE'/'EN_ROUTE'
    comparés a des enums minuscules passaient -> faux negatifs en serie.

Le script n'est pas un paquet importable : il est charge par chemin.
"""
import importlib.util
import os

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(BACKEND, "scripts", "audit_fidelite_champs.py")

CONTRAT = {
    "schemas": {
        "MissionResponse": {
            "champs": {"id": {}, "statut": {}, "point_depart": {}, "reference": {}},
            "enums": {"statut": ["planifiee", "en_cours", "terminee"]},
        },
        "CamionResponse": {
            "champs": {"id": {}, "marque": {}, "status": {}},
            "enums": {"status": ["active", "in_maintenance"]},
        },
    },
    "reponses": {
        "/api/v1/transport/missions": {"get": ["MissionResponse"]},
        "/api/v1/transport/camions": {"get": ["CamionResponse"]},
        # `/kpis` n'a pas de response_model : contrat muet, donc non verifiable.
        "/api/v1/transport/kpis": {"get": []},
    },
}
INDEX = {"transportAPI.getMissions": ("get", "/api/transport/missions")}


@pytest.fixture(scope="module")
def audit():
    spec = importlib.util.spec_from_file_location("audit_fidelite_champs", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ─── a qui appartient la donnee ────────────────────────────────────────────
DEUX_APPELS = """
const [vehicles, setVehicles] = useState<any[]>([]);
const [kpis, setKpis] = useState<any>(null);
const [v, k] = await Promise.all([
  apiClient.get('/api/v1/transport/camions'),
  apiClient.get('/api/v1/transport/kpis'),
]);
const rows = Array.isArray(v.data) ? v.data : [];
setVehicles(rows.map((c: any) => ({ brand: c.marque })));
setKpis(k?.data ?? null);
"""


def test_promise_all_apparie_positionnellement(audit):
    vars_, ambigus = audit.lien_donnees(CONTRAT, {}, DEUX_APPELS)
    assert vars_["vehicles"] == {"CamionResponse"}


def test_un_dictionnaire_sans_contrat_n_est_pas_juge(audit):
    """`kpis` vient d'un appel sans response_model : on declare l'ignorance."""
    vars_, ambigus = audit.lien_donnees(CONTRAT, {}, DEUX_APPELS)
    assert "kpis" not in vars_
    assert "kpis" in ambigus


# ─── vues locales ──────────────────────────────────────────────────────────
def test_une_cle_construite_par_la_page_n_est_pas_inventee(audit):
    """`brand: c.marque` definit `brand` : le juger hors contrat etait un faux
    positif, et c'est lui qui a revele que l'outil ne voyait pas les vues."""
    noms_lus, valeurs, retably, _ = audit.analyser(CONTRAT, {}, DEUX_APPELS + """
const lignes = vehicles.map((v: any) => `${v.brand}-${v.chassis}`);
""")
    assert retably
    signales = {s["champ"] for s in noms_lus}
    assert "brand" not in signales  # cle fabriquee par la page elle-meme
    assert "chassis" in signales    # la, rien ne la produit ni ne l'emmet


# ─── variables d'etat sans iteration ───────────────────────────────────────
FICHE_MISSION = """
const [mission, setMission] = useState<any>(null);
const res = await transportAPI.getMissions();
const actives = res.data?.filter((m: any) => m.statut === 'en_cours') || [];
setMission(actives[0]);
return <p>{mission.origine} {mission.reference}</p>;
"""


def test_une_variable_d_etat_se_verifie_sans_boucle(audit):
    """Le faux negatif le plus large de l'outil : `mission` n'est jamais par-
    courue par un .map(), et `mission.origine` sortait du champ de vision."""
    noms_lus, _valeurs, retably, _ = audit.analyser(CONTRAT, INDEX, FICHE_MISSION)
    assert retably
    signales = {s["champ"] for s in noms_lus}
    assert "origine" in signales
    assert "reference" not in signales


# ─── axe des valeurs ───────────────────────────────────────────────────────
def test_une_comparaison_impossible_est_revelee(audit):
    code = "const x = camions.filter((c: any) => c.status === 'ACTIVE');"
    suspects = audit.valeurs_hors_enum(CONTRAT, ["CamionResponse"], code)
    assert len(suspects) == 1
    assert suspects[0]["literal"] == "ACTIVE"
    assert suspects[0]["jumeau"] == "active"  # seul un decalage de casse


def test_une_valeur_conforme_ne_rit_pas(audit):
    code = "const x = camions.filter((c: any) => c.status === 'in_maintenance');"
    assert audit.valeurs_hors_enum(CONTRAT, ["CamionResponse"], code) == []


def test_une_valeur_sans_jumelle_restesignalee(audit):
    """'IMMOBILISE' n'existe dans aucun enum : a verifier a la main, mais le
    silence serait un mensonge — la comparaison ne reussira jamais."""
    code = "const x = camions.filter((c: any) => c.status === 'IMMOBILISE');"
    suspects = audit.valeurs_hors_enum(CONTRAT, ["CamionResponse"], code)
    assert len(suspects) == 1
    assert suspects[0]["jumeau"] is None


def test_le_enum_d_un_autre_schema_ne_passe_pas_pour_valide(audit):
    """`livree` est une valeur de CommandeResponse, pas de MissionResponse."""
    code = "const a = missions.filter((m: any) => m.statut === 'LIVREE');"
    suspects = audit.valeurs_hors_enum(CONTRAT, ["MissionResponse"], code)
    assert [s["literal"] for s in suspects] == ["LIVREE"]


# ─── outillage ─────────────────────────────────────────────────────────────
def test_bloc_apparie_ignore_les_delimitateurs_d_une_chaine(audit):
    code = "setX(a.map(s => `)}{`)); reste"
    assert audit.bloc_apparie(code, code.index("(")) == "a.map(s => `)}{`)"
    assert "reste" not in audit.bloc_apparie(code, code.index("("))


def test_decoupage_respecte_les_parentheses_imbriquees(audit):
    morceaux = audit.decoupage("get('/a'), get('/b', { x: 1 }), c")
    assert morceaux == ["get('/a')", " get('/b', { x: 1 })", " c"]

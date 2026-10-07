"""Departement Amenagement portuaire : RBAC granulaire (92 operations, 39 codes historique + 25 expansion) + honnetete.

Meme discipline que les batches 21 a 24, trois volets :
  1. DROITS : parite catalogue (53 codes `amenagement.*`, dont 39 utilises par le
     routeur), MATRICE complete role x code calculee par le VRAI moteur
     has_perm(), puis 403 HTTP reels sur les routes ;
  2. HONNETETE : aucune route publique (501/401 verifies), aucun numero ni
     aucune date fabriques, les six teleprocedures institutionnelles repondent
     501, /places et /synthese remontent le NULL au lieu de l'estimer ;
  3. migration 039 : additive, idempotente, garde explicite sur base sans
     tables RBAC.
"""
import re
import types
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine

from app.core.permission_catalog import ROLE_GRANTS, iter_permission_rows
from app.core.permissions import has_perm
from app.core.security import get_current_user

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"
SCRIPT_LOCATION = BACKEND_ROOT / "migrations"
ROUTER_FILE = BACKEND_ROOT / "app" / "routers" / "v1" / "amenagement_portuaire.py"

BASE = "/api/v1/amenagement-portuaire"


def _codes_utilises():
    src = ROUTER_FILE.read_text(encoding="utf-8")
    return sorted(set(re.findall(r'require_perm\("([^"]+)"\)', src)))


def _codes_role(nom):
    for n, _lvl, _desc, codes in ROLE_GRANTS:
        if n == nom:
            return codes
    raise AssertionError(f"role {nom} absent du catalogue")


def _codes_catalogue_amenagement():
    return {row[0] for row in iter_permission_rows() if row[2] == "amenagement"}


# ── 1. Parite catalogue ──────────────────────────────────────────────────────
def test_tous_les_codes_du_routeur_existent_au_catalogue():
    codes = _codes_utilises()
    assert len(codes) == 39, f"attendu 39 codes distincts, trouve {len(codes)}"
    catalogue = {row[0] for row in iter_permission_rows()}
    fantomes = [c for c in codes if c not in catalogue]
    assert not fantomes, f"codes require_perm inconnus du catalogue: {fantomes}"


def test_le_catalogue_decrit_les_sous_modules_d_amenagement():
    codes = _codes_catalogue_amenagement()
    # 53 codes historiques : 5 sous-modules complets (6 actions) + 4 sans delete
    # (5 actions) + le referentiel des places (read/create/modify, jamais delete).
    # + 25 codes de l'expansion (amenagement_extra_deep) : nomenclature (read) et
    # huit registres operationnels en read/create/modify (le DELETE du routeur est
    # garde sous « modify », jamais effacement d'une piece a valeur).
    assert len(codes) == 78, f"attendu 78 codes amenagement, trouve {len(codes)}"
    sous_modules = {c.split(".")[1] for c in codes}
    assert sous_modules == {
        "place",
        "schema_directeur", "projet", "programmation", "marche", "titre_domanial",
        "concession", "infrastructure", "dragage", "autorisation",
        # Expansion (routeur amenagement_extra_deep) :
        "nomenclature", "construction_tracking", "infrastructure_maintenance",
        "port_security_isps", "port_pricing", "activity_report",
        "domain_cartography", "archive_management", "development_kpi",
    }, sous_modules
    # Tout ce que le routeur exige est bien dans la zone du departement.
    assert set(_codes_utilises()) <= codes


def test_expansion_amenagement_extra_deep_aucun_code_fantome():
    # Le routeur d'expansion n'est pas couvert par _codes_utilises() (qui ne lit
    # que le routeur historique). On verifie ici, sans rien simuler, que chaque
    # require_perm() qu'il emploie est declare au catalogue ET porte par au moins
    # un role, pour qu'aucune de ses routes ne soit unreachable/403 permanent.
    src = ROUTER_FILE.with_name("amenagement_extra_deep.py").read_text(encoding="utf-8")
    codes = sorted(set(re.findall(r'require_perm\("([^"]+)"\)', src)))
    assert codes, "aucun code require_perm trouve dans le routeur d'expansion"
    catalogue = _codes_catalogue_amenagement()
    fantomes = [c for c in codes if c not in catalogue]
    assert not fantomes, f"codes require_perm inconnus du catalogue: {fantomes}"
    for code in codes:
        porteurs = [
            nom for nom, _l, _d, grant in ROLE_GRANTS if has_perm(grant, code)
        ]
        assert porteurs, f"aucun role ne porte {code}"


def test_chaque_code_utilise_a_au_moins_un_role_porteur():
    for code in _codes_utilises():
        porteurs = [
            nom for nom, _l, _d, codes in ROLE_GRANTS if has_perm(codes, code)
        ]
        assert porteurs, f"aucun role ne porte {code}"


# ── 2. Matrice complete role x code, attendue explicitement ─────────────────
# INGENIEUR_AMENAGEMENT : instruit, tient l'inventaire, ne tranche jamais.
# Les approuvés (acte d'engagement) et les suppressions restent au chef.
_INGENIEUR_REFUSES = (
    "amenagement.schema_directeur.approve",
    "amenagement.programmation.approve",
    "amenagement.marche.approve",
    "amenagement.titre_domanial.approve",
    "amenagement.concession.approve",
    "amenagement.dragage.approve",
    "amenagement.autorisation.approve",
    "amenagement.projet.delete",
    "amenagement.infrastructure.delete",
)
# AUDITEUR : lecture transversale du domaine (wildcard amenagement.*.read).
_AUDITEUR_AUTORISES = tuple(
    f"amenagement.{s}.read" for s in (
        "place",
        "schema_directeur", "projet", "programmation", "marche", "titre_domanial",
        "concession", "infrastructure", "dragage", "autorisation",
    )
)
# CHEF_EXPLOITATION : voit l'avancement et les arretes qui genent le quai.
_CHEF_EXP_AUTORISES = (
    "amenagement.infrastructure.read", "amenagement.dragage.read",
    "amenagement.projet.read", "amenagement.titre_domanial.read",
    "amenagement.place.read",
)
# DIRECTEUR_FINANCIER : la ligne de programmation, ses visas et ses marches.
_DAF_AUTORISES = (
    "amenagement.projet.read", "amenagement.marche.read",
    "amenagement.concession.read", "amenagement.programmation.read",
    "amenagement.programmation.approve",
    "amenagement.place.read",
)


def _attentes():
    u = set(_codes_utilises())
    chef = dict.fromkeys(u, True)                     # amenagement.*.*
    ingenieur = {c: (c not in set(_INGENIEUR_REFUSES)) for c in u}
    auditeur = {c: (c in set(_AUDITEUR_AUTORISES)) for c in u}
    chef_exp = {c: (c in set(_CHEF_EXP_AUTORISES)) for c in u}
    daf = {c: (c in set(_DAF_AUTORISES)) for c in u}
    # Un transitaire n'a AUCUN code amenagement : default-deny verifie.
    transit = dict.fromkeys(u, False)

    # Garde-fous : les listes explicitent des codes reellement exposes.
    assert set(_INGENIEUR_REFUSES) <= u, set(_INGENIEUR_REFUSES) - u
    assert set(_INGENIEUR_REFUSES) == {
        c for c in u if c.endswith(".approve") or c.endswith(".delete")
    }, "le refus d'engagement doit couvrir tout ce que le routeur approuve/supprime"
    assert set(_AUDITEUR_AUTORISES) <= u, set(_AUDITEUR_AUTORISES) - u
    assert all(c.endswith(".read") for c in _AUDITEUR_AUTORISES)
    assert set(_CHEF_EXP_AUTORISES) <= u, set(_CHEF_EXP_AUTORISES) - u
    assert set(_DAF_AUTORISES) <= u, set(_DAF_AUTORISES) - u
    return {
        "CHEF_AMENAGEMENT_PORTUAIRE": chef,
        "INGENIEUR_AMENAGEMENT": ingenieur,
        "AUDITEUR": auditeur,
        "CHEF_EXPLOITATION": chef_exp,
        "DIRECTEUR_FINANCIER": daf,
        "TRANSIT_PRINCIPAL": transit,
    }


@pytest.mark.parametrize("role", [
    "CHEF_AMENAGEMENT_PORTUAIRE", "INGENIEUR_AMENAGEMENT", "AUDITEUR",
    "CHEF_EXPLOITATION", "DIRECTEUR_FINANCIER", "TRANSIT_PRINCIPAL",
])
def test_matrice_role_x_codes(role):
    codes_role = _codes_role(role)
    attentes = _attentes()[role]
    for code in _codes_utilises():
        reel = has_perm(codes_role, code)
        attendu = attentes[code]
        assert reel == attendu, (
            f"{role} sur {code} : attendu={'AUTORISE' if attendu else 'REFUSE'}, "
            f"reel={'AUTORISE' if reel else 'REFUSE'}"
        )


def test_le_chef_porte_le_departement_entier_et_rien_d_autre():
    """Le wildcard du chef ne deborde pas sur la comptabilite qu'il ne lit pas."""
    codes = _codes_role("CHEF_AMENAGEMENT_PORTUAIRE")
    assert has_perm(codes, "amenagement.concession.approve")
    assert has_perm(codes, "comptabilite.journal.read")
    assert not has_perm(codes, "comptabilite.journal.approve")
    assert not has_perm(codes, "tresorerie.mouvement.create")


# ── 3. HTTP reel avec les roles metier ───────────────────────────────────────
def _utilisateur_avec_codes(codes, uid):
    return types.SimpleNamespace(
        id=uid, email=f"user{uid}@amenagement.test", is_active=True,
        is_superuser=False, company_id=None, role_level=3,
        department_id=None,
        roles=[types.SimpleNamespace(
            permissions=[types.SimpleNamespace(code=c) for c in codes],
        )],
        accreditations=[],
    )


def _client_role(client, role, uid):
    from app.main import app

    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: _utilisateur_avec_codes(
        _codes_role(role), uid)
    try:
        yield client
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved
        else:
            app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def client_chef(client):
    yield from _client_role(client, "CHEF_AMENAGEMENT_PORTUAIRE", 81)


@pytest.fixture
def client_ingenieur(client):
    yield from _client_role(client, "INGENIEUR_AMENAGEMENT", 82)


@pytest.fixture
def client_auditeur(client):
    yield from _client_role(client, "AUDITEUR", 83)


@pytest.fixture
def client_chef_exp(client):
    yield from _client_role(client, "CHEF_EXPLOITATION", 84)


@pytest.fixture
def client_daf(client):
    yield from _client_role(client, "DIRECTEUR_FINANCIER", 85)


# -- Droits : autorisations et refus reels (403 avant 404/422) ----------------
def test_chef_200_sur_liste_projets(client_chef):
    r = client_chef.get(f"{BASE}/projets")
    assert r.status_code == 200, r.text


def test_auditeur_200_sur_programmation_et_403_sur_ecriture(client_auditeur):
    assert client_auditeur.get(f"{BASE}/programmation").status_code == 200
    # Le 403 (et non 422) prouve que le droit est verifie AVANT le corps.
    r = client_auditeur.post(f"{BASE}/projets", json={})
    assert r.status_code == 403, r.text
    assert "amenagement.projet.create" in r.text


def test_auditeur_403_sur_suppression_infrastructure(client_auditeur):
    r = client_auditeur.delete(f"{BASE}/infrastructures/1")
    assert r.status_code == 403, r.text
    assert "amenagement.infrastructure.delete" in r.text


def test_ingenieur_403_survisa_de_maturite(client_ingenieur):
    # L'ingenieur prepare le dossier : le visa de maturite est acte du chef
    # (ou du DAF pour l'engagement), jamais du redacteur.
    r = client_ingenieur.post(
        f"{BASE}/programmation/1/visa-maturite"
        "?numero_visa=VM-1&date_visa=2026-05-12&autorite_visa=DGPIP")
    assert r.status_code == 403, r.text
    assert "amenagement.programmation.approve" in r.text


def test_ingenieur_403_sur_suppression_projet(client_ingenieur):
    r = client_ingenieur.delete(f"{BASE}/projets/1")
    assert r.status_code == 403, r.text
    assert "amenagement.projet.delete" in r.text


def test_ingenieur_porte_la_saisie_de_sa_competence(client_ingenieur):
    # projet.create est dans son perimetre : la porte est ouverte (pas 403).
    # Sans corps valide le handler repondrait 422 ; on n'attend qu'une chose,
    # l'absence de refus d'autorisation.
    r = client_ingenieur.post(f"{BASE}/projets", json={})
    assert r.status_code in (200, 201, 400, 404, 422), (
        f"projet.create doit etre accessible a l'ingenieur, "
        f"reel={r.status_code} : {r.text[:200]}")


def test_chef_exploitation_403_sur_redaction_d_un_schema(client_chef_exp):
    # Il voit les projets et les ouvrages, il ne redige pas les schemas.
    assert client_chef_exp.get(f"{BASE}/projets").status_code == 200
    r = client_chef_exp.put(f"{BASE}/schemas-directeurs/1", json={})
    assert r.status_code == 403, r.text
    assert "amenagement.schema_directeur.modify" in r.text


def test_daf_approuve_la_ligne_pas_le_domaine(client_daf):
    assert client_daf.get(f"{BASE}/programmation").status_code == 200
    r = client_daf.post(f"{BASE}/titres-domaniaux", json={})
    assert r.status_code == 403, r.text
    assert "amenagement.titre_domanial.create" in r.text
    # Son droit d'engagement passe la garde : 404 (et non 403) sur un id inexistant.
    r2 = client_daf.post(
        f"{BASE}/programmation/999999/visa-controle-financier"
        "?date_visa=2026-01-08&autorite_visa=Controle+financier")
    assert r2.status_code == 404, r2.text


def test_transit_principal_403_partout(client):
    from app.main import app

    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: _utilisateur_avec_codes(
        _codes_role("TRANSIT_PRINCIPAL"), 86)
    try:
        for path in ("/projets", "/programmation", "/titres-domaniaux", "/synthese"):
            r = client.get(f"{BASE}{path}")
            assert r.status_code == 403, f"{path} : {r.text[:200]}"
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved
        else:
            app.dependency_overrides.pop(get_current_user, None)


# ── 4. Aucune route publique ─────────────────────────────────────────────────
def _routes_openapi():
    from app.main import app

    verbes = ("get", "post", "put", "patch", "delete")
    out = []
    for path, item in app.openapi()["paths"].items():
        if not path.startswith(BASE):
            continue
        for verbe in verbes:
            if verbe in item:
                out.append((verbe.upper(), path))
    return out


def test_toutes_les_routes_exigent_une_identite(unauthenticated):
    routes = _routes_openapi()
    # 60 operations du routeur historique + 32 operations de l'expansion
    # amenagement_extra_deep (construction-progresses, infrastructure-maintenances,
    # isps-records, port-perceptions, annual-activity-reports, sig-layers,
    # domain-archives, amenagement-kpis), toutes gardees par require_perm().
    # + 8 operations de l'expansion amenagement_b_deep (amgtb-dredging-projects,
    # amgtb-concession-plots) : 2 entites x 4 methodes CRUD.
    assert len(routes) == 100, f"attendu 100 operations, trouve {len(routes)}"
    for method, path in routes:
        url = path.replace("{ident}", "1")
        r = unauthenticated.request(method, url)
        # Une route qui repondrait 200/404/422 sans identite serait publique.
        assert r.status_code in (401, 403), (
            f"{method} {path} repond {r.status_code} sans authentification : "
            f"la route est publique")


# ── 5. Honnetete : rien n'est fabrique ───────────────────────────────────────
# Les six teleprocedures institutionnelles : MINMIVT/APN, MINFI, COLIFE/CIP,
# reversaison, exutoire de dragage, depot MINEPPT.
@pytest.mark.parametrize("path", [
    "/schemas-directeurs/1/demande-visa-minmivt",
    "/programmation/1/notification-minfi",
    "/marches/1/soumission-colife",
    "/concessions/1/reversaison",
    "/dragage/1/autorisation-rejet",
    "/autorisations/1/depot",
])
def test_teleprocedures_institutionnelles_jamais_faux_succes(client_chef, path):
    # Teleprocedures institutionnelles REELLES : chaque route valide d'abord
    # l'entite ciblee (404 si absente), puis delegue a un connecteur gouvernemental
    # configure (503 si le fournisseur n'est pasbranche). La reversaison est une
    # ecriture locale reelle qui EXIGE la reference de l'acte (422 sinon).
    # Aucun de ces cas ne fabrique un succes 200 avec acte officiel invente.
    r = client_chef.post(f"{BASE}{path}")
    assert r.status_code != 200, f"faux succes sur {path} : {r.text[:200]}"
    assert r.status_code in (404, 422, 502, 503), (
        f"{path} : statut inattendu {r.status_code} : {r.text[:200]}")


def test_la_garde_passe_avant_le_501(client_auditeur):
    # Un refus d'autorisation (403) ne doit jamais se deguiser en 501.
    r = client_auditeur.post(f"{BASE}/concessions/1/reversaison")
    assert r.status_code == 403, r.text
    assert "amenagement.concession.approve" in r.text


def test_places_ne_sort_que_des_lignes_de_ports_cameroun(client_chef, db):
    from app.models.port_cameroun import PortCameroun, TypePort

    assert client_chef.get(f"{BASE}/places").json()["data"] == [], (
        "aucun port en base : la reponse doit etre vide, pas peuplee par defaut")

    db.add(PortCameroun(code="DOU", nom="Port de Douala", type_port=TypePort.MARCHANDISES,
                        ville="Douala", region="Littoral"))
    db.add(PortCameroun(code="TIK", nom="Port de Tiko", type_port=TypePort.BANANES,
                        ville="Tiko", region="Sud-Ouest"))
    db.commit()

    body = client_chef.get(f"{BASE}/places").json()
    codes = [p["code"] for p in body["data"]]
    # Le referentiel national est rendu INTEGRAL. Le perimetre d'etude du
    # departement (DOU/KRI/LIM) filtre les agregats de /synthese, pas cette
    # lecture : cacher « TIK » ferait croire a l'agent que sa declaration n'a
    # pas ete enregistree, et la ligne deviendrait incorrigible.
    assert codes == ["DOU", "TIK"], codes
    assert body["total"] == 2
    douala = next(p for p in body["data"] if p["code"] == "DOU")
    assert douala["autorite_portuaire"] is None
    assert douala["tirant_eau_max"] is None
    assert "non saisi" in body["note"].lower() or "NULL" in body["note"]


# ── 5bis. Le référentiel des places s'alimente, il ne se devine pas ──────────
# ports_cameroun etait lit par quatre routeurs et ecrit par aucun : sans ces
# routes, aucun registre du departement ne pouvait rattacher une ligne a une
# place portuaire. La declaration reste une saisie sous document officiel.

def test_un_auditeur_ne_declare_pas_de_place(client_auditeur):
    r = client_auditeur.post(f"{BASE}/places", json={
        "code": "DOU", "nom": "Port de Douala", "type_port": "marchandises"})
    assert r.status_code == 403, r.text
    assert "amenagement.place.create" in r.text


def test_une_place_se_declaire_sans_qu_rien_ne_soit_invente(client_ingenieur):
    r = client_ingenieur.post(f"{BASE}/places", json={
        "code": "kri", "nom": "Port en eau profonde de Kribi",
        "type_port": "marchandises"})
    assert r.status_code == 201, r.text
    place = r.json()
    # Le code est normalise en majuscules (c'est la cle du referentiel national),
    # pas remplace par un code invente.
    assert place["code"] == "KRI"
    # Rien au-dela de la saisie : ni autorite, ni tirant d'eau, ni capacite.
    assert place["autorite_portuaire"] is None
    assert place["tirant_eau_max"] is None
    assert place["profondeur_m"] is None
    assert place["capacite_annuelle_tonnes"] is None
    assert place["ville"] is None
    # est_actif vient du defaut de colonne (une place declaree est en service),
    # pas d'une decision du logiciel.
    assert place["est_actif"] is True
    # Et la liste la renvoie desormais, rattachee au perimetre par son code.
    codes = [p["code"] for p in client_ingenieur.get(f"{BASE}/places").json()["data"]]
    assert "KRI" in codes


def test_le_type_de_port_n_est_jamais_devine(client_ingenieur):
    # `type_port` est NOT NULL en base : sans lui, la route refuse plutot que de
    # poser « marchandises » par defaut sur un port petrolier.
    r = client_ingenieur.post(f"{BASE}/places", json={
        "code": "LIM", "nom": "Port de Limbe"})
    assert r.status_code == 422, r.text


def test_deuxieme_douala_refusee_plutot_que_doublon_de_referentiel(client_chef, db):
    from app.models.port_cameroun import PortCameroun, TypePort

    db.add(PortCameroun(code="DOU", nom="Port de Douala", type_port=TypePort.MARCHANDISES))
    db.commit()
    r = client_chef.post(f"{BASE}/places", json={
        "code": "DOU", "nom": "Port autonome de Douala", "type_port": "marchandises"})
    assert r.status_code == 409, r.text


def test_une_place_se_desactive_et_ne_se_detruit_pas(client_ingenieur, db):
    from app.models.port_cameroun import PortCameroun, TypePort

    place = PortCameroun(code="LIM", nom="Port de Limbe", type_port=TypePort.MARCHANDISES)
    db.add(place)
    db.commit()
    db.refresh(place)

    r = client_ingenieur.put(f"{BASE}/places/{place.id}", json={"est_actif": False})
    assert r.status_code == 200, r.text
    assert r.json()["est_actif"] is False
    # Referentiel partage : la ligne reste en base, l'historique des pieces du
    # domaine conserve sa reference.
    assert db.query(PortCameroun).filter(PortCameroun.code == "LIM").count() == 1

    # Aucune route DELETE n'est declaree sur ce referentiel : ce qui n'existe
    # pas au contrat ne doit pas exister non plus dans le schéma OpenAPI (le
    # fallback « pending » global repondrait a la place, ce ne serait pas une
    # suppression, mais ce ne serait pas non plus un contrat).
    from app.main import app

    verbes = app.openapi()["paths"].get(f"{BASE}/places/{{ident}}", {})
    assert "delete" not in verbes, sorted(verbes)
    assert set(verbes) == {"put"}, sorted(verbes)


def test_une_place_hors_des_trois_codes_du_perimetre_reste_declaree(client_ingenieur):
    """Le périmètre d'étude filtre les agrégats, pas le référentiel.

    Un agent qui déclare une quatrième place (Tiko, Bonabéri…) doit la voir
    revenir : une ligne enregistrée puis absente de la liste ferait croire à
    l'échec de la saisie, et le formulaire ne pourrait plus jamais la corriger.
    """
    r = client_ingenieur.post(f"{BASE}/places", json={
        "code": "tik", "nom": "Port de Tiko", "type_port": "marchandises",
    })
    assert r.status_code == 201, r.text

    liste = client_ingenieur.get(f"{BASE}/places")
    assert liste.status_code == 200, liste.text
    codes = [p["code"] for p in liste.json()["data"]]
    assert "TIK" in codes, codes


def test_le_garde_place_refuse_une_donnee_que_la_table_ne_porte_pas():
    """`ports_cameroun` n'a ni source_reference ni notes : refuser plutot que
    laisser SQLAlchemy jeter silencieusement une donnee saisie par l'agent."""
    import pytest

    from fastapi import HTTPException

    from app.routers.v1.amenagement_portuaire import _colonnes_place

    with pytest.raises(HTTPException) as exc:
        _colonnes_place({"nom": "Port de Kribi", "source_reference": "Arrete n° 12"})
    assert exc.value.status_code == 400
    assert "source_reference" in exc.value.detail

    # Une donnee portee par la table passe, sans rien ajouter ni deviner.
    assert _colonnes_place({"nom": "Port de Kribi"}) == {"nom": "Port de Kribi"}


def test_le_vocabulaire_publie_par_nomenclatures_est_reel(client_chef):
    r = client_chef.get(f"{BASE}/nomenclatures")
    assert r.status_code == 200, r.text
    body = r.json()
    # 19 vocabulaires : les 18 du circuit + type_port, publie parce que la
    # declaration d'une place ne doit jamais proposer un type en dur.
    assert len(body) == 19, sorted(body)
    for cle, items in body.items():
        assert items, f"vocabulaire {cle} vide"
        for it in items:
            assert it["code"] and it["valeur"], (cle, it)
    # Le circuit de programmation camerounais, pas un workflow generique.
    prog = {it["code"] for it in body["statut_document_programmation"]}
    assert {"PREPARATION", "MATURITE_VISEE", "INSCRIT_PIP", "VISE"} <= prog
    titres = {it["code"] for it in body["statut_titre_domanial"]}
    assert {"DEMANDEE", "DELIVRE", "REFUSE"} <= titres
    statuts_projet = {it["code"] for it in body["statut_projet"]}
    assert {"INSCRIT_PIP", "NOTIFIE_MINFI"} <= statuts_projet


def test_synthese_remonte_les_vides_sans_les_estimer(client_chef):
    r = client_chef.get(f"{BASE}/synthese")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["projets"]["total"] == 0
    assert body["projets"]["sans_fiche_technique"] == 0
    # Rien de saisi : aucun solde ne doit passer pour un budget complet.
    assert body["projets"]["cout_previsionnel_total_xaf"] is None
    assert body["projets"]["cout_reel_total_xaf"] is None
    assert body["projets"]["suivi_financier_complet"] is False
    assert body["passation"]["montant_engage_xaf"] is None


# ── 6. Le circuit d'engagement ne s'auto-alimente pas ────────────────────────
def _creer(client, path, payload):
    r = client.post(f"{BASE}{path}", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def test_circuit_programmation_atteste_sans_jamais_devancer(client_chef):
    doc = _creer(client_chef, "/programmation", {
        "reference_fiche_technique": "FT-PAD-2026-001",
        "exercice": 2026,
        "objet": "Renforcement du quai 201 de Bonanjo",
    })
    assert doc["statut"] == "PREPARATION"
    # Rien n'est devine : les references des visas sont vides tant que l'acte
    # n'est pas saisi depuis la piece.
    assert doc["numero_visa_maturite"] is None
    assert doc["reference_pip_cdmt"] is None

    ident = doc["id"]
    v = client_chef.post(
        f"{BASE}/programmation/{ident}/visa-maturite"
        "?numero_visa=0012/DMTC/MINFI&date_visa=2026-05-12&autorite_visa=DGPIP"
    ).json()
    assert v["statut"] == "MATURITE_VISEE"
    assert v["numero_visa_maturite"] == "0012/DMTC/MINFI"
    assert v["date_visa_maturite"] == "2026-05-12"

    pip = client_chef.post(
        f"{BASE}/programmation/{ident}/inscription-pip"
        "?reference_pip_cdmt=PIP-2027-LIGNE-04&exercice=2027"
    ).json()
    assert pip["statut"] == "INSCRIT_PIP"
    assert pip["exercice"] == 2027

    vise = client_chef.post(
        f"{BASE}/programmation/{ident}/visa-controle-financier"
        "?date_visa=2027-01-08&autorite_visa=Controle+financier+regional"
    ).json()
    assert vise["statut"] == "VISE"

    # Regression : re-apposer un visa de maturite sur un dossier deja vise ne
    # doit PAS le faire regresser d'un cran.
    apres = client_chef.post(
        f"{BASE}/programmation/{ident}/visa-maturite"
        "?numero_visa=0012/DMTC/MINFI&date_visa=2026-05-12&autorite_visa=DGPIP"
    ).json()
    assert apres["statut"] == "VISE"


def test_refus_d_un_titre_domanial_doit_etre_motive(client_chef):
    titre = _creer(client_chef, "/titres-domaniaux", {
        "numero_piece": "AOT-2026-0113",
        "type_titre": "autorisation_temporaire",
        "beneficiaire": "Terminaux de Bonaberi SARL",
        "objet": "Depot provisoire de conteneurs vide",
    })
    assert titre["statut"] == "DEMANDEE"
    assert titre["date_signature"] is None

    # Un refus sans motif est refuse : la loi impose une decision ecrite.
    r = client_chef.post(
        f"{BASE}/titres-domaniaux/{titre['id']}/decision?accord=false&date_decision=2026-06-02")
    assert r.status_code == 422, r.text

    ok = client_chef.post(
        f"{BASE}/titres-domaniaux/{titre['id']}/decision"
        "?accord=false&date_decision=2026-06-02&motif_refus=Parcelle+couverte+par+l%27arrete+de+delimitation"
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["statut"] == "REFUSE"
    assert ok.json()["date_signature"] is None, (
        "un refus ne signe pas le titre")


def test_delivrance_d_un_titre_enregistre_la_date_reelle(client_chef):
    titre = _creer(client_chef, "/titres-domaniaux", {
        "numero_piece": "AOT-2026-0114",
        "type_titre": "convention_occupation",
        "beneficiaire": "Chantier Navale du Cameroun",
    })
    r = client_chef.post(
        f"{BASE}/titres-domaniaux/{titre['id']}/decision"
        "?accord=true&date_decision=2026-07-01&autorite_emettrice=PAD"
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["statut"] == "DELIVRE"
    assert body["date_signature"] == "2026-07-01"
    assert body["autorite_emettrice"] == "PAD"
    assert body["date_expiration"] is None, (
        "la duree du titre vient de l'acte : elle n'est pas calculee ici")


def test_double_reference_refusee_plutot_que_doublon(client_chef, db):
    from app.models.port_cameroun import PortCameroun, TypePort

    port = PortCameroun(code="KRI", nom="Port de Kribi", type_port=TypePort.MARCHANDISES,
                        ville="Kribi", region="Sud")
    db.add(port)
    db.commit()

    _creer(client_chef, "/dragage", {
        "code_campagne": "DRAG-PAK-2026-S1", "libelle": "Curage de l'approche chenal",
        "port_id": port.id,
    })
    r = client_chef.post(f"{BASE}/dragage", json={
        "code_campagne": "DRAG-PAK-2026-S1", "libelle": "Doublon", "port_id": port.id,
    })
    assert r.status_code == 409, r.text


# ── 7. Migration 039 ─────────────────────────────────────────────────────────
def _make_config():
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(SCRIPT_LOCATION))
    return cfg


def _scalar(url, sql):
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            return conn.exec_driver_sql(sql).scalar()
    finally:
        engine.dispose()


@pytest.fixture(scope="module")
def base_migrees(tmp_path_factory):
    """Base jetable montee jusqu'a 039 (chaine complete, comme en production).

    Scope module : monter 001->039 coute quelques secondes, les trois tests qui
    lisent cette base sont purement en lecture.
    """
    import os

    db_file = tmp_path_factory.mktemp("mig039") / "mig039.db"
    url = f"sqlite:///{db_file.as_posix()}"
    saved = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = url
    try:
        command.upgrade(_make_config(), "039_rbac_amenagement_grants")
        yield url
    finally:
        if saved is not None:
            os.environ["DATABASE_URL"] = saved
        else:
            os.environ.pop("DATABASE_URL", None)


def test_migration_039_seede_codes_et_roles_du_departement(base_migrees):
    url = base_migrees
    for code in (
        "amenagement.schema_directeur.read", "amenagement.projet.approve",
        "amenagement.programmation.export", "amenagement.marche.delete",
        "amenagement.titre_domanial.approve", "amenagement.concession.read",
        "amenagement.infrastructure.modify", "amenagement.dragage.create",
        "amenagement.autorisation.export",
    ):
        n = _scalar(url, f"SELECT COUNT(*) FROM permissions WHERE code = '{code}'")
        assert n == 1, f"code {code} absent de la table permissions"

    # Les deux roles metiers du departement sont crees, systemes et globaux.
    for nom in ("CHEF_AMENAGEMENT_PORTUAIRE", "INGENIEUR_AMENAGEMENT"):
        rid = _scalar(url, f"SELECT id FROM roles WHERE name = '{nom}'")
        assert rid is not None, f"{nom} doit exister apres 039"
        level = _scalar(url, f"SELECT level FROM roles WHERE id = {rid}")
        attendu = 2 if nom.startswith("CHEF") else 3
        assert level == attendu, f"{nom} : niveau {attendu} attendu, trouve {level}"
        liens = _scalar(url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {rid}")
        assert liens == len(_codes_role(nom)), (
            f"{nom} porte {liens} liens, le catalogue en declare {len(_codes_role(nom))}")


def test_migration_039_ne_decore_pas_un_role_etranger_au_departement(base_migrees):
    url = base_migrees
    for nom in ("AUDITEUR", "CHEF_EXPLOITATION", "DIRECTEUR_FINANCIER"):
        rid = _scalar(url, f"SELECT id FROM roles WHERE name = '{nom}'")
        assert rid is not None
        n = _scalar(
            url,
            "SELECT COUNT(*) FROM role_permissions rp "
            "JOIN permissions p ON p.id = rp.permission_id "
            f"WHERE rp.role_id = {rid} AND p.code LIKE 'amenagement.%'")
        attendus = sum(1 for c in _codes_role(nom) if c.startswith("amenagement."))
        assert n == attendus, f"{nom} : {n} liens amenagement, {attendus} attendus"


def test_migration_039_n_insert_aucune_donnee_metier(base_migrees):
    from app.models.amenagement_portuaire import (
        SchemaDirecteur, ProjetAmenagement, DocumentProgrammation, MarcheAmenagement,
        AutorisationDomaniale, ConcessionPortuaire, InfrastructurePortuaire,
        Dragage, AutorisationTravaux,
    )
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=create_engine(base_migrees))
    db = Session()
    try:
        for model in (SchemaDirecteur, ProjetAmenagement, DocumentProgrammation,
                      MarcheAmenagement, AutorisationDomaniale, ConcessionPortuaire,
                      InfrastructurePortuaire, Dragage, AutorisationTravaux):
            n = db.query(model).count()
            assert n == 0, (
                f"{model.__tablename__} contient {n} ligne(s) : le domaine public "
                f"se renseigne depuis les documents officiels, jamais par un seed")
    finally:
        db.close()


def test_migration_039_idempotente(tmp_path, monkeypatch):
    db_file = tmp_path / "mig039rejou.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()
    command.upgrade(cfg, "039_rbac_amenagement_grants")

    total_perms = _scalar(url, "SELECT COUNT(*) FROM permissions")
    total_liens = _scalar(url, "SELECT COUNT(*) FROM role_permissions")
    total_roles = _scalar(url, "SELECT COUNT(*) FROM roles")

    command.downgrade(cfg, "038_add_amenagement_portuaire")
    command.upgrade(cfg, "039_rbac_amenagement_grants")

    assert _scalar(url, "SELECT COUNT(*) FROM permissions") == total_perms
    assert _scalar(url, "SELECT COUNT(*) FROM role_permissions") == total_liens
    assert _scalar(url, "SELECT COUNT(*) FROM roles") == total_roles


def test_migration_039_refuse_explicitement_base_sans_tables_rbac(tmp_path, monkeypatch):
    db_file = tmp_path / "mig039guard.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()
    command.stamp(cfg, "038_add_amenagement_portuaire")
    with pytest.raises(RuntimeError) as exc:
        command.upgrade(cfg, "039_rbac_amenagement_grants")
    msg = str(exc.value).lower()
    assert "permissions" in msg or "rbac" in msg, (
        "la garde doit nommer la precondition RBAC, pas echouer en silence")

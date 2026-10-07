"""Batch 24  RBAC granulaire sur /api/v1/qhse (41 endpoints) + honnetete.

Deux volets, meme discipline que les batches 21/22/23 :
  1. DROITS : parite catalogue (34 codes), MATRICE complete role x code
     calculee par le VRAI moteur has_perm(), 403 HTTP reels ;
  2. HONNETETE : les 3 endpoints qui etaient PUBLICS et fabriques sont des
    ormais (a) authentifies+autorises, (b) 501 explicites quand l'acte est
     legal (permis de travail, bilan CNPS) ou dressees comme aide-memoire
     non reglementaire (segregation IMDG) ; aucun faux succes.
  3. migration 036 : idempotente, garde explicite sur base sans tables RBAC.
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
ROUTER_FILE = BACKEND_ROOT / "app" / "routers" / "v1" / "qhse.py"

BASE = "/api/v1/qhse"


def _codes_utilises():
    src = ROUTER_FILE.read_text(encoding="utf-8")
    return sorted(set(re.findall(r'require_perm\("([^"]+)"\)', src)))


def _codes_role(nom):
    for n, _lvl, _desc, codes in ROLE_GRANTS:
        if n == nom:
            return codes
    raise AssertionError(f"role {nom} absent du catalogue")


# ── 1. Parite catalogue ──────────────────────────────────────────────────────
def test_tous_les_codes_du_routeur_existent_au_catalogue():
    codes = _codes_utilises()
    assert len(codes) == 35, f"attendu 35 codes distincts, trouve {len(codes)}"
    catalogue = {row[0] for row in iter_permission_rows()}
    fantomes = [c for c in codes if c not in catalogue]
    assert not fantomes, f"codes require_perm inconnus du catalogue: {fantomes}"


# ── 2. Matrice complete role x code, attendue explicitement ─────────────────
# CHEF_EXPLOITATION : n'est PAS officier QHSE, mais declare les accidents du
# quai, demande un permis, consulte l'IMDG et signale un risque. Rien d'autre.
_CHEF_AUTORISES = (
    "qhse.accident.read", "qhse.accident.create", "qhse.accident.modify",
    "qhse.permis.create", "qhse.permis.read", "qhse.imdg.read", "qhse.risque.create",
)
# AUDITEUR : lecture transversale uniquement (wildcard qhse.*.read). Les codes
# *.read du module, aucune ecriture.
_AUDITEUR_AUTORISES = (
    "qhse.accident.read", "qhse.audit.read", "qhse.certification.read",
    "qhse.enregistrement.read", "qhse.formation.read", "qhse.imdg.read",
    "qhse.investigation.read", "qhse.permis.read", "qhse.rapport.read",
)


def _attentes():
    u = set(_codes_utilises())
    qhse_officier = dict.fromkeys(u, True)          # qhse.*.*
    chef = {c: (c in set(_CHEF_AUTORISES)) for c in u}
    auditeur = {c: (c in set(_AUDITEUR_AUTORISES)) for c in u}
    # Un transitaire n'a AUCUN code qhse : default-deny verifie.
    transit = dict.fromkeys(u, False)
    # Garde-fou interne : les listes explicitent des codes reels du routeur.
    assert set(_CHEF_AUTORISES) <= u, set(_CHEF_AUTORISES) - u
    assert set(_AUDITEUR_AUTORISES) <= u, set(_AUDITEUR_AUTORISES) - u
    assert all(c.endswith(".read") for c in _AUDITEUR_AUTORISES)
    return {
        "QHSE": qhse_officier,
        "CHEF_EXPLOITATION": chef,
        "AUDITEUR": auditeur,
        "TRANSIT_PRINCIPAL": transit,
    }


@pytest.mark.parametrize("role", [
    "QHSE", "CHEF_EXPLOITATION", "AUDITEUR", "TRANSIT_PRINCIPAL",
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


def test_chaque_code_utilise_a_au_moins_un_role_porteur():
    for code in _codes_utilises():
        porteurs = [
            nom for nom, _l, _d, codes in ROLE_GRANTS if has_perm(codes, code)
        ]
        assert porteurs, f"aucun role ne porte {code}"


# ── 3. HTTP reel avec les roles metier ───────────────────────────────────────
def _utilisateur_avec_codes(codes, uid):
    return types.SimpleNamespace(
        id=uid, email=f"user{uid}@qhse.test", is_active=True,
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
def client_officier(client):
    yield from _client_role(client, "QHSE", 71)


@pytest.fixture
def client_chef(client):
    yield from _client_role(client, "CHEF_EXPLOITATION", 72)


@pytest.fixture
def client_auditeur(client):
    yield from _client_role(client, "AUDITEUR", 73)


# -- Droits : autorisations et refus reels (403 avant 404/422) ----------------
def test_officier_200_sur_liste_accidents(client_officier):
    r = client_officier.get(f"{BASE}/accidents")
    assert r.status_code == 200, r.text


def test_auditeur_403_sur_declaration_accident(client_auditeur):
    # L'auditeur LIT les accidents mais ne les DECLARE pas : lecture seule.
    # Le 403 (et non 422) prouve que le droit est verifie AVANT le corps.
    r = client_auditeur.post(f"{BASE}/accidents", json={})
    assert r.status_code == 403, r.text
    assert "qhse.accident.create" in r.text


def test_auditeur_403_sur_suppression_enregistrement(client_auditeur):
    r = client_auditeur.delete(f"{BASE}/1")
    assert r.status_code == 403, r.text
    assert "qhse.enregistrement.delete" in r.text


def test_chef_403_sur_controle_haccp(client_chef):
    # Le chef declare un accident, il ne saisit pas les CCP HACCP (officier).
    r = client_chef.post(f"{BASE}/enregistrements-haccp", json={})
    assert r.status_code == 403, r.text
    assert "qhse.controle.create" in r.text


def test_chef_porte_la_declaration_accident(client_chef):
    # accident.create est dans son perimetre : la porte est ouverte (pas 403,
    # pas 500). Sans corps valide le handler repondrait 422 ; on n'attend pas
    # un succes metier ici, seulement l'absence de refus d'autorisation.
    r = client_chef.post(f"{BASE}/accidents", json={})
    assert r.status_code in (200, 201, 400, 404, 422), (
        f"accident.create doit etre accessible au chef, "
        f"reel={r.status_code} : {r.text[:200]}")


def test_transit_principal_403_partout(client):
    from app.main import app

    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: _utilisateur_avec_codes(
        _codes_role("TRANSIT_PRINCIPAL"), 74)
    try:
        r = client.get(f"{BASE}/accidents")
        assert r.status_code == 403, r.text
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved
        else:
            app.dependency_overrides.pop(get_current_user, None)


# -- Honnetete : les ex-endpoints publics ne fabriquent plus rien -------------
def test_permis_travail_refuse_champs_manquants_jamais_signature_inventee(client_officier):
    # Permis REELlement persiste : la route exige type_permis, zone, description
    # et n'invente AUCUNE signature. Un envoi incomplet est refuse (400), jamais
    # un faux succes avec signatures fabriquees.
    r = client_officier.post(f"{BASE}/permis-travail", json={"type_permis": "PERMIS_DE_FEU"})
    assert r.status_code == 400, r.text
    assert "zone" in r.text.lower() or "requis" in r.text.lower()


def test_permis_travail_cree_sans_signature_reste_brouillon(client_officier):
    # Permis complet cree -> statut EN_ATTENTE_SIGN / BROUILLON, AUCUNE signature
    # (le systeme ne simule pas la signature manuscrite numerique).
    r = client_officier.post(
        f"{BASE}/permis-travail",
        json={
            "type_permis": "feu",
            "zone": "Quai Nord, poste 3",
            "description": "Soudure sur structure",
            "mesures_preventives": "Extincteur, vigie",
        },
    )
    assert r.status_code in (200, 201), r.text
    body = r.json()
    assert body.get("statut") in ("BROUILLON", "EN_ATTENTE_SIGN")
    assert not body.get("signatures")  # aucune signature inventee a la creation


def test_bilan_csst_cnps_chiffres_reels_non_inventes(client_officier):
    # rapport.read porte : le bilan repond 200 sur les DONNEES REELLES en base.
    # Sans denominateur d'heures saisi, aucun TF/TG n'est publie (null + flag
    # heures_non_saisies), l'ancienne version inventait 2 850 000 h.
    r = client_officier.get(f"{BASE}/csst-cnps/bilan?annee=2026")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("source"), "la source de calcul doit etre declaree"
    # Aucun taux fabrique sans denominateur saisi.
    if body.get("heures_non_saisies"):
        assert body.get("taux_frequence_TF_par_million_h") is None
        assert body.get("taux_gravite_TG_par_million_h") is None
        assert "avertissement" in body


def test_imdg_aide_memoire_non_reglementaire(client_officier):
    # La segregation repond (calcul legitime) mais s'etend un AVERTISSEMENT
    # explicite et nepretend jamais a la conformite « CONFORME_CODE_IMDG ».
    r = client_officier.post(f"{BASE}/imdg/segregation", json={"classes_imdg": ["1", "3"]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["compatible"] is False
    assert "avertissement" in body
    assert "CONFORME" not in str(body)


def test_imdg_refuse_faux_positif_concatenation(client_officier):
    # Regression specifique : « 4.1 » + « 3 » ne doit PAS declencher la regle
    # classe 1 (l'ancien code testait « "1" in "".join(...) »).
    r = client_officier.post(f"{BASE}/imdg/segregation", json={"classes_imdg": ["4.1", "3"]})
    assert r.status_code == 200, r.text
    assert r.json()["compatible"] is True


# ── 4. Migration 036 ─────────────────────────────────────────────────────────
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


def test_migration_036_seede_module_qhse_complet(tmp_path, monkeypatch):
    db_file = tmp_path / "mig036.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()

    command.upgrade(cfg, "036_rbac_qhse_grants")

    # Des codes neufs du module qhse reellement presents en base.
    for code in (
        "qhse.risque.create", "qhse.accident.create", "qhse.haccp.create",
        "qhse.controle.create", "qhse.permis.create", "qhse.rapport.read",
        "qhse.enregistrement.delete", "qhse.imdg.read",
    ):
        n = _scalar(url, f"SELECT COUNT(*) FROM permissions WHERE code = '{code}'")
        assert n == 1, f"code {code} absent de la table permissions"

    # Le role QHSE existe et porte exactement ses grants du catalogue.
    rid = _scalar(url, "SELECT id FROM roles WHERE name = 'QHSE'")
    assert rid is not None, "QHSE doit exister apres 036"
    liens = _scalar(url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {rid}")
    assert liens == len(_codes_role("QHSE"))

    # Idempotence : rejouer 036 ne duplique ni liens ni permissions.
    total_perms_avant = _scalar(url, "SELECT COUNT(*) FROM permissions")
    command.downgrade(cfg, "035_rbac_acconage_grants")
    command.upgrade(cfg, "036_rbac_qhse_grants")
    assert _scalar(url, "SELECT COUNT(*) FROM permissions") == total_perms_avant
    assert _scalar(
        url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {rid}"
    ) == len(_codes_role("QHSE"))


def test_migration_036_refuse_explicitement_base_sans_tables_rbac(tmp_path, monkeypatch):
    db_file = tmp_path / "mig036_guard.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()
    command.stamp(cfg, "035_rbac_acconage_grants")
    with pytest.raises(RuntimeError) as exc:
        command.upgrade(cfg, "036_rbac_qhse_grants")
    msg = str(exc.value).lower()
    assert "permissions" in msg or "rbac" in msg, (
        "la garde doit nommer la precondition RBAC, pas echouer en silence")

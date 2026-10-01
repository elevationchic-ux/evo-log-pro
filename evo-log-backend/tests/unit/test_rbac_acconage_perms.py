"""Batch 23  RBAC granulaire sur /api/v1/acconage-avance (38 endpoints).

Meme discipline que les batches 21/22 :
  1. parite catalogue : aucun code fantome dans le routeur ;
  2. MATRICE COMPLETE role x code : pour les 30 codes utilises, chaque role
     concerné par l'acconage a une attente explicite (autorise OU refuse),
     calculee par le VRAI moteur has_perm() — pas un mock ;
  3. HTTP reel : operateur = 200 sur la lecture d'escales, 403 sur la
     validation du plan d'arrimage, l'emission d'un connaissement et la
     cloture des dockers ; transitaire principal (lecture seule acconage)
     = 200 en lecture, 403 en creation ;
  4. migration 035 : cree CHEF_EXPLOITATION + OPERATEUR_ACCONAGE et les
     codes neufs, idempotente, garde explicite sur base sans tables RBAC.
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
ROUTER_FILE = BACKEND_ROOT / "app" / "routers" / "v1" / "acconage_avance.py"

BASE = "/api/v1/acconage-avance"


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
    assert len(codes) == 30, f"attendu 30 codes distincts, trouve {len(codes)}"
    catalogue = {row[0] for row in iter_permission_rows()}
    fantomes = [c for c in codes if c not in catalogue]
    assert not fantomes, f"codes require_perm inconnus du catalogue: {fantomes}"


# ── 2. Matrice complete role x code, attendue explicitement ─────────────────
# Chaque attente est une DECISION METIER relisible : le chef d'exploitation
# porte tout l'acconage ; l'operateur execute sans JAMAIS approuver
# (valider l'arrimage, cloturer les dockers) ni emettre de connaissement ;
# le transitaire principal ne fait que lire (acconage.*.read) ; le declarant
# ne lit que le manifeste.
_OPERATEUR_AUTORISES_ROUTEUR = (
    "acconage.navire.read",
    "acconage.escale.read", "acconage.escale.create", "acconage.escale.modify",
    "acconage.stowage.create", "acconage.stowage.modify",
    "acconage.moyen.read", "acconage.reservation.create",
    "acconage.conteneur.create", "acconage.conteneur.modify",
    "acconage.manifeste.read", "acconage.manifeste.create", "acconage.manifeste.modify",
    "acconage.packing_list.create",
    "acconage.frais.read", "acconage.frais.create",
    "acconage.nettoyage.create", "acconage.nettoyage.modify",
    "acconage.dockers.read", "acconage.dockers.create", "acconage.dockers.modify",
    "acconage.dockers.delete",
)

# Explicitement HORS PORTEE de l'operateur, meme s'il est sur le quai :
_OPERATEUR_REFUSES = (
    "acconage.navire.create",      # registre navire = administratif
    "acconage.stowage.approve",    # valider l'arrimage engage la securite
    "acconage.moyen.create", "acconage.moyen.modify",  # registre des grues
    "acconage.connaissement.create", "acconage.connaissement.modify",  # B/L
    "acconage.frais.modify",       # contester un frais
    "acconage.dockers.approve",    # cloture = paie engagee
)


def _attentes():
    u = set(_codes_utilises())
    lecture = {c for c in u if c.endswith(".read")}
    chef = dict.fromkeys(u, True)
    transit = {c: (c in lecture) for c in u}
    declarant = {c: (c == "acconage.manifeste.read") for c in u}
    operateur = {c: False for c in u}
    for c in _OPERATEUR_AUTORISES_ROUTEUR:
        operateur[c] = True
    # Garde-fou interne : les deux listes doivent epuiser les 30 codes.
    assert set(_OPERATEUR_AUTORISES_ROUTEUR) | set(_OPERATEUR_REFUSES) == u
    assert not set(_OPERATEUR_AUTORISES_ROUTEUR) & set(_OPERATEUR_REFUSES)
    return {
        "CHEF_EXPLOITATION": chef,
        "OPERATEUR_ACCONAGE": operateur,
        "TRANSIT_PRINCIPAL": transit,
        "DECLARANT": declarant,
    }


@pytest.mark.parametrize("role", [
    "CHEF_EXPLOITATION", "OPERATEUR_ACCONAGE", "TRANSIT_PRINCIPAL", "DECLARANT",
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
    # Un droit que AUCUN role metier ne porte = endpoint mur, fonctionlement
    # inatteignable (seul le bypass admin l'atteindrait). Detecte, pas assume.
    for code in _codes_utilises():
        porteurs = [
            nom for nom, _l, _d, codes in ROLE_GRANTS if has_perm(codes, code)
        ]
        assert porteurs, f"aucun role ne porte {code}"


# ── 3. HTTP reel avec les roles metier ───────────────────────────────────────
def _utilisateur_avec_codes(codes, uid):
    return types.SimpleNamespace(
        id=uid, email=f"user{uid}@acconage.test", is_active=True,
        is_superuser=False, company_id=None, role_level=3,
        department_id=None,
        roles=[types.SimpleNamespace(
            permissions=[types.SimpleNamespace(code=c) for c in codes],
        )],
        accreditations=[],
    )


@pytest.fixture
def client_operateur(client):
    from app.main import app

    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: _utilisateur_avec_codes(
        _codes_role("OPERATEUR_ACCONAGE"), 61)
    try:
        yield client
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved


@pytest.fixture
def client_transit(client):
    from app.main import app

    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: _utilisateur_avec_codes(
        _codes_role("TRANSIT_PRINCIPAL"), 62)
    try:
        yield client
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved


def test_operateur_200_sur_liste_escales(client_operateur):
    r = client_operateur.get(f"{BASE}/escales")
    assert r.status_code == 200, r.text


def test_operateur_403_sur_valider_stowage(client_operateur):
    # Valider un plan d'arrimage engage la securite du chargement : acte du
    # chef. Le 403 (et non 404) prouve que le droit est verifie AVANT la base.
    r = client_operateur.put(f"{BASE}/stowage-plans/1/valider", json={})
    assert r.status_code == 403, r.text
    assert "acconage.stowage.approve" in r.text


def test_operateur_403_sur_emission_connaissement(client_operateur):
    # Le connaissement est un titre juridique : l'operateur ne l'emet pas.
    r = client_operateur.post(f"{BASE}/connaissements", json={})
    assert r.status_code == 403, r.text
    assert "acconage.connaissement.create" in r.text


def test_operateur_403_sur_cloture_dockers(client_operateur):
    # Cloturer la liste des dockers = paie engagee : approve, hors portee.
    r = client_operateur.post(f"{BASE}/escales/1/cloture-dockers", json={})
    assert r.status_code == 403, r.text


def test_operateur_200_sur_reservation_grue(client_operateur):
    # Reservation d'execution : l'operateur la porte (reservation.create).
    # Sans corps valide le handler repondrait 422 ; ici on verifie d'abord que
    # LA PORTE n'est pas fermee : statut != 403.
    r = client_operateur.post(f"{BASE}/grues/reservations", json={})
    assert r.status_code != 403, (
        "reservation.create doit etre accessible a l'operateur, pas refuse")


def test_transit_principal_200_lecture_403_ecriture(client_transit):
    # acconage.*.read : toutes les lectures, aucune ecriture.
    assert client_transit.get(f"{BASE}/escales").status_code == 200
    r = client_transit.post(f"{BASE}/escales", json={})
    assert r.status_code == 403, r.text
    assert "acconage.escale.create" in r.text


# ── 4. Migration 035 ─────────────────────────────────────────────────────────
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


def test_migration_035_seede_roles_quai_et_nouveaux_codes(tmp_path, monkeypatch):
    db_file = tmp_path / "mig035.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()

    command.upgrade(cfg, "035_rbac_acconage_grants")

    # Les codes neufs du batch 23 existent reels en base.
    for code in (
        "acconage.navire.read", "acconage.stowage.approve",
        "acconage.dockers.approve", "acconage.frais.create",
        "acconage.connaissement.create", "acconage.packing_list.create",
    ):
        n = _scalar(url, f"SELECT COUNT(*) FROM permissions WHERE code = '{code}'")
        assert n == 1, f"code {code} absent de la table permissions"

    for role in ("CHEF_EXPLOITATION", "OPERATEUR_ACCONAGE"):
        rid = _scalar(url, f"SELECT id FROM roles WHERE name = '{role}'")
        assert rid is not None, f"{role} doit etre cree par 035"
        liens = _scalar(
            url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {rid}")
        assert liens == len(_codes_role(role))

    # Idempotence : rejouer 035 ne duplique ni liens ni permissions.
    total_perms_avant = _scalar(url, "SELECT COUNT(*) FROM permissions")
    command.downgrade(cfg, "034_rbac_finance_grants")
    command.upgrade(cfg, "035_rbac_acconage_grants")
    assert _scalar(url, "SELECT COUNT(*) FROM permissions") == total_perms_avant
    for role in ("CHEF_EXPLOITATION", "OPERATEUR_ACCONAGE"):
        rid = _scalar(url, f"SELECT id FROM roles WHERE name = '{role}'")
        assert _scalar(
            url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {rid}"
        ) == len(_codes_role(role))


def test_migration_035_refuse_explicitement_base_sans_tables_rbac(tmp_path, monkeypatch):
    db_file = tmp_path / "mig035_guard.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()
    command.stamp(cfg, "034_rbac_finance_grants")
    with pytest.raises(RuntimeError) as exc:
        command.upgrade(cfg, "035_rbac_acconage_grants")
    msg = str(exc.value).lower()
    assert "permissions" in msg or "rbac" in msg, (
        "la garde doit nommer la precondition RBAC, pas echouer en silence")

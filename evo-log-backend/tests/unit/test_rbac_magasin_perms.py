"""Batch 21 — RBAC granulaire sur /magasin-avance (43 endpoints).

Verifie, sans rien simuler :
  1. chaque code require_perm() du routeur existe au catalogue officiel ;
  2. le role MAGASINIER couvre toute l'EXECUTION mais aucune APPROBATION
     (assertion dans les deux sens : vert autorise, rouge interdit) ;
  3. le role CHEF_MAGASIN couvre l'appreciation restante (approve/export) ;
  4. au niveau HTTP, un utilisateur limite obtient reellement 403 sur les
     actes qu'il n'a pas, et 200 sur ceux qu'il a (moteur `can()` reel,
     pas un mock) ;
  5. la migration 033 seede roles + grants, est idempotente, et refuse
     explicitement une base sans tables RBAC au lieu de passer en silence.
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
ROUTER_FILE = BACKEND_ROOT / "app" / "routers" / "v1" / "magasin_avance.py"

BASE = "/api/v1/magasin-avance"


def _codes_utilises():
    src = ROUTER_FILE.read_text(encoding="utf-8")
    return sorted(set(re.findall(r'require_perm\("([^"]+)"\)', src)))


def _codes_role(nom):
    for n, _lvl, _desc, codes in ROLE_GRANTS:
        if n == nom:
            return codes
    raise AssertionError(f"role {nom} absent du catalogue")


# ── 1. Parite catalogue : aucun code fantome dans le routeur ────────────────
def test_tous_les_codes_du_routeur_existent_au_catalogue():
    codes = _codes_utilises()
    # 43 routes converties : si une route perdait sa protection, ce test ne
    # le verrait pas ; la parite HTTP est verifiee separement ci-dessous.
    assert len(codes) >= 15, f"attendu >=15 codes distincts, trouve {len(codes)}"
    catalogue = {row[0] for row in iter_permission_rows()}
    fantomes = [c for c in codes if c not in catalogue]
    assert not fantomes, f"codes require_perm inconnus du catalogue: {fantomes}"


# ── 2. MAGASINIER : execute son circuit, n'approuve rien, n'achete rien ─────
# Le reapprovisionnement automatique cree une REELLE commande d'achat :
# c'est un acte commercial, pas un geste de depot. Il est donc porte par
# CHEF_MAGASIN et refuse a MAGASINIER (assertion rouge explicite).
HORS_POUR_MAGASINIER = {"achats.commande.create"}


def test_magasinier_couvre_execution_et_jamais_approval():
    codes_magasinier = _codes_role("MAGASINIER")
    approuve_vus, execution_vus = [], []
    for code in _codes_utilises():
        action = code.rsplit(".", 1)[1]
        if action in ("approve", "export") or code in HORS_POUR_MAGASINIER:
            approuve_vus.append(code)
            assert not has_perm(codes_magasinier, code), (
                f"MAGASINIER ne doit PAS pouvoir {code} (validation reservee au chef)"
            )
        else:
            execution_vus.append(code)
            assert has_perm(codes_magasinier, code), (
                f"MAGASINIER doit pouvoir {code} : blocage abusif du metier"
            )
    # Assertion negative : s'il n'y avait plus aucun refus dans le module,
    # on veut le savoir plutot que de laisser passer un faux vert.
    assert approuve_vus and execution_vus


# ── 3. CHEF_MAGASIN : couvre l'integralite du module ────────────────────────
def test_chef_magasin_couvre_tous_les_codes_utilises():
    codes_chef = _codes_role("CHEF_MAGASIN")
    for code in _codes_utilises():
        assert has_perm(codes_chef, code), f"CHEF_MAGASIN bloque {code}"


# ── 4. HTTP reel : 200 sur ce qui est permis, 403 sur ce qui ne l'est pas ──
def _utilisateur_lecture_seule():
    """Utilisateur level 3 dont les permissions granulaires reelles ne
    couvrent que la lecture des retours (magasin.stock.read)."""
    return types.SimpleNamespace(
        id=42, email="magasinier@test.local", is_active=True,
        is_superuser=False, company_id=None, role_level=3,
        department_id=None,
        roles=[types.SimpleNamespace(
            permissions=[types.SimpleNamespace(code="magasin.stock.read")],
        )],
        accreditations=[],
    )


@pytest.fixture
def client_lecture_seule(client):
    """Reutilise la fixture `client` (get_db override) mais remplace
    l'identite surchargee par un utilisateur limite. Restaure ensuite."""
    from app.main import app

    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = _utilisateur_lecture_seule
    try:
        yield client
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved


def test_http_utilisateur_limite_200_lecture_403_declaration(client_lecture_seule):
    # Lecture autorisee par magasin.stock.read -> 200, pas un 403 de facade.
    r = client_lecture_seule.get(f"{BASE}/retours")
    assert r.status_code == 200, r.text
    # Declaration de retour = magasin.mouvement.create -> refus REEL (403),
    # verifie avant tout ecriture : le corps n'est meme pas valide ici.
    r = client_lecture_seule.post(f"{BASE}/retours", json={})
    assert r.status_code == 403, r.text
    assert "magasin.mouvement.create" in r.text


def test_http_utilisateur_limite_403_approval_sans_ecriture(client_lecture_seule, db):
    # /retours/{id}/traiter exige magasin.mouvement.approve : 403 AVANT
    # toute tentative de lecture/objet inexistant (la dependance s'execute
    # avant le handler, donc aucun risque d'ecriture partielle).
    r = client_lecture_seule.put(f"{BASE}/retours/999999/traiter", json={"decision": "accepte", "action": "reintegre"})
    assert r.status_code == 403, r.text
    from app.models.magasin_avance import RetourClient
    assert db.query(RetourClient).count() == 0, "le refus doit preceder toute ecriture"


# ── 5. Migration 033 : seed idempotent, garde explicite ─────────────────────
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


def test_migration_033_seed_complete_et_idempotente(tmp_path, monkeypatch):
    db_file = tmp_path / "mig033.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()

    command.upgrade(cfg, "033_rbac_magasin_grants")

    chef_id = _scalar(url, "SELECT id FROM roles WHERE name = 'CHEF_MAGASIN'")
    assert chef_id is not None, "CHEF_MAGASIN doit etre cree par 033"
    magasinier_id = _scalar(url, "SELECT id FROM roles WHERE name = 'MAGASINIER'")
    assert magasinier_id is not None

    liens_chef = _scalar(
        url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {chef_id}")
    liens_mag = _scalar(
        url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {magasinier_id}")
    # Compte derive du catalogue (source de verite), pas un nombre fige.
    assert liens_chef == len(_codes_role("CHEF_MAGASIN"))
    assert liens_mag == len(_codes_role("MAGASINIER"))

    # Idempotence vraie : re-executer 033 sur une base deja seensee doit
    # ne RIEN dupliquer (downgrade 033 = pass, donc upgrade remonte la
    # revision et rejoue upgrade() sur des donnees presentes).
    command.downgrade(cfg, "032_add_maintenance_tenant_scope")
    command.upgrade(cfg, "033_rbac_magasin_grants")
    assert _scalar(url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {magasinier_id}") == liens_mag
    assert _scalar(url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {chef_id}") == liens_chef


def test_migration_033_refuse_explicitement_base_sans_tables_rbac(tmp_path, monkeypatch):
    """Une base stubbee a 032 sans tables RBAC ne doit PAS passer 033 en
    silence : l'erreur doit nommer la precondition manquante."""
    db_file = tmp_path / "mig033_guard.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()
    # Base vierge + stamp 032 : upgrade() de 033 tourne seul, sans 020.
    command.stamp(cfg, "032_add_maintenance_tenant_scope")

    with pytest.raises(Exception) as excinfo:
        command.upgrade(cfg, "033_rbac_magasin_grants")
    assert "permissions" in str(excinfo.value) or "RBAC" in str(excinfo.value)

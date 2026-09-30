"""Batch 22 — RBAC granulaire sur /api/v1/finance (37 endpoints).

Meme discipline que le batch 21 :
  1. parite catalogue : aucun code fantome dans le routeur ;
  2. MATRICE COMPLETE role x code : pour les 24 codes utilises, chaque role
     finance a une attente explicite (autorise OU refuse), calculee par le
     VRAI moteur has_perm() — pas un mock, pas un sous-ensemble choisi ;
  3. HTTP reel : caissier = 200 sur ses encaissements, 403 sur la creation
     de facture (le refus precede toute ecriture) ;
  4. migration 034 : seeds CAISSIER + codes neufs du catalogue, idempotente,
     garde explicite sur base sans tables RBAC.
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
ROUTER_FILE = BACKEND_ROOT / "app" / "routers" / "v1" / "finance.py"

BASE = "/api/v1/finance"


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
    assert len(codes) == 24, f"attendu 24 codes distincts, trouve {len(codes)}"
    catalogue = {row[0] for row in iter_permission_rows()}
    fantomes = [c for c in codes if c not in catalogue]
    assert not fantomes, f"codes require_perm inconnus du catalogue: {fantomes}"


# ── 2. Matrice complete role x code, attendue explicitement ─────────────────
# Chaque attente est une DECISION METIER relisible, pas le resultat d'un
# algorithme : si un code change de camp, ce test rouge force la discussion.
def _attentes():
    u = set(_codes_utilises())
    lecture = {c for c in u if c.endswith(".read")}
    directeur = dict.fromkeys(u, True)
    chef = dict.fromkeys(u, True)
    # La saisie de tresorerie est le travail du caissier/comptable ; le chef
    # comptable la lit et l'approuve (mouvement.approve, hors ce routeur).
    for c in ("tresorerie.mouvement.create", "tresorerie.mouvement.modify"):
        chef[c] = False
    comptable = {c: False for c in u}
    for c in (
        "comptabilite.plan_comptable.read", "comptabilite.journal.create",
        "comptabilite.journal.modify", "comptabilite.exercice.read",
        "facturation.facture.create", "facturation.facture.modify",
        "facturation.facture.read", "facturation.facture.export",
        "tresorerie.mouvement.create", "tresorerie.mouvement.modify",
        "tresorerie.mouvement.read",
    ):
        comptable[c] = True
    caissier = {c: False for c in u}
    for c in (
        "tresorerie.mouvement.create", "tresorerie.mouvement.modify",
        "tresorerie.mouvement.read", "facturation.facture.read",
    ):
        caissier[c] = True
    auditeur = {c: (c in lecture) for c in u}
    return {
        "DIRECTEUR_FINANCIER": directeur,
        "CHEF_COMPTABLE": chef,
        "COMPTABLE": comptable,
        "CAISSIER": caissier,
        "AUDITEUR": auditeur,
    }


@pytest.mark.parametrize("role", [
    "DIRECTEUR_FINANCIER", "CHEF_COMPTABLE", "COMPTABLE", "CAISSIER", "AUDITEUR",
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


# ── 3. HTTP reel avec un caissier ────────────────────────────────────────────
def _utilisateur_caissier():
    return types.SimpleNamespace(
        id=43, email="caissier@test.local", is_active=True,
        is_superuser=False, company_id=None, role_level=3,
        department_id=None,
        roles=[types.SimpleNamespace(
            permissions=[
                types.SimpleNamespace(code=c) for c in _codes_role("CAISSIER")
            ],
        )],
        accreditations=[],
    )


@pytest.fixture
def client_caissier(client):
    from app.main import app

    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = _utilisateur_caissier
    try:
        yield client
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved


def test_caissier_200_sur_ses_encaissements(client_caissier):
    r = client_caissier.get(f"{BASE}/encaissements")
    assert r.status_code == 200, r.text


def test_caissier_403_sur_creation_facture_avant_ecriture(client_caissier, db):
    r = client_caissier.post(f"{BASE}/factures", json={})
    assert r.status_code == 403, r.text
    assert "facturation.facture.create" in r.text
    from app.models.finance_ohada import FactureNew
    assert db.query(FactureNew).count() == 0, "le refus doit preceder toute ecriture"


def test_caissier_403_sur_cloture_exercice(client_caissier):
    # cloturer un exercice = comptabilite.exercice.approve : hors de portee.
    r = client_caissier.put(f"{BASE}/exercices/1/cloturer", json={})
    assert r.status_code == 403, r.text


# ── 4. Migration 034 ─────────────────────────────────────────────────────────
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


def test_migration_034_seede_caissier_et_nouveaux_codes(tmp_path, monkeypatch):
    db_file = tmp_path / "mig034.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()

    command.upgrade(cfg, "034_rbac_finance_grants")

    # Les codes neufs du batch 22 existent reels en base.
    for code in (
        "comptabilite.plan_comptable.read", "comptabilite.exercice.approve",
        "comptabilite.compte_resultat.create", "fiscalite.declarations.modify",
        "comptabilite.bilan.create",
    ):
        n = _scalar(url, f"SELECT COUNT(*) FROM permissions WHERE code = '{code}'")
        assert n == 1, f"code {code} absent de la table permissions"

    caissier_id = _scalar(url, "SELECT id FROM roles WHERE name = 'CAISSIER'")
    assert caissier_id is not None, "CAISSIER doit etre cree par 034"
    liens = _scalar(
        url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {caissier_id}")
    assert liens == len(_codes_role("CAISSIER"))

    # Idempotence : rejouer 034 ne duplique ni liens ni permissions.
    total_perms_avant = _scalar(url, "SELECT COUNT(*) FROM permissions")
    command.downgrade(cfg, "033_rbac_magasin_grants")
    command.upgrade(cfg, "034_rbac_finance_grants")
    assert _scalar(url, "SELECT COUNT(*) FROM permissions") == total_perms_avant
    assert _scalar(
        url, f"SELECT COUNT(*) FROM role_permissions WHERE role_id = {caissier_id}") == liens


def test_migration_034_refuse_explicitement_base_sans_tables_rbac(tmp_path, monkeypatch):
    db_file = tmp_path / "mig034_guard.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()
    command.stamp(cfg, "033_rbac_magasin_grants")

    with pytest.raises(Exception) as excinfo:
        command.upgrade(cfg, "034_rbac_finance_grants")
    assert "permissions" in str(excinfo.value) or "RBAC" in str(excinfo.value)

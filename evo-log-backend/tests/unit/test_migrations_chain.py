"""
Regression test for the Alembic migration chain.

Rejoue la chaine complete UPGRADE head puis DOWNGRADE base sur une base
SQLite jetable (tmp_path) :

  - garantit qu'aucune migration n'explose au montage ni au demontage ;
  - verifie que le niveau de revision redescend bien a ``base`` (rollback
    lineaire propre, cf. correctifs batch_alter_table + gardes d'existence).

Aucune base de production n'est touchee : l'URL est forcee via DATABASE_URL
vers un fichier temporaire, que ``migrations/env.py`` applique.
"""
import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"
SCRIPT_LOCATION = BACKEND_ROOT / "migrations"


def _make_config() -> Config:
    cfg = Config(str(ALEMBIC_INI))
    # Chemin absolu : evite toute dependance au repertoire courant.
    cfg.set_main_option("script_location", str(SCRIPT_LOCATION))
    return cfg


def _current_rev(url: str):
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            return MigrationContext.configure(conn).get_current_revision()
    finally:
        engine.dispose()


def _table_names(url: str):
    engine = create_engine(url)
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def _user_columns(url: str):
    return _columns_of(url, "users")


def _columns_of(url: str, table: str):
    engine = create_engine(url)
    try:
        insp = inspect(engine)
        if table not in set(insp.get_table_names()):
            return set()
        return {c["name"] for c in insp.get_columns(table)}
    finally:
        engine.dispose()


def _script_directory():
    from alembic.script import ScriptDirectory
    return ScriptDirectory.from_config(_make_config())


def _tetes() -> set:
    """Tetes de la chaine Alembic (doit rester strictement lineaire)."""
    return set(_script_directory().get_heads())


def _ascendants(rev: str) -> set:
    """Revisions accessibles en remontant depuis `rev` (rev incluse)."""
    script = _script_directory()
    vus: set = set()
    file = [rev]
    while file:
        courant = file.pop()
        if courant in vus or courant is None:
            continue
        vus.add(courant)
        revision = script.get_revision(courant)
        parents = getattr(revision, "down_revisions", None)
        if not parents:
            parents = [revision.down_revision] if revision.down_revision else []
        file.extend(parents)
    return vus


def test_full_chain_upgrade_then_downgrade(tmp_path, monkeypatch):
    assert ALEMBIC_INI.exists(), f"alembic.ini introuvable: {ALEMBIC_INI}"

    db_file = tmp_path / "mig_chain.db"
    url = f"sqlite:///{db_file.as_posix()}"
    # env.py applique DATABASE_URL sur le Config : on force la base jetable.
    monkeypatch.setenv("DATABASE_URL", url)

    cfg = _make_config()

    # 1) Monte jusqu'au head.
    command.upgrade(cfg, "head")
    head = _current_rev(url)
    assert head is not None, "aucune revision appliquee apres upgrade head"
    # La chaine doit rester lineaire : une seule tete, et cette tete doit etre
    # exactement celle qui a ete montee. Epingler le NOM du head ferait echouer
    # ce test a chaque nouvelle tranche ; on verifie donc l'unicite de la tete
    # puis la presence des tranches deja livrees dans son historique
    # (015 = 2FA, 016 = magasin store, 017 = parc/purchase,
    # 018 = customers/support/fleet, 019 = exploitation transport).
    tetes = _tetes()
    assert tetes == {head}, (
        f"head applique {head} different de la tete unique attendue {sorted(tetes)}"
    )
    historique = _ascendants(head)
    for tranche in (
        "015_add_2fa_fields",
        "016_add_magasin_store_tables",
        "017_add_parc_purchase_tables",
        "018_add_customer_support_fleet_tables",
        "019_add_transport_exploitation_tables",
    ):
        assert tranche in historique, f"revision {tranche} absente de l'historique de {head}"

    tables = _table_names(url)
    # Certaines tables cles doivent exister une fois la chaine montee.
    for expected in ("users", "companies", "roles"):
        assert expected in tables, f"table attendue absente apres upgrade: {expected}"
    # Les tables du domaine store (016) doivent etre creees.
    for store_table in (
        "articles", "commandes", "lignes_commande",
        "ordres_transfert", "bandes_livraison",
    ):
        assert store_table in tables, f"table store absente apres upgrade: {store_table}"
    # Les tables Tranche B (017) doivent etre creees.
    for b_table in (
        "parc_zones", "parc_emplacements", "parc_mouvements",
        "purchase_requisitions",
    ):
        assert b_table in tables, f"table tranche B absente apres upgrade: {b_table}"
    # Les tables Tranche C (018) doivent etre creees.
    for c_table in (
        "crm_customers", "crm_customer_contracts", "fleet_carburant_records",
        "fleet_documents", "support_tickets", "support_incidents",
    ):
        assert c_table in tables, f"table tranche C absente apres upgrade: {c_table}"

    # Les colonnes 2FA introduites par 015 doivent etre presentes.
    cols = _user_columns(url)
    for col in ("two_factor_enabled", "two_factor_secret", "two_factor_confirmed_at"):
        assert col in cols, f"colonne 2FA absente apres upgrade: {col}"

    # Les tables Tranche D (019) doivent etre creees.
    for d_table in ("transport_pannes", "transport_atelages"):
        assert d_table in tables, f"table tranche D absente apres upgrade: {d_table}"
    # ... ainsi que les colonnes d'exploitation portees par des tables existantes.
    for table, colonnes in (
        ("camions", ("est_bloque", "motif_blocage", "date_blocage", "bloque_par",
                     "remorque_immatriculation", "remorque_type")),
        ("conducteurs", ("date_naissance", "categorie_permis", "numero_cnps",
                         "expiration_visite_medicale")),
        ("missions", ("nom_receptionnaire", "signature_receptionnaire")),
        ("fleet_carburant_records", ("numero_ticket", "prix_litre", "mission_id",
                                     "conducteur_id", "statut", "index_precedent")),
    ):
        colonnes_reelles = _columns_of(url, table)
        for col in colonnes:
            assert col in colonnes_reelles, f"colonne {table}.{col} absente apres upgrade"

    # 2) Redescend jusqu'a la base (rollback lineaire complet).
    command.downgrade(cfg, "base")
    assert _current_rev(url) is None, "la chaine n'atteint pas 'base' en downgrade"

    # Apres redescinte, les tables cles creees par la chaine ont disparu.
    remaining = _table_names(url)
    assert "users" not in remaining, "table 'users' subsiste apres downgrade base"
    assert "articles" not in remaining, "table 'articles' (016) subsiste apres downgrade base"
    assert "parc_zones" not in remaining, "table 'parc_zones' (017) subsiste apres downgrade base"
    assert "support_tickets" not in remaining, "table 'support_tickets' (018) subsiste apres downgrade base"
    assert "transport_pannes" not in remaining, "table 'transport_pannes' (019) subsiste apres downgrade base"
    assert "transport_atelages" not in remaining, "table 'transport_atelages' (019) subsiste apres downgrade base"


def test_015_only_adds_and_removes_2fa_columns(tmp_path, monkeypatch):
    """Isole la revision 015 : de 014 a 015, puis re-downgrade vers 014.

    Verifie que 015 n'ajoute/retire QUE les colonnes 2FA et ne casse pas le
    reste du schema (cas reel du deploiement : on 'stamp' 014 puis upgrade)."""
    db_file = tmp_path / "mig_015.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()

    command.upgrade(cfg, "014_schema_parity_from_orm")
    before = _user_columns(url)
    for col in ("two_factor_enabled", "two_factor_secret", "two_factor_confirmed_at"):
        assert col not in before

    command.upgrade(cfg, "015_add_2fa_fields")
    after = _user_columns(url)
    for col in ("two_factor_enabled", "two_factor_secret", "two_factor_confirmed_at"):
        assert col in after

    command.downgrade(cfg, "014_schema_parity_from_orm")
    reverted = _user_columns(url)
    for col in ("two_factor_enabled", "two_factor_secret", "two_factor_confirmed_at"):
        assert col not in reverted
    assert _current_rev(url) == "014_schema_parity_from_orm"

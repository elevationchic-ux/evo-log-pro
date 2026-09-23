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

    tables = _table_names(url)
    # Certaines tables cles doivent exister une fois la chaine montee.
    for expected in ("users", "companies", "roles"):
        assert expected in tables, f"table attendue absente apres upgrade: {expected}"

    # 2) Redescend jusqu'a la base (rollback lineaire complet).
    command.downgrade(cfg, "base")
    assert _current_rev(url) is None, "la chaine n'atteint pas 'base' en downgrade"

    # Apres redescinte, les tables cles creees par la chaine ont disparu.
    remaining = _table_names(url)
    assert "users" not in remaining, "table 'users' subsiste apres downgrade base"

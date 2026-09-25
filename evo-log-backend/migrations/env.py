"""Alembic environment configuration"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, inspect, text
from alembic import context
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import Base
from app.models import *  # Import all models

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# DATABASE_URL (Railway, Docker, local) prime sur la valeur encodee dans
# alembic.ini : sans ca, `alembic upgrade head` applique les migrations a la
# base SQLite du depot meme quand la vraie base est Postgres ailleurs.
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # set_main_option passe par l'interpolation ConfigParser : echapper les %.
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def _ensure_version_column_wide(connection) -> None:
    """Garantir que alembic_version.version_num accepte les identifiants de
    revision longs (> 32 caracteres).

    Alembic cree la colonne en VARCHAR(32) par defaut ; Postgres tronque alors
    et leve StringDataRightTruncation sur des revisions comme
    '018_add_customer_support_fleet_tables' (37) ou
    '020_rbac_granulaire_accreditations' (34). SQLite ignore les bornes
    VARCHAR, donc l'operation est specifique Postgres.

    - Table existante -> ALTER COLUMN ... TYPE VARCHAR(255).
    - Table absente   -> la pre-creer large pour qu'un 'upgrade head' en une
      seule passe sur base vierge fonctionne (alembic.recreate est checkfirst).
    """
    try:
        dialect = connection.dialect.name
        if dialect != "postgresql":
            return
        inspector = inspect(connection)
        if "alembic_version" in inspector.get_table_names():
            row = connection.execute(text(
                "SELECT character_maximum_length FROM information_schema.columns "
                "WHERE table_name = 'alembic_version' AND column_name = 'version_num'"
            )).first()
            current_len = row[0] if row else None
            if current_len is not None and current_len < 255:
                connection.execute(text(
                    "ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(255)"
                ))
                connection.commit()
        else:
            connection.execute(text(
                "CREATE TABLE IF NOT EXISTS alembic_version ("
                "version_num VARCHAR(255) NOT NULL, "
                "CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"
            ))
            connection.commit()
    except Exception as exc:  # ne jamais bloquer une migration pour ca
        print(f"[env.py] avertissement: alembic_version non elargi: {exc}")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _ensure_version_column_wide(connection)
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""Garde-fou PostgreSQL : aucun DDL ORM ne doit emettre de modificateur de
type sur TEXT (RAILWAY = PostgreSQL ; `TEXT(2000)` y est une erreur de syntaxe,
toleree uniquement par SQLite).

Cas reel (2026-10-08) : la migration 028_full_orm_parity materialise les tables
absentes via metadata.create_all(). Un modele declarant Column(Text(2000)) fait
echouer `alembic upgrade head` des la premiere table fautive (hs_classifications),
l'entrypoint bloque sur la migration, le conteneur crash-loop, l'app n'ecoute
jamais : le proxy Railway renvoie ses erreurs sans en-tete CORS et le navigateur
crie « blocked by CORS » sur evo-log-pro.vercel.app alors que le CORS n'y est
pour rien. Les listes de nomenclatures cote front restent vides.

Double protection testee ici :
  1. la regle de compilation @compiles(Text, "postgresql") de
     app/core/database.py force `TEXT` quelle que soit la longueur declaree ;
  2. le DDL complete de TOUTES les tables de la metadata doit compiler pour le
     dialecte PostgreSQL sans modificateur illegal.

Ce test ne touche aucune base : pure compilation SQLAlchemy.
"""
import re
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

# meme convention que les tests unitaires : base memoire, Redis coupe
# (setdefault : une DATABASE_URL exportee, ex. CI Postgres, est respectee)
import os  # noqa: E402
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "disabled")

from app.core.database import Base  # noqa: E402  (enregistre @compiles Text->PG)

_ILLEGAL_PG = re.compile(r"\bTEXT\s*\(\s*\d", re.IGNORECASE)


def _charger_tous_les_modeles():
    """Meme scan que 028_full_orm_parity : la reference du test doit couvrir
    les 47+ modules du paquet, pas seulement app/models/__init__.py."""
    dossier = Path(__file__).resolve().parents[2] / "app" / "models"
    import importlib
    for fichier in sorted(dossier.glob("*.py")):
        if fichier.name == "__init__.py":
            continue
        importlib.import_module("app.models.%s" % fichier.name[:-3])


@pytest.fixture(scope="module", autouse=True)
def metadata_complete():
    _charger_tous_les_modeles()
    assert len(Base.metadata.tables) > 800, (
        "metadata incompleite : le scan des modeles ne couvre pas tout app/models"
    )


def test_compiles_pg_strips_text_length():
    """La regle de securite doit neutraliser tout Text(n) futur, a la source."""
    pg = postgresql.dialect()
    assert str(sa.Text(2000).compile(dialect=pg)) == "TEXT"
    assert str(sa.Text().compile(dialect=pg)) == "TEXT"
    # SQLite (dev local) reste inchange :
    assert "TEXT(2000)" in str(sa.Text(2000).compile())


def test_all_tables_compile_for_postgresql(metadata_complete):
    pg = postgresql.dialect()
    fautives = []
    for nom, table in sorted(Base.metadata.tables.items()):
        try:
            ddl = str(CreateTable(table).compile(dialect=pg))
        except Exception as exc:
            fautives.append("%s : compilation impossible (%s)" % (nom, exc))
            continue
        if _ILLEGAL_PG.search(ddl):
            fautives.append("%s : TEXT(n) avec modificateur interdit sur PG" % nom)
    assert not fautives, (
        "DDL non compatible PostgreSQL (ferait crash-loop l'entrypoint "
        "Railway via alembic 028, lu « CORS » par le navigateur) :\n"
        + "\n".join(fautives)
    )

#!/bin/sh
# ============================================================================
# Entrypoint de production : rend le schema Alembic-pilote AU DEMARRAGE, puis
# lance l'API. Concu pour etre SUR aussi bien sur une base VIERGE que sur une
# base deja "bootstrapee" par l'ancien Base.metadata.create_all() (cas de la
# prod actuelle), sans jamais toucher aux donnees existantes.
#
# Regles :
#   - alembic_version presente  -> alembic upgrade head (incrementaire normal)
#   - pas d'alembic_version mais table 'users' existante (base heritee de
#     create_all) -> on "stamp" a 014_schema_parity_from_orm (le point de
#     parite ORM) PUIS on monte a head : seules les revisions vraiment
#     nouvelles (ex. 015 2FA) sont appliquees. Aucune table existante n'est
#     recreee, aucune donnee n'est ecrasee.
#   - base totalement vide -> alembic upgrade head rejoue toute la chaine.
#
# Toute echec de migration est BLOQUANT (on n'eleve pas une API sur un schema
# faux/partiel).
# ============================================================================
set -e

python <<'PY'
import os, sys
from sqlalchemy import create_engine, inspect

url = os.environ.get("DATABASE_URL")
if not url:
    print("[entrypoint] DATABASE_URL absent ; migration ignoree (dev sqlite?).")
    sys.exit(0)

# alembic attend postgresql:// ; Railway fournit parfois postgresql+... ou
# des URLs heroku postgres:// -> normalisation minimale.
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url)
insp = inspect(engine)
tables = set(insp.get_table_names())

if "alembic_version" in tables:
    mode = "upgrade"
elif "users" in tables:
    mode = "stamp014+upgrade"
else:
    mode = "upgrade"

with open("/tmp/_alembic_mode", "w") as f:
    f.write(mode)
print(f"[entrypoint] mode de migration detecte : {mode}")
PY

MODE="$(cat /tmp/_alembic_mode 2>/dev/null || echo upgrade)"

if [ "$MODE" = "stamp014+upgrade" ]; then
    echo "[entrypoint] Base heritee de create_all -> stamp 014_schema_parity_from_orm"
    alembic stamp 014_schema_parity_from_orm
fi

echo "[entrypoint] alembic upgrade head"
alembic upgrade head

echo "[entrypoint] demarrage uvicorn sur port ${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}"

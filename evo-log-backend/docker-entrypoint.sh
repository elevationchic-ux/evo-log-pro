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

# ----------------------------------------------------------------------------
# Migration SERIALIZÉE par verrou advisory PostgreSQL.
# Railway peut demarrer plusieurs conteneurs en concurrence (relances sur
# ON_FAILURE + nouveaux deploys declenches par l'auto-push). Si deux conteneurs
# lancent `alembic upgrade head` en meme temps, la migration 028 (qui
# materialise ~639 tables via create_all) se retrouve dans DEUX transactions
# concurrentes : la seconde recoit « relation already exists » / deadlock quand
# la premiere commit, donc ROLLBACK complet, set -e tue le conteneur, Railway le
# relance, et la chaine repart de 024 en boucle. L'app ne se stabilise jamais ->
# le proxy renvoie ses 502 sans en-tete CORS, lus « No Access-Control-Allow-Origin
# » par le navigateur (listes de nomenclatures vides). serialized_migrate.py
# prend un pg_advisory_lock de session avant de lancer alembic : un seul
# conteneur migre a la fois, les suivants trouvent la base a head (no-op
# instantane). Le code retour reste propage : une VRAIE erreur de migration est
# toujours BLOQUANTE (on ne supprime que la fausse erreur due a la concurrence).
# ----------------------------------------------------------------------------
echo "[entrypoint] alembic upgrade head (serialise PG advisory lock, mode=$MODE)"
python scripts/serialized_migrate.py "$MODE"

# ----------------------------------------------------------------------------
# Auto-reparation NON-BLOQUANTE du chemin de login. Le `SELECT users` de
# /auth/login projette TOUTES les colonnes du modele User ; si la table est
# partielement desynchronisee (colonne declaree par l'ORM jamais posee sur la
# base), le login leve une erreur 500 pour n'importe quel identifiant, meme
# inexistant, alors que /health (SELECT 1) reste vert. Ce script refait la
# parite `users` (colonnes NULLABLES uniquement, idempotent, non destructif)
# et garantit les comptes de secours.
#
# STRICTEMENT NON-BLOQUANT : on ne doit JAMAIS empecher uvicorn de demarrer a
# cause de cette etape facultative. On la BORNE EN PLUS dans le temps
# (`timeout 90`) : sous un redéploiement frequent, une reparation qui traine
# (verrou BDD, introspection sur grosse base) ne doit pas repousser l'ecoute
# HTTP et creer une fenetre de 502. `timeout` renvoie 124 a l'echéance -> le `||`
# absorbe le code retour (set -e ne coupe pas une commande suivie de `||`).
# ----------------------------------------------------------------------------
echo "[entrypoint] auto-reparation login/users (non-bloquante, <=90s)"
if command -v timeout >/dev/null 2>&1; then
    timeout 90 python scripts/ensure_login_railway.py || echo "[entrypoint] reparation ignoree (non-fatale ou timeout)"
else
    python scripts/ensure_login_railway.py || echo "[entrypoint] reparation ignoree (non-fatale)"
fi

echo "[entrypoint] demarrage uvicorn sur port ${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}"

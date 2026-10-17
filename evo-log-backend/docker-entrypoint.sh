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

# ----------------------------------------------------------------------------
# PATIENCE POSTGRESQL : Railway demarre tres souvent ce conteneur AVANT que
# Postgres ait fini son initialisation ("Connection refused") ou pendant sa
# reprise apres un redemarrage ("FATAL: the database system is starting up").
# Sans attente, l'introspection et les migrations ci-dessous leves par
# `inspect(engine)` declenchent une OperationalError ; `set -e` tue alors le
# conteneur, Railway le relance (restartPolicy ON_FAILURE) et le log se
# remplit de tracebacks identiques en boucle. On boucle donc ici jusqu'a ce
# que la base accepte une vraie requete, avec un delai BORNE et sans traceback
# parasite (un simple message "pas encore pret" par essai).
# ----------------------------------------------------------------------------
export DB_WAIT_TIMEOUT="${DB_WAIT_TIMEOUT:-120}"
echo "[entrypoint] attente de la base PostgreSQL (max ${DB_WAIT_TIMEOUT}s)..."
python <<'PY'
import os, sys, time
import sqlalchemy as sa
from sqlalchemy.pool import NullPool

raw = os.environ.get("DATABASE_URL", "")
if not raw:
    print("[entrypoint] DATABASE_URL absent ; attente ignoree (dev sqlite?).")
    sys.exit(0)
# alembic attend postgresql:// ; Railway fournit parfois des URLs heroku
# postgres:// -> normalisation minimale.
if raw.startswith("postgres://"):
    raw = raw.replace("postgres://", "postgresql://", 1)

timeout = float(os.environ.get("DB_WAIT_TIMEOUT", "120"))
deadline = time.time() + timeout
engine = sa.create_engine(
    raw,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args={"connect_timeout": 5},
)

attempt = 0
while True:
    attempt += 1
    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        print("[entrypoint] PostgreSQL pret (essai %d)." % attempt)
        engine.dispose()
        sys.exit(0)
    except Exception as exc:
        lines = str(exc).strip().splitlines()
        short = lines[-1] if lines else exc.__class__.__name__
        remaining = deadline - time.time()
        if remaining <= 0:
            print("[entrypoint] TIMEOUT: PostgreSQL indisponible apres %ss "
                  "(%d essais) : %s" % (int(timeout), attempt, short),
                  file=sys.stderr)
            engine.dispose()
            sys.exit(1)
        print("[entrypoint] PostgreSQL pas encore pret (essai %d) : %s ; "
              "nouvelle tentative..." % (attempt, short), file=sys.stderr)
        time.sleep(min(3.0, max(0.5, remaining)))
PY

python <<'PY'
import os, sys, time
from sqlalchemy import create_engine, exc as sa_exc, inspect

url = os.environ.get("DATABASE_URL")
if not url:
    print("[entrypoint] DATABASE_URL absent ; migration ignoree (dev sqlite?).")
    sys.exit(0)

# alembic attend postgresql:// ; Railway fournit parfois postgresql+... ou
# des URLs heroku postgres:// -> normalisation minimale.
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url, pool_pre_ping=True)

# Filet de securite : on attend quelques secondes de plus si la base re-echoe
# pile pendant l'introspection (redemarrage Postgres en cours). On n'imprime
# JAMAIS le traceback brut, seulement une ligne concise.
tables = None
last_err = None
for attempt in range(1, 6):
    try:
        insp = inspect(engine)
        tables = set(insp.get_table_names())
        break
    except sa_exc.OperationalError as e:
        last_err = str(e).strip().splitlines()[-1] if str(e).strip() else "OperationalError"
        print("[entrypoint] introspection indisponible (essai %d/5) : %s" % (attempt, last_err),
              file=sys.stderr)
        time.sleep(3)

if tables is None:
    print("[entrypoint] ECHEC introspection apres 5 essais : %s" % last_err,
          file=sys.stderr)
    sys.exit(1)

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

"""Migration Alembic SERIALIZ EE par verrou advisory PostgreSQL.

POURQUOI CE SCRIPT EXISTE (cas reel 2026-10-08, prod Railway) :
    L'entrypoint lance `alembic upgrade head` PUIS uvicorn, et toute echec de
    migration est BLOQUANT (set -e). Or Railway peut demarrer PLUSIEURS
    conteneurs en concurrence (redemarrages sur ON_FAILURE + nouveaux deploys
    declenches par l'auto-push toutes les ~2 min). Chacun lit alembic_version a
    son propre instant (tous voient 024) et lance la chaine complete, y compris
    la migration 028 qui materialise ~639 tables via metadata.create_all().

    Deux transactions concurrentes qui creent les MEMES tables : la seconde se
    bloque sur les verrous DDL de la premiere, puis recoit « relation already
    exists » / deadlock quand la premiere commit -> ROLLBACK de toute la
    deuxieme transaction (le schema Postgres est transactionnel). Le conteneur
    sort en erreur (set -e), Railway le relance, et la boucle recommence : le
    log montre 028 recreeant « 639 tables » en boucle, repartant toujours de 024.
    L'app n'atteint JAMAIS un etat stable chauffe -> le proxy Railway renvoie
    ses 502/« Application failed to respond » SANS en-tete CORS, que le
    navigateur lit a tort « No Access-Control-Allow-Origin » (les listes de
    nomenclatures du front restent donc vides).

CE QUE FAIT CE SCRIPT :
    Il prend un verrou advisory de SESSION PostgreSQL (pg_advisory_lock) sur UNE
    connexion dediee, PUIS lance `alembic` en sous-processus tant que le verrou
    est tenu. Un second conteneur qui appelle ce meme script BLOQUE sur
    pg_advisory_lock jusqu'a ce que le premier ait fini ; quand il obtient le
    verrou, alembic_version est deja a head, donc `upgrade head` est un no-op
    quasi instantane. resultat : UNE SEULE migration a la fois, plus jamais de
    course ni de rollback mutuel.

    - Le verrou est de SESSION : il se libere automatiquement si le processus
      qui le detient meurt (connexion fermee par Postgres). Pas de verrou
      orphelin persistant apres un crash.
    - Sur SQLite (dev/test) il n'y a pas d'advisory lock : le script execute
      alembic directement (une base fichier de dev n'est pas partagee entre
      conteneurs).
    - Le code retour du sous-processus est PROPAGE : une vraie erreur de
      migration reste BLOQUANTE (on ne diminue aucune garde de securite ; on
      supprime seulement la fausse erreur due a la concurrence).

Usage (entrepoint) : python scripts/serialized_migrate.py [MODE]
    MODE = "upgrade" (defaut) ou "stamp014+upgrade".
"""
import os
import subprocess
import sys

# Cle du verrou advisory : constante arbitraire, unique pour ce projet. Deux
# services differents ne doivent pas partager la meme cle ; celle-ci est choisie
# grande et sans collision evidente avec d'eventuels locks d'autres outils.
_LOCK_KEY = 2026_1008_001


def _normalize_db_url(url: str) -> str:
    """alembic attend postgresql:// ; Railway fournit parfois postgres:// ou
    postgresql+psycopg2:// -> normalisation minimale (meme regle que l'entrypoint)."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _run(cmd):
    """Execute cmd en inheritant stdout/stderr (les logs [alembic.*] doivent
    rester visibles dans la sortie Railway). Renvoie le code retour."""
    print("[serialized_migrate] $ " + " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def main() -> int:
    mode = (sys.argv[1] if len(sys.argv) > 1 else "upgrade").strip()
    url = _normalize_db_url(os.environ.get("DATABASE_URL", ""))

    if not url:
        # Dev sqlite sans DATABASE_URL exporte : settings a un defaut sqlite,
        # alembic le resoud lui-meme via env.py. Pas de concurrence possible.
        print("[serialized_migrate] DATABASE_URL absent -> alembic direct (dev).",
              flush=True)
        if mode == "stamp014+upgrade":
            subprocess.call(["alembic", "stamp", "014_schema_parity_from_orm"])
        return _run(["alembic", "upgrade", "head"])

    is_pg = url.startswith("postgresql") or url.startswith("postgres+")

    # Non-PostgreSQL (SQLite dev/test) : pas d'advisory lock, execution directe.
    if not is_pg:
        if mode == "stamp014+upgrade":
            subprocess.call(["alembic", "stamp", "014_schema_parity_from_orm"])
        return _run(["alembic", "upgrade", "head"])

    # PostgreSQL : serialization par verrou advisory de session.
    from sqlalchemy import create_engine, text

    engine = create_engine(url)
    conn = engine.connect()
    rc = 1
    try:
        print("[serialized_migrate] acquisition du verrou advisory PG "
              "(%d) ... un autre conteneur peut tenir le verrou, on attend."
              % _LOCK_KEY, flush=True)
        conn.execute(text("SELECT pg_advisory_lock(:k)"), {"k": _LOCK_KEY})
        print("[serialized_migrate] verrou acquis.", flush=True)

        if mode == "stamp014+upgrade":
            # Idempotence du stamp : si deja a head, le stamp+upgrade suivant
            # est un no-op ; on ne casse rien si la table alembic_version existe.
            subprocess.call(["alembic", "stamp", "014_schema_parity_from_orm"])
        rc = _run(["alembic", "upgrade", "head"])
    finally:
        try:
            conn.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": _LOCK_KEY})
            print("[serialized_migrate] verrou libere.", flush=True)
        except Exception as exc:  # pragma: no cover - unlock best-effort
            print("[serialized_migrate] unlock ignore (%s)" % exc, flush=True)
        finally:
            conn.close()
            engine.dispose()
    return rc


if __name__ == "__main__":
    sys.exit(main())

"""Replay vierge deterministe de la chaine alembic (SQLite) + bilan dans un fichier.

Usage: python scripts/scratch_replay_clean.py
Sortie: evo-log-backend/_replay_clean_report.txt
"""
import os
import subprocess
import sys

BACKEND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "evo-log-backend")
DB = os.path.join(BACKEND, "_ci_replay_clean.db")
REPORT = os.path.join(BACKEND, "_replay_clean_report.txt")


def main() -> int:
    for suffix in ("", "-journal", "-wal", "-shm"):
        try:
            os.remove(DB + suffix)
        except FileNotFoundError:
            pass

    env = dict(os.environ, DATABASE_URL=f"sqlite:///./_ci_replay_clean.db")
    proc = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND, env=env, capture_output=True, text=True,
    )

    lines = [f"returncode={proc.returncode}", "--- stdout ---", proc.stdout,
             "--- stderr (last 40) ---"]
    err = (proc.stderr or "").splitlines()
    lines.extend(err[-40:])

    # Verif etat final de la base
    import sqlite3
    try:
        con = sqlite3.connect(DB)
        ver = con.execute("SELECT version_num FROM alembic_version").fetchall()
        ntables = con.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        users = con.execute(
            "SELECT username, is_active, is_superuser, role_level FROM users "
            "WHERE username LIKE 'CADC%'").fetchall()
        roles = con.execute(
            "SELECT name, is_active, is_system, level FROM roles "
            "WHERE name='CADC'").fetchall()
        lines += ["--- db state ---", f"alembic_version={ver}",
                  f"tables={ntables}", f"cadc_users={users}", f"cadc_roles={roles}"]
    except Exception as exc:  # noqa: BLE001
        lines.append(f"db_check_error={exc!r}")

    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(str(x) for x in lines))
    print(f"report -> {REPORT} (rc={proc.returncode})")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())

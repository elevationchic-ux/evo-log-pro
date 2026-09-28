"""Reproduit l'environnement CI: venv strict avec seulement requirements.txt,
puis importe ce que migrations/env.py importe (app.core.database + app.models)
et tente une connexion Postgres au meme format d'URL que la CI.

Bilan ecrit dans evo-log-backend/_ci_env_report.txt
Usage: python scripts/scratch_ci_env_repro.py [--create-venv]
"""
import os
import subprocess
import sys

BACKEND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "evo-log-backend")
VENV = os.path.join(BACKEND, ".venv_ci")
REPORT = os.path.join(BACKEND, "_ci_env_report.txt")
IS_WIN = os.name == "nt"


def venv_python():
    return os.path.join(VENV, "Scripts" if IS_WIN else "bin", "python.exe" if IS_WIN else "python")


def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return p


lines = []
if "--create-venv" in sys.argv:
    lines.append("=== creating venv ===")
    p = run([sys.executable, "-m", "venv", VENV])
    lines.append(f"venv rc={p.returncode} err={p.stderr[-500:]}")
    lines.append("=== pip install -r requirements.txt (CI-identique) ===")
    p = run([venv_python(), "-m", "pip", "install", "--upgrade", "pip", "-q"])
    p = run([venv_python(), "-m", "pip", "install", "-q", "-r",
             os.path.join(BACKEND, "requirements.txt")], cwd=BACKEND)
    lines.append(f"pip rc={p.returncode}")
    lines.append("pip stderr tail:\n" + (p.stderr or "")[-2000:])
else:
    lines.append("(skip creation, reuse venv)")

PROBE = (
    "import os\n"
    "os.environ['DATABASE_URL']='postgresql://test:test@127.0.0.1:1/testdb'\n"
    "import importlib, traceback\n"
    "out=[]\n"
    "try:\n"
    "    import app.core.database as db\n"
    "    out.append('app.core.database OK')\n"
    "    from app.core.security import get_password_hash\n"
    "    out.append('app.core.security OK')\n"
    "except Exception:\n"
    "    out.append('IMPORT core FAILED:\\n'+traceback.format_exc())\n"
    "try:\n"
    "    import app.models as m\n"
    "    out.append('app.models OK, tables=%d' % len(m.Base.metadata.tables) if hasattr(m,'Base') else 'app.models OK')\n"
    "except Exception:\n"
    "    out.append('IMPORT models FAILED:\\n'+traceback.format_exc())\n"
    "print('\\n'.join(out))\n"
)
p = run([venv_python(), "-c", PROBE], cwd=BACKEND)
lines += ["=== import probe (venv strict) ===", f"rc={p.returncode}",
          p.stdout, "STDERR tail:\n" + (p.stderr or "")[-1500:]]

# Vraie alembic upgrade head vers une URL invalide -> le message d'erreur
# exact doit ressembler a celui de la CI (connexion refusee) si on passe les imports.
p = run([venv_python(), "-m", "alembic", "upgrade", "head"], cwd=BACKEND,
        env=dict(os.environ, DATABASE_URL="postgresql://test:test@127.0.0.1:1/testdb"))
lines += ["=== alembic upgrade head (venv strict, pg injoignable: rc attendu!=0) ===",
          f"rc={p.returncode}", "STDERR tail:\n" + (p.stderr or "")[-2500:],
          "STDOUT tail:\n" + (p.stdout or "")[-800:]]

with open(REPORT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(str(x) for x in lines))
print("report ->", REPORT)

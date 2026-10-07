# Scratch : rejoue "alembic upgrade head" depuis une base SQLite jetable.
# But : reproduire l'erreur MultipleHeads du test de chaine hors pytest.
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DB = ROOT / "_scratch_chain.db"
if DB.exists():
    DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{DB.as_posix()}"

from alembic import command
from alembic.config import Config

cfg = Config(str(ROOT / "alembic.ini"))
cfg.set_main_option("script_location", str(ROOT / "migrations"))

try:
    command.upgrade(cfg, "head")
    print("UPGRADE OK ->", DB)
except Exception as exc:
    print(f"UPGRADE FAIL -> {type(exc).__module__}.{type(exc).__name__}: {exc}")
    raise
finally:
    if DB.exists():
        DB.unlink()

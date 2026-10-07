# Scratch : upgrade puis downgrade base sur base jetable, via la CLI (comme le test).
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DB = ROOT / "_scratch_chain.db"
if DB.exists():
    DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{DB.as_posix()}"

import alembic
print("alembic version:", alembic.__version__)

from alembic import command
from alembic.config import Config

cfg = Config(str(ROOT / "alembic.ini"))
cfg.set_main_option("script_location", str(ROOT / "migrations"))

command.upgrade(cfg, "head")
print("UPGRADE OK")
try:
    command.downgrade(cfg, "base")
    print("DOWNGRADE OK")
except Exception as exc:
    print(f"DOWNGRADE FAIL -> {type(exc).__module__}.{type(exc).__name__}: {exc}")
finally:
    if DB.exists():
        DB.unlink()

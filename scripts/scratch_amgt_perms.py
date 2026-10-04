"""Controle de parite catalogue <-> routeur amenagement portuaire.

Verifie que chaque require_perm() du routeur correspond a une ligne reelle du
catalogue (regle reprise par tests/unit/test_rbac_amenagement_perms.py).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evo-log-backend"))

from app.core.permission_catalog import iter_permission_rows  # noqa: E402

ROUTER = (Path(__file__).resolve().parents[1] / "evo-log-backend"
          / "app" / "routers" / "v1" / "amenagement_portuaire.py")

source = ROUTER.read_text(encoding="utf-8")
used = set(re.findall(r"""require_perm\(["']([^"']+)["']\)""", source))
catalogue = {row[0] for row in iter_permission_rows()}

missing = sorted(used - catalogue)
print(f"codes utilises     : {len(used)}")
print(f"codes catalogue    : {len(catalogue)}")
print(f"introuvables       : {missing or 'AUCUN'}")
sys.exit(1 if missing else 0)

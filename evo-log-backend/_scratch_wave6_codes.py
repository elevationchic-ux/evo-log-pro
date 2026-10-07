# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.path.insert(0, ".")
V1 = Path("app/routers/v1")
from app.core.permission_catalog import iter_permission_rows, ROLE_GRANTS
from app.core.permissions import has_perm

CAT = {row[0] for row in iter_permission_rows()}

for r in ("maintenance_deep.py", "tracabilite_deep.py"):
    src = (V1 / r).read_text(encoding="utf-8")
    codes = set(re.findall(r'require_perm\(\s*"([^"]+)"', src))
    codes = sorted(c for c in codes if "{" not in c)
    phantoms = [c for c in codes if c not in CAT]
    no_carrier = []
    for c in codes:
        carriers = [n for n, _l, _d, g in ROLE_GRANTS if has_perm(g, c)]
        if not carriers:
            no_carrier.append(c)
    print(f"{r}: distinct={len(codes)} phantoms={phantoms} no_carrier={no_carrier}")

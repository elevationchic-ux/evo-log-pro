# -*- coding: utf-8 -*-
"""Extrait les permSousModule + les entities pour wave5."""
import re
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FILES = [
    "evo-log-backend/app/routers/v1/pipeline_deep.py",
    "evo-log-backend/app/routers/v1/courier_deep.py",
    "evo-log-backend/app/routers/v1/coldchain_deep.py",
    "evo-log-backend/app/routers/v1/heavylift_deep.py",
]

for f in FILES:
    print("===", f)
    t = open(f, encoding="utf-8").read()
    seen = set()
    for m in re.findall(r'require_perm\("([a-z_]+\.[a-z_]+)\.(read|create|modify)"\)', t):
        k = m[0]
        if k not in seen:
            seen.add(k)
            print("  ", k)
    # sub_paths from router decorators
    for p in re.findall(r'@router\.(?:get|post|put|delete)\("(/[\w-]+)"', t):
        pass

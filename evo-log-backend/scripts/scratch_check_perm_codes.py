# -*- coding: utf-8 -*-
"""Controle one-shot : chaque require_perm("x") du routeur existe au catalogue."""
import io
import re
import sys

from app.core.permission_catalog import iter_permission_rows

path = sys.argv[1] if len(sys.argv) > 1 else "app/routers/v1/magasin_avance.py"
codes = {row[0] for row in iter_permission_rows()}
with io.open(path, encoding="utf-8") as fh:
    src = fh.read()
used = set(re.findall(r'require_perm\("([^"]+)"\)', src))
inconnus = sorted(used - codes)
print("routes=%d codes_utilises=%d" % (src.count("require_perm("), len(used)))
print("inconnus au catalogue:", inconnus or "AUCUN")
sys.exit(1 if inconnus else 0)

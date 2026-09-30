# -*- coding: utf-8 -*-
"""Inventaire (methode, chemin, fonction, type de dependance) d'un routeur."""
import io
import re
import sys

path = sys.argv[1]
lines = io.open(path, encoding="utf-8").read().splitlines()
cur = None
for i, l in enumerate(lines):
    m = re.match(r'\s*@router\.(get|post|put|patch|delete)\("([^"]+)"', l)
    if m:
        cur = (m.group(1).upper(), m.group(2))
        continue
    d = re.match(r'\s*def (\w+)', l)
    if d and cur:
        # cherche la dependance dans les 15 lignes suivantes
        bloc = "\n".join(lines[i:i + 18])
        if "require_perm" in bloc:
            kind = re.findall(r'require_perm\("([^"]+)"\)', bloc)
            dep = "require_perm " + ",".join(kind)
        elif "get_current_user" in bloc:
            dep = "AUTH-SEULE"
        else:
            dep = "aucune"
        print("%-7s %-55s %-38s %s" % (cur[0], cur[1], d.group(1), dep))
        cur = None

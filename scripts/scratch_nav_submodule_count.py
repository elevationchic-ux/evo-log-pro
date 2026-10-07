# -*- coding: utf-8 -*-
"""Compte les sous-modules declares par module dans navigationRegistry.ts."""
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-frontend\src\config\navigationRegistry.ts"
s = io.open(P, encoding="utf-8").read()
parts = re.split(r"\n(?=    key: ')", s)
rows = []
for p in parts[1:]:
    k = re.search(r"key: '([a-z0-9-]+)'", p)
    subs = len(re.findall(r"^\s{6}\{$", p, re.M))
    if k:
        rows.append((k.group(1), subs))
for k, n in rows:
    flag = "  <-- <20" if n < 20 else ""
    print(f"{k:28s} {n:3d}{flag}")
print("modules:", len(rows), "total submodules:", sum(n for _, n in rows))

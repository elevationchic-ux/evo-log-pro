# -*- coding: utf-8 -*-
"""Liste les chemins deja references dans NAVIGATION_REGISTRY, filtres mot-cle."""
import io
import re
import sys

SRC = "evo-log-frontend/src/config/navigationRegistry.ts"
KEYWORDS = sys.argv[1:] or [
    "rh", "finance", "parc", "qhse", "audit", "settings", "chauffeur",
    "fournisseur", "supplier", "gateway", "api", "role", "tenant",
    "agency", "notif", "acquisition", "logout", "tiers",
]

src = io.open(SRC, encoding="utf-8").read()
paths = sorted(set(re.findall(r"path:\s*'([^']+)'", src)))
for p in paths:
    if any(k in p.lower() for k in KEYWORDS):
        print(p)
print("---- total chemins registry:", len(paths))

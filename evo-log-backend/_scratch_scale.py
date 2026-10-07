# -*- coding: utf-8 -*-
import re, os, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro"

p = os.path.join(root, r"evo-log-backend\app\core\permission_catalog.py")
s = open(p, encoding="utf-8").read()
codes = re.findall(r'"([a-z0-9_]+)\.([a-z0-9_*]+)\.(read|create|update|delete|validate|export|import|approve)"', s)
mods = {}
for m, sub, act in codes:
    mods.setdefault(m, set()).add(sub)
print("perm_catalog modules:", len(mods))
for m in sorted(mods):
    print("  ", m, len(mods[m]), sorted(mods[m])[:8])

# frontend nav registry
for cand in [r"evo-log-frontend\src\lib\nav-registry.ts", r"evo-log-frontend\src\lib\navigation.ts"]:
    fp = os.path.join(root, cand)
    if os.path.exists(fp):
        print("NAV FILE:", cand)

# find nav registry file
lib = os.path.join(root, r"evo-log-frontend\src\lib")
for f in os.listdir(lib):
    print("lib:", f)

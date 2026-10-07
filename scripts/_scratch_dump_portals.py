# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-frontend\src\config\navigationRegistry.ts"
s = io.open(P, encoding="utf-8").read()
parts = re.split(r"\n(?=    key: ')", s)
for p in parts[1:]:
    k = re.search(r"key: '([a-z0-9-]+)'", p)
    if not k or k.group(1) not in ("portail-chauffeur", "chef-personnel", "chat"):
        continue
    print("========", k.group(1), "========")
    print(p[:1600])

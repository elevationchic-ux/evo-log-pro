# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-frontend\src\config\navigationRegistry.ts"
s = io.open(P, encoding="utf-8").read()
parts = re.split(r"\n(?=    key: ')", s)
targets = ["portail-chauffeur","portail-magasinier","portail-technicien","portail-employe",
           "portail-frais","portail-qhse","portail-declarant","portail-commercial",
           "portail-collaborateur","annuaire-prestataires","chef-personnel","departement","chat"]
for p in parts[1:]:
    k = re.search(r"key: '([a-z0-9-]+)'", p)
    if not k or k.group(1) not in targets:
        continue
    paths = re.findall(r'path:\s*"(/[^"]+)"', p)
    perms = re.findall(r'requiredRoles:\s*\[([^\]]*)\]', p)
    print("###", k.group(1), f"(submodules={len(re.findall(r'^\s{6}\{$', p, re.M))})")
    for i, pt in enumerate(paths[:30]):
        pr = perms[i] if i < len(perms) else "?"
        print("   ", pt, "|", pr)

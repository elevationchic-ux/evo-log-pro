import re
from collections import Counter

p = r"evo-log-frontend/src/config/navigationRegistry.ts"
txt = open(p, encoding="utf-8").read()
tcodes = re.findall(r'tcode:\s*"([^"]+)"', txt)
paths = re.findall(r'path:\s*"(/[^"]+)"', txt)
dups_t = {k: v for k, v in Counter(tcodes).items() if v > 1}
dups_p = {k: v for k, v in Counter(paths).items() if v > 1}
print("tcode entries:", len(tcodes), "dup tcodes:", len(dups_t))
print("path entries:", len(paths), "dup paths:", len(dups_p))
for k, v in list(dups_p.items())[:15]:
    print("DUP PATH", k, v)

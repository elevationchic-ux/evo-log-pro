"""Dedup subModule entries in navigationRegistry.ts (same path appearing twice)."""
import re

P = r"evo-log-frontend/src/config/navigationRegistry.ts"
txt = open(P, encoding="utf-8").read()

entry_pat = re.compile(r"[ \n]\{\n(?:\s+[a-zA-Z]+:.*?\n)+?\s+\},", re.M)

seen = set()
spans_to_remove = []
pos = 0
for m in entry_pat.finditer(txt):
    block = m.group(0)
    pm = re.search(r'path:\s*"([^"]+)"', block)
    if not pm:
        continue
    path = pm.group(1)
    key = re.sub(r"\s+", " ", block)
    if key in seen:
        # remove the duplicate block, keep one leading newline
        spans_to_remove.append((m.start() + 1, m.end()))
    else:
        seen.add(key)

out = []
last = 0
for a, b in spans_to_remove:
    out.append(txt[last:a])
    last = b
out.append(txt[last:])
new = "".join(out)

open(P, "w", encoding="utf-8").write(new)
removed = len(spans_to_remove)
print("removed duplicates:", removed)

tcodes = re.findall(r'tcode:\s*"([^"]+)"', new)
paths = re.findall(r'path:\s*"(/[^"]+)"', new)
from collections import Counter
print("remaining dup paths:", sum(1 for v in Counter(paths).values() if v > 1))

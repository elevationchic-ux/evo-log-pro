"""Classification des codes require_perm par module : couverts par un role ?"""
import re
import pathlib
from collections import defaultdict
from app.core.permission_catalog import iter_permission_rows, ROLE_GRANTS
from app.core.permissions import has_perm

catalog = {r[0] for r in iter_permission_rows()}

def porteurs(code):
    return [n for n, _l, _d, grants in ROLE_GRANTS if has_perm(grants, code)]

root = pathlib.Path('app/routers')
used = {}
for f in sorted(root.rglob('*.py')):
    for m in re.findall(r'require_perm\(\s*"([^"]+)"', f.read_text(encoding='utf-8')):
        used.setdefault(m, f.name)

by_module = defaultdict(lambda: {'total': 0, 'orphelins': [], 'fantomes': 0})
for code, fname in used.items():
    mod = code.split('.')[0]
    d = by_module[mod]
    d['total'] += 1
    if code not in catalog:
        d['fantomes'] += 1
    if not porteurs(code):
        d['orphelins'].append(code)

print(f"{'module':22} {'codes':>6} {'fantomes':>9} {'orphelins(aucun role)':>22}")
for mod in sorted(by_module):
    d = by_module[mod]
    print(f"{mod:22} {d['total']:>6} {d['fantomes']:>9} {len(d['orphelins']):>22}")

print("\n=== ORPHELINS (aucun role ne les porte => bypass 0/1 seul) ===")
tot = 0
for mod in sorted(by_module):
    o = by_module[mod]['orphelins']
    if o:
        tot += len(o)
        print(f"[{mod}] ({len(o)}) via {used[o[0]]}: {sorted(o)[:4]}{' ...' if len(o)>4 else ''}")
print("TOTAL orphelins:", tot)

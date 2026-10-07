import re, pathlib
from collections import defaultdict
from app.core.permission_catalog import iter_permission_rows, ROLE_GRANTS
from app.core.permissions import has_perm

catalog = {r[0] for r in iter_permission_rows()}
def porteurs(code):
    return [n for n, _l, _d, g in ROLE_GRANTS if has_perm(g, code)]

root = pathlib.Path('app/routers')
used = {}
for f in sorted(root.rglob('*.py')):
    for m in re.findall(r'require_perm\(\s*"([^"]+)"', f.read_text(encoding='utf-8')):
        used.setdefault(m, f.name)

phantom_mods = defaultdict(int)
orphan_mods = defaultdict(int)
for code, fn in used.items():
    if '{' in code:
        continue
    mod = code.split('.')[0]
    if code not in catalog:
        phantom_mods[mod] += 1
    if not porteurs(code):
        orphan_mods[mod] += 1

print("TOTAL catalog codes:", len(catalog))
print("remaining phantom by module:", dict(phantom_mods))
print("remaining orphan by module:", dict(orphan_mods))
print("phantom total:", sum(phantom_mods.values()), "orphan total:", sum(orphan_mods.values()))

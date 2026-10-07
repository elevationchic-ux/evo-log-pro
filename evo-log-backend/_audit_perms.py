"""Audit global : codes require_perm() utilises par les routers vs catalogue."""
import re
import pathlib
from app.core.permission_catalog import iter_permission_rows, ROLE_GRANTS
from app.core.permissions import has_perm

catalog = {r[0] for r in iter_permission_rows()}

# Un code est reachable si au moins un role du catalogue le porte (wildcard ou liste).
def porteurs(code):
    return [n for n, _l, _d, grants in ROLE_GRANTS if has_perm(grants, code)]

root = pathlib.Path('app/routers')
used = {}  # code -> set(files)
for f in sorted(root.rglob('*.py')):
    src = f.read_text(encoding='utf-8')
    for m in re.findall(r'require_perm\(\s*"([^"]+)"', src):
        used.setdefault(m, set()).add(f.name)

phantoms = {c: fs for c, fs in used.items() if c not in catalog}
orphans_no_role = {c: porteurs(c) for c in used if c in catalog and not porteurs(c)}

print('=== total codes utilises dans les routers:', len(used))
print('=== FANTOMES (utilises, absents du catalogue):', len(phantoms))
for c, fs in sorted(phantoms.items()):
    print('  ', c, '<-', sorted(fs))
print('=== CATALOGUES AUCUN PORTEUR (inaccessibles):', len(orphans_no_role))
for c, p in sorted(orphans_no_role.items()):
    print('  ', c, 'porteurs=', p)

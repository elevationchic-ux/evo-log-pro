"""Inventaire par router deep: (module,sous_module,action) + fichier + prefix."""
import re
import pathlib
from collections import defaultdict

from app.core.permission_catalog import iter_permission_rows, ROLE_GRANTS
from app.core.permissions import has_perm

catalog_modules = {r[2] for r in iter_permission_rows()}
catalog = {r[0] for r in iter_permission_rows()}


def porteurs(code):
    return [n for n, _l, _d, g in ROLE_GRANTS if has_perm(g, code)]

# quel module canonique existe deja au catalogue ?
print("CATALOG MODULES:", sorted(catalog_modules))
print()

targets = [
    'port_deep', 'transit_deep', 'transport_deep', 'magasin_deep',
    'comptabilite_deep', 'finance_deep', 'parc_deep', 'rh_deep', 'qhse_deep',
    'b2b_deep', 'reports_deep', 'admin_deep', 'superadmin_deep', 'dashboard_deep',
]
root = pathlib.Path('app/routers/v1')
for name in targets:
    f = root / f"{name}.py"
    if not f.exists():
        print(f"### {name}: ABSENT")
        continue
    codes = sorted(set(re.findall(r'require_perm\(\s*"([^"]+)"', f.read_text(encoding='utf-8'))))
    mods = defaultdict(lambda: defaultdict(set))
    for c in codes:
        parts = c.split('.')
        if len(parts) == 3:
            mods[parts[0]][parts[1]].add(parts[2])
        else:
            mods[parts[0]]['_raw_'].add(c)
    print(f"### {name}.py  ({len(codes)} codes)")
    for mod, subs in mods.items():
        canon = 'CANON' if mod in catalog_modules else 'NOUVEAU'
        # representative porteurs for one sub
        anycode = next(iter(next(iter(subs.values()))))
        carrier = porteurs(f"{mod}.{list(subs)[0]}.{list(subs.values())[0]}")
        print(f"   module={mod} [{canon}] porteur-type={carrier}")
        for sub in sorted(subs):
            print(f"       {sub}: {sorted(subs[sub])}")
    print()

import re, pathlib
from collections import defaultdict

targets = [
    "transport_deep.py", "port_deep.py", "comptabilite_deep.py", "finance_deep.py",
    "b2b_deep.py", "reports_deep.py", "admin_deep.py", "superadmin_deep.py",
    "dashboard_deep.py",
]
root = pathlib.Path("app/routers")
byname = {f.name: f for f in root.rglob("*.py")}
for t in targets:
    f = byname.get(t)
    if not f:
        print(f"!! missing {t}")
        continue
    codes = sorted(set(re.findall(r'require_perm\(\s*"([^"]+)"', f.read_text(encoding="utf-8"))))
    subs = defaultdict(set)
    for c in codes:
        if "{" in c:
            continue
        parts = c.split(".")
        if len(parts) == 3:
            subs[parts[0] + "." + parts[1]].add(parts[2])
    print(f"=== {t}  ({len([c for c in codes if '{' not in c])} codes) ===")
    for key in sorted(subs):
        print(f"  {key}: {sorted(subs[key])}")

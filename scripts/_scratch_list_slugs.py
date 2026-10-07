import re
t = open('evo-log-frontend/src/config/navigationRegistry.ts', encoding='utf-8').read()
for mod in ["finance-ohada", "reports-bi", "admin-saas"]:
    print(f"=== {mod} ===")
    i = t.index(f'key: "{mod}"')
    blk = t[i:i + 6000]
    slugs = sorted(set(re.findall(r'/' + re.escape(mod) + r'"?/([a-z0-9-]+)"', blk)))
    # also capture path: "/mod/slug"
    paths = sorted(set(re.findall(r'"/' + re.escape(mod) + r'/([a-z0-9-]+)"', blk)))
    for p in paths:
        print("  ", p)

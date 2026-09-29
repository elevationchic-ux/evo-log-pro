"""Analyse chaine Alembic : tete(s), down_revision de 028, et colonnes `users`
creees par chaque migration (pour diagnostiquer une eventuelle colonne du
modele User jamais ajoutee -> SELECT users 500 sur PostgreSQL)."""
import glob
import os
import re

D = "migrations/versions"
revs, downs, files = {}, {}, {}
for f in glob.glob(os.path.join(D, "*.py")):
    t = open(f, encoding="utf-8").read()
    r = re.search(r"revision\s*=\s*['\"]([^'\"]+)", t)
    dn = re.search(r"down_revision\s*=\s*['\"]([^'\"]+)['\"]", t)
    k = r.group(1) if r else os.path.basename(f)
    revs[k] = t
    files[k] = os.path.basename(f)
    downs[k] = dn.group(1) if dn else None

all_down = set(x for x in downs.values() if x)
heads = [k for k in revs if k not in all_down]
print("REVISIONS", len(revs))
print("HEADS", [(h, files[h]) for h in heads])
print("028 down =", downs.get("028"))

# Colonnes `users` citees dans chaque migration (add_column / create_table users)
print("\n=== references a la table users par migration ===")
for k in sorted(revs, key=lambda x: files[x]):
    t = revs[k]
    adds = re.findall(r'add_column\(\s*[\'"]users[\'"]\s*,\s*[\'"](\w+)[\'"]', t, re.I)
    ct = re.search(r'create_table\(\s*[\'"]users[\'"]', t, re.I)
    if adds or ct:
        print(f"{files[k]:45} create={bool(ct)} add={adds}")

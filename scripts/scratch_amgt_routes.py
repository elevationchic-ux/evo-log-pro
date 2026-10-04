"""Dump des routes du departement amenagement portuaire : methode, chemin, code.

Sert a ecrire les tests HTTP sur des chemins reels plutot que devines.
"""
import re
from pathlib import Path

ROUTER = Path(__file__).resolve().parents[1] / "evo-log-backend" / "app" / "routers" / "v1" / "amenagement_portuaire.py"

src = ROUTER.read_text(encoding="utf-8")

# decorateur @router.<meth>("<chemin>", ...)  -- sur plusieurs lignes possibles
dec_re = re.compile(r'@router\.(\w+)\(\s*"([^"]+)"', re.S)
perm_re = re.compile(r'require_perm\("([^"]+)"\)')

out = []
for m in dec_re.finditer(src):
    meth, path = m.group(1).upper(), m.group(2)
    # bloc = du decorateur jusqu'au prochain decorateur
    nxt = dec_re.search(src, m.end())
    bloc = src[m.start():nxt.start() if nxt else len(src)]
    perms = perm_re.findall(bloc)
    out.append((meth, path, ",".join(sorted(set(perms))) or "-"))

for line in out:
    print(f"{line[0]:6} /api/v1/amenagement-portuaire{line[1]:52} {line[2]}")
print("total:", len(out))

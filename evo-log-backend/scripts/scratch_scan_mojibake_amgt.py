"""Detecte les sequences de sur-encodage (mojibake) dans les fichiers touches.

Un fichier en UTF-8 strict peut contenir 'Ã©' : c'est alors du UTF-8 qui a ete
relu en latin-1 puis re-encode. Ce scan ne regarde donc pas la validite de
l'encodage (toujours vraie) mais la presence des bigrammes typiques.
"""
import pathlib
import re

SIGNES = re.compile(r"Ã©|Ã¨|Ã|Ãª|Ãª|â€|Â|\ufffd")

CIBLES = [
    "app/routers/v1/amenagement_portuaire.py",
    "app/schemas/amenagement_portuaire.py",
    "app/core/permission_catalog.py",
    "migrations/versions/042_rbac_amenagement_place_grants.py",
    "tests/unit/test_rbac_amenagement_perms.py",
]

racine = pathlib.Path(__file__).resolve().parents[1]
total = 0
for rel in CIBLES:
    p = racine / rel
    if not p.exists():
        print(f"ABSENT  {rel}")
        continue
    raw = p.read_bytes()
    bom = raw[:3] == b"\xef\xbb\xbf"
    texte = raw.decode("utf-8")
    lignes = texte.splitlines()
    hits = [(i + 1, l.strip()[:90]) for i, l in enumerate(lignes) if SIGNES.search(l)]
    status = "MOJIBAKE" if hits else ("BOM" if bom else "OK")
    print(f"{status:9} {rel}  lignes={len(lignes)} hits={len(hits)} bom={bom}")
    for n, extrait in hits[:12]:
        print(f"    {n}: {extrait}")
    total += len(hits)
print(f"\nTOTAL hits = {total}")

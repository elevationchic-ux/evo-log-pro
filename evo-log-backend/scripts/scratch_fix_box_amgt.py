"""Detecte et repare le sur-encodage par aller-retour auto-validant.

Principe : une ligne n'est candidate que si son encoding cp1252 est du UTF-8
VALIDE et donne un texte different. Un texte francais legitime ("chateau",
"« non enregistre »") echoue a cette condition (octet 0xE2/0xE9 sans suite
UTF-8 correcte) et reste donc intact.

Usage :
    python scripts/scratch_fix_box_amgt.py            # rapport
    python scripts/scratch_fix_box_amgt.py --apply    # repare les cibles
"""
import pathlib
import sys

racine = pathlib.Path(__file__).resolve().parents[1]
apply_fix = "--apply" in sys.argv

CIBLES = [
    "app/routers/v1/amenagement_portuaire.py",
    "app/schemas/amenagement_portuaire.py",
    "app/core/permission_catalog.py",
    "app/models/amenagement_portuaire.py",
    "migrations/versions/042_rbac_amenagement_place_grants.py",
    "migrations/versions/038_amenagement_portuaire_tables.py",
    "migrations/versions/039_rbac_amenagement_grants.py",
    "tests/unit/test_rbac_amenagement_perms.py",
]


def reparee(ligne: str):
    if ligne.isascii():
        return None
    try:
        candidat = ligne.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None
    return candidat if candidat != ligne else None


for rel in CIBLES:
    p = racine / rel
    if not p.exists():
        print(f"ABSENT  {rel}")
        continue
    lignes = p.read_text(encoding="utf-8").split("\n")
    nouvelles, changees = [], []
    for i, l in enumerate(lignes):
        rep = reparee(l)
        if rep is None:
            nouvelles.append(l)
        else:
            nouvelles.append(rep)
            changees.append((i + 1, l.strip()[:70], rep.strip()[:70]))
    print(f"\n=== {rel} : {len(changees)} ligne(s)")
    for n, avant, apres in changees[:10]:
        print(f"  {n}: {avant!r}\n      -> {apres!r}")
    if len(changees) > 10:
        print(f"  ... {len(changees) - 10} autres")
    if changees and apply_fix:
        p.write_text("\n".join(nouvelles), encoding="utf-8", newline="")

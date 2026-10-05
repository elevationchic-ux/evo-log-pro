"""Balaye le backend et repare les lignes sur-encodees (UTF-8 relu en cp1252).

Reparation ligne par ligne : une ligne n'est touchee que si son aller-retour
cp1252 -> utf-8 reussit ET qu'elle contient un bigramme typique. Une ligne
deja correcte (contenant par exemple un vrai tiret cadratin) echoue au
round-trip et reste intacte. Mode par defaut : ecrit un rapport, ne modifie
pas, sauf --apply.
"""
import pathlib
import re
import sys

SIGNES = re.compile(r"Ã©|Ã¨|Ã|Ãª|â€|Â|\ufffd")

racine = pathlib.Path(__file__).resolve().parents[1]
apply_fix = "--apply" in sys.argv

cibles = sorted((racine / "app").rglob("*.py")) + sorted((racine / "migrations").rglob("*.py")) + sorted((racine / "tests").rglob("*.py"))

nb_fichiers = 0
nb_lignes = 0
for p in cibles:
    texte = p.read_text(encoding="utf-8")
    lignes = texte.split("\n")
    changees = 0
    nouvelles = []
    for l in lignes:
        if SIGNES.search(l):
            try:
                reparee = l.encode("cp1252").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                nouvelles.append(l)
                if "\ufffd" in l:
                    print(f"  IRREPARABLE {p.relative_to(racine)}: {l.strip()[:80]}")
                continue
            if reparee != l:
                changees += 1
                nouvelles.append(reparee)
            else:
                nouvelles.append(l)
        else:
            nouvelles.append(l)
    if changees:
        nb_fichiers += 1
        nb_lignes += changees
        print(f"{p.relative_to(racine)} : {changees} ligne(s)")
        if apply_fix:
            p.write_text("\n".join(nouvelles), encoding="utf-8", newline="")

print(f"\nfichiers concernes = {nb_fichiers}, lignes = {nb_lignes}, apply = {apply_fix}")

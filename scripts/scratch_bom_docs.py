"""BOM dans les documents : est-ce que mes editions en ajoutent, ou est-ce herite ?

Repond a une seule question, pour chaque fichier marque : le BOM etait-il deja la
dans l'historique git. Utile parce qu'un editeur qui ecrit un BOM a chaque
sauvegarde pollue silencieusement tous les documents qu'on touche.
"""
import pathlib
import subprocess

BOM = b"\xef\xbb\xbf"
RACINE = pathlib.Path(__file__).resolve().parents[1]
CIBLES = [p for p in RACINE.rglob("*.md")
          if p.is_file() and not {"node_modules", ".next", ".venv_ci", "_tmpreplay"} & set(p.parts)]

for chemin in sorted(CIBLES):
    if not chemin.read_bytes().startswith(BOM):
        continue
    rel = chemin.relative_to(RACINE).as_posix()
    deja_la = "?"
    for loin in (1, 20, 60, 200, 600):
        brut = subprocess.run(
            ["git", "show", f"HEAD~{loin}:{rel}"], capture_output=True, cwd=RACINE
        ).stdout
        if brut:
            deja_la = "OUI" if brut.startswith(BOM) else "NON (ajoute recent)"
            break
    print(f"{rel:<60} BOM present, deja dans l'historique : {deja_la}")

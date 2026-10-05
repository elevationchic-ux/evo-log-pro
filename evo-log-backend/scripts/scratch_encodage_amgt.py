"""Controle d'encodage des fichiers touches par le batch « referentiel places ».

Verifie que chaque fichier se decode bien en UTF-8 strict (pas de BOM, pas de
mojibake) et affiche les lignes non ASCII ajoutees, pour que les accents restent
lisibles la ou le projet en met deja.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CIBLES = [
    ROOT / "app" / "core" / "permission_catalog.py",
    ROOT / "app" / "routers" / "v1" / "amenagement_portuaire.py",
    ROOT / "app" / "schemas" / "amenagement_portuaire.py",
]

for chemin in CIBLES:
    brut = chemin.read_bytes()
    bom = brut.startswith(b"\xef\xbb\xbf")
    try:
        texte = brut.decode("utf-8", errors="strict")
        ok = True
    except UnicodeDecodeError as exc:
        texte, ok = "", f"ERREUR {exc}"
    lignes = texte.splitlines()
    excent = [(i, l.strip()[:90]) for i, l in enumerate(lignes, 1)
              if any(ord(c) > 127 for c in l)][:4]
    print(f"--- {chemin.name}: bom={bom} utf8={ok} lignes={len(lignes)}")
    for i, l in excent:
        print(f"    {i}: {l}")

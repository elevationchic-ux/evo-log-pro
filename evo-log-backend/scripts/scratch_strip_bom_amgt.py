"""Remet les deux fichiers du departement en UTF-8 sans BOM (etat d'origine).

`Set-Content -Encoding UTF8` de Windows PowerShell 5 prepend un BOM que le reste
du backend ne porte pas ; ce script le retire et laisse le fichier nu.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CIBLES = [
    ROOT / "app" / "routers" / "v1" / "amenagement_portuaire.py",
    ROOT / "app" / "schemas" / "amenagement_portuaire.py",
]

for chemin in CIBLES:
    brut = chemin.read_bytes()
    avant = brut[:3] == b"\xef\xbb\xbf"
    if avant:
        chemin.write_bytes(brut[3:])
    print(f"{chemin.name}: BOM={'retire' if avant else 'absent'}, lignes={len(chemin.read_text(encoding='utf-8').splitlines())}")

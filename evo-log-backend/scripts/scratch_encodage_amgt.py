from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CIBLES = [
    ROOT / "app" / "core" / "permission_catalog.py",
    ROOT / "app" / "routers" / "v1" / "amenagement_portuaire.py",
    ROOT / "app" / "schemas" / "amenagement_portuaire.py",
]
out = []
for chemin in CIBLES:
    texte = chemin.read_bytes().decode("utf-8")
    uffd = texte.count("\ufffd")
    ete = texte.count("\u00eatre") + texte.count("d'\u00eatre")
    lignes = [f"{i}:{l.strip()[:60]}" for i, l in enumerate(texte.splitlines(), 1) if "\ufffd" in l][:3]
    out.append(f"{chemin.name}: U+FFFD={uffd} e_accent_aigu_lignes={ete} {lignes}")
Path("_encodage_check.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out).encode("ascii", errors="backslashreplace").decode())

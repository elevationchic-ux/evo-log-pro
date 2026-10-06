"""Ou viennent les 3 « liaisons mortes » remontees par audit_endpoint_bindings.py ?

L'audit extrait toute chaine citee commencant par /api. Une URL citee dans un
commentaire ou un JSDoc n'est pas un appel : c'est du bruit. Ce scratch montre le
contexte exact de chaque occurrence pour trancher (faux positif de l'outil ou
vraie liaison morte).
"""
import pathlib
import re

SRC = pathlib.Path("evo-log-frontend/src")
LIT = re.compile(r"['\"`]((?:/api/v1|/api)/[^'\"`\s]+)['\"`]")
CIBLES = {
    "/api/v1/docs",
    "/api/v1/parc/ocr-extract",
    "/api/v1/purchase/requisitions/{p}/{p}",
}

for fichier in sorted(SRC.rglob("*.ts*")):
    txt = fichier.read_text(encoding="utf-8", errors="ignore")
    for i, ligne in enumerate(txt.split("\n"), 1):
        for m in LIT.finditer(ligne):
            u = m.group(1).split("?")[0]
            u = re.sub(r"\$\{[^}]*\}", "{p}", u).rstrip("/")
            if not u.startswith("/api/v1/"):
                u = "/api/v1" + u[len("/api"):]
            if u in CIBLES:
                stripped = ligne.strip()
                estimation = (
                    "COMMENTAIRE"
                    if stripped.startswith(("//", "*", "/*"))
                    else "CODE"
                )
                print(f"{fichier.relative_to(SRC)}:{i} [{estimation}] {u}")
                print(f"      {ligne.strip()[:150]}")

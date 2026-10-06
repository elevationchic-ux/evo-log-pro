"""Pourquoi audit_endpoint_bindings.py cite-t-il /api/v1/parc/ocr-extract ?

Le litteral n'existe nulle part dans le frontend (only comments). Ce scratch
reproduit la mechine d'extraction de l'audit, ligne par ligne, et montre
l'occurrence exacte qui produit l'orphelin. But : decider si l'audit doit ignorer
les commentaires (et donc devenir un garde fiable pour la grosse extension a
venir) ou si une liaison morte reelle est cachee.
"""
import pathlib
import re

SRC = pathlib.Path("evo-log-frontend/src")
LIT = re.compile(r"['\"`]((?:/api/v1|/api)/[^'\"`\s]+)['\"`]")

for fichier in sorted(SRC.rglob("*.ts*")):
    txt = fichier.read_text(encoding="utf-8", errors="ignore")
    for i, ligne in enumerate(txt.split("\n"), 1):
        for m in LIT.finditer(ligne):
            u = m.group(1)
            if "ocr" in u or u.endswith("/docs") or "requisitions/" in u:
                print(f"{fichier.relative_to(SRC)}:{i}  extrait={u!r}")

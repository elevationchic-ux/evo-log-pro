"""Quel exact appel regex ne termine plus sur acconage/create/page.tsx ?

Le scan de l'audit marque le passe des le premier fichier. Ce scratch isole les
deux suspects (nettoyage des commentaires, regex d'appel) et, si la regex est en
cause, montre le fragment qui la declenche, pour corriger le motif plutot que le
juger « lent ».
"""
import importlib.util
import pathlib
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
spec = importlib.util.spec_from_file_location("aeb", pathlib.Path("scripts/audit_endpoint_bindings.py"))
aeb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aeb)

CIBLE = aeb.FRONTEND_SRC / "app" / "(app)" / "acconage" / "create" / "page.tsx"
brut = CIBLE.read_text(encoding="utf-8", errors="ignore")
print(f"taille {len(brut)} caracteres")

t0 = time.time()
sans = aeb.retirer_commentaires(brut)
print(f"retirer_commentaires : {time.time() - t0:.2f}s")

# Ou sont les .get/.post/... qui font partir la recherche de quote fermante ?
amorce = re.compile(r"\b[A-Za-z_$][\w$]*(?:API|api|Client|client)\.(?:get|post|put|patch|delete)\b")
t0 = time.time()
amorces = [m for m in amorce.finditer(sans)]
print(f"{len(amorces)} amorces en {time.time() - t0:.2f}s")

for m in amorces:
    extrait = sans[m.start():m.start() + 160].replace("\n", "\\n")
    debut = time.time()
    try:
        aeb.APPEL.match(sans, m.start())
    except Exception as exc:  # pragma: no cover - diagnostic
        print(f"  ECHEC {exc}")
    coute = time.time() - debut
    if coute > 0.05:
        print(f"  LENT ({coute:.2f}s) : {extrait!r}")

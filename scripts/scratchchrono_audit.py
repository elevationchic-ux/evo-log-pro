"""Ou passe le temps audit_endpoint_bindings.py ?

L'audit complet ne termine plus depuis que la resolution des prefixes a ete
ajoutee. Deux suspects : l'import de app.main (OpenAPI a chaud) et le balayage
des 360+ fichiers du frontend. Ce scratch minute chaque phase, fichier par
fichier au-dela d'un seuil, pour ne pas corriger au jug.
"""
import importlib.util
import pathlib
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CHEMIN = pathlib.Path("scripts/audit_endpoint_bindings.py")
spec = importlib.util.spec_from_file_location("aeb", CHEMIN)
aeb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aeb)

t0 = time.time()
fichiers = sorted(aeb.FRONTEND_SRC.rglob("*.ts*"))
print(f"{len(fichiers)} fichiers ts/tsx, listing {time.time() - t0:.2f}s")

lent = []
t0 = time.time()
for f in fichiers:
    d = time.time()
    brut = f.read_text(encoding="utf-8", errors="ignore")
    sans = aeb.retirer_commentaires(brut)
    sites = list(aeb.APPEL.finditer(sans))
    aeb.FETCH.finditer(sans)
    coute = time.time() - d
    if coute > 0.4:
        lent.append((coute, f, len(sites)))
print(f"scan frontend total {time.time() - t0:.2f}s")
for coute, f, n in sorted(lent, reverse=True)[:15]:
    print(f"   {coute:6.2f}s  {n:>4} appels  {f.relative_to(aeb.root)}")

t0 = time.time()
chemins, meth = aeb.backend_operations()
print(f"OpenAPI a chaud {time.time() - t0:.2f}s  ({len(chemins)} chemins)")

t0 = time.time()
index = aeb.IndexRoutes(meth)
sites, non_res, opaques = aeb.scanner_front(None)
print(f"scanner_front complet {time.time() - t0:.2f}s  ({len(sites)} sites)")

t0 = time.time()
orph = sum(1 for _f, _l, _m, u in sites if not index.existe(u))
print(f"resolution des sites {time.time() - t0:.2f}s  ({orph} orphelins)")

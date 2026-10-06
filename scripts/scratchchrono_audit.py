"""Chronometre fichier par fichier de l'audit de liaisons.

Le scan frontend ne termine plus depuis l'ajout de la resolution des prefixes.
Ce scratch affiche CHAQUE fichier avant de le traiter : le dernier nom affiche
est le fichier qui coince, et la separation des deux cotes (nettoyage des
commentaires vs regex d'appel) dit quelle partie corriger.
"""
import importlib.util
import sys
import time
import pathlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
spec = importlib.util.spec_from_file_location("aeb", pathlib.Path("scripts/audit_endpoint_bindings.py"))
aeb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aeb)

for n, f in enumerate(sorted(aeb.FRONTEND_SRC.rglob("*.ts*")), 1):
    if n % 25 == 0:
        print(f"... {n} fichiers traites (dernier : {f.name})", flush=True)
    brut = f.read_text(encoding="utf-8", errors="ignore")
    t0 = time.time()
    sans = aeb.retirer_commentaires(brut)
    t1 = time.time()
    sites = list(aeb.APPEL.finditer(sans))
    t2 = time.time()
    if (t1 - t0) > 0.3 or (t2 - t1) > 0.3:
        print(f"COMITE {f.relative_to(aeb.root)}  com={t1 - t0:.2f}s regex={t2 - t1:.2f}s "
              f"taille={len(brut)} appels={len(sites)}", flush=True)
print("TERMINE", flush=True)

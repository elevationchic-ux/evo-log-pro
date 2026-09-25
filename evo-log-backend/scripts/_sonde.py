# -*- coding: utf-8 -*-
"""Sonde temporaire : diagnostic de chainedonne sur deux fichiers connus."""
import importlib.util
import pathlib

B = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("afc", B / "scripts" / "audit_fidelite_champs.py")
afc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(afc)

contrat = afc.charger_contrat()
index = afc.index_client(afc.FRONT)

for nom in ("transport/epod", "transport/flotte", "transport/drivers"):
    cible = afc.FRONT / "app" / "(app)" / nom / "page.tsx"
    texte = cible.read_text(encoding="utf-8")
    print("=" * 70)
    print(nom)
    trace = {}
    vars_, ambigus = afc.lien_donnees(contrat, index, texte, trace)
    print("  vars_   :", {k: sorted(v) for k, v in vars_.items()})
    print("  ambigus :", sorted(ambigus))
    print("  sources :", {k: sorted(v) for k, v in trace["sources"].items()})
    print("  affectes:", {k: v for k, v in trace["affectes"].items()})

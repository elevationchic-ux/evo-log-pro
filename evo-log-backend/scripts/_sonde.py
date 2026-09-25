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

for nom in ("transport/epod", "transport/flotte"):
    cible = afc.FRONT / "app" / "(app)" / nom / "page.tsx"
    texte = cible.read_text(encoding="utf-8")
    print("=" * 70)
    print(nom)
    print("  AFFECTATION trouvees :",
          [(m.group(1), m.group(2)[:60]) for m in afc.AFFECTATION.finditer(texte)][:6])
    vars_, ambigus = afc.lien_donnees(contrat, index, texte)
    print("  vars_   :", {k: sorted(v) for k, v in vars_.items()})
    print("  ambigus :", sorted(ambigus))
    # detail des sources, c'est la que le ble est visible
    import re as _re
    sources = {}
    for m in afc.AFFECTATION.finditer(texte):
        pass
    print("  ETAT    :", afc.ETAT.findall(texte)[:8])

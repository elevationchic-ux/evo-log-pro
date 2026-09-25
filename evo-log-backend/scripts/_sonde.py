# -*- coding: utf-8 -*-
"""Sonde temporaire : pourquoi transport/epod n'est-il pas verifie ?"""
import importlib.util
import pathlib
import sys

B = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("afc", B / "scripts" / "audit_fidelite_champs.py")
afc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(afc)

contrat = afc.charger_contrat()
index = afc.index_client(afc.FRONT)
print("index client (transportAPI.getMissions) :", index.get("transportAPI.getMissions"))
cible = afc.FRONT / "app" / "(app)" / "transport" / "epod" / "page.tsx"
texte = cible.read_text(encoding="utf-8")
vars_ = afc.lien_donnees(contrat, index, texte)
print("lien_donnees ->", {k: sorted(v) for k, v in vars_.items()})
print("schemas_de_reponse('/api/transport/missions','get') ->",
      afc.schemas_de_reponse(contrat, "/api/transport/missions", "get"))
mots = [p for p in contrat["reponses"] if p.endswith("transport/missions")]
print("paths du contrat finissant par transport/missions :", mots)
for p in mots:
    print("   ", p, "->", contrat["reponses"][p])

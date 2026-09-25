"""Sonde temporaire : le contrat extracteur resout-il bien heritage + enums ?"""
import json
import pathlib

c = json.loads(pathlib.Path("_openapi_contrat.json").read_text(encoding="utf-8"))
sch = c["schemas"]

print("schemas:", len(sch), "| reponses:", len(c["reponses"]))

for nom in ("CamionResponse", "MissionResponse", "ConducteurResponse"):
    s = sch.get(nom)
    if not s:
        print("%-20s ABSENT" % nom)
        continue
    print("%-20s %2d champs | enums=%s" % (nom, len(s["champs"]), s["enums"]))
    if nom == "CamionResponse":
        print("   heritage base visible ? immatriculation=%s status=%s kilometrage=%s"
              % ("immatriculation" in s["champs"], "status" in s["champs"],
                 "kilometrage" in s["champs"]))
    if nom == "ConducteurResponse":
        print("   champs enums:", sorted(s["champs"])[:30])

# Tous les noms de proprietes porteuses d'un enum, et leurs valeurs.
par_prop = {}
for nom, s in sch.items():
    for prop, vals in s["enums"].items():
        par_prop.setdefault(prop, set()).update(vals)
print("\npropriete -> valeurs d'enum (%d proprietes) :" % len(par_prop))
for prop in sorted(par_prop):
    print("   %-22s %s" % (prop, sorted(par_prop[prop])[:12]))

un_seul = [n for n, s in sch.items() if not s["champs"]]
print("\nschemas sans aucun champ resolu : %d (exemples %s)"
      % (len(un_seul), un_seul[:6]))

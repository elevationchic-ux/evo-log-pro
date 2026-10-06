"""Combien d'appels du frontend echappent aux audits parce que l'URL est composee ?

Les deux audits de contrat (liaisons et fidelite des champs) extraient les URL
par une regex qui exige `/api...` juste apres le delimiter. Un appel ecrit
`apiClient.get(`${AMGT}/places`)` ne commence pas par `/` : il est invisible.
Ce scratch compte ce qui est visible et ce qui ne l'est pas, pour dimensionner
le trou avant de durcir les gardes.
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = pathlib.Path("evo-log-frontend/src")

DECL = re.compile(r"(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*[`'\"](/api[^`'\"]*)[`'\"]")
APPEL = re.compile(r"\b(?:apiClient|[\w$]*API)\.(get|post|put|patch|delete)\(\s*([`'\"])((?:[^`'\"]|\.)*?)\2")

stat = {"litteral_api": 0, "template_prefixe": 0, "template_injecte": 0, "autre": 0}
par_fichier = {}
prefixes = {}

for fichier in sorted(SRC.rglob("*.ts*")):
    txt = fichier.read_text(encoding="utf-8", errors="ignore")
    locales = {n: v for n, v in DECL.findall(txt)}
    prefixes.update(locales)
    for m in APPEL.finditer(txt):
        url = m.group(3)
        cle = str(fichier)
        if url.startswith("/api"):
            stat["litteral_api"] += 1
        elif url.startswith("${"):
            var = re.match(r"\$\{([A-Za-z_$][\w$]*)", url).group(1)
            if var in locales:
                stat["template_prefixe"] += 1
                par_fichier[cle] = par_fichier.get(cle, 0) + 1
            else:
                stat["template_injecte"] += 1
        else:
            stat["autre"] += 1

print("appel par variable de prefix locale (INVISIBLE aux audits) :", stat["template_prefixe"])
print("appel par template injectee d'ailleurs                 :", stat["template_injecte"])
print("appel en litteral /api (vu par les audits)             :", stat["litteral_api"])
print("autres (chemin relatif, concat, fetch brut)            :", stat["autre"])
print()
print("constantes de prefix declarees :", len(prefixes))
for n, v in sorted(prefixes.items())[:40]:
    print(f"   {n:<22} {v}")
print()
print("fichiers les plus concernes :")
for f, n in sorted(par_fichier.items(), key=lambda kv: -kv[1])[:12]:
    print(f"   {n:>4}  {f}")

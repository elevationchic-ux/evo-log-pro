# -*- coding: utf-8 -*-
"""Audite la fidelite des CHAMPS lus par le frontend par rapport au contrat
reellement repondu par le backend (outil de audit, complementaire de
`audit_api_gaps.py`).

`audit_api_gaps.py` repond a « cette URL existe-t-elle, et travaille-t-elle ? ».
Celui-ci repond a « une fois la reponse recue, les proprietes que l'ecran
lit sont-elles bien dans le schema emis ? ». Les deux families de defauts sont
differentes et la seconde est silencieuse : l'appel passe en HTTP 200, le
tableau se remplit, et seule la colonne est vide — ou pire, fausse.

Deux bugs reels de ce repertoire, trouve a la main puis mecanises ici :
  * `transport/drivers` testait `chauffeur.actif` ; l'API envoie `is_active`.
    Resultat : 100 % des conducteurs affiches « Inactif », quel que soit l'etat.
  * `transport/map` comparait `c.statut` a 'EN_MAINTENANCE' ; `CamionResponse`
    expose `status` et les valeurs reelles sont minuscules. Resultat : le
    compteur « Hors Ligne » avalait toute la flotte.

Regle de non-surprise : un champ n est signale que si le cheminement de la
donnee est RETABLI dans le fichier (appel API -> variable -> acces). Une
simple ressemblance de nom ne suffit pas, sinon l'outil hurlerait sur chaque
`item.key` de React. Les files non resolus sont comptes et affiches a part :
un silence de l'outil doit rester distinguishable d'un « tout va bien ».

Usage: python scripts/audit_fidelite_champs.py [--json sortie]
"""
import argparse
import json
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
BACKEND = RACINE
FRONT = RACINE.parent / "evo-log-frontend" / "src"
CONTRAT = BACKEND / "_openapi_contrat.json"

# `apiClient.get('/api/x')`, `transportAPI.getMissions()`, backticks inclus.
APPEL_API = re.compile(
    r"\b(?:apiClient|[\w.]*API)\.(get|post|put|patch|delete)\(\s*[`'\"]([^`'\"]+)[`'\"]"
)
# Methodes centralisees de api-client.ts : `getMissions: (p) => apiClient.get('/api/..')`
METHODE_CLIENT = re.compile(
    r"^\s*(\w+)\s*:\s*(?:\([^)]*\)|[\w$]+)\s*=>\s*[\w.]*\.(get|post|put|patch|delete)\(\s*[`'\"]([^`'\"]+)[`'\"]",
    re.M,
)
NOM_OBJET = re.compile(r"^\s*export const (\w+API)\s*=", re.M)
# `const [camions, setCamions] = useState...` puis `setCamions(res.data)`
STATE = re.compile(r"const \[(\w+), set(\w+)\] = useState")
# `x.map((v) =>`, `x.filter(v =>`, `x.find(v =>` ... : objet itere -> alias
ITERATION = re.compile(r"\b([A-Za-z_$][\w$]*)\s*\.\s*(?:map|filter|find|some|every|forEach)\s*\(\s*\(?\s*([A-Za-z_$][\w$]*)")
# Acces en properties sur un alias connu : `c.statut`, `chauffeur?.actif`
ACCES = r"(?:%s)\s*(?:\?\.|\.)\s*([A-Za-z_$][\w$]*)"

# Menages : ce qui n'est PAS une donnee metier, meme lu sur un objet metier.
BUILTIN = frozenset("""
length map filter find findIndex some every forEach reduce flat flatArray sort push pop
join split replace replaceAll toLowerCase toUpperCase trim padStart padEnd includes indexOf
lastIndexOf slice concat indexOf keys values entries hasOwnProperty toString toFixed
toLocaleString toLocaleDateString toLocaleTimeString then catch finally
label value id name type items total count data error message statusText ok url params
""".split())
# Champs de l'enveloppe de pagination / reponse generee : jamais dans un modele.
ENVELOPPE = frozenset("""
items total page size pages count detail pending message data results limit offset
""".split())
# React / DOM / conventions de rendu.
RENDU = frozenset("""
className style onClick onChange onKeyDown href src alt key ref children checked disabled
placeholder title width height target rel props state setState router
""".split())


def normaliser(chemin: str) -> str:
    """`/api/x` -> `/api/v1/x`, comme le middleware du backend. Retire la query."""
    chemin = chemin.split("?", 1)[0]
    if chemin.startswith("/api/") and not chemin.startswith("/api/v1/"):
        chemin = "/api/v1/" + chemin[len("/api/"):]
    return chemin


def charger_contrat():
    if not CONTRAT.exists():
        sys.exit("%s absent : lancer scripts/dump_openapi_paths.py d'abord" % CONTRAT.name)
    return json.loads(CONTRAT.read_text(encoding="utf-8"))


def chemin_de_reponse(contrat, path, methode):
    """Noms de schemas emis par `methode path`, ou None si l'URL n'est pas connue."""
    ops = contrat["reponses"].get(normaliser(path))
    if ops is None:
        return None
    return ops.get(methode) or []


def champs_de(contrat, noms):
    """Union des proprietes des schemas demandes, en suivant une imbrication."""
    rendu = set()
    schemas = contrat["schemas"]
    for nom in noms:
        s = schemas.get(nom)
        if not s:
            continue
        rendu.update(s["champs"])
        # une list-wrapper (`XResponse` contenant `items: [Y]`) doit etre ouverte
        for imb in s.get("sous", []):
            rendu.update(champs_de(contrat, [imb]))
    return rendu


def index_client(front_src):
    """`{transportAPI.getMissions: ('get', '/api/transport/missions')}`."""
    cible = front_src / "lib" / "api-client.ts"
    if not cible.exists():
        return {}
    texte = cible.read_text(encoding="utf-8", errors="replace")
    index = {}
    courant = None
    # le fichier est decoupe en blocs `export const xxxAPI = { ... }`
    morceaux = re.split(r"export const (\w+API)\s*=", texte)
    # re.split avec un groupe : [prefixe, NOM, bloc, NOM, bloc, ...]
    for i in range(1, len(morceaux), 2):
        nom, bloc = morceaux[i], morceaux[i + 1]
        for m in METHODE_CLIENT.finditer(bloc):
            index["%s.%s" % (nom, m.group(1))] = (m.group(2), m.group(3))
    if courant:
        pass
    return index


def analyser_fichier(contrat, index, fichier, texte):
    """Renvoie (soupcons, fichiers_non_resolus)."""
    # 1. liens API -> variable d'etat
    variables = {}   # nom d'etat -> set de (methode, path)
    etats = {nom: set() for nom, _ in re.findall(r"const \[(\w+), set(\w+)\]", texte)}
    setters = {"set%s" % cap: nom for nom, cap in re.findall(r"const \[(\w+), set(\w+)\]", texte)}
    if not etats:
        return [], 0
    resolved = 0
    for m in APPEL_API.finditer(texte):
        methode, path = m.group(1), m.group(2)
        if path.startswith("http"):
            continue
        noms = chemin_de_reponse(contrat, path, methode)
        if noms is None:
            continue
        resolved += 1
        # qui recoit cette reponse ? `setFoo(res.data)` dans les 400 caracteres
        fenetre = texte[m.end():m.end() + 700]
        for seteur in setters:
            if re.search(r"\b%s\s*\(" % seteur, fenetre):
                variables.setdefault(setters[seteur], set()).update(noms)
    for m in METHODE_APPELE.finditer(texte):
        cle = "%s.%s" % (m.group(1), m.group(2))
        if cle not in index:
            continue
        methode, path = index[cle]
        noms = chemin_de_reponse(contrat, path, methode)
        if not noms:
            continue
        fenetre = texte[max(0, m.start() - 700):m.start() + 700]
        for seteur in setters:
            if re.search(r"\b%s\s*\(" % seteur, fenetre):
                variables.setdefault(setters[seteur], set()).update(noms)

    # 2. alias d'iteration sur ces variables
    alias = {}   # nom d'alias -> set de noms de schemas
    for itere, nom in ITERATION.findall(texte):
        if itere in variables and variables[itere]:
            alias.setdefault(nom, set()).update(variables[itere])
        elif itere in alias:
            alias.setdefault(nom, set()).update(alias[itere])

    # 3. acces en propriete sur les alias
    soupcons = []
    for nom, schemas in alias.items():
        disponibles = champs_de(contrat, schemas)
        if not disponibles:
            continue
        for champ in re.findall(ACCES % re.escape(nom), texte):
            if champ in BUILTIN or champ in ENVELOPPE or champ in RENDU:
                continue
            if champ in disponibles:
                continue
            soupcons.append({"variable": nom, "champ": champ,
                             "attendus": sorted(disponibles)[:14],
                             "schemas": sorted(schemas)})
    return soupcons, (0 if resolved else 1)


METHODE_APPELE = re.compile(r"\b([\w$]*API)\.(\w+)\s*\(")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(BACKEND / "_fidelite_champs.json"))
    args = ap.parse_args()

    contrat = charger_contrat()
    index = index_client(FRONT)
    chemin_soupe = {}
    total_vars = 0
    non_resolus = []
    for fichier in sorted(FRONT.rglob("*.tsx")) + sorted(FRONT.rglob("*.ts")):
        if "node_modules" in fichier.parts:
            continue
        try:
            texte = fichier.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "useState" not in texte:
            continue
        soupcons, mutisme = analyser_fichier(contrat, index, fichier, texte)
        if mutisme:
            non_resolus.append(str(fichier))
        for s in soupcons:
            cle = (str(fichier.relative_to(FRONT.parent)), s["variable"], s["champ"])
            chemin_soupe.setdefault(cle, s)
    rendus = sorted(chemin_soupe.values(), key=lambda d: (d.get("fichier") or "", d["champ"]))
    for (fichier, variable, champ), detail in zip(chemin_soupe, rendus):
        detail["fichier"] = fichier
        detail["variable"] = variable
    with open(args.json, "w", encoding="utf-8") as fh:
        json.dump(rendus, fh, indent=1)

    par_champ = {}
    for d in rendus:
        par_champ.setdefault(d["champ"], []).append(d["fichier"])
    print("fichiers analyses sans lien retabli (silence = non verifie) : %d"
          % len(non_resolus))
    print("champs lus hors contrat : %d occurrence(s), %d nom(s) distinct(s)"
          % (len(rendus), len(par_champ)))
    for champ in sorted(par_champ, key=lambda c: -len(par_champ[c])):
        ou = par_champ[champ]
        print("   %-26s x%-3d %s" % (champ, len(ou), ou[0] if len(ou) == 1 else ""))
    print("detail : %s" % args.json)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Audite la fidelite des CHAMPS lus par le frontend par rapport au contrat
reellement repondu par le backend (outil de audit, complementaire de
`audit_api_gaps.py`).

`audit_api_gaps.py` repond a « cette URL existe-t-elle, et travaille-t-elle ? ».
Celui-ci repond a « une fois la reponse recue, les proprietes que l'ecran lit
sont-elles bien dans le schema emis ? ». Les deux families de defauts sont
differentes et la seconde est silencieuse : l'appel passe en HTTP 200, le
tableau se remplit, et seule la colonne est vide — ou pire, fausse.

Deux bugs reels de ce repertoire, trouve a la main puis mecanises ici :
  * `transport/drivers` testait `chauffeur.actif` ; l'API envoie `is_active`.
    Resultat : 100 % des conducteurs affiches « Inactif », quel que soit l'etat.
  * `transport/map` comparait `c.statut` a 'EN_MAINTENANCE' ; `CamionResponse`
    expose `status`, aux valeurs minuscules. Le compteur « Hors Ligne »
    avalait toute la flotte.

Regle de non-surprise : un champ n'est signale que si le cheminement de la
donnee est RETABLI dans le fichier (appel API -> variable d'etat -> acces).
Une simple ressemblance de nom ne suffirait pas : l'outil hurlerait sur chaque
`item.key` de React. Inversement, un fichier dont le lien n'a pas pu etre
retabli est compte a part : le silence de l'outil doit rester distinguishable
d'un « tout va bien ».

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

# `apiClient.get('/api/x')` — objet client + verbe + literal de chemin.
APPEL_DIRECT = re.compile(
    r"\b(apiClient|[\w$]*API)\.(get|post|put|patch|delete)\(\s*[`'\"](/[^`'\"]*)[`'\"]"
)
# Appel d'une methode centralisee : `transportAPI.getMissions()`.
APPEL_METODE = re.compile(r"\b([\w$]*API)\.(\w+)\s*\(")
# Dans api-client.ts : `getMissions: (p) => apiClient.get('/api/transport/missions'`
METHODE_CLIENT = re.compile(
    r"^\s*(\w+)\s*:\s*(?:\([^)]*\)|[\w$]+)\s*=>\s*[\w.]*\.(get|post|put|patch|delete)\(\s*[`'\"](/[^`'\"]*)[`'\"]",
    re.M,
)
# `const [camions, setCamions] = useState(...)`
ETAT = re.compile(r"const \[(\w+), (set\w+)\] = useState")
# `camions.map((c) =>`, `data.filter(x =>` : collection iteree -> alias
ITERATION = re.compile(
    r"\b([A-Za-z_$][\w$]*)\s*\.\s*(?:map|filter|find|some|every|forEach)\s*\(\s*\(?\s*([A-Za-z_$][\w$]*)\s*[,)]"
)
# `rows.map((c) => ({ brand: c.marque, ... }))` : la page FABRIQUE un view-model.
# Sans cette regle, l'outil signale `v.brand` comme champ invente alors que la
# cle est definie deux cents lignes plus haut — c'etait le premier faux positif
# produit par cet outil, sur `transport/flotte`.
CONSTRUCTION = re.compile(
    r"\.\s*(?:map)\s*\(\s*\(?\s*([A-Za-z_$][\w$]*)\s*\)?\s*=>\s*\(?\s*\{"
)
# Litteral compare a quelque chose qui porte le nom du champ :
# `c.status === 'ACTIVE'`, `item.statut == "EN_COURS"`.
COMPARAISON = re.compile(
    r"([\w$.]*\b%s\b[\w$.\[\]']*)\s*[=!]==?\s*([`'\"])([^`'\"]+)\2"
)

# Ce qui n'est pas une donnee metier, meme lu sur un objet metier.
BUILTIN = frozenset("""
length map filter find findIndex some every forEach reduce flat sort push pop shift join
split replace replaceAll match toLowerCase toUpperCase trim padStart padEnd includes
indexOf lastIndexOf slice concat keys values entries hasOwnProperty toString toFixed
toLocaleString toLocaleDateString toLocaleTimeString then catch finally charAt charCodeAt
label value id name items total count data error message statusText ok url params props
""".split())
# Enveloppe de reponse paginee : ces cles sont reelles mais hors modele.
ENVELOPPE = frozenset("""
items total page pages size count detail pending message data results limit offset
next previous tcode libelle_code
""".split())
# React / DOM / conventions de rendu.
RENDU = frozenset("""
className style onClick onChange onKeyDown onSubmit href src alt key ref children checked
disabled placeholder title width height target rel type role tabIndex autoFocus required
""".split())


def normaliser(chemin):
    """`/api/x` -> `/api/v1/x`, comme le middleware du backend. Query retirlee."""
    chemin = chemin.split("?", 1)[0]
    if chemin.startswith("/api/") and not chemin.startswith("/api/v1/"):
        chemin = "/api/v1/" + chemin[len("/api/"):]
    return chemin


def charger_contrat():
    if not CONTRAT.exists():
        sys.exit("%s absent : lancer scripts/dump_openapi_paths.py d'abord" % CONTRAT.name)
    return json.loads(CONTRAT.read_text(encoding="utf-8"))


def schemas_de_reponse(contrat, path, methode):
    """Liste de noms de schemas emis, ou None si l'URL est inconnue du contrat."""
    ops = contrat["reponses"].get(normaliser(path))
    if ops is None:
        return None
    return ops.get(methode) or []


def champs_de(contrat, noms):
    rendu = set()
    for nom in noms:
        s = contrat["schemas"].get(nom)
        if s:
            rendu.update(s["champs"])
    return rendu


def index_client(front_src):
    """`{'transportAPI.getMissions': ('get', '/api/transport/missions')}`."""
    cible = front_src / "lib" / "api-client.ts"
    if not cible.exists():
        return {}
    texte = cible.read_text(encoding="utf-8", errors="replace")
    index = {}
    # `export const xxxAPI = { ... }` : re.split avec groupe -> [pref, NOM, bloc, ...]
    morceaux = re.split(r"export const (\w+API)\s*=\s*\{", texte)
    for i in range(1, len(morceaux) - 1, 2):
        nom, bloc = morceaux[i], morceaux[i + 1]
        for m in METHODE_CLIENT.finditer(bloc):
            index.setdefault("%s.%s" % (nom, m.group(1)), (m.group(2), m.group(3)))
    return index


def lien_donnees(contrat, index, texte):
    """variable d'etat -> set de noms de schemas qui la nourrissent.

    Deux motifs couverts, les deux reels dans ce code :
      `const res = await apiClient.get('/api/x'); setFoo(res.data)`
      `const {data: foo = []} = useQuery({queryFn: () => transportAPI.getX()})`
    La proximite (fenetre de caracteres) tient lieu d'analyse de flot : grossier,
    mais une erreur d'affectation ne cree qu'un faux negatif, jamais un faux
    positif — le sens qui compte pour un outil de tri.
    """
    vars_ = {}
    setters = {}
    for nom, seteur in ETAT.findall(texte):
        setters[seteur] = nom
    fournisseurs = []
    for m in APPEL_DIRECT.finditer(texte):
        obj, methode, path = m.group(1), m.group(2), m.group(3)
        if obj != "apiClient" and not obj.endswith("API"):
            continue
        fournisseurs.append((methode, path, m.end(), m.end() + 900))
    for m in APPEL_METODE.finditer(texte):
        cle = "%s.%s" % (m.group(1), m.group(2))
        if cle not in index:
            continue
        methode, path = index[cle]
        fournisseurs.append((methode, path, max(0, m.start() - 900), m.start() + 900))
    for methode, path, debut, fin in fournisseurs:
        noms = schemas_de_reponse(contrat, path, methode)
        if not noms:
            continue
        fenetre = texte[debut:fin]
        for seteur, etat in setters.items():
            if re.search(r"\b%s\s*\(" % re.escape(seteur), fenetre):
                vars_.setdefault(etat, set()).update(noms)
        # `data: foo` destructures depuis useQuery, et `const foo = res.data`
        for m in re.finditer(r"data\s*:\s*([A-Za-z_$][\w$]*)", fenetre):
            vars_.setdefault(m.group(1), set()).update(noms)
    return vars_


def analyser(contrat, index, texte):
    """-> (liste de soupcons, lien_retably: bool)."""
    vars_ = lien_donnees(contrat, index, texte)
    if not vars_:
        return [], False
    alias = {}
    for _ in range(2):  # une passe de propagation suffit pour `x = foo.filter(...)`
        for iteree, nom in ITERATION.findall(texte):
            if iteree in vars_ and vars_[iteree]:
                alias.setdefault(nom, set()).update(vars_[iteree])
            elif iteree in alias:
                alias.setdefault(nom, set()).update(alias[iteree])
    soupcons = []
    for nom, schemas in sorted(alias.items()):
        disponibles = champs_de(contrat, schemas)
        if not disponibles:
            continue
        vus = set()
        for champ in re.findall(
                r"(?:%s)\s*(?:\?\.|\.)\s*([A-Za-z_$][\w$]*)" % re.escape(nom), texte):
            if champ in vus:
                continue
            if champ in BUILTIN or champ in ENVELOPPE or champ in RENDU:
                continue
            if champ in disponibles:
                continue
            vus.add(champ)
            soupcons.append({
                "variable": nom,
                "champ": champ,
                "schemas": sorted(schemas),
                "attendus": sorted(disponibles),
            })
    return soupcons, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(BACKEND / "_fidelite_champs.json"))
    args = ap.parse_args()

    contrat = charger_contrat()
    index = index_client(FRONT)
    rendu = []
    muets = 0
    parles = 0
    for fichier in sorted(FRONT.rglob("*.tsx")) + sorted(FRONT.rglob("*.ts")):
        try:
            texte = fichier.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "useState" not in texte and "useQuery" not in texte:
            continue
        soupcons, retably = analyser(contrat, index, texte)
        if retably:
            parles += 1
            for s in soupcons:
                s = dict(s)
                s["fichier"] = str(fichier.relative_to(FRONT.parent))
                rendu.append(s)
        else:
            # Pas de lien retabli : ce fichier n'a pas ete verifie, ce qui ne
            # vaut pas dire qu'il est propre.
            muets += 1

    avec_chemin = {}
    for d in rendu:
        avec_chemin[(d["fichier"], d["variable"], d["champ"])] = d
    rendus = sorted(avec_chemin.values(), key=lambda d: (d["fichier"], d["champ"]))
    with open(args.json, "w", encoding="utf-8") as fh:
        json.dump(rendus, fh, indent=1)

    par_champ = {}
    for d in rendus:
        par_champ.setdefault(d["champ"], []).append(d["fichier"])
    print("fichiers ou le lien donnee->variable est retabli : %d" % parles)
    print("fichiers a donnees API non retablis (NON verifies) : %d" % muets)
    print("champs lus hors contrat : %d occurrence(s), %d nom(s) distinct(s)"
          % (len(rendus), len(par_champ)))
    for champ in sorted(par_champ, key=lambda c: (-len(par_champ[c]), c)):
        ou = par_champ[champ]
        print("   %-28s x%-3d %s" % (champ, len(ou), ou[0] if len(ou) == 1 else ""))
    print("detail : %s" % args.json)


if __name__ == "__main__":
    main()

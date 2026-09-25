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
# `camions.map((c) =>`, `data.filter(x =>`, et surout `rows.map((c: any) =>` :
# l'annotation de type est la norme dans ce frontend, l'omettre laissait la
# moitie des alias non lies, donc le fichier entier non verifie.
ITERATION = re.compile(
    r"\b([A-Za-z_$][\w$]*)\s*\.\s*(?:map|filter|find|some|every|forEach)\s*"
    r"\(\s*\(?\s*([A-Za-z_$][\w$]*)\s*(?::[^)]*)?[,)]"
)
# `rows.map((c) => ({ brand: c.marque, ... }))` : la page FABRIQUE un view-model.
# Sans cette regle, l'outil signale `v.brand` comme champ invente alors que la
# cle est definie deux cents lignes plus haut — c'etait le premier faux positif
# produit par cet outil, sur `transport/flotte`.
CONSTRUCTION = re.compile(
    r"\.\s*map\s*\(\s*\(?\s*([A-Za-z_$][\w$]*)\s*(?::[^)]*)?\)?\s*=>\s*\(?\s*\{"
)
# Litteral compare a quelque chose qui porte le nom du champ :
# `c.status === 'ACTIVE'`, `item.statut == "EN_COURS"`. Gabarit : le nom du
# champ n'est connu qu'a l'analyse, d'ou le re.compile a chaque usage.
COMPARAISON = (
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


def corps_litteral(texte, debut):
    """Texte entre `{` a `debut` et son `}` apparie (imbrications et chaines)."""
    i, profondeur = debut, 0
    while i < len(texte):
        c = texte[i]
        if c in "'\"`":
            i += 1
            while i < len(texte) and texte[i] != c:
                i += 2 if texte[i] == "\\" else 1
        elif c == "{":
            profondeur += 1
        elif c == "}":
            profondeur -= 1
            if profondeur == 0:
                return texte[debut:i]
        i += 1
    return ""


def formes_locales(texte):
    """alias d'iteration -> cles que la page lui construit elle-meme.

    `vehicles.map((v) => ...)` et `rows.map((c) => ({ brand: c.marque }))`
    definissent ensemble la VRAIE forme de `v` : aucune de ces cles ne transite
    par le contrat. Les ignorer est la seule facon d'evoyer l'outil noyer les
    vrais trous sous des vues locales legitimes.
    """
    formes = {}
    for m in CONSTRUCTION.finditer(texte):
        acc = texte.find("{", m.end() - 1)
        bloc = corps_litteral(texte, acc) if acc >= 0 else ""
        cles = set(re.findall(r"(?:^|[{,])\s*([A-Za-z_$][\w$]*)\s*:", bloc))
        if not cles:
            continue
        # A QUI appartient l'objet construit ? Pas au parametre du map (`c` est
        # la source, elle cote sur le contrat) : a la variable d'etat que le
        # `set...(` enveloppant alimente, donc aux alias qui parcourent cette
        # variable. Attribuer au parametre ne filtrait rien du tout.
        amont = texte[max(0, m.start() - 600):m.start()]
        ports = set()
        for sm in re.finditer(r"\bset([A-Z]\w*)\s*\(", amont):
            ports.add(sm.group(1)[0].lower() + sm.group(1)[1:])
        for nom in ports:
            formes.setdefault(nom, set()).update(cles)
    return formes


def valeurs_hors_enum(contrat, schemas, texte):
    """Litteraux compares a un champ a enum, mais absents de ce enum.

    C'est l'autre moitie du defaut, et la plus dangereuse : le champ existe,
    la comparaison s'execute, et elle ne reussit jamais. `transport/map`
    comparait `statut` a 'EN_MAINTENANCE' pour `in_maintenance`.
    """
    perms = set()
    for nom in schemas:
        perms.update((contrat["schemas"].get(nom) or {}).get("enums", {}))
    suspects = []
    for champ in sorted(perms):
        for regex in re.finditer(COMPARAISON % re.escape(champ), texte):
            cible, _, litteral = regex.group(1), regex.group(2), regex.group(3)
            admises = set()
            for nom in schemas:
                admises.update(
                    ((contrat["schemas"].get(nom) or {}).get("enums") or {}).get(champ, []))
            if not admises or litteral in admises:
                continue
            jumeau = next((v for v in sorted(admises) if v.lower() == litteral.lower()), None)
            suspects.append({
                "champ": champ,
                "literal": litteral,
                "variable": cible,
                "admis": sorted(admises),
                "jumeau": jumeau,
            })
    return suspects


def analyser(contrat, index, texte):
    """-> (soupcons de noms, soupcons de valeurs, lien_retably: bool)."""
    vars_ = lien_donnees(contrat, index, texte)
    if not vars_:
        return [], [], False
    formes = formes_locales(texte)
    alias = {}
    for _ in range(2):  # une passe de propagation suffit pour `x = foo.filter(...)`
        for iteree, nom in ITERATION.findall(texte):
            # La forme locale voyage avec la donnee : `vehicles` porte les cles
            # construites, `v` en herite en le parcourant.
            heritees = formes.get(iteree)
            if heritees:
                formes.setdefault(nom, set()).update(heritees)
            if iteree in vars_ and vars_[iteree]:
                alias.setdefault(nom, set()).update(vars_[iteree])
            elif iteree in alias:
                alias.setdefault(nom, set()).update(alias[iteree])
    soupcons = []
    pour_valeurs = set()
    for schemas in vars_.values():
        pour_valeurs.update(schemas)
    # Les variables d'etat se verifient AUSSI : `setMission(activeMissions[0])`
    # puis `mission.origine` ne passe par aucune iteration, et c'est le motif le
    # plus frequent de ce frontend. Ne verifier que les alias d'iteration
    # laissait l'ecran e-pod entier sous silence alors que le lien etait retabli.
    a_verifier = dict(alias)
    for nom, schemas in vars_.items():
        a_verifier.setdefault(nom, set()).update(schemas)
    for nom, schemas in sorted(a_verifier.items()):
        disponibles = champs_de(contrat, schemas)
        if not disponibles:
            continue
        # Une cle construite par la page elle-meme n'est pas une lecture du contrat.
        locales = formes.get(nom, set())
        vus = set()
        for champ in re.findall(
                r"(?:%s)\s*(?:\?\.|\.)\s*([A-Za-z_$][\w$]*)" % re.escape(nom), texte):
            if champ in vus or champ in locales:
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
    return soupcons, valeurs_hors_enum(contrat, pour_valeurs, texte), True


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
        noms_lus, valeurs, retably = analyser(contrat, index, texte)
        if not retably:
            # Pas de lien retabli : ce fichier n'a pas ete verifie, ce qui ne
            # vaut pas dire qu'il est propre.
            muets += 1
            continue
        parles += 1
        for s in noms_lus:
            s = dict(s, genre="champ_inexistant")
            s["fichier"] = str(fichier.relative_to(FRONT.parent))
            rendu.append(s)
        for s in valeurs:
            s = dict(s, genre="valeur_hors_enum")
            s["fichier"] = str(fichier.relative_to(FRONT.parent))
            rendu.append(s)

    cles_dedoublonnage = {
        "champ_inexistant": lambda d: (d["fichier"], d["variable"], d["champ"]),
        "valeur_hors_enum": lambda d: (d["fichier"], d["champ"], d["literal"]),
    }
    avec_chemin = {}
    for d in rendu:
        avec_chemin[cles_dedoublonnage[d["genre"]](d)] = d
    rendus = sorted(avec_chemin.values(), key=lambda d: (d["fichier"], d["champ"]))
    with open(args.json, "w", encoding="utf-8") as fh:
        json.dump(rendus, fh, indent=1)

    champs = [d for d in rendus if d["genre"] == "champ_inexistant"]
    valeurs = [d for d in rendus if d["genre"] == "valeur_hors_enum"]
    print("fichiers ou le lien donnee->variable est retabli : %d" % parles)
    print("fichiers a donnees API non retablis (NON verifies) : %d" % muets)
    print("-- axe noms : %d champ(s) lu(s) hors contrat dans %d fichier(s)"
          % (len(champs), len({d["fichier"] for d in champs})))
    for d in champs:
        print("   %-24s .%-22s %s" % (d["champ"], d["variable"], d["fichier"]))
    print("-- axe valeurs : %d comparaison(s) qui ne peuvent jamais reussir"
          % len(valeurs))
    for d in valeurs:
        vers = ("  (la valeur reelle est %r)" % d["jumeau"]) if d["jumeau"] else ""
        print("   %-14s == %-22s %s%s"
              % (d["champ"], repr(d["literal"]), d["fichier"], vers))
    print("detail : %s" % args.json)


if __name__ == "__main__":
    main()

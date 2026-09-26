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
# `const res = await transportAPI.getMissions()` — le nom lie a l'appel est la
# seule facon de savoir QUI remplit quelle variable d'etat.
AFFECTATION = re.compile(
    r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*([^;\n]{0,220})"
)
PROMESSE = re.compile(
    r"(?:const|let|var)\s*\[([^\]]*)\]\s*=\s*(?:await\s*)?Promise\.all\(\s*\["
)
DATA_QUERY = re.compile(r"\bdata\s*:\s*([A-Za-z_$][\w$]*)")

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


def retirer_commentaires(texte):
    """Remplace le contenu des commentaires par des espaces, en preservant les
    chaines. Sans ce nettoyage, l'outil signale ce que le code EXPLIQUE : apres
    la correction de `transport/control`, le commentaire
    « lisait m.immatriculation / m.conducteur » produisait trois faux positifs.
    """
    out = list(texte)
    i, n = 0, len(texte)
    while i < n:
        c = texte[i]
        if c in "'\"`":
            i += 1
            while i < n and texte[i] != c:
                i += 2 if texte[i] == "\\" else 1
            i += 1
        elif texte.startswith("/*", i):
            fin = texte.find("*/", i + 2)
            fin = n if fin < 0 else fin + 2
            for j in range(i, min(fin, n)):
                if out[j] != "\n":
                    out[j] = " "
            i = fin
        elif texte.startswith("//", i):
            fin = texte.find("\n", i)
            fin = n if fin < 0 else fin
            for j in range(i, fin):
                out[j] = " "
            i = fin
        else:
            i += 1
    return "".join(out)


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


def bloc_apparie(texte, debut):
    """Contenu (hors delimitateurs) du bloc `{} [] ()` ouvert a `debut`."""
    if debut >= len(texte) or texte[debut] not in "{[(":
        return ""
    i, prof = debut, 0
    while i < len(texte):
        c = texte[i]
        if c in "'\"`":
            i += 1
            while i < len(texte) and texte[i] != c:
                i += 2 if texte[i] == "\\" else 1
        elif c in "{[(":
            prof += 1
        elif c in ")]}":
            prof -= 1
            if prof == 0:
                return texte[debut + 1:i]
        i += 1
    return ""


def decoupage(corps):
    """Decoupe le contenu d'un tableau aux virgules de profondeur 0."""
    morceaux, prof, buf = [], 0, []
    for c in corps:
        if c in "{[(":
            prof += 1
        elif c in ")]}":
            prof -= 1
        if c == "," and prof == 0:
            morceaux.append("".join(buf))
            buf = []
        else:
            buf.append(c)
    if buf:
        morceaux.append("".join(buf))
    return morceaux


def lien_donnees(contrat, index, texte, trace=None):
    """variable d'etat -> set de noms de schemas qui la nourrissent.

    Deux motifs couverts, les deux reels dans ce code :
      `const res = await apiClient.get('/api/x'); setFoo(res.data)`
      `const {data: foo = []} = useQuery({queryFn: () => transportAPI.getX()})`
    La proximite (fenetre de caracteres) tient lieu d'analyse de flot : grossier.
    Pour qu'elle ne tourne pas en affirmation fausse, une variable touchee par
    PLUSIEURS chemins d'API distincts est tenue pour SANS SOURCE etablie : on ne
    peut pas savoir lequel la remplit. `transport/flotte` appelle `/camions` et
    `/kpis` a deux lignes d'ecart ; `kpis` (dictionnaire brut, sans
    response_model, donc sans contrat lisible) heritait des champs de
    CamionResponse et l'outil y aurait cherche `vehicules_actifs` en croyant
    savoir. Ces variables sont comptees a part : le silence reste distinguishable
    d'un « tout va bien ».
    """
    vars_, sources, ambigus, affectes = {}, {}, set(), {}

    def resoudre(expr):
        """(methode, path) depuis le texte d'un appel, ou None."""
        m = APPEL_DIRECT.search(expr)
        if m and (m.group(1) == "apiClient" or m.group(1).endswith("API")):
            return m.group(2), m.group(3)
        for m in APPEL_METODE.finditer(expr):
            cle = "%s.%s" % (m.group(1), m.group(2))
            if cle in index:
                return index[cle]
        return None

    def apporter_source(nom, chemin):
        sources.setdefault(nom, set()).add(chemin)

    # 1) `const res = await transportAPI.getMissions()`
    for m in AFFECTATION.finditer(texte):
        c = resoudre(m.group(2))
        if c:
            apporter_source(m.group(1), c)
    # 2) `const [v, k] = await Promise.all([get('/a'), get('/b')])` : ce motif
    #    est courant et la simple proximite y melange les deux reponses.
    for m in PROMESSE.finditer(texte):
        noms = [n.strip() for n in m.group(1).split(",")]
        corps = bloc_apparie(texte, texte.find("[", m.end() - 1))
        morceaux = decoupage(corps)
        for i, nom in enumerate(noms):
            if nom and i < len(morceaux):
                c = resoudre(morceaux[i])
                if c:
                    apporter_source(nom, c)
    # 3) une passe de propagation sur les affectations locales :
    #    `const rows = v.data` puis `setVehicles(rows.map(...))`.
    for _ in range(2):
        for m in AFFECTATION.finditer(texte):
            cible, droite = m.group(1), m.group(2)
            if cible in sources:
                continue
            for nom in re.findall(r"[A-Za-z_$][\w$]*", droite):
                if nom in sources:
                    sources[cible] = set(sources[nom])
                    break
    def resoudre_tout(expr):
        """Tous les appels distincts resolus dans un bloc d'options."""
        trouves = set()
        for m in APPEL_DIRECT.finditer(expr):
            if m.group(1) == "apiClient" or m.group(1).endswith("API"):
                trouves.add((m.group(2), m.group(3)))
        for m in APPEL_METODE.finditer(expr):
            cle = "%s.%s" % (m.group(1), m.group(2))
            if cle in index:
                trouves.add(index[cle])
        return trouves

    # 4) `const {data: factures = []} = useQuery({queryFn: () => financeAPI.x()})`
    #    Ces pages n'ont AUCUN useState : le nom destructure est la variable
    #    d'etat. Oublier cette branche laissait `transport/drivers` entierement
    #    hors de verification.
    #    L'attribution se fait par le BLOC useQuery apparie, plus par une
    #    fenetre de caracteres : la fenetre ±300 avait accole le schema des
    #    MISSIONS a `corridorsData`, trois declarations plus bas dans le fichier,
    #    et l'outil signait des signaux inventes de toutes pieces.
    pour_query = {}
    pour_query_multi = set()
    for m in DATA_QUERY.finditer(texte):
        q = re.compile(r"=\s*use[A-Za-z]*\(").search(texte, m.end())
        if not q:
            continue
        options = bloc_apparie(texte, q.end() - 1)
        if not options:
            continue
        trouves = resoudre_tout(options)
        if len(trouves) == 1:
            c = next(iter(trouves))
            apporter_source(m.group(1), c)
            pour_query.setdefault(m.group(1), set()).add(c)
        elif len(trouves) > 1:
            pour_query_multi.add(m.group(1))

    # 5) la source d'une variable d'etat est celle NOMMEE dans l'argument de son
    #    setter, pas celle qui passe a cote. C'est ce qui distingue `setKpis(k)`
    #    (aucun contrat : dictionnaire brut) de `setVehicles(rows.map(...))`.
    for nom, seteur in ETAT.findall(texte):
        chemins = set()
        for m in re.finditer(r"\b%s\s*\(" % re.escape(seteur), texte):
            arg = bloc_apparie(texte, m.end() - 1)
            # Seules les RACINES de l'argument comptent : au-dela du premier
            # `=>`, on est dans un callback qui cite la moitie du fichier, et
            # tout juger ambigu a partir de la n'aurait plus rien mesure
            # (23 fichiers verifies sur 314 au lieu de 73).
            amorce = arg.split("=>")[0]
            for local, si in sources.items():
                if re.search(r"\b%s\b" % re.escape(local), amorce):
                    chemins |= si
        affectes[nom] = sorted(chemins)
        if len(chemins) > 1:
            ambigus.add(nom)
            continue
        if not chemins:
            continue
        methode, path = next(iter(chemins))
        noms = schemas_de_reponse(contrat, path, methode)
        if not noms:
            # L'appel existe mais n'emet aucun schema : rien a verifier ici,
            # et ce n'est pas pour autant une donnee conforme.
            ambigus.add(nom)
            continue
        vars_[nom] = set(noms)
        affectes[nom] = sorted(chemins)
    for nom in pour_query_multi:
        # Deux appels distincts dans le meme useQuery : on ne peut attribuer
        # l'un ni l'autre. Declaration d'ignorance, pas de benediction muette.
        ambigus.add(nom)
    for nom, chemins in pour_query.items():
        if nom in vars_ or nom in ambigus:
            continue
        affectes[nom] = sorted(chemins)
        if len(chemins) > 1:
            ambigus.add(nom)
            continue
        methode, path = next(iter(chemins))
        schemas = schemas_de_reponse(contrat, path, methode)
        if not schemas:
            ambigus.add(nom)
            continue
        vars_[nom] = set(schemas)
    if trace is not None:
        # Diagnostic : par quelle porte chaque variable a ete accostee.
        trace.update({"sources": sources, "affectes": affectes,
                      "ambigus": sorted(ambigus)})
    return vars_, ambigus


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
        # `const missions = missionsData.map((m) => ({...}))` : le view-model est
        # aussi porte par une constante locale, pas seulement par un setter.
        # Sans quoi `m.status` (cle construite) etait signale comme lecture du
        # contrat — premier signal faussement neuf sur `transport/control`.
        consts = list(re.finditer(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=", amont))
        if consts:
            ports.add(consts[-1].group(1))
        for nom in ports:
            formes.setdefault(nom, set()).update(cles)
    # `setStats({ total: ..., enRoute: ... })` : agregat construit de bout en
    # bout par la page. Ses cles ne transitent par aucun contrat.
    for sm in re.finditer(r"\bset([A-Z]\w*)\s*\(\s*\{", texte):
        acc = texte.find("{", sm.end() - 1)
        bloc = corps_litteral(texte, acc) if acc >= 0 else ""
        cles = set(re.findall(r"(?:^|[{,])\s*([A-Za-z_$][\w$]*)\s*:", bloc))
        if cles:
            formes.setdefault(sm.group(1)[0].lower() + sm.group(1)[1:], set()).update(cles)
    return formes


def valeurs_hors_enum(contrat, schemas, texte, formes=None):
    """Litteraux compares a un champ a enum, mais absents de ce enum.

    C'est l'autre moitie du defaut, et la plus dangereuse : le champ existe,
    la comparaison s'execute, et elle ne reussit jamais. `transport/map`
    comparait `statut` a 'EN_MAINTENANCE' pour `in_maintenance`.
    Une comparaison portee par une CLE CONSTRITE par la page (`m.status` issu
    d'un view-model local) n'est pas une lecture du contrat : la filtrer par
    `formes`, sinon chaque vue locale legitime devient un faux positif.
    """
    formes = formes or {}
    perms = set()
    for nom in schemas:
        perms.update((contrat["schemas"].get(nom) or {}).get("enums", {}))
    suspects = []
    for champ in sorted(perms):
        for regex in re.finditer(COMPARAISON % re.escape(champ), texte):
            cible, _, litteral = regex.group(1), regex.group(2), regex.group(3)
            morceaux = cible.split(".")
            if len(morceaux) >= 2:
                porteur = morceaux[-2]
                if champ in formes.get(porteur, set()):
                    continue
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
    """-> (soupcons de noms, soupcons de valeurs, lien_retably, variables ambiguës)."""
    vars_, ambigus = lien_donnees(contrat, index, texte)
    if not vars_:
        return [], [], False, ambigus
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
        # \\b de chaque cote : sans lui, `React.FormEvent` se lisait comme le
        # variable `t` suivie du champ `FormEvent` (signal hallucine sur
        # TransactionSearch.tsx, chercheur magasin reel).
        for champ in re.findall(
                r"(?<![\w$])(?:%s)\s*(?:\?\.|\.)\s*([A-Za-z_$][\w$]*)\b" % re.escape(nom), texte):
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
    return soupcons, valeurs_hors_enum(contrat, pour_valeurs, texte, formes), True, ambigus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(BACKEND / "_fidelite_champs.json"))
    args = ap.parse_args()

    contrat = charger_contrat()
    index = index_client(FRONT)
    rendu = []
    sans_source = set()
    muets = 0
    parles = 0
    for fichier in sorted(FRONT.rglob("*.tsx")) + sorted(FRONT.rglob("*.ts")):
        try:
            texte = fichier.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "useState" not in texte and "useQuery" not in texte:
            continue
        # Ce que le code explique dans un commentaire n'est pas ce qu'il fait.
        noms_lus, valeurs, retably, ambigus = analyser(contrat, index, retirer_commentaires(texte))
        sans_source.update("%s::%s" % (fichier.relative_to(FRONT.parent), v)
                           for v in ambigus)
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
    print("variables sans source etablie (plusieurs appels, non jugees) : %d"
          % len(sans_source))
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

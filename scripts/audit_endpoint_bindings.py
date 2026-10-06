"""Audit des liaisons frontend -> backend, par module, avec methode HTTP.

Pourquoi ce garde existe et ce qu'il corrige : les versions precedentes extrayaient
les URL par une regex qui exigeait `/api...` juste apres le delimiter. Or ce
frontend ecrit ses appels sur des constantes de prefix
(`const AMGT = '/api/v1/amenagement-portuaire'` puis
``apiClient.get(`${AMGT}/places`)``). Ces appels ne commencent pas par `/` : ils
n'etaient JAMAIS controles. 106 sites d'appel (5 namespaces) echappaient donc au
contrat, ce qui est pire qu'une liaison morte : une liaison morte, elle, se voit.

Trois ameliorements durables, chacun justifie :

  1. RESOLUTION DES PREFIXES. Deux passes : recensement des `const X = '/api/...'`
     du fichier, puis remplacement de `${X}` en tete de litteral. Un site qui ne
     se resout pas est COMPTE et AFFICHE : le silence doit rester suspect.
  2. METHODE HTTP. `GET /api/v1/x` alors que seule `POST /api/v1/x` existe n'est pas
     une liaison morte, c'est une liaison 405 : l'ecran tourne a vide. L'OpenAPI
     regenere a chaud donne les methodes reellement declarees.
  3. COMMENTAIRES RETIRES. Une URL citee dans un commentaire ou un JSDoc n'est pas
     un appel (faux positifs constates). Le meme nettoyage que
     `evo-log-backend/scripts/audit_fidelite_champs.py` est applique.

Usage :
    python scripts/audit_endpoint_bindings.py                     # tout le depot
    python scripts/audit_endpoint_bindings.py --module amenagement # un seul domaine
    python scripts/audit_endpoint_bindings.py --details            # ligne precise
    python scripts/audit_endpoint_bindings.py --json               # pour outiller la campagne

Sortie : 0 si toutes les liaisons resolues touchent une route reelle avec la
bonne methode, 1 sinon.
"""
import os
import re
import sys
import json
import pathlib
import argparse

# Ne pollue pas la vraie base : openapi() ne se connecte pas, mais l'import de
# app.main lit Settings.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "disabled")

root = pathlib.Path(__file__).resolve().parent.parent
BACKEND = root / "evo-log-backend"
FRONTEND_SRC = root / "evo-log-frontend" / "src"

sys.path.insert(0, str(BACKEND))

# Declaration d'un prefix d'API, sous ses deux formes rencontrees au depot :
#   `const AMGT = '/api/v1/amenagement-portuaire'`
#   `const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'`
# Ces pages appellent `fetch` directement, hors de l'intercepteur axios qui porte
# le token, la base et le refresh : la seconde forme est signalee comme une classe
# de defaut propre (origine codee, authentification recomposee a la main).
DECLARATION_URL = re.compile(
    r"(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*=[^;\n]*?[`'\"]((?:https?://|/api/)[^`'\"]*)[`'\"]"
)
# Appel client : `amenagementAPI.get(...)`, `apiClient.post('/x', data)`, y compris
# generiques `<Response>` et instance axios locale. Le 2e groupe est le delimiter,
# retrouve en 3e pour borner exactement le litteral.
#
# Deux contraintes qui ne sont pas esthetiques :
#   - l'identificateur doit finir par API/api/Client/client : sans cela, chaque
#     `.get(` du depot (y compris `Map.get`, `ctx.get`) declenchait une recherche
#     de quote fermante et l'audit ne terminait plus ;
#   - pas de re.S et longueur bornee : une URL d'API ne franchit jamais une ligne.
APPEL = re.compile(
    r"\b([A-Za-z_$][\w$]*(?:API|api|Client|client))\.(get|post|put|patch|delete)\s*"
    r"(?:<[^<>()]*>)?\(\s*([`'\"])((?:\\.|[^\\`'\n]){0,220})\3"
)
# `fetch(...)` avec un chemin en dur, hors instance cliente.
FETCH = re.compile(r"\bfetch\(\s*([`'\"])((?:\\.|[^\\`'\n]){0,220})\1")
INTERPOLATION = re.compile(r"\$\{[^}]*\}")


def chemin_de_valeur(valeur):
    """Partie `/api/...` d'une constante de prefix, y compris sur URL absolue.

    `http://localhost:8000/api/v1/x` et `/api/v1/x` designent la meme route : le
    contrat porte sur le chemin, pas sur l'hote.
    """
    if valeur.startswith("/api/"):
        return valeur
    if "://" in valeur:
        sans_hote = re.sub(r"^[a-z][a-z0-9+.-]*://[^/]+", "", valeur)
        idx = sans_hote.find("/api/")
        return sans_hote[idx:] if idx >= 0 else None
    return None


def retirer_commentaires(texte):
    """Remplace le contenu des commentaires par des espaces, en preservant les chaines."""
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
            # Branche indispensable : sans elle, tout caractere courant relance la
            # boucle sur lui-meme et l'audit ne termine jamais (bug constate : le
            # scan marqua au passe des le premier fichier, sans la moindre sortie).
            i += 1
    return "".join(out)


def backend_operations():
    """`({chemins}, {gabarit_norm: methodes})`, generes a chaud depuis l'app.

    Les methodes sont indexees par GABARIT normalise : sans ce cache, chaque site
    d'appel balayait toutes les operations de toutes les routes (1 195 x 1 400),
    ce qui fit tourner l'audit quinze minutes sans le finir.
    """
    import app.main as m
    spec = m.app.openapi()
    methodes_par_gabarit = {}
    chemins = set()
    for path, item in spec.get("paths", {}).items():
        chemins.add(path)
        decl = methodes_par_gabarit.setdefault(norm_backend(path), set())
        for verb in ("get", "post", "put", "patch", "delete"):
            if verb in item:
                decl.add(verb.upper())
        if not decl:
            decl.add("ANY")
    return chemins, methodes_par_gabarit


def norm_backend(chemin):
    return re.sub(r"\{[^}]+\}", "{p}", chemin).rstrip("/") or "/"


def norme_frontend(url):
    """Chemin normalise pour la comparaison : sans query, sans interpolation JS."""
    url = url.split("?")[0]
    url = INTERPOLATION.sub("{p}", url)
    if url.startswith("/api/") and not url.startswith("/api/v1/"):
        # L'intercepteur axios re-prefixe /api/x en /api/v1/x.
        url = "/api/v1" + url[len("/api"):]
    return url.rstrip("/") or "/"


def resoudre_litteral(corps, prefixes):
    """(chemin, nom_de_variable) ou (None, None) si le site n'est pas materialisable.

    Un `${X}` en tete est remplace par son prefix declare ; les autres `${...}`
    deviennent des jokers {p} (semantique REST : un parametre accepte n'importe
    quel litteral). Le nom de variable est rendu pour que l'on puisse signaler les
    appels partis d'une origine codee en dur.
    """
    m = re.match(r"^\$\{([A-Za-z_$][\w$]*)\}", corps)
    if m:
        nom = m.group(1)
        prefixe = prefixes.get(nom)
        if prefixe is None:
            return None, None
        corps = prefixe + corps[m.end():]
        return (corps, nom) if corps.startswith("/") else (None, nom)
    if corps.startswith("/"):
        return INTERPOLATION.sub("{p}", corps), None
    return None, None


def segment_equal(gabarit, chemin):
    """Un segment `{p}` du gabarit backend accepte n'importe quel litteral frontend."""
    b = [s for s in gabarit.split("/") if s]
    f = [s for s in chemin.split("/") if s]
    if len(b) != len(f):
        return False
    return all(bs == "{p}" or bs == fs for bs, fs in zip(b, f))


class IndexRoutes:
    """Gabarits backend indexes par nombre de segments, avec cache de correspondance.

    L'audit compare ~1 200 gabarits a ~700 sites d'appel : sans index, il ne
    finissait plus. Le cache rend aussi la regle « chemin de rattachement »
    (ex. `/api/v1/departement` alors que seules des sous-routes existent) utile,
    parce qu'elle ne s'applique que sur un echec de correspondence.
    """

    def __init__(self, methodes_par_gabarit):
        self.methodes = methodes_par_gabarit
        self.par_segments = {}
        for gabarit in methodes_par_gabarit:
            n = len([s for s in gabarit.split("/") if s])
            self.par_segments.setdefault(n, []).append(gabarit)
        self._cache = {}

    def gabarits_pour(self, chemin):
        if chemin not in self._cache:
            n = len([s for s in chemin.split("/") if s])
            self._cache[chemin] = [
                g for g in self.par_segments.get(n, []) if segment_equal(g, chemin)
            ]
        return self._cache[chemin]

    def existe(self, chemin):
        return bool(self.gabarits_pour(chemin)) or any(
            g.startswith(chemin + "/") for g in self.methodes
        )

    def methodes_pour(self, chemin):
        decl = set()
        for gabarit in self.gabarits_pour(chemin):
            decl |= self.methodes[gabarit]
        if not decl:
            for gabarit, verbs in self.methodes.items():
                if gabarit.startswith(chemin + "/"):
                    decl |= verbs
        return decl


def scanner_front():
    """(sites, non_resolution, opaques, origines_dures).

    `opaques` compte les appels dont l'URL est une variable (`apiClient.get(path)`).
    Ils ne sont pas auditables statiquement : les compter empeche de prendre
    un silence pour une sante.

    Deux passes. La premiere recense TOUTES les declarations de prefix du frontend,
    la seconde resout les appels. Sans la carte globale, une page qui fait
    ``fetch(`${API_BASE}/rh-avance/dipe-mensuel`)`` avec `API_BASE` declare dans un
    autre fichier restait aveugle : 14 sites echappaient encore au contrat.
    """
    fichiers = sorted(FRONTEND_SRC.rglob("*.ts*"))
    carte_globale = {}
    contenus = {}
    pour_fichier = {}
    for fichier in fichiers:
        brut = fichier.read_text(encoding="utf-8", errors="ignore")
        contenus[fichier] = brut
        locals_ = {}
        for nom, valeur in DECLARATION_URL.findall(brut):
            chemin = chemin_de_valeur(valeur)
            if chemin is None:
                continue
            locals_[nom] = (chemin, "://" in valeur)
            carte_globale.setdefault(nom, locals_[nom])
        pour_fichier[fichier] = locals_

    sites, non_resolution, opaques, origines_dures = [], [], [], []

    def enregistrer(fichier, ligne, methode, corps):
        chemin, nom = resoudre_litteral(corps, prefixes)
        if chemin is None:
            if corps[:1] in "/$":
                non_resolution.append((fichier, ligne, methode, corps[:70]))
            else:
                opaques.append((fichier, ligne, methode, corps[:70]))
            return
        if not chemin.startswith("/api/") or chemin.startswith("/api/auth"):
            return  # /api/auth = NextAuth, pas le backend FastAPI
        if nom in absolues:
            origines_dures.append((fichier, ligne, methode, nom))
        sites.append((fichier, ligne, methode, norme_frontend(chemin)))

    for fichier in fichiers:
        prefixes = {nom: chemin for nom, (chemin, _dure) in pour_fichier[fichier].items()}
        absolues = {nom for nom, (_c, dure) in pour_fichier[fichier].items() if dure}
        for nom, (chemin, dure) in carte_globale.items():
            prefixes.setdefault(nom, chemin)   # la declaration locale gagne
            if dure:
                absolues.add(nom)
        texte = retirer_commentaires(contenus[fichier])
        for m in APPEL.finditer(texte):
            enregistrer(
                fichier,
                texte[:m.start()].count("\n") + 1,
                m.group(2).upper(),
                m.group(4),
            )
        for m in FETCH.finditer(texte):
            enregistrer(
                fichier,
                texte[:m.start()].count("\n") + 1,
                "ANY",
                m.group(2),
            )
    return sites, non_resolution, opaques, origines_dures


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--module", help="filtre sur les URL resolues contenant ce mot (ex: amenagement)")
    ap.add_argument("--details", action="store_true", help="affiche fichier:ligne de chaque defaut")
    ap.add_argument("--json", action="store_true", help="sortie machine-lisible")
    args = ap.parse_args()

    chemins_bruts, methodes_par_gabarit = backend_operations()
    index = IndexRoutes(methodes_par_gabarit)
    nb_operations = sum(len(verbs) for verbs in methodes_par_gabarit.values())
    sites, non_resolution, opaques, origines_dures = scanner_front()
    if args.module:
        # Le filtre porte sur l'URL resolue, pas sur le fichier : un departement
        # est appele depuis api-client.ts par une methode nommee, pas depuis ses
        # pages. Filtrer sur les fichiers masquait la totalite du domaine.
        mot = args.module.lower()
        sites = [s for s in sites if mot in s[3].lower()]
        non_resolution = [x for x in non_resolution if mot in x[3].lower()]
        origines_dures = [x for x in origines_dures if mot in x[3].lower()]

    orphelins, methodes = [], []
    for fichier, ligne, methode, url in sites:
        if not index.existe(url):
            orphelins.append((fichier, ligne, methode, url))
        elif methode != "ANY":
            decl = index.methodes_pour(url)
            if decl and methode not in decl:
                methodes.append((fichier, ligne, methode, url, sorted(decl)))

    if args.json:
        print(json.dumps({
            "routes_backend": len(chemins_bruts),
            "operations_backend": nb_operations,
            "sites_controles": len(sites),
            "sites_prefixe_inconnu": len(non_resolution),
            "sites_opaques": len(opaques),
            "origines_codees_en_dur": [
                {"fichier": str(f), "ligne": l, "methode": m, "variable": v}
                for f, l, m, v in origines_dures
            ],
            "liaisons_mortes": [
                {"fichier": str(f), "ligne": l, "methode": m, "url": u}
                for f, l, m, u in orphelins
            ],
            "methodes_fausses": [
                {"fichier": str(f), "ligne": l, "methode": m, "url": u, "declarees": d}
                for f, l, m, u, d in methodes
            ],
        }, ensure_ascii=False, indent=1))
        return 1 if (orphelins or methodes) else 0

    print(f"Routes backend (OpenAPI a chaud)     : {len(chemins_bruts)}")
    print(f"Operations backend (path+methode)     : {nb_operations}")
    print(f"Sites d'appel resolves et controles   : {len(sites)}")
    print(f"Sites NON resolutionnes (prefix inconnu): {len(non_resolution)}")
    print(f"Sites opaques (URL en variable)         : {len(opaques)}")
    print(f"LIAISONS MORTES (aucune route)         : {len(orphelins)}")
    print(f"MAUVAISE METHODE (route en 405)        : {len(methodes)}")
    print(f"ORIGINES CODEES EN DUR (hors client)   : {len(origines_dures)}")
    print("=" * 74)

    for fichier, ligne, methode, url in sorted(orphelins, key=lambda s: (s[3], str(s[0]))):
        marque = f"{fichier}:{ligne}" if args.details else str(fichier)
        print(f"{methode:<6} {url:<58} {marque}")
    if methodes:
        print("-" * 74)
        for fichier, ligne, methode, url, decl in sorted(methodes, key=lambda s: (s[3], str(s[0]))):
            marque = f"{fichier}:{ligne}" if args.details else str(fichier)
            print(f"{methode:<6} {url:<58} declare: {','.join(decl):<16} {marque}")
    if origines_dures:
        print("-" * 74)
        print("Appels partis d'une constante d'URL absolue (origine codee en dur, "
              "hors intercepteur qui porte token/base/refresh) :")
        par_fichier_tri = {}
        for fichier, ligne, methode, nom in origines_dures:
            par_fichier_tri.setdefault(str(fichier), []).append(f"{methode} L{ligne} ${{{nom}}}")
        for nom_fichier, details in sorted(par_fichier_tri.items()):
            print(f"   {nom_fichier}  ({len(details)} appel(s)) : {', '.join(details[:6])}")

    if non_resolution:
        print("-" * 74)
        print("Sites dont l'URL n'a pas pu etre materialisee (verifier la main) :")
        for fichier, ligne, methode, corps in non_resolution[:20]:
            print(f"{methode:<6} {corps:<58} {fichier}:{ligne}")
    if opaques and args.details:
        print("-" * 74)
        print(f"{len(opaques)} site(s) dont l'URL vient d'une variable (non auditables) :")
        for fichier, ligne, methode, corps in opaques[:30]:
            print(f"{methode:<6} {corps:<58} {fichier}:{ligne}")

    defauts = len(orphelins) + len(methodes) + len(origines_dures)
    if defauts:
        print(f"\n{defauts} defaut(s) de liaison. Une page qui appelle une route absente "
              "affiche un etat vide sans erreur visible ; une page qui colle son "
              "URL absolue court-circuite l'intercepteur (token, base, refresh).")
        return 1
    print("\nLiaisons OK : tout appel resolutionne touche une route reelle, bonne methode.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

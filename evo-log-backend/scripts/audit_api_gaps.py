# -*- coding: utf-8 -*-
"""Audit des ecarts entre appels du frontend et routes declarees par le backend.

Outil de suivi du plan : chaque tranche doit faire baisser le nombre d'ecarts.

Usage :
    python scripts/dump_openapi_paths.py     # regenere _openapi_paths.json
                                             # et _openapi_stubs.json
    python scripts/audit_api_gaps.py         # produit _gap_report.json

Les artefacts d'audit ne sont pas versionnes a la main.

Ce que « ecart » veut dire ici. Le backend ne repond jamais 404 sur l'API metier :
`app/routers/v1/pending_modules.py` installe un catch-all de derniere priorite,
declare `include_in_schema=False` (donc absent du snapshot), qui renvoie une
enveloppe vide marquee `pending: true`. Un appel sans route correspondante n'est
donc pas une erreur visible : c'est un ecran qui affiche « module en cours de
deploiement » sans donnee reelle. C'est exactement ce que l'audit doit compter.
De meme, une route qui existe mais dont le handler appelle
`app.core.not_implemented` repond 501 : la route est la, la donnee non.

Les regles de comparaison, pour que le chiffre soit traitable tel quel :
  * un segment interpole `${id}` du frontend est un joker face a un parametre
    `{conge_id}` du backend : `rh/conges/${id}/approuver` n'est pas un ecart ;
  * le meme jeton face a un LITERAL backend (`acconage/${id}` vs `acconage/yard`)
    reste une supposition : c'est signale `joker_ambigu`, jamais `couvert` ;
  * les commentaires et la normalisation d'URL du client ne sont pas des appels.
"""
import json
import os
import re
import sys
from pathlib import Path

BACKEND = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND = BACKEND.parent / "evo-log-frontend" / "src"
SNAPSHOT = BACKEND / "_openapi_paths.json"
STUBS = BACKEND / "_openapi_stubs.json"
RAPPORT = BACKEND / "_gap_report.json"

# Un appel d'API du frontend : chaine literal commencant par /api/, avec des
# interpolations ${...} eventuelles (template literals).
APPEL = re.compile(r"""['"`](/api/[^'"`\n]*)['"`]""")
# Interpolation a effacer AVANT l'extraction : sinon le quote d'un ternaire
# imbrique (`${statut === 'APPROUVE' ? 'approuver' : 'rejeter'}`) clot le literal
# trop tot et fabrique un faux chemin.
INTERPOLATION = re.compile(r"\$\{[^{}]*\}")
JETON = "{p}"
PARAM_NOM = re.compile(r"^\{([a-zA-Z0-9_]+)(?::(path))?\}$")

# Litteraux qui ne declenchent aucun appel HTTP : la normalisation d'URL du
# client (`apiUrl`, intercepteur axios) manipule des prefixes et compare des
# chaines. Le motif est ancre en fin de fenetre pour ne rejeter que le literal
# place LA comme operande : un vrai appel ternaire (`x ? '/api/a' : '/api/b'`)
# doit rester signale, sinon l'audit masquerait des ecarts.
NON_APPEL = re.compile(
    r"((startsWith|endsWith|includes)\s*\(\s*$|(===|!==|\+)\s*$|\b(const|let|var)\s+\w*(PREFIX|BASE)\w*\s*=\s*$)"
)
# Commentaire pur (JSDoc, ligne `//`, ligne ` * ...`) : les exemples d'URL y sont
# de la documentation, pas des appels.
COMMENTAIRE = re.compile(r"^\s*(//|/\*|\*)")
# Le backend expose ces endpoints HORS de l'arbre versionne /api/v1 : le
# middleware de `app/main.py` les met explicitement hors reecriture, une absence
# de correspondance dans le snapshot n'est donc pas un ecart.
HORS_VERSIONNE = ("/api/health", "/api/docs", "/api/redoc", "/api/openapi.json",
                  "/api/setup", "/api/seed")

# Le catch-all pending ne sert pas tout : ces premiers segments gardent un vrai
# 404. Source de verite : le routeur lui-meme, avec repli si l'import echoue
# (l'audit doit pouvoir tourner sans l'environnement serveur).
PREFIQUES_REPLI = ("auth", "health", "docs", "redoc", "openapi", "status",
                   "setup", "seed", "public", "ws")


def prefixes_exclus():
    try:
        sys.path.insert(0, str(BACKEND))
        from app.routers.v1.pending_modules import _EXCLUDED_PREFIXES
        return frozenset(_EXCLUDED_PREFIXES)
    except Exception:  # noqa: BLE001
        return frozenset(PREFIQUES_REPLI)


def segments(chemin: str):
    """Decoupe stable, sans slash de fin fantome."""
    return [s for s in chemin.strip("/").split("/") if s != ""]


def normaliser(chemin: str) -> str:
    """Chaine du frontend -> chemin comparable aux templates OpenAPI.

    Les clients appellent indifferemment /api/x et /api/v1/x : le middleware de
    `app/main.py` reecrit /api/<suite> en /api/v1/<suite>, donc les deux formes
    designent la meme route. Les interpolations ${id} deviennent un jeton joker.
    """
    chemin = INTERPOLATION.sub(JETON, chemin.split("?")[0].split("#")[0])
    if not chemin.startswith("/api/v1/"):
        chemin = "/api/v1/" + chemin[len("/api/"):]
    return re.sub(r"/{2,}", "/", chemin)


def compat(front: str, template: str, exige_prouve: bool = False):
    """`template` peut-il servir `front` ? Renvoie le degre de certitude.

    Les deux colonnes ont des jokers : `{param}` cote backend, `{p}`
    (interpolation `${id}`, `${action}`) cote frontend. Mais un jeton frontend
    qui retombe sur un LITERAL backend n'est pas une preuve :
    `acconage/${id}` ressemble a `acconage/yard` sans l'etre. On separe donc :
      * "strict"  correspondence sans supposition ;
      * "lax"     possible seulement si l'interpolation designe ce literal ;
      * None      impossible.

    `exige_prouve` (domaines sous regle « aucune fausse couverture ») supprime
    le degre "lax" : sans preuve, la route ne couvre pas l'appel.
    """
    a, b = segments(front), segments(template)
    strict = True
    for i, seg in enumerate(b):
        m = PARAM_NOM.match(seg)
        if m:
            if m.group(2) == "path":  # joker multi-troncons
                return "strict" if len(a) >= i else None
            if i >= len(a):
                return None
            continue  # un parametre accepte n'importe quel segment
        if i >= len(a):
            return None
        if a[i] == seg:
            continue
        if a[i] == JETON:
            if exige_prouve:
                return None
            strict = False
            continue
        return None
    if len(a) != len(b):
        return None
    return "strict" if strict else "lax"


def charger_routes():
    if not SNAPSHOT.exists():
        sys.exit("%s absent : lancer scripts/dump_openapi_paths.py d'abord" % SNAPSHOT.name)
    routes = json.loads(SNAPSHOT.read_text(encoding="utf-8-sig"))
    if STUBS.exists():
        stubs = set(json.loads(STUBS.read_text(encoding="utf-8-sig")))
    else:
        print("AVERTISSEMENT : %s absent, les routes 501 seront comptees comme couvertes"
              % STUBS.name)
        stubs = set()
    return routes, stubs


def est_un_appel(ligne: str, offset: int) -> bool:
    """Le literal a `offset` designe-t-il vraiment un appel HTTP ?

    `offset` pointe APRES le quote d'ouverture : la fenetre doit perdre ce
    delimiteur, sinon `startsWith('` ne se reconnait jamais comme un test de
    predicat et la normalisation du client repasse en faux appel.
    """
    if COMMENTAIRE.match(ligne):
        return False
    fenetre = ligne[max(0, offset - 60):offset].rstrip()
    fenetre = fenetre[:-1].rstrip() if fenetre[-1:] in ("'", '"', "`") else fenetre
    return not NON_APPEL.search(fenetre)


def appels_frontend():
    """Tous les appels /api/ du frontend, avec leur position."""
    trouves = []
    for fichier in sorted(FRONTEND.rglob("*")):
        if not fichier.is_file() or fichier.suffix not in (".ts", ".tsx"):
            continue
        if "node_modules" in str(fichier):
            continue
        texte = fichier.read_text(encoding="utf-8", errors="replace")
        for numero, ligne in enumerate(texte.splitlines(), 1):
            clean = INTERPOLATION.sub(JETON, ligne)
            for m in APPEL.finditer(clean):
                brut = m.group(1)
                if brut.startswith(HORS_VERSIONNE):
                    continue
                if not est_un_appel(clean, m.start()):
                    continue
                trouves.append((normaliser(brut), str(fichier), numero, brut))
    return trouves


# Domaines sous politique « aucune fausse couverture » : le chiffre d'un
# transport ou d'un magasin engage la douane, la TVA et l'inventaire physique.
# Un appel qui n'y est pas prouve par un {parametre} est un trou a reboucher,
# pas une zone grise. Les autres domaines gardent le signalement `joker_ambigu`
# (a trier a la main) : durcir sans connaitre le metier ferait apparaitre des
# trous imaginaires.
DOMAINES_EXIGEANTS = ("transport", "magasin")


def domaine(chemin):
    seg = segments(chemin)
    return seg[2] if len(seg) > 2 else ""


def classifier(chemin, routes, stubs, exclus, exige_prouve=False):
    """(genre, route) pour un appel frontend : reelle, 501, pending ou 404.

    Toutes les routes candidates sont collectees : un appel peut correspondre a
    la fois a un handler reel et a un stub (deux routeurs sur le meme chemin) ;
    annoncer alors `repond_501` serait un faux positif.

    `exige_prouve` (voir DOMAINES_EXIGEANTS) ferme le degre "lax" : dans ces
    domaines, un joker qu'on ne peut pas prouver est compte comme trou 
    `pending_sans_donnee`  et non comme une zone grise qu'on pourrait laisser
    passer en la classant « couvert » sur une simple ressemblance de chemin.
    """
    candidates = [(r, k) for r in routes if (k := compat(chemin, r, exige_prouve))]
    reels = [(r, k) for r, k in candidates if r not in stubs]
    strictes = [r for r, k in reels if k == "strict"]
    if strictes:
        return "couvert", strictes[0]
    if reels:
        return "joker_ambigu", reels[0][0]
    if candidates:
        return "repond_501", candidates[0][0]
    seg = segments(chemin)
    if len(seg) > 2 and seg[2] in exclus:
        return "404_reel", None
    return "pending_sans_donnee", None


def main():
    routes, stubs = charger_routes()
    exclus = prefixes_exclus()

    ecarts = []
    vus = set()
    for chemin, fichier, numero, brut in appels_frontend():
        genre, route = classifier(chemin, routes, stubs, exclus,
                                  exige_prouve=domaine(chemin) in DOMAINES_EXIGEANTS)
        if genre == "couvert":
            continue
        cle = (chemin, fichier, numero)
        if cle in vus:
            continue
        vus.add(cle)
        ecarts.append({
            "appel": chemin,
            "brut": brut,
            "fichier": os.path.relpath(fichier, BACKEND.parent).replace("\\", "/"),
            "ligne": numero,
            "genre": genre,
            "route": route,
        })

    ecarts.sort(key=lambda e: (e["genre"], e["fichier"], e["ligne"]))
    RAPPORT.write_text(json.dumps(ecarts, indent=1, ensure_ascii=False), encoding="utf-8")

    par_genre = {}
    for e in ecarts:
        par_genre[e["genre"]] = par_genre.get(e["genre"], 0) + 1
    print("routes OpenAPI examinees : %d (dont %d repondant 501)" % (len(routes), len(stubs)))
    print("appels frontend sans donnee reelle : %d" % len(ecarts))
    for genre, n in sorted(par_genre.items(), key=lambda kv: -kv[1]):
        print("  %-22s %d" % (genre, n))
    par_module = {}
    for e in ecarts:
        seg = segments(e["appel"])
        cle = seg[2] if len(seg) > 2 else "(racine)"
        par_module[cle] = par_module.get(cle, 0) + 1
    for module, n in sorted(par_module.items(), key=lambda kv: -kv[1]):
        print("  %-22s %d" % ("/api/v1/" + module, n))
    print("rapport detaille : %s" % RAPPORT.name)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Regenere le snapshot des routes OpenAPI exposees par l'app (outil de audit).

Usage: python scripts/dump_openapi_paths.py
Ecrit: _openapi_paths.json (liste des templates de paths, racine du backend)
       _openapi_stubs.json  (paths dont TOUS les handlers sont des stubs 501)

Le second fichier est indispensable a l'audit des ecarts : une route declaree
dans l'OpenAPI n'est pas une donnee reelle. `app/core/not_implemented.py` pose
volontairement des 501 a la place d'un faux succes ; un ecran qui appelle l'une
de ces routes affiche un etat vide, exactement comme si la route manquait.

Note d'implementation : depuis FastAPI 0.115, `include_router()` n'aplatit plus
l'arbre : il insere un `_IncludedRouter` paresseux. Les chemins absolus se
reconstruisent depuis `include_context.prefix` + `original_router.routes`, et
non plus depuis `app.routes` seul (qui ne donne que 133 objets pour 1088 paths).
"""
import inspect
import json
import os
import sys

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND)
os.chdir(BACKEND)

# Marqueurs du choix d'honnetete : le handler ne fait pas le travail.
STUB = ("not_implemented(", "HTTP_501", "status_code=501")


def routes_absolues(app):
    """Yield (chemin_absolu, objet_route) pour toutes les feuilles de l'app."""
    def parcourir(routes, prefixe):
        for route in routes:
            ctx = getattr(route, "include_context", None)
            if ctx is not None:  # _IncludedRouter : inclusion paresseuse
                sous = getattr(getattr(route, "original_router", None), "routes", []) or []
                yield from parcourir(sous, prefixe + (getattr(ctx, "prefix", "") or ""))
                continue
            chemin = getattr(route, "path", None)
            if chemin is None:  # Mount, static files, etc.
                sous = getattr(route, "routes", None) or []
                yield from parcourir(sous, prefixe + (getattr(route, "path", "") or ""))
                continue
            yield prefixe + chemin, route

    yield from parcourir(app.routes, "")


def est_stub(route) -> bool:
    endpoint = getattr(route, "endpoint", None)
    if endpoint is None:
        return False
    try:
        source = inspect.getsource(endpoint)
    except (TypeError, OSError):
        return False
    return any(marque in source for marque in STUB)


def aplatir(nom, schemas, memo, profondeur=0):
    """Proprietes effectives d'un schema, herite `allOf` resolus.

    Pydantic/FastAPI rend un sous-classe comme
    `{"CamionResponse": {"allOf": [{"$ref": "#/.../CamionBase"}, {propriete: ...}]}}` :
    sans resolution recursive, la moitie des champs d'un objet repondu
    seraient invisibles et l'audit des champs les signalerait comme inventes.
    """
    if nom in memo or profondeur > 6:
        return memo.get(nom, {})
    memo[nom] = champs = {}
    brut = schemas.get(nom) or {}
    morceaux = [brut] + list(brut.get("allOf") or []) + list(brut.get("oneOf") or []) \
        + list(brut.get("anyOf") or [])
    for morceau in morceaux:
        for cible in refs_herites(morceau, schemas):
            for cle, val in aplatir(cible, schemas, memo, profondeur + 1).items():
                champs.setdefault(cle, val)
        for cle, val in (morceau.get("properties") or {}).items():
            champs.setdefault(cle, val)
    return champs


def enums_de(prop_schema, schemas):
    """Valeurs admises d'une proprieté, en suivant les $ref vers les enums."""
    for morceau in [prop_schema] + list(prop_schema.get("allOf") or []):
        if isinstance(morceau.get("enum"), list):
            return [v for v in morceau["enum"] if isinstance(v, str)]
        ref = morceau.get("$ref")
        if isinstance(ref, str):
            cible = ref.rsplit("/", 1)[-1]
            sous = schemas.get(cible) or {}
            if isinstance(sous.get("enum"), list):
                return [v for v in sous["enum"] if isinstance(v, str)]
    return []


def refs_herites(morceau, schemas):
    """schemas dont `morceau` HERITE (allOf/oneOf/$ref/items de tableau)."""
    out = []
    ref = morceau.get("$ref")
    if isinstance(ref, str):
        out.append(ref.rsplit("/", 1)[-1])
    for cle in ("items", "additionalProperties"):
        sous = morceau.get(cle)
        if isinstance(sous, dict):
            out.extend(refs_herites(sous, schemas))
    return out


def refs_contenus(morceau, schemas, profondeur=0):
    """schemas CONTENTUS par une reponse, enveloppes de liste incluses.

    Distinction indispensable : `PanneListResponse` n'a pour proprietes que
    `items`/`total`. Si l'audit des champs ne voit que ce nom-la, il signale
    chaque champ reel comme inexistant. On descend donc aussi dans
    `properties`, ce qu'on refuse de faire pour l'heritage.
    """
    out = []
    if profondeur > 3:
        return out
    ref = morceau.get("$ref")
    if isinstance(ref, str):
        cible = ref.rsplit("/", 1)[-1]
        out.append(cible)
        sous = schemas.get(cible) or {}
        out.extend(refs_contenus(sous, schemas, profondeur + 1))
        return out
    for cle in ("items", "additionalProperties"):
        sous = morceau.get(cle)
        if isinstance(sous, dict):
            out.extend(refs_contenus(sous, schemas, profondeur + 1))
    for sous in (morceau.get("properties") or {}).values():
        if isinstance(sous, dict):
            out.extend(refs_contenus(sous, schemas, profondeur + 1))
    for cle in ("allOf", "oneOf", "anyOf"):
        for sous in morceau.get(cle) or []:
            if isinstance(sous, dict):
                out.extend(refs_contenus(sous, schemas, profondeur + 1))
    return out


def contrat(spec):
    """{schemas: {nom: {champs, enums}}, reponses: {path: {method: [noms]}}}."""
    schemas = ((spec.get("components") or {}).get("schemas")) or {}
    memo = {}
    rendus = {}
    for nom in schemas:
        champs = aplatir(nom, schemas, memo)
        rendus[nom] = {
            "champs": sorted(champs),
            "enums": {c: enums_de(v, schemas) for c, v in champs.items()
                      if enums_de(v, schemas)},
        }
    reponses = {}
    for path, ops in (spec.get("paths") or {}).items():
        par_method = {}
        for method, op in (ops or {}).items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            reponses_op = op.get("responses") or {}
            # Ce backend repond 201 sur les créations (`status_code=201_CREATED`) :
            # ne lire que « 200 » priverait l'audit de contrat toute la mutation.
            corps = {}
            for code in sorted(k for k in reponses_op if str(k).startswith("2")):
                contenu = ((reponses_op[code].get("content") or {})
                           .get("application/json") or {})
                if isinstance(contenu.get("schema"), dict):
                    corps = contenu["schema"]
                    break
            if not isinstance(corps, dict):
                par_method[method] = []
                continue
            par_method[method] = sorted(set(refs_contenus(corps, schemas)))
        reponses[path] = par_method
    return {"schemas": rendus, "reponses": reponses}


def main():
    from app.main import app

    spec = app.openapi()
    paths = sorted(spec.get("paths", {}).keys())
    out = os.path.join(BACKEND, "_openapi_paths.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(paths, fh, indent=1)
    print(f"{len(paths)} routes OpenAPI -> {out}")

    ctr = contrat(spec)
    out_ctr = os.path.join(BACKEND, "_openapi_contrat.json")
    with open(out_ctr, "w", encoding="utf-8") as fh:
        json.dump(ctr, fh, indent=1)
    avec_enum = sum(1 for s in ctr["schemas"].values() if s["enums"])
    print("%d schemas (dont %d porteurs d'enum) -> %s"
          % (len(ctr["schemas"]), avec_enum, out_ctr))

    par_chemin = {}
    for chemin, route in routes_absolues(app):
        par_chemin.setdefault(chemin, []).append(est_stub(route))
    # Une path n'est un trou fonctionnel que si AUCUN de ses handlers ne travaille.
    completement_stub = sorted(p for p, v in par_chemin.items() if v and all(v))
    inattendues = [p for p in completement_stub if p not in set(paths)]
    out_stub = os.path.join(BACKEND, "_openapi_stubs.json")
    with open(out_stub, "w", encoding="utf-8") as fh:
        json.dump(completement_stub, fh, indent=1)
    print("%d routes dont tous les handlers repondent 501 -> %s"
          % (len(completement_stub), out_stub))
    print("  (routes resolues : %d paths, %d handlers)"
          % (len(par_chemin), sum(len(v) for v in par_chemin.values())))
    if inattendues:
        print("  HORS snapshot OpenAPI (a verifier) : %s" % inattendues[:5])


if __name__ == "__main__":
    main()

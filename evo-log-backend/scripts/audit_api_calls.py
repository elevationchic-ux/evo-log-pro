"""Audit : quels appels API du frontend ne touchent AUCUNE route reelle du backend ?

Un appel qui ne matche rien tombe dans le catch-all de pending_modules.py, qui
repond une enveloppe « pending » 200 au lieu d'un 404. Ce rapport liste ces
appels pour qu'ils soient relies a une route existante (ou que la route soit
creee) : c'est le seul pre-requis pour supprimer l'enveloppe factice sans
laisser une page sur un echec brut.

Les chemins du front sont ecrits en litteraux ou en modeles (`${API_PREFIX}`,
`/tiers/${id}`) : les variables deviennent des jokers, et le rapprochement avec
les gabarits de routes FastAPI (`/tiers/{tier_id}`) se segment par segment.

Usage :  python scripts/audit_api_calls.py          (depuis evo-log-backend)
"""
from __future__ import annotations

import difflib
import re
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONT = ROOT / "evo-log-frontend" / "src"
BACKEND_APP_DIR = ROOT / "evo-log-backend"

sys.path.insert(0, str(BACKEND_APP_DIR))
from app.main import app  # noqa: E402

# appelClient.get('/tiers/12') | apiClient.post(`/x/${id}`) | apiUrl('/y') | fetch('/z')
APPEL = re.compile(
    r"""api(?:Client|)\s*\.\s*(get|post|put|patch|delete)\s*\(\s*[`'"]([^`'"]+)[`'"]"""
    r"""|apiUrl\s*\(\s*[`'"]([^`'"]+)[`'"]"""
    r"""|\bfetch\s*\(\s*[`'"]([^`'"]+)[`'"]""",
    re.IGNORECASE,
)
VAR = re.compile(r"\$\{[^{}]*\}")
PLACEHOLDER = "\u0000"   # segment inconnu (variable ou {param}) -> joker
RESTE = "\u0001"         # {x:path} de FastAPI -> joker multi-segments
SEG_GABARIT = re.compile(r"\{[^/{}]+(:path)?\}")
ROUTES: list = []        # (METHODE, segments gabarit, chemin brut), rempli dans main()


def segments_chemin(url: str):
    """Chemin d'appel -> liste de segments, variables remplacees par le joker.

    Les modeles de chaine sont ambigus (${API_PREFIX} vaut « /api/v1 », soit 2
    segments ; ${id} vaut 1 segment). On garde donc le joker et le rapprochement
    accepte qu'il couvre un ou plusieurs segments.
    """
    if url.startswith("http"):
        from urllib.parse import urlparse

        url = urlparse(url).path
    url = url.split("?")[0]
    url = VAR.sub(PLACEHOLDER, url)
    url = re.sub(r"\{[^/{}]+\}", PLACEHOLDER, url)
    if not url.startswith("/"):
        url = "/" + url
    if url.startswith("/api/v1/"):
        pass
    elif url.startswith("/api/"):
        url = "/api/v1/" + url[len("/api/"):]
    elif not url.startswith("/api/v1"):
        url = "/api/v1" + url
    seg = [s for s in url.split("/") if s != ""]
    return seg


def segments_gabarit(path: str):
    """Gabarit de route FastAPI -> segments, `{param}` converti en joker.

    Sans cette conversion, `/magasin/articles/{article_id}` restait un segment
    litteral `{article_id}` : TOUTES les routes de detail du backend (soit la
    moitie de l'API) etaient signalees a tort comme orphelines.
    """
    out = []
    for seg in path.split("/"):
        if seg == "":
            continue
        if SEG_GABARIT.fullmatch(seg):
            # `{x:path}` avale plusieurs segments, `{x}` exactement un.
            out.append(RESTE if seg.endswith(":path}") else PLACEHOLDER)
        else:
            out.append(seg)
    return out


@lru_cache(maxsize=4096)
def correspond(call: tuple, route: tuple) -> bool:
    """Match segment a segment. Un joker represente TOUJOURS au moins un segment :

    `/x/{id}` ne matche pas `/x` (la route collecte n'est pas la route detail), et
    `/x/${id}/pdf` ne matche pas `/x` non plus. Autoriser le joker vide faisait
    disparaitre de vrais orphelins du rapport.
    """
    call, route = list(call), list(route)
    memo = {}

    def suit(i: int, j: int) -> bool:
        cle = (i, j)
        if cle in memo:
            return memo[cle]
        if i == len(call) or j == len(route):
            ok = i == len(call) and j == len(route)
            memo[cle] = ok
            return ok
        a, b = call[i], route[j]
        if b == RESTE:
            # {x:path}: le gabarit avale tout le reste de l'appel.
            memo[cle] = True
            return True
        if a == PLACEHOLDER:
            for k in range(i + 1, len(call) + 1):
                if suit(k, j):
                    memo[cle] = True
                    return True
            memo[cle] = False
            return False
        if b == PLACEHOLDER:
            ok = suit(i + 1, j + 1)
            memo[cle] = ok
            return ok
        ok = a == b and suit(i + 1, j + 1)
        memo[cle] = ok
        return ok

    return suit(0, 0)


def methode_reelle(meth: str, seg: tuple):
    """Routes declarant explicitement cette methode et matchant le chemin."""
    return {p for m, g, p in ROUTES if m == meth and correspond(seg, g)}


def chemin_existant(seg: tuple):
    return {p for m, g, p in ROUTES if correspond(seg, g)}


def suggestions(seg: tuple, n: int = 3):
    """Gabarits reales les plus proches, pour recabler plutot que creer ex nihilo."""
    cible = "/" + "/".join(s if s != PLACEHOLDER else "{x}" for s in seg)
    candidats = sorted({p for m, g, p in ROUTES}, key=len)
    note = sorted(candidats, key=lambda p: -rapport(cible, p))[:n]
    return [(p, round(rapport(cible, p) * 100)) for p in note if rapport(cible, p) > 0.55]


def rapport(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def methodes_reelles():
    """Routes reelslement enregistrees dans l'app, et non l'OpenAPI.

    L'OpenAPI omet les routes declarees `include_in_schema=False` (celles du
    pont S3, des websockets, etc.) : les ignorer ferait passer des endpoints
    existants pour des orphelins. On itere donc `app.routes`, en excluant nos
    propres catch-all (`pending_modules`), qui matcheront tout par definition.
    """
    out = []
    catch_all = {"/api/v1/{full_path:path}"}
    for route in app.routes:
        path = getattr(route, "path", None)
        if not path or path in catch_all:
            continue
        methodes = getattr(route, "methods", None) or set()
        gabarit = tuple(segments_gabarit(path))
        for meth in sorted(methodes):
            if meth in ("HEAD", "OPTIONS"):
                continue
            out.append((meth.upper(), gabarit, path))
    return out


def main():
    global ROUTES
    ROUTES = methodes_reelles()
    orphelins = defaultdict(set)
    ambigus = defaultdict(set)
    indetermine = defaultdict(set)

    for fichier in sorted(FRONT.rglob("*.ts*")):
        if "node_modules" in str(fichier):
            continue
        texte = fichier.read_text(encoding="utf-8", errors="ignore")
        for match in APPEL.finditer(texte):
            meth = (match.group(1) or "").upper()
            cible = match.group(2) or match.group(3) or match.group(4)
            if not cible:
                continue
            if cible.startswith("/api/docs") or cible.startswith("/api/health"):
                continue
            where = str(fichier.relative_to(ROOT))
            if "'" in cible or '"' in cible:
                # Litteral tronque par l'expression capturee (${a || b}) :
                # non resolvable statiquement, a controler a la main.
                indetermine[where].add(f"{meth or 'ANY'} {cible}")
                continue
            seg = tuple(segments_chemin(cible))
            if not seg:
                continue
            entete = f"{'ANY' if not meth else meth} {'/' + '/'.join(s if s != PLACEHOLDER else '{x}' for s in seg)}"
            if not meth:
                # fetch() : la methode est portee par l'objet d'options. Des qu'une
                # route existe sur ce chemin, l'appel est considere vivant.
                if chemin_existant(seg):
                    continue
                proches = "; ".join(f"{p} ({d}%)" for p, d in suggestions(seg))
                orphelins[where].add(f"ANY {entete.split(' ', 1)[1]} (fetch) " + (
                    f"\n        proche: {proches}" if proches else ""
                ))
                continue
            if methode_reelle(meth, seg):
                continue
            vues = chemin_existant(seg)
            if vues:
                # Le chemin existe mais pas pour cette methode : a verifier.
                ambigus[where].add(f"{entete}  -> route existe: {sorted(vues)}")
            else:
                proches = "; ".join(f"{p} ({d}%)" for p, d in suggestions(seg))
                orphelins[where].add(f"{entete}" + (f"\n        proche: {proches}" if proches else ""))

    total = sum(len(v) for v in orphelins.values())
    sous = sum(len(v) for v in ambigus.values())
    if not orphelins and not ambigus:
        print("AUCUN appel orphelin : tout correspond a une route reelle.")
        if indetermine:
            print("(restent resoudre manuellement: gabarits de chaine imbriques)")
        return

    print("=" * 72)
    print(f"APPELS SANS ROUTE EQUIVALENTE ({total}) — servis par le catch-all pending")
    print("=" * 72)
    for fichier in sorted(orphelins):
        print(f"\n{fichier}")
        for l in sorted(orphelins[fichier]):
            print(f"   {l}")

    print()
    print("=" * 72)
    print(f"CHEMINS EXISTANTS MAIS METHODE NON DECLAREE ({sous})")
    print("=" * 72)
    for fichier in sorted(ambigus):
        print(f"\n{fichier}")
        for l in sorted(ambigus[fichier]):
            print(f"   {l}")

    if indetermine:
        print()
        print("=" * 72)
        print("LITTERAUX NON RESOLUS STATIQUEMENT (a controls manuels)")
        print("=" * 72)
        for fichier in sorted(indetermine):
            print(f"\n{fichier}")
            for l in sorted(indetermine[fichier]):
                print(f"   {l}")


if __name__ == "__main__":
    main()

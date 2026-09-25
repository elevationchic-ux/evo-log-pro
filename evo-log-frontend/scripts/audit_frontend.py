#!/usr/bin/env python3
"""Audit UX/frontend EVO-LOG.

Detecte, par module (dossier de premier niveau sous src/app) :
  - broken_links   : liens de navigation (href, router.push, Link) vers des routes sans page.tsx
  - dead_buttons   : alert(...), onClick={() => {}}, href="#"
  - fake_data      : constantes MOCK_/DEMO_/INITIAL_/SAMPLE_/Fake + tableaux litteraux longs hors API
  - api_gaps       : appels apiClient vers des endpoints absents du backend FastAPI (/api/v1/...)
  - ghost_routes   : fichiers dechets dans le route tree Next.js (*~1, .xaml, .BAK, .CON...)

Sortie : stdout lisible + scripts/audit_report.json (par module).
Exit code : 0 si aucun residu, 1 sinon (definition "fini" de chaque vague).

Usage : python scripts/audit_frontend.py [--module magasin] [--backend ../evo-log-backend]
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FE_ROOT = os.path.dirname(HERE)                      # evo-log-frontend/
SRC = os.path.join(FE_ROOT, "src")
APP = os.path.join(SRC, "app")

# ---------------------------------------------------------------- sources
def ts_sources():
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".next", "__pycache__")]
        for f in files:
            if f.endswith((".tsx", ".ts")):
                yield os.path.join(root, f)


def read(path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def module_of(rel):
    """Module = 1er segment de chemin sous src/, '(app)' et '(auth)' normalises."""
    parts = rel.replace("\\", "/").split("/")
    for i, p in enumerate(parts):
        if p == "app" and i + 1 < len(parts):
            nxt = parts[i + 1]
            if nxt.startswith("("):  # route groups partages
                return parts[i + 2] if len(parts) > i + 2 else "_root"
            return "_app_root"
    return parts[0] if parts[0] not in ("app",) else "_root"


# ---------------------------------------------------------------- routes
def build_routes():
    routes = set()
    for root, dirs, files in os.walk(APP):
        if "page.tsx" in files:
            rel = os.path.relpath(root, APP).replace(os.sep, "/")
            rel = "/".join(p for p in rel.split("/") if not (p.startswith("(") and p.endswith(")")))
            routes.add("/" + rel if rel else "/")
    return routes


LINK_PAT = re.compile(
    r"""(?:router\.push\(\s*|Link\s+href=|href=\s*|push\(\s*|to=\s*|["']url["']\s*:\s*|url\s*:\s*|path\s*:\s*|href\s*:\s*)"""
    r"""["'`](/[a-zA-Z0-9\-_/.${}]*?)["'`]"""
)


def route_exists(target, routes):
    if target in routes:
        return True
    parts = target.split("/")
    for r in routes:
        rp = r.split("/")
        if len(rp) != len(parts):
            continue
        if all(p == q or q.startswith("[") or any(c in p for c in "${") or q in ("new",) and p == "new"
               for p, q in zip(parts, rp)):
            return True
    return False


# ---------------------------------------------------------------- backend
ROUTER_PAT = re.compile(r"@router\.(?:get|post|put|patch|delete)\(\s*[\"']([^\"']+)[\"']")
APIROUTER_PREFIX_PAT = re.compile(r"APIRouter\((?:[^)]*?)prefix\s*=\s*[\"']([^\"']+)[\"']")
INCLUDE_PAT = re.compile(r"include_router\(\s*([\w.]+)\.router\s*,\s*prefix\s*=\s*[\"']([^\"']+)[\"']")


def build_backend_paths(backend_dir):
    """Chemins complets du backend : prefix d'include (main.py) + prefix APIRouter + route."""
    paths = set()
    routers_dir = os.path.join(backend_dir, "app", "routers")
    if not os.path.isdir(routers_dir):
        return paths
    # index des fichiers router : nom normalise -> (routes, prefix_propre)
    index = {}
    for root, dirs, files in os.walk(routers_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".py") or f == "__init__.py":
                continue
            txt = read(os.path.join(root, f))
            routes = ROUTER_PAT.findall(txt)
            pm = APIROUTER_PREFIX_PAT.search(txt)
            stem = f[:-3].lower().replace("_", "-")
            index[stem] = (routes, pm.group(1) if pm else "")
    # en l'absence de main.py, considerer les routes fichiers tels quels
    main = os.path.join(backend_dir, "app", "main.py")
    if not os.path.isfile(main):
        for routes, pref in index.values():
            for r in routes:
                paths.add((pref + r) if pref else "/" + r.lstrip("/"))
        return paths
    for alias, prefix in INCLUDE_PAT.findall(read(main)):
        key = alias.lower().replace("_", "-")
        entry = index.get(key)
        if entry is None:  # alias = dernier segment d'un module (ex: v1.transit_douane_avance)
            entry = index.get(key.split(".")[-1])
        if entry is None:
            continue
        routes, file_pref = entry
        base = prefix.rstrip("/") + (file_pref if file_pref else "")
        for r in routes:
            paths.add(base.rstrip("/") + "/" + r.lstrip("/") if r != "/" else base or "/")
    # routes declarees hors pattern "<alias>.router" (app directly)
    return paths


FE_CALL_PAT = re.compile(r"""api(?:Client)?\.(?:get|post|put|patch|delete)\(\s*[`"'](/[a-zA-Z0-9\-_/]+)[`"']""")


def api_gap(path, backend_paths):
    """Frontend path '/api/x/y' -> backend '/api/v1/x/y' (rewriting existante)."""
    p = re.sub(r"/\$\{[^}]*\}.*$", "", path)
    p = re.sub(r"/\{[^}]*\}$", "", p)
    if p.startswith("/api/"):
        candidates = [p, p.replace("/api/", "/api/v1/", 1)]
    else:
        candidates = ["/api/v1" + p]
    for cand in candidates:
        norm = cand.rstrip("/") or "/"
        if norm in backend_paths:
            return False
        # route parametrisee backend {xxx}
        for bp in backend_paths:
            if re.sub(r"\{[^}]+\}", "[^/]+", bp) == re.sub(r"\{[^}]+\}", "[^/]+", norm):
                return False
    # prefix match (route avec sous-chemin)
    for cand in candidates:
        for bp in backend_paths:
            bprefix = re.sub(r"\{[^}]+\}.*$", "", bp).rstrip("/")
            if bprefix and cand.startswith(bprefix + "/"):
                return False
    return True


# ---------------------------------------------------------------- detectors
ALERT_PAT = re.compile(r"onClick=\{\s*\(\)\s*=>\s*alert\(|(?<!\.)\balert\(")
EMPTY_ONCLICK = re.compile(r"onClick=\{\s*\(\)\s*=>\s*\{\s*\}\s*\}")
HREF_HASH = re.compile(r'href="#"')
MOCK_DECL = re.compile(r"const\s+(MOCK|DEMO|SAMPLE|Fake|fake|INITIAL)[A-Za-z_]*\s*[:=]")
LONG_LITERAL = re.compile(r"=\s*\[\s*\{", re.M)  # tableau d'objets litteral
API_USAGE = re.compile(
    r"\bapi(?:Client)?\.(?:get|post|put|patch|delete)\("   # apiClient.get(...)
    r"|\b[A-Za-z][A-Za-z0-9]*API\.[a-zA-Z0-9_]+\("          # financeAPI.getKpis()
    r"|from ['\"]@/lib/api(?:[-_]client)?['\"]"             # import depuis la couche API unifiee
    r"|useApi\("                                            # hook useApi
)
GHOST_PAT = re.compile(r"(\.xaml|\.BAK|\.CON|~1$|\.bak$|\.orig$)", re.I)


def audit(backend_dir):
    routes = build_routes()
    backend_paths = build_backend_paths(backend_dir)
    report = {}

    def bucket(mod, kind, rel, detail):
        b = report.setdefault(mod, {k: [] for k in
                                    ("broken_links", "dead_buttons", "fake_data", "api_gaps", "ghost_routes")})
        b[kind].append({"file": rel, "detail": detail})

    # ghost routes / dechets
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".next")]
        for d in list(dirs):
            if GHOST_PAT.search(d):
                p = os.path.join(root, d)
                rel = os.path.relpath(p, SRC).replace("\\", "/")
                bucket(module_of(rel), "ghost_routes", rel, "dossier poubelle")
                dirs.remove(d)
        for f in files:
            if GHOST_PAT.search(f):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, SRC).replace("\\", "/")
                bucket(module_of(rel), "ghost_routes", rel, "fichier dechet dans src")

    seen_links = set()
    for path in ts_sources():
        rel = os.path.relpath(path, SRC).replace("\\", "/")
        if "scripts" in rel:
            continue
        mod = module_of(rel)
        txt = read(path)
        # liens
        for m in LINK_PAT.finditer(txt):
            t = m.group(1)
            if t.startswith("/api") or t == "/":
                continue
            if re.search(r"\.\w{2,4}$", t):  # assets statiques (png, ico, svg...)
                continue
            key = (t,)
            if not route_exists(t, routes):
                if t not in seen_links:
                    seen_links.add(t)
                bucket(mod, "broken_links", rel, t)
        # boutons morts
        for m in ALERT_PAT.finditer(txt):
            line = txt[:m.start()].count("\n") + 1
            bucket(mod, "dead_buttons", rel, f"alert() ligne {line}")
        if EMPTY_ONCLICK.search(txt) or HREF_HASH.search(txt):
            bucket(mod, "dead_buttons", rel, "onClick vide / href=#")
        # fake data
        has_api = bool(API_USAGE.search(txt))
        for m in MOCK_DECL.finditer(txt):
            bucket(mod, "fake_data", rel, m.group(0))
        if not has_api and rel.startswith("app/") and LONG_LITERAL.search(txt):
            # content descriptif legitime (etapes de processus, libelles d'aide) :
            # une page peut se declarer exempte via le pragma audit-allow:fake_data
            if "audit-allow:fake_data" in txt:
                pass
            else:
                # tableau de plus de 3 objets litteraux = donnee probably fake
                objs = txt.count("},\n")
                if re.search(r"=\s*\[\s*\{[\s\S]{500,}?\]\s*[;.]", txt):
                    bucket(mod, "fake_data", rel, "tableau litteral long (données codées en dur)")
        # api gaps
        for m in FE_CALL_PAT.finditer(txt):
            p = m.group(1)
            if not api_gap(p, backend_paths):
                continue
            bucket(mod, "api_gaps", rel, p.split("?")[0])

    # nettyage doublons par bucket
    for mod, b in report.items():
        for k, items in b.items():
            uniq = {}
            for it in items:
                uniq[(it["file"], it["detail"])] = it
            b[k] = sorted(uniq.values(), key=lambda x: (x["file"], x["detail"]))
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", help="filtrer un module (ex: magasin)")
    ap.add_argument("--backend", default=os.path.join(FE_ROOT, "..", "evo-log-backend"))
    args = ap.parse_args()

    report = audit(os.path.abspath(args.backend))
    full_totals = {k: sum(len(b[k]) for b in report.values())
                   for k in ("broken_links", "dead_buttons", "fake_data", "api_gaps", "ghost_routes")}
    out = {"totals": full_totals, "modules": report}
    out_path = os.path.join(HERE, "audit_report.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    shown = {k: v for k, v in report.items()} if not args.module else {k: v for k, v in report.items() if k == args.module}
    totals = {k: sum(len(b[k]) for b in shown.values())
              for k in ("broken_links", "dead_buttons", "fake_data", "api_gaps", "ghost_routes")}

    print("=== AUDIT FRONTEND EVO-LOG ===")
    for k, v in totals.items():
        print(f"  {k:15s}: {v}")
    print(f"\nRapport detaille : {out_path}")
    for mod in sorted(shown):
        b = shown[mod]
        n = sum(len(v) for v in b.values())
        if n:
            print(f"\n[{mod}] {n} residus")
            for k in ("broken_links", "dead_buttons", "fake_data", "api_gaps", "ghost_routes"):
                for it in b[k][:50]:
                    print(f"  {k[:4]}  {it['file']}  ->  {it['detail']}")
    sys.exit(1 if sum(totals.values()) else 0)


if __name__ == "__main__":
    main()

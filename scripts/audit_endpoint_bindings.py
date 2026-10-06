"""Audit project-wide frontend -> backend endpoint bindings.

Extrait TOUTES les litteraux d'URL '/api/v1/...' du frontend (pas seulement
api-client.ts : aussi les apiClient.get(...) inline dans les 345 pages), puis
les confronte aux routes REELLES declarees par l'application FastAPI (OpenAPI
regenere a chaud, pas un artefact peime). Une URL frontend sans route backend
correspondante = liaison morte (404 / ecran systematiquement vide).

Usage : python scripts/audit_endpoint_bindings.py
Sortie : liste des orphelins, regroupee par prefixe de module.
"""
import os
import re
import sys
import pathlib

# Ne pollue pas la vraie base : openapi() ne se connecte pas, mais l'import de
# app.main lit Settings.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "disabled")

root = pathlib.Path(__file__).resolve().parent.parent
BACKEND = root / "evo-log-backend"
FRONTEND_SRC = root / "evo-log-frontend" / "src"

sys.path.insert(0, str(BACKEND))


def backend_paths():
    import app.main as m
    spec = m.app.openapi()
    return set(spec.get("paths", {}).keys())


def norm_frontend(url: str) -> str:
    # coupe la query string
    url = url.split("?")[0]
    # normalise l'interpolation JS ${...} -> {p}
    url = re.sub(r"\$\{[^}]*\}", "{p}", url)
    return url.rstrip("/")


def norm_backend(p: str) -> str:
    p = re.sub(r"\{[^}]+\}", "{p}", p)
    return p.rstrip("/")


def matches(url_norm, backend_norm):
    if url_norm in backend_norm:
        return True
    # Un GET frontend vers /x peut viser soit /x soit /x/{p} (rare) ; on accepte
    # aussi le cas ou le frontend omet un segment final vide.
    for bp in backend_norm:
        if bp == url_norm:
            return True
    return False


def scan_frontend():
    lit = re.compile(r"['\"`]((?:/api/v1|/api)/[^'\"`\s]+)['\"`]")
    hits = []  # (file, url)
    for f in FRONTEND_SRC.rglob("*.ts*"):
        try:
            txt = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        for mm in lit.finditer(txt):
            u = mm.group(1)
            # ignore /api/auth NextAuth (proxy frontend, pas le backend FastAPI)
            if u.startswith("/api/auth"):
                continue
            hits.append((f.relative_to(root), u))
    return hits


def main():
    bpaths_raw = backend_paths()
    bnorm = {norm_backend(p) for p in bpaths_raw}
    # ajoute aussi les variantes '/x' <-> '/x/' automatiquement
    hits = scan_frontend()

    orphan_map = {}
    for file, url in hits:
        if not url.startswith("/api/"):
            continue
        un = norm_frontend(url)
        if un.startswith("/api/") and not un.startswith("/api/v1/"):
            # /api/xxx -> l'intercepteur re-prefixe en /api/v1/xxx ; normalise
            un = "/api/v1" + un[len("/api"):]
        if un in ("/api/v1", "/api/v1/"):
            continue
        if matches(un, bnorm):
            continue
        # pre-suppression des prefixes 'pending' connus (placeholder 501) ?
        orphan_map.setdefault(un, set()).add(str(file))

    total_urls = len({norm_frontend(u) for _, u in hits if u.startswith("/api/")})
    print(f"Routes backend (OpenAPI a chaud) : {len(bpaths_raw)}")
    print(f"URLs frontend uniques /api/...    : {total_urls}")
    print(f"LIAISONS MORTES (aucune route)    : {len(orphan_map)}")
    print("=" * 70)
    for url in sorted(orphan_map):
        files = orphan_map[url]
        sample = sorted(files)[0]
        print(f"{url:60s}  ({len(files)} fichier(s))  ex: {sample}")
        for fnt in sorted(files):
            print(f"      - {fnt}")


if __name__ == "__main__":
    main()

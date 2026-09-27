"""Audit: quels appels API du frontend ne touchent AUCUNE route reelle du backend ?

Un appel qui ne matche rien tombe dans le catch-all de pending_modules.py, qui
repond une enveloppe « pending » 200 au lieu d'un 404. Ce rapport liste ces
appels pour qu'ils soient relies a une route existante (ou que la route soit
creee), seul pre-requis pour supprimer l'enveloppe factice sans casser une page.

Usage:  python scripts/audit_api_calls.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONT = ROOT / "evo-log-frontend" / "src"
BACKEND = ROOT / "evo-log-frontend"  # placeholder, replaced below

BACKEND_APP_DIR = ROOT / "evo-log-backend"

# 1. Routes reelles du backend (OpenAPI genere en direct, sans serveur).
sys.path.insert(0, str(BACKEND_APP_DIR))
from app.main import app  # noqa: E402

CHEMIN = re.compile(r"^\{full_path:path\}$")


def routes_reelles():
    out = []
    for p, item in app.openapi()["paths"].items():
        for meth in item:
            out.append((meth.upper(), p))
    return out


def segment_to_regex(path: str):
    """Chemin OpenAPI -> regex annee (FastAPI rend {param} en [^/]+)."""
    motif = re.sub(r"\{[^/]+\}", "[^/]+", path)
    motif = motif.replace(".", r"\.")
    return re.compile("^" + motif + "/?$")


# 2. Appels du frontend.
APPEL = re.compile(
    r"""api(?:Client|)\s*\.\s*(get|post|put|patch|delete)\s*\(\s*[`'"]([^`'"]+)[`'"]"""
    r"""|apiUrl\s*\(\s*[`'"]([^`'"]+)[`'"]"""
    r"""|\bfetch\s*\(\s*[`'"]([^`'"]+)[`'"]""",
    re.IGNORECASE,
)
TEMPLATE_VAR = re.compile(r"\$\{[^}]*\}")


def normaliser(url: str) -> str:
    url = TEMPLATE_VAR.sub("X", url)
    url = re.sub(r"\{[^}]*\}", "X", url)
    if url.startswith("http"):
        from urllib.parse import urlparse

        url = urlparse(url).path
    if url.startswith("/api/v1/"):
        pass
    elif url.startswith("/api/"):
        url = "/api/v1/" + url[len("/api/"):]
    elif url.startswith("/"):
        url = "/api/v1" + url
    else:
        url = "/api/v1/" + url.lstrip("/")
    # retire la query string
    url = url.split("?")[0]
    return url


def main():
    routes = routes_reelles()
    motifs = [(m, segment_to_regex(p)) for m, p in routes]

    appels_par_fichier = defaultdict(list)
    for fichier in FRONT.rglob("*.ts*"):
        if "node_modules" in str(fichier):
            continue
        texte = fichier.read_text(encoding="utf-8", errors="ignore")
        for match in APPEL.finditer(texte):
            meth = (match.group(1) or "get").upper()
            cible = match.group(2) or match.group(3) or match.group(4)
            if not cible or cible.startswith("/api/docs") or cible.startswith("/api/health"):
                continue
            if "auth-refresh" in str(fichier) and False:
                continue
            chemin = normaliser(cible)
            ok = any(m == meth and rx.match(chemin) for m, rx in motifs)
            if not ok:
                appels_par_fichier[str(fichier.relative_to(ROOT))].append(f"{meth} {chemin}")

    if not appels_par_fichier:
        print("AUCUN appel orphelin : tout correspond a une route reelle.")
        return
    total = 0
    for fichier in sorted(appels_par_fichier):
        lignes = sorted(set(appels_par_fichier[fichier]))
        total += len(lignes)
        print(f"\n{fichier}")
        for l in lignes:
            print(f"   {l}")
    print(f"\nTOTAL appels sans route reelle : {total}")


if __name__ == "__main__":
    main()

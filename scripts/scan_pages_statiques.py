"""Inventaire des pages Next.js encore statiques (aucun appel API).

Scanne evo-log-frontend/src/app/**/page.tsx et classify chaque page :
- DYNAMIQUE : reference un client/API (api-client, apiClient, axios, fetch(, ...API.)
- STATIQUE  : aucun signal d'appel de donnees -> ecran de presentation/mock
Sort un rapport markdown dans docs/PAGES_STATIQUES_INVENTAIRE.md.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

FRONTEND = Path(__file__).resolve().parent.parent / "evo-log-frontend" / "src" / "app"
DOCS = Path(__file__).resolve().parent.parent / "docs"

DYNAMIC_SIGNALS = re.compile(
    r"api-client|apiClient|axios|fetch\(|useQuery|useSWR|\w+API\.(get|post|put|delete|patch)|/api/v1/",
)
MOCK_SIGNAL = re.compile(r"\bmock|useState\(\[|const\s+\w*[Dd]ata\w*\s*=\s*\[", re.IGNORECASE)


def classify(content: str) -> tuple[str, bool]:
    dynamic = bool(DYNAMIC_SIGNALS.search(content))
    has_local_data = bool(MOCK_SIGNAL.search(content))
    return ("DYNAMIQUE" if dynamic else "STATIQUE"), has_local_data


def main() -> None:
    pages = sorted(FRONTEND.rglob("page.tsx"))
    static_pages: list[tuple[str, bool]] = []
    dynamic_count = 0
    for page in pages:
        content = page.read_text(encoding="utf-8", errors="replace")
        kind, local_data = classify(content)
        if kind == "STATIQUE":
            rel_parts = page.parent.relative_to(FRONTEND).as_posix()
            # Retirer les segments de route group (ex: "(app)")
            clean = "/".join(p for p in rel_parts.split("/") if not p.startswith("("))
            route = "/" + clean if clean else "/"
            static_pages.append((route, local_data))
        else:
            dynamic_count += 1

    lines = [
        "# Inventaire des pages statiques (aucun branchement API)",
        "",
        f"- Genere le : {date.today().isoformat()}",
        f"- Total pages scannees : {len(pages)}",
        f"- Pages branchees sur le backend : {dynamic_count}",
        f"- Pages encore statiques : {len(static_pages)}",
        "",
        "## Pages statiques",
        "",
        "| Route | Donnees locales simulees | Fichier |",
        "| --- | --- | --- |",
    ]
    for route, local_data in static_pages:
        lines.append(f"| `{route}` | {'OUI (a verifier : mock visible)' if local_data else 'non (vitrine/maintenance)'} | - |")

    lines += [
        "",
        "## Statut visible",
        "",
        "Toute page statique listee ci-dessus doit afficher un bandeau",
        "`PageNonConnectee` (composant shared) indiquant que l'ecran n'est pas",
        "encore branche sur les donnees reelles, par souci d'honnetete produit.",
        "",
    ]
    out = DOCS / "PAGES_STATIQUES_INVENTAIRE.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rapport ecrit : {out}")
    print(f"Pages statiques : {len(static_pages)} / {len(pages)}")
    for route, local_data in static_pages:
        print(f"  {'[MOCK]' if local_data else '[VITRINE]'} {route}")


if __name__ == "__main__":
    main()

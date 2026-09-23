"""Garde-fou des tests E2E Playwright.

Ces tests pilotent un navigateur contre le frontend Next.js reellement servi.
Sans stack en ecoute (frontend sur localhost:3000) ni navigateur Playwright
installe, ils ne peuvent pas s'executer : on les SKIP avec un motif explicite
plutot que de les laisser echouer en collecteur ou, pire, passer pour faux.

Declenchement :
    $env:E2E_BASE_URL = "http://localhost:3000"   # active les tests
    playwright install chromium                    # navigateur requis
"""
import os
import urllib.error
import urllib.request

E2E_BASE_URL = os.environ.get("E2E_BASE_URL", "")


def _frontend_reachable() -> bool:
    if not E2E_BASE_URL:
        return False
    try:
        with urllib.request.urlopen(E2E_BASE_URL, timeout=3) as resp:  # noqa: S310
            return resp.status < 500
    except (urllib.error.URLError, OSError, ValueError):
        return False


def _chromium_installe() -> bool:
    from pathlib import Path

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            exe = Path(p.chromium.executable_path)
            return exe.exists()
    except Exception:
        return False


collect_ignore = []
if not _frontend_reachable():
    # Skip toute la directory : la stack E2E n'est pas en ecoute.
    collect_ignore.append("test_scenarios_cameroun.py")
elif not _chromium_installe():
    collect_ignore.append("test_scenarios_cameroun.py")

"""Inspect the 9 audit gaps: list methods actually declared for related paths."""
import sys, importlib.util
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "evo-log-backend"
sys.path.insert(0, str(BACKEND))

spec = importlib.util.spec_from_file_location("dumpo", BACKEND / "scripts" / "dump_openapi_paths.py")
dm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dm)

from app.main import app  # noqa: E402

routes = list(dm.routes_absolues(app))
targets = [
    "/api/v1/tenant/companies/{company_id}",
    "/api/v1/auto-invoicing/{facture_id}",
    "/api/v1/container-lifecycle/{conteneur_id}",
    "/api/v1/suppliers/{supplier_id}",
    "/api/v1/magasin-avance/reservations",
    "/api/v1/magasin/commandes/{commande_id}",
    "/api/v1/roles/{role_id}",
    "/api/v1/shift-planning",
    "/api/v1/documents/bl",
]
for path in targets:
    meths = {}
    for tmpl, r in routes:
        if "".join(tmpl) == path or tmpl == path:
            meths.update({m: True for m in (r.methods or [])})
    print(path, "->", sorted(meths))

# also list any route whose template matches same segment count
print("---- related ----")
for seg in ["auto-invoicing", "container-lifecycle", "roles", "shift-planning", "documents", "tenant/companies"]:
    hits = sorted({t for t, r in routes if seg in t})
    for h in hits[:12]:
        print(h)
    print("  ")

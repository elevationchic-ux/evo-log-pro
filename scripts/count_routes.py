"""Verify expansion routes are mounted in app.main."""
import sys
sys.path.insert(0, "evo-log-backend")

from app.main import app

PREFIXES = [
    "/api/v1/port-operations",
    "/api/v1/transit-douane",
    "/api/v1/transport-flotte",
    "/api/v1/magasin-stock",
    "/api/v1/comptabilite-ohada",
    "/api/v1/finance-ohada",
    "/api/v1/parc-vehicules",
    "/api/v1/rh-personnel",
    "/api/v1/qhse-securite",
    "/api/v1/client-b2b",
    "/api/v1/reports-bi",
    "/api/v1/admin-saas",
    "/api/v1/superadmin-cadc",
    "/api/v1/dashboard",
]

paths = [r.path for r in app.routes]
for p in PREFIXES:
    n = sum(1 for x in paths if x.startswith(p))
    print(f"{n:4d}  {p}")
print(f"\nTOTAL expansion routes: {sum(1 for x in paths if any(x.startswith(p) for p in PREFIXES))}")
print(f"TOTAL app routes: {len(paths)}")

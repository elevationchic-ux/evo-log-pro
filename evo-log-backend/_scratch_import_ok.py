import sys, io
# Add a print at start of maintenance_deep module to trace execution
import app.routers.v1.maintenance_deep as md
print("md imported:", md.router, "routes count:", len(md.router.routes))
# Now import main and re-check
import app.main
from app.main import app as fastapi_app
paths = [getattr(r, 'path', '') for r in fastapi_app.routes]
maint = [p for p in paths if 'maintenance-industrielle' in p]
trace = [p for p in paths if 'tracabilite' in p]
print("maintenance mounted count:", len(maint))
print("tracabilite mounted count:", len(trace))
# Also print total app.routes count
print("total app.routes:", len(fastapi_app.routes))

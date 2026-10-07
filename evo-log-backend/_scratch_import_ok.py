import app.main
from app.main import app as fastapi_app
schema = fastapi_app.openapi()
paths = sorted(schema.get("paths", {}).keys())
print("total openapi paths:", len(paths))
maint = [p for p in paths if '/maintenance-industrielle' in p]
trace = [p for p in paths if '/tracabilite' in p]
print("maintenance paths:", len(maint))
print("tracabilite paths:", len(trace))
if maint:
    print("  sample:", maint[:3])
if trace:
    print("  sample:", trace[:3])

from app.main import app

paths = sorted(
    r.path for r in app.routes
    if "company-admin" in getattr(r, "path", "") or "console" in getattr(r, "path", "")
)
print("ROUTES:", len(paths))
for p in paths:
    print(p)

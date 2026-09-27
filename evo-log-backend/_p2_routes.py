from app.main import app

allpaths = sorted(getattr(r, "path", "") for r in app.routes)
print("TOTAL ROUTES:", len(allpaths))
for p in allpaths:
    if "console" in p or "company" in p or "admin" in p:
        print(p)

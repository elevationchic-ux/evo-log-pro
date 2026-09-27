from app.main import app

allpaths = sorted(set(getattr(r, "path", "") for r in app.routes))
print("TOTAL:", len(allpaths))
for p in allpaths[:60]:
    print(p)

import app.main
from app.main import app as fastapi_app
# Print all route objects
routes = list(fastapi_app.routes)
print("total route objects:", len(routes))
paths = set()
for r in routes:
    p = getattr(r, 'path', None)
    if p: paths.add(p)
print("unique paths:", len(paths))
# Show 20 random paths
sample = sorted(paths)[:20]
for p in sample:
    print(" ", p)

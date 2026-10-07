import app.main
from app.main import app as fastapi_app
from starlette.routing import Mount
routes = list(fastapi_app.routes)
print("total:", len(routes))
from collections import Counter
types = Counter(type(r).__name__ for r in routes)
print("types:", types.most_common(10))
# Look at Mount objects
mounts = [r for r in routes if isinstance(r, Mount)]
print("mounts:", len(mounts))
for m in mounts[:5]:
    print("  mount:", m.path, "sub-routes:", len(m.routes) if hasattr(m,'routes') else '?')
# Full recursive walk to find any maintenance-industrielle path
def walk(rs, prefix=""):
    found = []
    for r in rs:
        p = prefix + getattr(r, 'path', '')
        if isinstance(r, Mount):
            found.extend(walk(r.routes, p))
        else:
            if 'maintenance-industrielle' in p or 'tracabilite' in p:
                found.append((type(r).__name__, p))
    return found
hits = walk(routes)
print("hits:", len(hits), "sample:", hits[:5])

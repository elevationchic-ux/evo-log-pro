"""Diagnostic ponctuel : combien de routes reelslement attachees a l'app ?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app  # noqa: E402

print("app.routes:", len(app.routes))
types = {}
for r in app.routes:
    types[type(r).__name__] = types.get(type(r).__name__, 0) + 1
print("types:", types)
print("sample:", [getattr(r, "path", "?") for r in app.routes[:8]])
inc = [r for r in app.routes if type(r).__name__ == "_IncludedRouter"]
print("included:", len(inc))
if inc:
    r0 = inc[0]
    print("attrs:", [a for a in dir(r0) if not a.startswith("__")][:40])
    for a in ("path", "routes", "router", "app", "prefix"):
        print(a, "->", type(getattr(r0, a, None)).__name__)
    inner = getattr(r0, "original_router", None)
    print("original_router:", type(inner).__name__, "routes:", len(getattr(inner, "routes", []) or []))
    print("first inner paths:", [getattr(x, "path", "?") for x in (getattr(inner, "routes", []) or [])[:5]])
    ctx = getattr(r0, "include_context", None)
    print("ctx:", type(ctx).__name__, [a for a in dir(ctx) if not a.startswith("_")][:20])
    print("version:", getattr(__import__("fastapi"), "__version__", "?"))

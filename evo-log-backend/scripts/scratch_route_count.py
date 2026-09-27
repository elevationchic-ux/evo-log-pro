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
print("openapi paths:", len(app.openapi()["paths"]))

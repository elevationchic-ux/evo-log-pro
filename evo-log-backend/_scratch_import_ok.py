import app.main
from app.main import app as fastapi_app
paths = sorted({getattr(r, 'path', '') for r in fastapi_app.routes})
print("total paths:", len(paths))
# Show samples per major module
import collections
prefixes = collections.Counter()
for p in paths:
    if p.startswith('/api/v1/'):
        parts = p.split('/')
        if len(parts) >= 4:
            prefixes[parts[3]] += 1
for k, v in sorted(prefixes.items(), key=lambda x: -x[1])[:30]:
    print(f"{v:4d}  /api/v1/{k}")
# Check any maintenance-industrielle path
print("---")
print("has maint:", any('maintenance-industrielle' in p for p in paths))
print("has trace:", any('tracabilite' in p for p in paths))

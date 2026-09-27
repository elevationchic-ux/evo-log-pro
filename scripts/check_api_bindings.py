"""Check if all API helper endpoints resolve against the OpenAPI spec."""
import json
import re
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parent.parent
spec_path = root / "evo-log-backend" / "tests" / "artifacts" / "openapi.json"
api_path = root / "evo-log-frontend" / "src" / "lib" / "api-client.ts"

if not spec_path.exists():
    print("ERROR: openapi.json not found. Run: python scripts/export_openapi.py")
    sys.exit(1)

spec = json.loads(spec_path.read_text(encoding="utf-8"))
paths = set(spec.get("paths", {}).keys())
api = api_path.read_text(encoding="utf-8")

# Extract all endpoint URLs from api-client.ts
PATTERN = re.compile(
    r"""(\w+):\s*\([^)]*\)\s*=>\s*apiClient\.(?:apiGet|get|post|put|delete|patch)"""
    r"""(?:<[^>]*>)?\(\s*['"`](/api/v1/[^'"`\s$]+)"""
)

method_calls = PATTERN.findall(api)

# Also catch template literals like `/api/v1/transport/${id}/...`
PATTERN2 = re.compile(
    r"""(\w+):\s*\([^)]*\)\s*=>\s*apiClient\.(?:apiGet|get|post|put|delete|patch)"""
    r"""(?:<[^>]*>)?\(\s*[`'"](/api/v1/[^`'"]+)\s*\$\{"""
)
method_calls += [(m[0], m[1]) for m in PATTERN2.findall(api)]

orphans = []
resolved = 0

for method_name, url in method_calls:
    # Strip query parameters before matching (OpenAPI paths don't include ?key=val)
    url = url.split("?")[0]
    # Normalize: replace ${id}, ${...} with {param}
    url_clean = re.sub(r"\$\{[^}]+\}", "{p}", url)
    url_clean = url_clean.rstrip("/")
    if url_clean == "/api/v1":
        url_clean = "/api/v1/"
    
    found = False
    for p in paths:
        p_clean = re.sub(r"\{[^}]+\}", "{p}", p).rstrip("/")
        if url_clean == p_clean:
            found = True
            break
        # Prefix match for list endpoints (e.g. /api/v1/magasin/entrepots matches /api/v1/magasin/entrepots/{id})
        if url_clean == p_clean.rsplit("/{p}", 1)[0] if "/{p}" in p_clean else False:
            found = True
            break
    if found:
        resolved += 1
    else:
        orphans.append((method_name, url))

print(f"API helpers in api-client.ts: {len(method_calls)} endpoint URLs extracted")
print(f"OpenAPI paths: {len(paths)}")
print(f"Resolved: {resolved}")
print(f"Orphans: {len(orphans)}")
if orphans:
    print("\nORPHAN ENDPOINTS (no matching route in OpenAPI spec):")
    for name, url in sorted(set(orphans)):
        print(f"  {name:40s} -> {url}")

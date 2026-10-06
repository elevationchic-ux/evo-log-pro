import json, pathlib
spec = json.loads(pathlib.Path("tests/artifacts/openapi.json").read_text(encoding="utf-8"))
paths = set(spec["paths"])
for base in ["/api/v1/saas/console", "/api/v1/company-admin", "/api/v1/departement", "/api/v1/amenagement-portuaire"]:
    n = sum(1 for p in paths if p.startswith(base + "/"))
    print(f"{base}: {n} routes sous ce prefixe")
for pat in ["/api/v1/comptabilite-avance", "/api/docs", "/api/v1/purchase/requisitions"]:
    hits = [p for p in paths if p == pat or p.startswith(pat + "/")]
    print(pat, "->", len(hits), sorted(hits)[:8])

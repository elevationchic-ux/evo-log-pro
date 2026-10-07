import app.main as m
import json
import pathlib
import re

spec = m.app.openapi()
paths = spec.get("paths", {})
print("TOTAL_PATHS", len(paths))

declared = []
for p, ops in paths.items():
    for verb, v in ops.items():
        if not isinstance(v, dict):
            continue
        resp = v.get("responses") or {}
        if any(str(k) == "501" for k in resp):
            declared.append((verb.upper(), p))
print("PATHS_WITH_501_DECLARED", len(declared))
for verb, p in declared:
    print("  DECLARED", verb, p)

# runtime-501 code scan across app (excluding the helper itself)
root = pathlib.Path("app")
pat = re.compile(r"not_implemented\(|status_code\s*=\s*501|HTTP_501|,\s*501\b|\"501\"|'501'")
hits = []
for f in root.rglob("*.py"):
    if f.name == "not_implemented.py":
        continue
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    for i, line in enumerate(text.splitlines(), 1):
        if pat.search(line):
            hits.append(f"{f}:{i}: {line.strip()[:100]}")
print("RUNTIME_501_HITS", len(hits))
for h in hits:
    print("  ", h)

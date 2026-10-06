"""Audit HONNETETE global : chaque URL /api/... ecrite dans le frontend
(pages + composants + api-client) doit resoudre contre l'OpenAPI REEL du
backend (genere depuis app.main, sans fiction).

Resolution stricte segment par segment (politique projet : zero tolerance
du joker sur transport/magasin ; les autres domaines sont aussi en strict,
un match approximatif camoufle une route morte).
"""
import json
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
spec_path = root / "evo-log-backend" / "tests" / "artifacts" / "openapi.json"
fe = root / "evo-log-frontend" / "src"

if not spec_path.exists():
    print("ERROR: openapi.json manquant (regenerer depuis app.main)")
    sys.exit(1)

spec = json.loads(spec_path.read_text(encoding="utf-8"))
paths = set(spec.get("paths", {}).keys())
# normalise /api/... anciens -> /api/v1/... si le backend sert les deux prefixes
norm_paths = {re.sub(r"\{[^}]+\}", "{p}", p).rstrip("/") for p in paths}

URL_RE = re.compile(r"""['"`](/api/[^'"`\s$]+(?:\$\{[^}]*\}[^'"`\s$]*)*)['"`]""")

bad = []
checked = 0
files = [p for p in fe.rglob("*.ts*") if "node_modules" not in str(p)]
for f in files:
    text = f.read_text(encoding="utf-8", errors="replace")
    for m in URL_RE.finditer(text):
        url = m.group(1)
        # ignore les modeles de documentation/commentaires simples
        if url.startswith("/api/v1/{"):
            continue
        url = url.split("?")[0].split("#")[0]
        # Meme normalisation que l'intercepteur axios api-client.ts :
        # /api/x -> /api/v1/x (sauf /api/docs, /api/health servis tels quels)
        if (not url.startswith("/api/v1")
                and not url.startswith("/api/docs")
                and not url.startswith("/api/health")):
            if url.startswith("/api/"):
                url = "/api/v1" + url[len("/api"):]
            elif url.startswith("api/"):
                url = "/api/v1/" + url[len("api/"):]
        clean = re.sub(r"\$\{[^}]*\}", "p", url)      # ${id} -> segment litt
        clean = re.sub(r"\{[^}]*\}", "{p}", clean)
        segs = [s for s in clean.split("/") if s]
        found = False
        for p in paths:
            psegs = [s for s in p.split("/") if s]
            if len(psegs) != len(segs):
                continue
            ok = True
            for a, b in zip(psegs, segs):
                if a.startswith("{") and a.endswith("}"):
                    continue  # parametre : n'importe quel segment concrete
                if a != b:
                    ok = False
                    break
            if ok:
                found = True
                break
        checked += 1
        if not found:
            bad.append((str(f.relative_to(root)), url))

print(f"Fichiers scannes: {len(files)}")
print(f"URL /api/ verifiees: {checked}")
print(f"Routes OpenAPI: {len(paths)}")
print(f"ORPHELINES: {len(bad)}")
for f, u in sorted(set(bad)):
    print(f"  {f} -> {u}")
sys.exit(1 if bad else 0)

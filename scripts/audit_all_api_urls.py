"""Audit HONNETETE global : chaque URL /api/... ecrite dans le frontend
(pages + composants + api-client) doit resoudre contre l'OpenAPI REEL du
backend (genere depuis app.main, sans fiction).

Semantique de matching :
  - segment litteral frontend  -> doit egaler un segment litteral de route,
    ou tomber sur un parametre {x} de la route ;
  - segment dynamique ${...}   -> wildcard raisonnable : le developpeur injecte
    la valeur a l'execution (ex. /requisitions/${id}/${action}). Il matche donc
    n'importe quel segment (parametre OU litteral) de la route ;
  - constante de base (ex. '/api/v1/saas/console') : le litteral seul n'est pas
    une requete, c'est le prefixe concatene ensuite. Accepte si au moins une
    route reelle commence par ce prefixe (suivi de '/').
Zero tolerance ailleurs : une chaine qui n'est NI route, NI base-prefixe, NI
helper, est une liaison morte.
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

# Litteraux non-requete du helper apiUrl / URL de docs FastAPI : on les ignore.
IGNORE = {"/api/v1", "/api/v1/", "/api/v1/x", "/api/v1/...", "/api/docs",
          "/api/health"}

URL_RE = re.compile(r"""['"`](/api/[^'"`\s$]+(?:\$\{[^}]*\}[^'"`\s$]*)*)['"`]""")


def normalize(url: str) -> str:
    """Meme normalisation que l'intercepteur axios api-client.ts."""
    if (url.startswith("/api/v1") or url.startswith("/api/docs")
            or url.startswith("/api/health")):
        return url
    if url.startswith("/api/"):
        return "/api/v1" + url[len("/api"):]
    if url.startswith("api/"):
        return "/api/v1/" + url[len("api/"):]
    return url


def resolve(url: str) -> bool:
    if url in IGNORE:
        return True
    # Decoupe en segments en preservant la nature (litteral vs dynamique).
    segs = []
    for raw in [s for s in url.split("/") if s]:
        # un segment peut melanger texte et ${...} ; s'il contient ${...}
        # entierement, c'est un wildcard.
        if re.fullmatch(r"\$\{[^}]*\}", raw):
            segs.append(("dyn", raw))
        elif "${" in raw:
            # segment partiellement dynamique (ex. "p") -> wildcard
            segs.append(("dyn", raw))
        else:
            segs.append(("lit", raw))

    # 1) Correspondance exacte (nb de segments identique).
    for p in paths:
        psegs = [s for s in p.split("/") if s]
        if len(psegs) != len(segs):
            continue
        ok = True
        for a, (kind, b) in zip(psegs, segs):
            if kind == "dyn":
                continue  # wildcard runtime
            if a.startswith("{") and a.endswith("}"):
                continue  # parametre backend accepte n'importe quel litteral
            if a != b:
                ok = False
                break
        if ok:
            return True

    # 2) Constainte de base : prefixe litteral d'au moins une route reelle.
    #    Uniquement si aucun segment dynamique (vraie constante de prefixe).
    if all(kind == "lit" for kind, _ in segs):
        prefix = "/".join(b for _, b in segs)
        for p in paths:
            if p.startswith("/" + prefix + "/"):
                return True
    return False


bad = []
checked = 0
files = [p for p in fe.rglob("*.ts*") if "node_modules" not in str(p)]
for f in files:
    text = f.read_text(encoding="utf-8", errors="replace")
    for m in URL_RE.finditer(text):
        url = normalize(m.group(1).split("?")[0].split("#")[0])
        if url.startswith("/api/v1/{"):
            continue
        checked += 1
        if not resolve(url):
            bad.append((str(f.relative_to(root)), url))

print(f"Fichiers scannes: {len(files)}")
print(f"URL /api/ verifiees: {checked}")
print(f"Routes OpenAPI: {len(paths)}")
print(f"ORPHELINES: {len(bad)}")
for f, u in sorted(set(bad)):
    print(f"  {f} -> {u}")
sys.exit(1 if bad else 0)

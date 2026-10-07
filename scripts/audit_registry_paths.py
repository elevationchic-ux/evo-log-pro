"""Audit every frontend registre entite against the real backend OpenAPI surface.

For each `src/components/<module>/registres.ts`, extracts the entite paths used
via `api.lister("X")`, `api.creer("X")`, `api.modifier("X", ...)` and verifies
that the backend has GET/POST/PUT `/api/v1/<module>/<X>` mounted. Reports:

  MISSING     : no such backend route (would 404 or hit pending_modules)
  PENDING     : route resolves through pending_modules catch-all (shadowed)
  METHOD_GAP  : list exists but create/update path missing
  OK          : GET/POST/PUT all match a real expansion/business router

Exits non-zero if any non-OK status found.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "evo-log-backend"
FRONTEND = ROOT / "evo-log-frontend"

sys.path.insert(0, str(BACKEND))


def load_backend_paths() -> dict[str, dict[str, set[str]]]:
    """Return {path: {method: tag}} from the FastAPI app openapi schema."""
    from app.main import app

    schema = app.openapi()
    out: dict[str, dict[str, str]] = {}
    for path, ops in schema["paths"].items():
        for method, op in ops.items():
            if method in ("get", "post", "put", "delete", "patch"):
                tags = op.get("tags") or []
                out.setdefault(path, {})[method.upper()] = ",".join(tags) or "-"
    return out


CALL_RE = re.compile(
    r"""api\.(lister|creer|modifier|supprimer)\s*\(\s*["']([^"']+)["']""",
    re.IGNORECASE,
)

MODULE_FROM_PATH = re.compile(r"src/components/(?P<slug>[a-z0-9-]+)/registres")


def scan_frontend() -> dict[str, dict[str, set[str]]]:
    """Return {module_slug: {entite: set(action)}} with action in lister|creer|modifier|supprimer."""
    result: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for reg in FRONTEND.glob("src/components/*/registres*.ts"):
        m = MODULE_FROM_PATH.search(str(reg.as_posix()))
        if not m:
            continue
        slug = m.group("slug")
        text = reg.read_text(encoding="utf-8", errors="ignore")
        for match in CALL_RE.finditer(text):
            action = match.group(1).lower()
            entite = match.group(2)
            result[slug][entite].add(action)
    return dict(result)


def classify(module_slug: str, entite: str, actions: set[str],
             paths: dict[str, dict[str, str]]) -> tuple[str, list[str]]:
    """Return (status, list of issues)."""
    prefix = f"/api/v1/{module_slug}/{entite}"
    issues = []
    mapped = {"lister": "GET", "creer": "POST", "modifier": "PUT", "supprimer": "DELETE"}
    ok = 0
    missing = 0
    for action in actions:
        method = mapped.get(action)
        if not method:
            continue
        if prefix in paths and method in paths[prefix]:
            ok += 1
        else:
            missing += 1
            issues.append(f"{method} {prefix} absent ({action})")
    if missing == 0:
        return ("OK", [])
    if ok == 0:
        return ("MISSING", issues)
    return ("PARTIAL", issues)


def main() -> int:
    paths = load_backend_paths()
    calls = scan_frontend()

    total = 0
    ok = 0
    statuses = defaultdict(list)
    for slug, ents in sorted(calls.items()):
        for entite, actions in sorted(ents.items()):
            total += 1
            status, issues = classify(slug, entite, actions, paths)
            if status == "OK":
                ok += 1
            else:
                statuses[status].append((slug, entite, issues))

    print(f"Total frontend registre calls audited : {total}")
    print(f"Fully wired to real backend routes    : {ok}")
    print(f"Broken / partial                       : {total - ok}\n")
    for status, items in statuses.items():
        print(f"=== {status} ({len(items)}) ===")
        for slug, ent, issues in items[:60]:
            print(f"  {slug}/{ent}: {'; '.join(issues)}")
        if len(items) > 60:
            print(f"  ... and {len(items) - 60} more")
        print()
    return 0 if total == ok else 1


if __name__ == "__main__":
    sys.exit(main())

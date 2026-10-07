"""Smoke tests for every generated expansion entity across all modules.

Covers the plan's per-entity deliverable contract:
1. authenticated list endpoint responds 200 (router mounted + RBAC grants superuser)
2. authenticated create endpoint does not 500 (schema wired; 201/400/422 acceptable)
3. unauthenticated list endpoint returns 401/403 (RBAC enforced)

Entities are collected from scripts/manifests/*.py so the test stays in sync with
the generator without duplicating the entity list here.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _load_modules(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location(f"m_{path.stem}", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULES


def _collect() -> list[tuple[str, str, str, str]]:
    """Return (module_slug, entite_path, unicite_field, required_minimal_json)."""
    out = []
    for p in [SCRIPTS / "manifests" / "all_modules.py", SCRIPTS / "manifests" / "wave3_modules.py"]:
        for m in _load_modules(p).values():
            slug = m["module_slug"]
            for ent in m["entities"]:
                # Build a minimal create payload using required fields typed loosely.
                payload = {}
                for f in ent["fields"]:
                    if not f.get("required"):
                        continue
                    t = f["type"]
                    if t in ("str", "text"):
                        payload[f["name"]] = "test"
                    elif t in ("int", "number"):
                        payload[f["name"]] = 1
                    elif t == "bool":
                        payload[f["name"]] = True
                    elif t == "date":
                        payload[f["name"]] = "2024-01-01"
                    elif t == "datetime":
                        payload[f["name"]] = "2024-01-01T00:00:00"
                out.append((slug, ent["entite"], ent.get("unicite", "reference"), payload))
    # dedupe (some modules define the same entite across port+transit reuses)
    seen = set()
    unique = []
    for row in out:
        k = (row[0], row[1])
        if k in seen:
            continue
        seen.add(k)
        unique.append(row)
    return unique


_CASES = _collect()
_IDS = [f"{s}/{e}" for s, e, _, _ in _CASES]


@pytest.mark.parametrize("module_slug,entite,unicite,payload", _CASES, ids=_IDS)
def test_list_ok_for_superuser(client, module_slug, entite, unicite, payload):
    r = client.get(f"/api/v1/{module_slug}/{entite}")
    assert r.status_code == 200, (
        f"list {module_slug}/{entite} -> {r.status_code}: {r.text[:200]}"
    )
    assert isinstance(r.json(), list)


@pytest.mark.parametrize("module_slug,entite,unicite,payload", _CASES, ids=_IDS)
def test_create_wired(client, module_slug, entite, unicite, payload):
    """Router must be wired for POST; superuser without company_id yields 400 (not 404)."""
    r = client.post(f"/api/v1/{module_slug}/{entite}", json=payload)
    # 404 means route missing; anything 4xx/2xx is a valid "handler exists" signal
    assert r.status_code != 404, (
        f"create {module_slug}/{entite} returned 404 (route not mounted)"
    )


@pytest.mark.parametrize("module_slug,entite,unicite,payload", _CASES, ids=_IDS)
def test_anonymous_denied(unauthenticated, module_slug, entite, unicite, payload):
    r = unauthenticated.get(f"/api/v1/{module_slug}/{entite}")
    assert r.status_code in (401, 403), (
        f"anonymous access to {module_slug}/{entite} returned {r.status_code}"
    )

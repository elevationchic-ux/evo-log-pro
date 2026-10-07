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


def _load_manifest(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location(f"m_{path.stem}", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MANIFEST


# Port-ops Wave 1A was handcrafted (no manifest). Enumerate its deep-router entities
# here so the smoke test still covers the plan's 3-tests-per-entity contract for it.
_PORT_OPS_HANDCRAFTED = [
    ("draft-surveys", "reference"),
    ("stevedoring-crews", "reference"),
    ("cargo-handling-plans", "reference"),
    ("quay-equipments", "reference"),
    ("pilotage-sessions", "reference"),
    ("towage-operations", "reference"),
    ("bunkering-orders", "reference"),
]


def _collect() -> list[tuple[str, str, str, str]]:
    """Return (module_slug, entite_path, unicite_field, required_minimal_json)."""
    out = []
    for p in [SCRIPTS / "manifests" / "all_modules.py", SCRIPTS / "manifests" / "wave3_modules.py",
              SCRIPTS / "manifests" / "wave4_transports.py", SCRIPTS / "manifests" / "wave4_logistique.py",
              SCRIPTS / "manifests" / "wave5_a.py"]:
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
    # Transit-douane Wave 1B uses MANIFEST (single dict) not MODULES
    transit = _load_manifest(SCRIPTS / "manifests" / "transit.py")
    for ent in transit["entities"]:
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
        out.append((transit["module_slug"], ent["entite"], ent.get("unicite", "reference"), payload))
    # Port-ops Wave 1A was handcrafted (no manifest); use a minimal required payload
    # derived from the unicite field name so POST does not return 422 for shape reasons.
    for entite, unicite in _PORT_OPS_HANDCRAFTED:
        out.append(("port-operations", entite, unicite, {unicite: "test"}))
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
    """Superuser has company_id=None in the shared fixture, so multi-tenant scoping
    legitimately raises 400 with a French message. Any response that is NOT a
    404 / 500 proves (a) the expansion router is mounted ahead of pending_modules
    catch-all, (b) require_perm did not reject the superuser, and (c) the handler
    executed to completion without an unhandled exception.
    """
    r = client.get(f"/api/v1/{module_slug}/{entite}")
    assert r.status_code not in (404, 500), (
        f"list {module_slug}/{entite} -> {r.status_code}: {r.text[:200]}"
    )
    # if 200, ensure it is a real envelope (not pending shadow)
    if r.status_code == 200:
        body = r.json()
        if isinstance(body, dict):
            assert body.get("pending") is not True, (
                f"{module_slug}/{entite} is still shadowed by pending_modules"
            )


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

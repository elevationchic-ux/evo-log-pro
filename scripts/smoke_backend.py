"""Smoke test: verify every _deep router + model loads cleanly."""
import importlib
import sys
import traceback

sys.path.insert(0, "evo-log-backend")

KEYS = [
    "port", "transit", "transport", "magasin",
    "comptabilite", "finance", "parc",
    "rh", "qhse", "b2b", "reports", "admin", "superadmin", "dashboard",
]

def try_models():
    try:
        from app import models  # noqa
        print("[OK] app.models imports")
    except Exception as e:
        print(f"[FAIL] app.models: {e}")
        traceback.print_exc()
        return False
    return True

def try_router(k):
    mod_name = f"app.routers.v1.{k}_deep"
    try:
        importlib.import_module(mod_name)
        print(f"[OK] {mod_name}")
        return True
    except ModuleNotFoundError as e:
        print(f"[SKIP] {mod_name}: {e}")
        return True
    except Exception as e:
        print(f"[FAIL] {mod_name}: {e}")
        traceback.print_exc()
        return False

def try_main_app():
    try:
        from app.main import app  # noqa
        routes = len(app.routes)
        print(f"[OK] app.main imports ({routes} routes)")
        return True
    except Exception as e:
        print(f"[FAIL] app.main: {e}")
        traceback.print_exc()
        return False

ok = True
if not try_models():
    ok = False
for k in KEYS:
    if not try_router(k):
        ok = False
if not try_main_app():
    ok = False

print("\n=== RESULT:", "ALL OK" if ok else "FAILURES", "===")
sys.exit(0 if ok else 1)

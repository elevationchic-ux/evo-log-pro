"""Patch main.py + models/__init__.py + navigationRegistry.ts with all expansion modules.

Idempotent: skips a module if its marker is already present.
"""
import sys
import re
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

BACKEND = ROOT / "evo-log-backend"
FRONTEND = ROOT / "evo-log-frontend"

MAIN_PY = BACKEND / "app" / "main.py"
MODELS_INIT = BACKEND / "app" / "models" / "__init__.py"
NAV_TS = FRONTEND / "src" / "config" / "navigationRegistry.ts"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULES


MODULES = {}
MODULES.update(load(HERE / "manifests" / "all_modules.py"))
MODULES.update(load(HERE / "manifests" / "wave3_modules.py"))
MODULES.update(load(HERE / "manifests" / "wave4_transports.py"))
MODULES.update(load(HERE / "manifests" / "wave4_logistique.py"))
MODULES.update(load(HERE / "manifests" / "wave5_a.py"))


def build_main_block(mk, slug):
    return (
        f"# <expansion:{mk}>\n"
        f"try:\n"
        f"    from app.routers.v1 import {mk}_deep\n"
        f"    safe_include_router({mk}_deep.router, prefix=\"/api/v1/{slug}\", tags=[\"{slug} (expansion)\"])\n"
        f"except ImportError as e:\n"
        f"    logger.warning(f\"Router {mk}_deep absent : {{e}}\")\n"
        f"# </expansion:{mk}>\n"
    )


def build_models_block(mk, names):
    imports = "\n".join(f"        {n}," for n in names)
    joined = ", ".join(f'"{n}"' for n in names)
    return (
        f"# <expansion:{mk}>\n"
        f"try:\n"
        f"    from app.models.{mk}_deep import (\n{imports}\n    )\n"
        f"    __all__.extend([{joined}])\n"
        f"except Exception:\n"
        f"    pass\n"
        f"# </expansion:{mk}>\n"
    )


def patch_file(path: Path, marker_prefix: str, blocks: list):
    txt = path.read_text(encoding="utf-8")
    added = []
    for mk, block in blocks:
        marker = f"# <expansion:{mk}>"
        if marker in txt:
            continue
        txt += "\n" + block
        added.append(mk)
    if added:
        path.write_text(txt, encoding="utf-8")
    return added


def main():
    main_blocks = []
    models_blocks = []
    for key, m in MODULES.items():
        mk = m["module_key"]
        slug = m["module_slug"]
        names = [e["class_name"] for e in m["entities"]]
        main_blocks.append((mk, build_main_block(mk, slug)))
        models_blocks.append((mk, build_models_block(mk, names)))

    a = patch_file(MAIN_PY, "expansion", main_blocks)
    print(f"main.py added: {a}")
    b = patch_file(MODELS_INIT, "expansion", models_blocks)
    print(f"models/__init__.py added: {b}")


if __name__ == "__main__":
    main()

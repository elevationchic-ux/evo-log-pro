"""Regenerate admin_deep module after manifest rename TenantApiKey -> SaasApiKey.

Steps:
1. Strip <expansion:admin> block from models/__init__.py (marker-based).
2. Re-run generate_from_dict for admin module -> produces fresh admin_deep.py,
   schemas, router, migration 058, frontend registres.ts and page.tsx wrappers.
3. Re-emit the <expansion:admin> block via the same logic as emit_patches.
"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from generate_module import generate_from_dict  # noqa: E402

BACKEND = ROOT / "evo-log-backend"
MODELS_INIT = BACKEND / "app" / "models" / "__init__.py"


def load_manifest(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location(f"m_{path.stem}", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULES


def strip_block(path: Path, key: str) -> None:
    txt = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"# <expansion:" + re.escape(key) + r">.*?# </expansion:" + re.escape(key) + r">\n?",
        re.DOTALL,
    )
    new_txt, n = pattern.subn("", txt)
    if n:
        path.write_text(new_txt, encoding="utf-8")
    print(f"stripped {n} block(s) for {key}")


def build_models_block(mk: str, names: list) -> str:
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


def main():
    wave3 = load_manifest(HERE / "manifests" / "wave3_modules.py")
    m = wave3["admin"]

    # 1) remove old admin block
    strip_block(MODELS_INIT, "admin")

    # 2) regenerate admin module files
    print(f"regenerating admin ({m['module_slug']})...")
    generate_from_dict(m, apply=True)

    # 3) re-emit block with new class names
    names = [e["class_name"] for e in m["entities"]]
    block = build_models_block("admin", names)
    txt = MODELS_INIT.read_text(encoding="utf-8")
    if "# <expansion:admin>" not in txt:
        txt = txt.rstrip() + "\n\n" + block
        MODELS_INIT.write_text(txt, encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()

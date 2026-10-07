"""Applique la Vague A : generation + patching idempotent (main, models, nav).

Etapes :
  1. Pre-check collisions : table / class_name / entite / chemin nav complet
     contre les modeles deja generees et navigationRegistry.ts. Echoue si conflit.
  2. generate_from_dict pour chaque module wave5_a.
  3. emit_patches (main.py + models/__init__.py) via les blocs <expansion:mk>.
  4. Insertion nav idempotente (skip si le chemin existe deja).

Reutilisent les builders testes de emit_patches.py et patch_nav.py.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "evo-log-backend"))

from generate_module import generate_from_dict  # noqa: E402
import emit_patches as EP  # noqa: E402
import patch_nav as PN  # noqa: E402


def _load(path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULES


WAVE5 = _load(HERE / "manifests" / "wave5_a.py")

# ── 1. Collision pre-check ───────────────────────────────────────────────────
def check_collisions():
    # Tables / classes deja presentes dans les modeles generees (app/models/*_deep.py)
    models_dir = ROOT / "evo-log-backend" / "app" / "models"
    existing_tables = set()
    existing_classes = set()
    for f in models_dir.glob("*_deep.py"):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith("__tablename__"):
                existing_tables.add(s.split("=", 1)[1].strip().strip('"').strip("'"))
            if s.startswith("class ") and "(Base)" in s:
                existing_classes.add(s.split(" ")[1].split("(")[0])

    # Chemins nav existants
    nav_txt = PN.NAV_TS.read_text(encoding="utf-8")

    problems = []
    new_tables = set()
    new_classes = set()
    new_paths = set()
    for mk, m in WAVE5.items():
        for e in m["entities"]:
            if e["table"] in existing_tables or e["table"] in new_tables:
                problems.append(f"table collision: {e['table']} ({mk})")
            new_tables.add(e["table"])
            if e["class_name"] in existing_classes or e["class_name"] in new_classes:
                problems.append(f"class collision: {e['class_name']} ({mk})")
            new_classes.add(e["class_name"])
            path = f"/{m['module_slug']}/{e['slug']}"
            if path in nav_txt or path in new_paths:
                problems.append(f"nav path collision: {path} ({mk})")
            new_paths.add(path)
    if problems:
        print("COLLISIONS:")
        for p in problems:
            print("  -", p)
        sys.exit(2)
    print(f"OK: 0 collision (tables={len(new_tables)} classes={len(new_classes)} paths={len(new_paths)})")


def generate_all():
    for mk, m in WAVE5.items():
        print(f"\n--- generate {mk} ({m['module_slug']}) ---")
        generate_from_dict(m, apply=True)


def patch_main_models():
    main_blocks, models_blocks = [], []
    for mk, m in WAVE5.items():
        main_blocks.append((mk, EP.build_main_block(mk, m["module_slug"])))
        names = [e["class_name"] for e in m["entities"]]
        models_blocks.append((mk, EP.build_models_block(mk, names)))
    a = EP.patch_file(EP.MAIN_PY, "expansion", main_blocks)
    print(f"main.py added: {a}")
    b = EP.patch_file(EP.MODELS_INIT, "expansion", models_blocks)
    print(f"models/__init__.py added: {b}")


def patch_nav():
    txt = PN.NAV_TS.read_text(encoding="utf-8")
    added_total = 0
    for mk, m in WAVE5.items():
        slug = m["module_slug"]
        perm_module = m["perm_module"]
        block = PN.find_module_block(txt, slug)
        if not block:
            print(f"WARN module block not found: {slug}")
            continue
        sub = PN.find_submodules_array(txt, block[0], block[1])
        if not sub:
            print(f"WARN subModules array not found: {slug}")
            continue
        open_p, close_p = sub
        existing = txt[open_p:close_p]
        new_entries = []
        for e in m["entities"]:
            path = f"/{slug}/{e['slug']}"
            if f'"{path}"' in txt:  # idempotent
                continue
            new_entries.append(PN.build_entry(slug, e, perm_module))
        if not new_entries:
            continue
        insert_at = close_p
        prefix = "\n" if txt[insert_at - 1] == "\n" else ""
        txt = txt[:insert_at] + prefix + "\n".join(new_entries) + "\n    " + txt[insert_at:]
        added_total += len(new_entries)
        print(f"nav +{len(new_entries)} -> {slug}")
    PN.NAV_TS.write_text(txt, encoding="utf-8")
    print(f"nav entries added: {added_total}")


if __name__ == "__main__":
    check_collisions()
    if "--dry" in sys.argv:
        print("DRY: collisions OK, nothing generated")
        sys.exit(0)
    generate_all()
    patch_main_models()
    patch_nav()
    print("\nVAGUE A APPLIED.")

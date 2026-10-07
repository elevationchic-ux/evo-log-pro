"""Generic wave driver : generation + patching idempotent (main, models, nav)
suivi du reordering des routeurs expansion au-dessus du catch-all pending_modules.

Usage :
    python scripts/wave_apply.py manifests/wave5_b.py           # full apply (collision-gated)
    python scripts/wave_apply.py manifests/wave5_b.py --dry      # collision pre-check only
    python scripts/wave_apply.py manifests/wave5_b.py --regen    # overwrite files, skip collision gate + reorder

Reutilise les builders testes de generate_module / emit_patches / patch_nav.
"""
from __future__ import annotations
import importlib.util
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "evo-log-backend"))

from generate_module import generate_from_dict  # noqa: E402
import emit_patches as EP  # noqa: E402
import patch_nav as PN  # noqa: E402


def _load(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULES


def check_collisions(MODS):
    models_dir = ROOT / "evo-log-backend" / "app" / "models"
    existing_tables, existing_classes = set(), set()
    for f in models_dir.glob("*_deep.py"):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith("__tablename__"):
                existing_tables.add(s.split("=", 1)[1].strip().strip('"').strip("'"))
            if s.startswith("class ") and "(Base)" in s:
                existing_classes.add(s.split(" ")[1].split("(")[0])

    nav_txt = PN.NAV_TS.read_text(encoding="utf-8")
    problems = []
    new_tables, new_classes, new_paths = set(), set(), set()
    for mk, m in MODS.items():
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


def generate_all(MODS):
    for mk, m in MODS.items():
        print(f"\n--- generate {mk} ({m['module_slug']}) ---")
        generate_from_dict(m, apply=True)


def patch_main_models(MODS):
    main_blocks, models_blocks = [], []
    for mk, m in MODS.items():
        main_blocks.append((mk, EP.build_main_block(mk, m["module_slug"])))
        names = [e["class_name"] for e in m["entities"]]
        models_blocks.append((mk, EP.build_models_block(mk, names)))
    a = EP.patch_file(EP.MAIN_PY, "expansion", main_blocks)
    print(f"main.py added: {a}")
    b = EP.patch_file(EP.MODELS_INIT, "expansion", models_blocks)
    print(f"models/__init__.py added: {b}")


def patch_nav(MODS):
    txt = PN.NAV_TS.read_text(encoding="utf-8")
    added_total = 0
    for mk, m in MODS.items():
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
        new_entries = []
        for e in m["entities"]:
            path = f"/{slug}/{e['slug']}"
            if f'"{path}"' in txt:  # idempotent
                continue
            new_entries.append(PN.build_entry(slug, e, perm_module))
        if not new_entries:
            continue
        head = txt[:close_p].rstrip()
        # The pre-existing last entry of a bespoke portal may end with '}' and NO
        # trailing comma; the generated entries are comma-terminated. Add the
        # missing separator so the spliced block stays valid TypeScript.
        if head.endswith("}"):
            head += ","
        txt = head + "\n" + "\n".join(new_entries) + "\n    " + txt[close_p:]
        added_total += len(new_entries)
        print(f"nav +{len(new_entries)} -> {slug}")
    PN.NAV_TS.write_text(txt, encoding="utf-8")
    print(f"nav entries added: {added_total}")


def reorder():
    r = subprocess.run([sys.executable, str(HERE / "reorder_expansion_routers.py")],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: wave_apply.py <manifest.py> [--dry|--regen]")
        sys.exit(1)
    arg = sys.argv[1]
    mpath = (HERE / arg) if not Path(arg).is_absolute() else Path(arg)
    MODS = _load(mpath)
    print(f"loaded {len(MODS)} modules from {mpath.name}")

    if "--regen" in sys.argv:
        generate_all(MODS)
        print("\nREGEN done (files overwritten; main/models/nav untouched).")
        sys.exit(0)

    check_collisions(MODS)
    if "--dry" in sys.argv:
        print("DRY: collisions OK, nothing generated")
        sys.exit(0)
    generate_all(MODS)
    patch_main_models(MODS)
    patch_nav(MODS)
    reorder()
    print("\nWAVE APPLIED.")

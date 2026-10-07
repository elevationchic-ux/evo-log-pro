"""Dump existing (slug, table, class_name, entite) per module to avoid collisions."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAN = HERE / "manifests"


def load_modules(path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "MODULES", None)


def load_manifest(path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "MANIFEST", None)


targets = {"log3pl", "fluvial", "aerien", "ferroviaire", "parc", "qhse"}
rows = {}
for p in [MAN / "all_modules.py", MAN / "wave3_modules.py",
          MAN / "wave4_transports.py", MAN / "wave4_logistique.py"]:
    M = load_modules(p)
    if not M:
        continue
    for k, m in M.items():
        if m["perm_module"] in targets or m["module_key"] in targets:
            rows.setdefault(m["module_key"], set())
            for e in m["entities"]:
                rows[m["module_key"]].add((e["slug"], e["table"], e["class_name"], e["entite"]))

for k in sorted(rows):
    print(f"=== {k} ({len(rows[k])}) ===")
    for s, t, c, en in sorted(rows[k]):
        print(f"  slug={s}  table={t}  class={c}  entite={en}")

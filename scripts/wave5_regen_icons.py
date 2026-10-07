# -*- coding: utf-8 -*-
"""Regenereres Vague A (overwrite same files, no collision gate) + corrige les
3 icones lucide invalides dans navigationRegistry.ts."""
import importlib.util
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from generate_module import generate_from_dict  # noqa: E402

spec = importlib.util.spec_from_file_location("w5", HERE / "manifests" / "wave5_a.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
for mk, mod in m.MODULES.items():
    generate_from_dict(mod, apply=True)
print("regenerated wave5 files")

# Correction des icones dans le nav (les entrées sont déjà insérées).
NAV = ROOT / "evo-log-frontend" / "src" / "config" / "navigationRegistry.ts"
txt = NAV.read_text(encoding="utf-8")
for bad, good in [("TriangleAlert", "AlertTriangle"),
                  ("SquareCheckBig", "CheckSquare"),
                  ("ReceiptText", "Receipt")]:
    n = txt.count(f'(LUCIDE as any)["{bad}"]')
    txt = txt.replace(f'(LUCIDE as any)["{bad}"]', f'(LUCIDE as any)["{good}"]')
    print(f"nav {bad}->{good}: {n}")
NAV.write_text(txt, encoding="utf-8")
print("done")

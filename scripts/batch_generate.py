"""Batch generator for all remaining ERP expansion modules (Waves 1C, 1D, 2, 3).

Reads MODULES dict from scripts/manifests/all_modules.py and scripts/manifests/wave3_modules.py
and calls generate_from_dict for each.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from generate_module import generate_from_dict  # noqa: E402


def _load_modules(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location(f"m_{path.stem}", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULES


def main():
    manifests = [
        HERE / "manifests" / "all_modules.py",
        HERE / "manifests" / "wave3_modules.py",
        HERE / "manifests" / "wave4_transports.py",
        HERE / "manifests" / "wave4_logistique.py",
    ]
    for p in manifests:
        print(f"\n=== {p.name} ===")
        MODULES = _load_modules(p)
        for key, m in MODULES.items():
            print(f"\n--- Generating module: {key} ({m['module_slug']}) ---")
            try:
                generate_from_dict(m, apply=True)
            except Exception as e:
                print(f"ERROR while generating {key}: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()

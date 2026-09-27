"""Fix double-encoded UTF-8 in 3 remaining vitrine pages."""
import pathlib
import re

ROOT = pathlib.Path("evo-log-frontend/src/app/(app)/magasin")
TARGETS = ["import-export", "inventory/physical", "magasins"]

for t in TARGETS:
    p = ROOT / t / "page.tsx"
    if not p.exists():
        print(f"SKIP    {p}")
        continue
    raw = p.read_bytes()
    # Detect double-encoding: presence of \xc3\x83 (Ã) which means UTF-8 of UTF-8
    if b'\xc3\x83' not in raw:
        print(f"CLEAN   {p}")
        continue
    # Fix: decode as UTF-8 twice
    try:
        text = raw.decode('utf-8')  # First decode: gives us the Latin-1 interpretation
        fixed = text.encode('latin-1').decode('utf-8')  # Reinterpret as original UTF-8 bytes
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        print(f"ERROR   {p}: {e}")
        continue
    # Verify fix worked
    assert 'Syst\u00e8me' in fixed or 'Connect' in fixed, f"Fix failed for {p}"
    p.write_bytes(fixed.encode('utf-8'))
    print(f"FIXED   {p} (encoding repair)")

print("\nDone. Re-run fix_magasin_vitrine_honnetete.py for content replacement.")

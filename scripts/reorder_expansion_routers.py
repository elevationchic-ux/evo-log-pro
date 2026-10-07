"""Relocate all <expansion:...> blocks in main.py to sit BEFORE pending_modules.

pending_modules is a catch-all `/api/v1/{full_path:path}` router. Starlette
resolves routes in registration order, so any expansion router included AFTER
pending_modules is shadowed. This script extracts every expansion block from
main.py and re-inserts the group just before `from app.routers.v1 import pending_modules`.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "evo-log-backend" / "app" / "main.py"

ANCHOR = "from app.routers.v1 import pending_modules"

pattern = re.compile(
    r"# <expansion:\w+>\n.*?# </expansion:\w+>\n?",
    re.DOTALL,
)

txt = MAIN.read_text(encoding="utf-8")
blocks = pattern.findall(txt)
if not blocks:
    print("no expansion blocks found")
    raise SystemExit(1)

stripped = pattern.sub("", txt)
# Remove excessive blank lines from stripping
stripped = re.sub(r"\n{3,}", "\n\n", stripped)

if ANCHOR not in stripped:
    print("anchor missing, cannot reorder")
    raise SystemExit(1)

group = "\n".join(b.rstrip() for b in blocks) + "\n"
new = stripped.replace(ANCHOR, group + "\n" + ANCHOR, 1)
MAIN.write_text(new, encoding="utf-8")
print(f"relocated {len(blocks)} expansion blocks above pending_modules")

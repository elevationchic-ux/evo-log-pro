"""Fix navigationRegistry.ts: insert comma between existing last entry and expansion entries."""
from pathlib import Path
import re

p = Path(__file__).resolve().parents[1] / "evo-log-frontend" / "src" / "config" / "navigationRegistry.ts"
txt = p.read_text(encoding="utf-8")

pat = re.compile(r"\}(\s+)(\{[\s\S]{0,300}?badge:\s*['\"]Expansion\.)")


def fix(m):
    return "},\n      " + m.group(2)


new = pat.sub(fix, txt)
p.write_text(new, encoding="utf-8")
print(f"chars delta: {len(new) - len(txt)}")
print(f"matches applied")

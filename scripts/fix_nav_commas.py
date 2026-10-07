"""Fix navigationRegistry.ts: add comma between existing last entry and expansion entries."""
from pathlib import Path
import re

p = Path(__file__).resolve().parents[1] / "evo-log-frontend" / "src" / "config" / "navigationRegistry.ts"
txt = p.read_text(encoding="utf-8")

pat = re.compile(r'\}(?!,)[\s]+\{[\s\S]{0,300}?badge: "Expansion')


def replacer(m):
    # Rebuild the matched span: '}' + ',' + '\n      ' + '{...badge: "Expansion'
    full = m.group(0)
    brace_end = full.index('}') + 1
    open_brace = full.index('{')
    tail = full[open_brace:]
    return '},\n      ' + tail


new = pat.sub(replacer, txt)
p.write_text(new, encoding="utf-8")
print(f"chars delta: {len(new) - len(txt)}")

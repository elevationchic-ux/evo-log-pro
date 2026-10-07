from pathlib import Path
import re

p = Path("evo-log-frontend/src/config/navigationRegistry.ts")
txt = p.read_text(encoding="utf-8")

pat = re.compile(r'(\})(?!,)(\s+)(\{[\s\S]{0,400}?badge:\s*"Expansion\.)')
matches = list(pat.finditer(txt))
print(f"matches: {len(matches)}")
if matches:
    for i, m in enumerate(matches[:3]):
        print(f"[{i}] at {m.start()}: {m.group(0)[:80]!r}")

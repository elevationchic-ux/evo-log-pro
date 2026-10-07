from pathlib import Path
import re

p = Path("evo-log-frontend/src/config/navigationRegistry.ts")
txt = p.read_text(encoding="utf-8")

# Just look for occurrences of 'badge: "Expansion"' with any preceding context
matches = list(re.finditer(r'badge:\s*"Expansion', txt))
print(f"badge Expansion occurrences: {len(matches)}")

# Look at context around first one
if matches:
    m = matches[0]
    ctx = txt[max(0,m.start()-500):m.end()+50]
    print("---- 500 chars before first badge:")
    print(ctx)

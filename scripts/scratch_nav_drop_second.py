"""Remove the second occurrence of duplicated nav entries (same tcode/path, older icon set)."""
import re

P = "evo-log-frontend/src/config/navigationRegistry.ts"
txt = open(P, encoding="utf-8").read()

dupes = [
    "/transit-douane/trader-registration",
    "/magasin-stock/consignment-stock",
    "/comptabilite-ohada/treasury-accounts",
    "/finance-ohada/credit-facilities",
    "/parc-vehicules/registration-tracking",
    "/superadmin-cadc/partner-network",
]

entry_pat = re.compile(r"[ ]*\{\n(?:\s+[a-zA-Z]+:.*?\n)+?\s+\},")

for path in dupes:
    blocks = [m for m in entry_pat.finditer(txt) if re.search(r'path:\s*"%s"' % re.escape(path), m.group(0))]
    if len(blocks) < 2:
        print("skip", path, len(blocks))
        continue
    m = blocks[1]
    # remove block plus surrounding blank-line noise up to previous '},'
    start = m.start()
    end = m.end()
    txt = txt[:start] + txt[end:]
    print("removed second", path)

open(P, "w", encoding="utf-8").write(txt)

paths = re.findall(r'path:\s*"(/[^"]+)"', txt)
from collections import Counter
print("remaining dup paths:", {k: v for k, v in Counter(paths).items() if v > 1})

# -*- coding: utf-8 -*-
"""Injecte le fragment de navigation wave 5 dans navigationRegistry.ts.

Point d'insertion : juste avant la ligne `};` qui ferme NAVIGATION_REGISTRY
(et qui suit immediatement la cloture du module logistique-3pl).

Idempotent : si un marker WAVE 5 existe deja, on remplace le bloc.
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NAV = os.path.join(ROOT, "evo-log-frontend", "src", "config", "navigationRegistry.ts")
FRAG = os.path.join(ROOT, "scripts", "_wave5_nav_fragment.txt")

BEGIN = "// <WAVE5-EXPANSION-BEGIN>"
END = "// <WAVE5-EXPANSION-END>"

with open(NAV, "r", encoding="utf-8") as f:
    src = f.read()

with open(FRAG, "r", encoding="utf-8") as f:
    fragment = f.read().rstrip()

block = BEGIN + "\n" + fragment + "\n" + END + "\n"

if BEGIN in src and END in src:
    new_src = re.sub(
        re.escape(BEGIN) + r"[\s\S]*?" + re.escape(END) + r"\n?",
        block,
        src,
        count=1,
    )
    print("REPLACE existing WAVE5 block")
else:
    # inserer avant le `};` qui ferme NAVIGATION_REGISTRY
    # ancre specifique : cloture de logistique-3pl (dernier module wave4)
    anchor = (
        '        requiredRoles: ["log3pl.damage_claim.read"],\n'
        "      },\n"
        "    ]\n"
        "  },\n"
        "};\n"
    )
    idx = src.find(anchor)
    if idx < 0:
        print("ERROR: anchor (log3pl.damage_claim + };) not found")
        sys.exit(2)
    insert_at = idx + len(anchor) - len("};\n")
    new_src = src[:insert_at] + "\n" + block + src[insert_at:]
    print("INSERT new WAVE5 block before NAVIGATION_REGISTRY closing")

with open(NAV, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_src)

print("OK", NAV)

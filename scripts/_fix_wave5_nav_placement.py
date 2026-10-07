# -*- coding: utf-8 -*-
"""Repositionne le bloc WAVE 5 au bon endroit dans navigationRegistry.ts.

Bug precedent: rfind('\\n};') avait chope le '};' final du fichier (apres
MODULE_TITLES_EN + ADVANCED_SUBMODULES etc.), et non la cloture de
NAVIGATION_REGISTRY. On retire le bloc mal place, puis on le re-insere juste
apres la cloture de logistique-3pl (ancre = requiredRoles de damage_claim).
"""
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

# 1) enlever l'ancien bloc s'il existe
pat = re.compile(re.escape(BEGIN) + r"[\s\S]*?" + re.escape(END) + r"\n?")
if BEGIN in src:
    src2, n = pat.subn("", src, count=1)
    print(f"REMOVED old WAVE5 block (matches={n})")
    src = src2

with open(FRAG, "r", encoding="utf-8") as f:
    fragment = f.read().rstrip()

block = BEGIN + "\n" + fragment + "\n" + END + "\n"

# 2) ancre unique = cloture de logistique-3pl
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
# inserer le bloc entre `  },` (fin logistique-3pl) et `};` (fin NAV_REGISTRY)
insert_at = idx + len(anchor) - len("};\n")  # avant '};\n'
new_src = src[:insert_at] + block + src[insert_at:]

with open(NAV, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_src)
print("OK reinserted WAVE5 block before NAVIGATION_REGISTRY closing")

# -*- coding: utf-8 -*-
"""Inject (idempotent) le bloc navigationRegistry WAVE 6.

Insere le fragment genere entre // <WAVE6-EXPANSION-BEGIN> et
// <WAVE6-EXPANSION-END>, immediatement apres la balise WAVE5-EXPANSION-END.
Re-executable : remplace le bloc existant s'il est deja present.
"""
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
NAV = os.path.join(ROOT, "evo-log-frontend", "src", "config", "navigationRegistry.ts")
FRAG = os.path.join(ROOT, "scripts", "_wave6_nav_fragment.txt")

src = open(NAV, encoding="utf-8").read()
frag_full = open(FRAG, encoding="utf-8").read()

# extraire l'interieur du fragment (entre les deux balises)
m = re.search(r"// <WAVE6-EXPANSION-BEGIN>\n(.*?)\n?// <WAVE6-EXPANSION-END>", frag_full, re.S)
if not m:
    print("ERR: fragment introuvable")
    raise SystemExit(2)
inner = m.group(1)

block = "// <WAVE6-EXPANSION-BEGIN>\n" + inner + "\n// <WAVE6-EXPANSION-END>\n"

# 1) si deja present, remplacer (idempotent)
if "// <WAVE6-EXPANSION-BEGIN>" in src:
    src = re.sub(
        r"// <WAVE6-EXPANSION-BEGIN>.*?// <WAVE6-EXPANSION-END>\n",
        block,
        src,
        flags=re.S,
    )
    open(NAV, "w", encoding="utf-8", newline="\n").write(src)
    print("REPLACED existing WAVE6 block")
    raise SystemExit(0)

# 2) sinon inserer apres l'END de WAVE5
anchor = "// <WAVE5-EXPANSION-END>\n"
if anchor not in src:
    print("ERR: ancre WAVE5-EXPANSION-END absente")
    raise SystemExit(3)
src = src.replace(anchor, anchor + block, 1)
open(NAV, "w", encoding="utf-8", newline="\n").write(src)
print("INSERTED WAVE6 block after WAVE5-EXPANSION-END")

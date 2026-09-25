# -*- coding: utf-8 -*-
"""Sweep dark-only PASSE 2: badges semantiques clairs + overlays opacity.

- bg-{couleur}-50/100  -> bg-{couleur}-500/10|15 (badges sombres)
- text-{couleur}-700/800/900 -> text-{couleur}-300/200
- border-{couleur}-100/200/300 -> border-{couleur}-500/x (sombres)
- bg-{slate,gray}-{50,100}/NN (opacity) -> bg-slate-800/NN
- bg-white/80|90|95 (panneaux quasi-blancs) -> bg-slate-900/NN
- hover:bg-white/50 -> hover:bg-white/10
- text-slate-600 -> text-slate-400 (contraste)
Ignore les variantes print: et dark: (dejа foncees ou destinees a l'impression).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "evo-log-frontend" / "src"

COLORS = "blue|green|red|yellow|amber|emerald|rose|sky|teal|indigo|violet|purple|orange|pink|cyan|lime|fuchsia"
VAR = r"((?:[A-Za-z0-9_-]+:)*)"
TAIL = r"(?![0-9A-Za-z_/-])"

# (regex, replacement)
RULES = [
    (VAR + r"bg-(" + COLORS + r")-50" + TAIL, r"\g<1>bg-\g<2>-500/10"),
    (VAR + r"bg-(" + COLORS + r")-100" + TAIL, r"\g<1>bg-\g<2>-500/15"),
    (VAR + r"text-(" + COLORS + r")-(700|800)" + TAIL, r"\g<1>text-\g<2>-300"),
    (VAR + r"text-(" + COLORS + r")-900" + TAIL, r"\g<1>text-\g<2>-200"),
    (VAR + r"border-(" + COLORS + r")-100" + TAIL, r"\g<1>border-\g<2>-500/30"),
    (VAR + r"border-(" + COLORS + r")-200" + TAIL, r"\g<1>border-\g<2>-500/40"),
    (VAR + r"border-(" + COLORS + r")-300" + TAIL, r"\g<1>border-\g<2>-500/50"),
    (VAR + r"bg-(?:slate|gray)-(?:50|100)(/\d+)" + TAIL, r"\g<1>bg-slate-800\g<2>"),
    (VAR + r"bg-slate-200(/\d+)" + TAIL, r"\g<1>bg-slate-700\g<2>"),
    (VAR + r"border-slate-200(/\d+)" + TAIL, r"\g<1>border-slate-700\g<2>"),
    (VAR + r"hover:bg-white/50" + TAIL, r"\g<1>hover:bg-white/10"),
    (VAR + r"bg-white/(80|90|95)" + TAIL, r"\g<1>bg-slate-900/\g<2>"),
    (VAR + r"text-slate-600" + TAIL, r"\g<1>text-slate-400"),
]

SKIP = {"print", "dark"}
COMPILED = [(re.compile(p), r) for p, r in RULES]


def fix(text: str):
    n = 0
    for pat, repl in COMPILED:
        def cb(m):
            nonlocal n
            variants = (m.group(1) or "").lower()
            if any(v + ":" in variants for v in SKIP):
                return m.group(0)
            n += 1
            return m.expand(repl)
        text = pat.sub(cb, text)
    return text, n


def main():
    files = repls = 0
    for tsx in sorted(ROOT.rglob("*.tsx")):
        original = tsx.read_text(encoding="utf-8")
        fixed, count = fix(original)
        if count:
            tsx.write_text(fixed, encoding="utf-8", newline="\n")
            files += 1
            repls += count
            print(f"{count:5d}  {tsx.relative_to(ROOT.parent)}")
    print(f"\n{files} fichiers, {repls} remplacements.")


if __name__ == "__main__":
    main()

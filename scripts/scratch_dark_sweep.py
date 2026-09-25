# -*- coding: utf-8 -*-
"""Sweep dark-only: remplace les classes Tailwind claires par leurs équivalents dark.

Prudent par conception:
- ne touche jamais aux utilitaires préfixés `print:` (documents à imprimer, ex: BL)
- ne touche jamais aux variantes `dark:` (déjà dark)
- ne touche pas aux opacités (`bg-white/10` reste un overlay clair valide sur dark)
- remplace uniquement des tokens de classe complets (word-boundary)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "evo-log-frontend" / "src"

# paires (token clair -> token dark), ordre = priorité
PAIRS = [
    ("hover:bg-white", "hover:bg-slate-800"),
    ("hover:bg-gray-50", "hover:bg-slate-800"),
    ("hover:bg-gray-100", "hover:bg-slate-800"),
    ("hover:bg-slate-50", "hover:bg-slate-800"),
    ("hover:bg-slate-100", "hover:bg-slate-800"),
    ("bg-white", "bg-slate-900"),
    ("bg-gray-50", "bg-slate-800"),
    ("bg-gray-100", "bg-slate-800"),
    ("bg-gray-200", "bg-slate-700"),
    ("bg-slate-50", "bg-slate-800"),
    ("bg-slate-100", "bg-slate-900"),
    ("bg-slate-200", "bg-slate-700"),
    ("divide-gray-100", "divide-slate-800"),
    ("divide-gray-200", "divide-slate-800"),
    ("divide-slate-100", "divide-slate-800"),
    ("divide-slate-200", "divide-slate-800"),
    ("border-gray-100", "border-slate-700"),
    ("border-gray-200", "border-slate-700"),
    ("border-gray-300", "border-slate-600"),
    ("border-slate-100", "border-slate-700"),
    ("border-slate-200", "border-slate-700"),
    ("border-slate-300", "border-slate-600"),
    ("text-gray-500", "text-slate-400"),
    ("text-gray-600", "text-slate-400"),
    ("text-gray-700", "text-slate-200"),
    ("text-gray-800", "text-slate-100"),
    ("text-gray-900", "text-slate-100"),
    ("text-slate-700", "text-slate-300"),
    ("text-slate-800", "text-slate-200"),
    ("text-slate-900", "text-slate-200"),
]

SKIP_VARIANTS = {"print", "dark"}

compiled = []
for src, dst in PAIRS:
    # variantes optionnelles devant le token, token non suivi de / - . ou alphanumérique
    pat = re.compile(r"((?:[A-Za-z0-9_-]+:)*)" + re.escape(src) + r"(?![A-Za-z0-9/_.-])")
    compiled.append((src, dst, pat))


def fix_text(text: str):
    n = 0
    for src, dst, pat in compiled:
        def repl(m):
            nonlocal n
            variants = m.group(1) or ""
            prefix = variants.lower()
            for v in SKIP_VARIANTS:
                if (v + ":").lower() in prefix:
                    return m.group(0)
            n += 1
            return variants + dst
        text = pat.sub(repl, text)
    return text, n


def main():
    total_files = 0
    total_repl = 0
    for tsx in sorted(ROOT.rglob("*.tsx")):
        original = tsx.read_text(encoding="utf-8")
        fixed, count = fix_text(original)
        if count:
            tsx.write_text(fixed, encoding="utf-8", newline="\n")
            total_files += 1
            total_repl += count
            print(f"{count:5d}  {tsx.relative_to(ROOT.parent)}")
    print(f"\n{total_files} fichiers modifiés, {total_repl} remplacements.")


if __name__ == "__main__":
    main()

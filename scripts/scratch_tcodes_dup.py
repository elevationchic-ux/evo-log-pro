"""Comparaison transient des deux registres de T-Codes du frontend.

Le depot porte `src/lib/tcodes.ts` (32 codes, consomme par le seul
`components/ui/TCodeSearch.tsx`) et `src/utils/tcodeLookup.ts` (registre canonique,
consomme par ModuleHeader, PermissionGuard, dashboard/global). Ce script dit
seulement si le petit est un sous-ensemble du grand : c'est la condition pour
faire deleguer l'un a l'autre sans rien perdre.
"""
import pathlib
import re

FRONT = pathlib.Path(__file__).resolve().parents[1] / "evo-log-frontend" / "src"
CODE_RE = re.compile(r"^\s*'([A-Za-z0-9_]+)':\s*'(/[^']*)'", re.M)

petit = dict(CODE_RE.findall((FRONT / "lib" / "tcodes.ts").read_text(encoding="utf-8")))
grand = dict(CODE_RE.findall((FRONT / "utils" / "tcodeLookup.ts").read_text(encoding="utf-8")))

orphelins = {k: v for k, v in petit.items() if k not in grand}
conflits = {k: (petit[k], grand[k]) for k in petit if k in grand and petit[k] != grand[k]}
print(f"lib/tcodes       : {len(petit)} codes")
print(f"utils/tcodeLookup: {len(grand)} codes")
print(f"absents du registre canonique : {len(orphelins)} -> {orphelins}")
print(f"memes codes, routes differentes : {len(conflits)} -> {conflits}")

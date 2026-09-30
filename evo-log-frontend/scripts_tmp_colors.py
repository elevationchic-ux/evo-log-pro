"""Genere les variables CSS --module-*-{bg,text} depuis modulePalette.ts.

Regle produit "une couleur unique par module" : la palette TS est la source de
verite. Les badges de globals.css doivent donc porter EXACTEMENT la meme teinte
que la sidebar / le dropdown / la bulle orbitale. Le mode jour etant supprime,
les deux blocs (:root et .dark) recoivent la meme valeur sombre.
"""
import io, re, colorsys

PAL_SRC = io.open("src/config/modulePalette.ts", encoding="utf-8").read()
CSS = "src/app/globals.css"

# 1. Palette : cle -> hex
entries = {}
for m in re.finditer(r"^  '?" r"([a-zA-Z][a-zA-Z0-9-]*)" r"'?: \{\n    hex: '#([0-9A-Fa-f]{6})'", PAL_SRC, re.M):
    entries[m.group(1)] = m.group(2).upper()

# 2. Aliases legacy declares dans le fichier TS
alias = {}
tail = PAL_SRC[PAL_SRC.index("const LEGACY_ALIAS"):]
for m in re.finditer(r"^\s*'?([a-zA-Z][a-zA-Z0-9-]*)" r"'?: '?([a-zA-Z][a-zA-Z0-9-]*)" r"',?$", tail, re.M):
    alias[m.group(1)] = m.group(2)
# Noms utilises uniquement par les variables CSS (pas de cle de palette).
alias.setdefault("audit", "admin-tenant")
alias.setdefault("master", "admin-tenant")
alias.setdefault("integration", "transit-douane")

DEFAULT = "dashboard"


def resolve(name):
    if name in entries:
        return name
    a = alias.get(name)
    if a and a in entries:
        return a
    return DEFAULT


def hsl(hexcode):
    r, g, b = (int(hexcode[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return round(h * 360), round(s * 100), round(l * 100)


s = io.open(CSS, encoding="utf-8").read()
report = []


def sub(m):
    indent, name, kind = m.group(1), m.group(2), m.group(3)
    key = resolve(name)
    hue, sat, _ = hsl(entries[key])
    sat = max(45, min(sat, 92))
    if kind == "bg":
        val = f"{hue} {sat}% 18%"
    else:
        val = f"{hue} {max(sat, 70)}% 74%"
    old = m.group(4).strip()
    if old.split()[0] != str(hue):
        report.append(f"{name:<20} hue {old.split()[0]:>3} -> {hue:<3} ({key})")
    return f"{indent}--module-{name}-{kind}: {val};"


pattern = re.compile(r"^(\s*)--module-([a-z0-9_-]+)-(bg|text):\s*([^;]+);", re.M)
s = pattern.sub(sub, s)
io.open(CSS, "w", encoding="utf-8", newline="\n").write(s)

print(f"{len(entries)} couleurs de palette, {len(alias)} aliases")
print("divergences corrigees:")
for line in report:
    print("  " + line)
if not report:
    print("  (aucune)")

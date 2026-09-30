"""Audit de la hierarchie de navigation.

Croise le NAVIGATION_REGISTRY (chemins affiches dans la sidebar) avec les
vraies pages Next.js sous app/(app). But : trouver (1) les modules/pages qui
EXISTENT mais n'apparaissent dans AUCUNE entree de menu (invisibles = la
plainte 'je ne vois pas les modules avances'), et (2) les entrees de menu qui
pointent vers une page inexistante (liens morts).

Sortie : liste triee, sans inventer. Les pages de detail (create/edit/view/[id])
 sont légitimement hors menu ; on ne signale que les RACINES de module absentes.
"""
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FE = os.path.join(ROOT, "evo-log-frontend", "src")
REG = os.path.join(FE, "config", "navigationRegistry.ts")
APP = os.path.join(FE, "app", "(app)")

# --- 1) chemins references dans le registre -------------------------------
reg_txt = open(REG, encoding="utf-8").read()
nav_paths = set()
for m in re.finditer(r"""path:\s*['"`]([^'"`]+)['"`]""", reg_txt):
    p = m.group(1).strip()
    if p.startswith("/"):
        nav_paths.add(p.split("?")[0].rstrip("/") or "/")

# --- 2) vraies pages -> URLs ----------------------------------------------
def page_to_url(fp):
    rel = os.path.relpath(fp, APP).replace("\\", "/")
    rel = os.path.dirname(rel) if rel.lower().endswith("page.tsx") else rel
    parts = [seg for seg in rel.split("/") if seg and not seg.startswith("(")]
    url = "/" + "/".join(parts)
    return url.rstrip("/")

pages = []
for fp in glob.glob(os.path.join(APP, "**", "page.tsx"), recursive=True):
    pages.append(page_to_url(fp))
pages = sorted(set(pages))

# racines de module = 1er segment ; le menu doit en couvrir au moins un chemin
def root_of(u):
    seg = u.strip("/").split("/")
    return "/" + seg[0] if seg and seg[0] else "/"

module_roots = {}  # root -> list of page urls
for u in pages:
    module_roots.setdefault(root_of(u), []).append(u)

# un chemin de menu couvre une racine si prefixe /<root>
nav_roots = {r for r in module_roots if any(np == r or np.startswith(r + "/") for np in nav_paths)}

print("=" * 72)
print(f"entrees de menu (chemins): {len(nav_paths)}   pages reelles: {len(pages)}   racines module: {len(module_roots)}")
print("=" * 72)

print("\n### RACINES DE MODULE ABSENTES DU MENU (invisibles utilisateur) ###")
missing = sorted(module_roots.keys() - nav_roots)
for r in missing:
    print(f"  {r}  ({len(module_roots[r])} pages)")
if not missing:
    print("  (aucune - toute racine est couverte)")

print("\n### ENTTRES DE MENU SANS PAGE CORRESPONDANTE (lien mort potentiel) ###")
def has_page(np):
    # page exacte, ou dynamique [id]/[x] sur n'importe quel segment
    for u in pages:
        segs_menu = np.strip("/").split("/")
        segs_page = u.strip("/").split("/")
        if len(segs_menu) != len(segs_page):
            continue
        ok = all(sm == sp or sp.startswith("[") for sm, sp in zip(segs_menu, segs_page))
        if ok:
            return True
    return False

dead = sorted(np for np in nav_paths if not has_page(np))
for d in dead:
    print(f"  {d}")
if not dead:
    print("  (aucun - tout chemin de menu mene a une page)")

print("\n### TOUTES LES RACINES DE MODULE (couvertes ou non) ###")
for r in sorted(module_roots):
    flag = "OK-menu" if r in nav_roots else "--ABSENT--"
    print(f"  [{flag:11}] {r}  ({len(module_roots[r])} pages)")

"""Audit de hierarchie, AVEC resolution des redirections.

Le menu (NAVIGATION_REGISTRY) pointe parfois vers des pages qui ne sont qu'un
redirect() vers le vrai arbre (ex /magasin-stock/dashboard -> /magasin/dashboard).
Un module n'est DONC caché que si aucune chaine partant d'une entree de menu ne
l'atteint. On calcule l'ensemble atteignable par fermeture transitive des
redirect(), puis on signale les racines de pages qui en sont absentes.
"""
import os
import re
import glob
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FE = os.path.join(ROOT, "evo-log-frontend", "src")
REG = os.path.join(FE, "config", "navigationRegistry.ts")
APP = os.path.join(FE, "app", "(app)")


def page_to_url(fp):
    rel = os.path.relpath(fp, APP).replace("\\", "/")
    rel = os.path.dirname(rel) if rel.lower().endswith("page.tsx") else rel
    parts = [seg for seg in rel.split("/") if seg and not seg.startswith("(")]
    return ("/" + "/".join(parts)).rstrip("/") or "/"


reg_txt = open(REG, encoding="utf-8").read()
nav_paths = set()
for m in re.finditer(r"""path:\s*['"`]([^'"`]+)['"`]""", reg_txt):
    p = m.group(1).strip()
    if p.startswith("/"):
        nav_paths.add(p.split("?")[0].rstrip("/") or "/")

pages = sorted({page_to_url(fp) for fp in glob.glob(os.path.join(APP, "**", "page.tsx"), recursive=True)})

# url -> cible de redirect (s'il n'y a qu'un redirect et rien d'essentiel autour)
RED_RE = re.compile(r"""redirect\(\s*[`'"]([^`'"]+)[`'"]\s*\)""")
url2red = {}
for fp in glob.glob(os.path.join(APP, "**", "page.tsx"), recursive=True):
    u = page_to_url(fp)
    txt = open(fp, encoding="utf-8", errors="ignore").read()
    ms = RED_RE.findall(txt)
    if ms:
        url2red[u] = [t.split("?")[0].rstrip("/") or "/" for t in ms]

pages_set = set(pages)


def resolve(u, seen=None):
    """Retourne l'ensemble des URLs atteignables depuis u en suivant les redirects."""
    seen = seen or set()
    out = set()
    dq = deque([u])
    while dq:
        cur = dq.popleft()
        if cur in seen:
            continue
        seen.add(cur)
        out.add(cur)
        for nxt in url2red.get(cur, []):
            # cible dynamique ?params -> normalise vers la page /params absente
            base = nxt
            dq.append(base)
    return out


reachable = set()
for np in nav_paths:
    reachable |= resolve(np)

# une racine de page est couverte si AU MOINS une de ses pages est reachable
def root_of(u):
    seg = u.strip("/").split("/")
    return "/" + seg[0] if seg and seg[0] else "/"


roots = {}
for u in pages:
    roots.setdefault(root_of(u), []).append(u)

covered_roots = {r for r, us in roots.items() if any(u in reachable for u in us)}

print("=" * 74)
print(f"nav={len(nav_paths)}  pages={len(pages)}  racines={len(roots)}  reachable_urls={len(reachable)}")
print("=" * 74)

hidden = sorted(set(roots) - covered_roots)
print("\n### RACINES TOTALEMENT INATTEIGNABLES DEPUIS LE MENU (vrais modules caches) ###")
for r in hidden:
    sample = ", ".join(sorted(roots[r])[:4])
    print(f"  {r:26} ({len(roots[r]):2} pages)  ex: {sample}")
if not hidden:
    print("  (aucun)")

print("\n### ENTTRES DE MENU MORTS (aucune page, meme apres redirection) ###")
# un chemin de menu est 'vivant' s'il existe comme page OU redirige vers une page
def menu_alive(np):
    for u in pages_set:
        sm, sp = np.strip("/").split("/"), u.strip("/").split("/")
        if len(sm) == len(sp) and all(a == b or b.startswith("[") for a, b in zip(sm, sp)):
            return True
    # chaine de redirect depuis une page concordante
    for u in pages_set:
        sm, sp = np.strip("/").split("/"), u.strip("/").split("/")
        if len(sm) == len(sp) and all(a == b or b.startswith("[") for a, b in zip(sm, sp)):
            for t in url2red.get(u, []):
                if t in pages_set:
                    return True
    return False


dead = sorted(np for np in nav_paths if not menu_alive(np))
for d in dead:
    print(f"  {d}")
if not dead:
    print("  (aucun)")

# -*- coding: utf-8 -*-
"""Cartographie les pages-redirect (server redirect('/x') ou client
ClientRedirectPage / router.replace('/x')) sous app/(app) et detecte les
incoherences: page listee dans une famille canonique mais dont la cible
appartient a un AUTRE module, et eventuelles boucles."""
import io
import os
import re
import sys

APP = os.path.join("evo-log-frontend", "src", "app", "(app)")
REG = os.path.join("evo-log-frontend", "src", "config", "navigationRegistry.ts")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 1) toutes les pages + leur eventual cible de redirection
pages = {}
for root, _dirs, files in os.walk(APP):
    for fn in files:
        if fn != "page.tsx":
            continue
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, APP).replace("\\", "/")
        rel = "/" + rel[: -len("/page.tsx")] if rel != "page.tsx" else "/"
        if rel == "/":
            rel = "/" + os.path.relpath(root, APP).replace("\\", "/").split("/")[0]
        try:
            txt = io.open(full, encoding="utf-8").read()
        except Exception:
            txt = ""
        target = None
        m = re.search(r"redirect\(\s*['\"]([^'\"]+)['\"]", txt)
        if m:
            target = m.group(1)
        else:
            m2 = re.search(r"router\.(?:replace|push)\(\s*['\"]([^'\"]+)['\"]", txt)
            if m2:
                target = m2.group(1)
        pages[rel] = target

# 2) famille -> chemins de sous-modules (regex sur le bloc advance + cle de famille)
reg_txt = io.open(REG, encoding="utf-8").read()
fam_paths = {}
# entries de type { family: 'X', ... path: '/y' ...}
for m in re.finditer(r"family:\s*'([^']+)'.*?path:\s*'([^']+)'", reg_txt, re.S):
    fam, path = m.group(1), m.group(2)
    fam_paths.setdefault(fam, []).append(path)


def root_seg(p):
    seg = p.split("/")[1] if p.startswith("/") and len(p.split("/")) > 1 else ""
    return "/" + seg if seg else p


def is_client_redirect_stub(path):
    full = os.path.join(APP, path.lstrip("/").replace("/", os.sep), "page.tsx")
    if not os.path.exists(full):
        return None
    txt = io.open(full, encoding="utf-8", errors="replace").read()
    if "ClientRedirectPage" in txt:
        m = re.search(r"router\.(?:replace|push)\(\s*['\"]([^'\"]+)['\"]", txt)
        return m.group(1) if m else "CLIENT_REDIRECT_INDETERMINABLE"
    return None


print("== CIBLES DE REDIRECTION (serveur) depuis des pages ==")
loops = 0
mismatch = 0
for p, t in sorted(pages.items()):
    if t:
        own = root_seg(p)
        dest = root_seg(t)
        flag = ""
        if own != dest:
            flag = "  <== change de module (%s -> %s)" % (own, dest)
            mismatch += 1
        # boucle: cible renvoie vers nous
        if pages.get(t) == p or (t.rstrip("/") + "/") .rstrip("/") and pages.get(t.rstrip("/")) == p:
            flag += "  <== BOUCLE"
            loops += 1
        print("  %-34s -> %-28s%s" % (p, t, flag))

print("\n== STUBS client (ClientRedirectPage) ==")
for p in sorted(pages):
    tgt = is_client_redirect_stub(p)
    if tgt:
        own = root_seg(p)
        dest = root_seg(tgt) if isinstance(tgt, str) and tgt.startswith("/") else tgt
        flag = ""
        if dest and own != dest:
            flag = "  <== change de module (%s -> %s)" % (own, dest)
        print("  %-30s -> %-24s%s" % (p, tgt, flag))

print("\nresume: redirects serveur=%d  mismatch=%d  boucles=%d"
      % (sum(1 for t in pages.values() if t), mismatch, loops))

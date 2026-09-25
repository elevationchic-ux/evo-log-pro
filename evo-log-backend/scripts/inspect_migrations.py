# -*- coding: utf-8 -*-
"""Inspection rapide de la chaine de migrations alembic."""
import glob
import re

for f in sorted(glob.glob('migrations/versions/*.py')):
    c = open(f, encoding='utf-8', errors='replace').read()
    r = re.search(r"^revision[^=]*=\s*['\"]([^'\"]+)", c, re.M)
    d = re.search(r"^down_revision[^=]*=\s*(?:['\"]([^'\"]+)|None)", c, re.M)
    print(f"{f.split(chr(92))[-1]:48s} rev={r.group(1) if r else '?':22s} down={d.group(1) if d else 'None'}")

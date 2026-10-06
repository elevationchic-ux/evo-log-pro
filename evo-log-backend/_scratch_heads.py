import re, glob, os
revs = {}
downs = set()
for f in glob.glob('migrations/versions/*.py'):
    txt = open(f, encoding='utf-8').read()
    m = re.search(r"^revision\s*=\s*['\"]([^'\"]+)", txt, re.M)
    d = re.search(r"^down_revision\s*=\s*['\"]([^'\"]+)", txt, re.M)
    if not m:
        continue
    revs[m.group(1)] = os.path.basename(f)
    if d:
        downs.add(d.group(1))
heads = [r for r in revs if r not in downs]
print('HEADS:', [(h, revs[h]) for h in heads])

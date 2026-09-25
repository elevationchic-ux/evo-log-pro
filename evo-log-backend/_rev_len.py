import re, glob, os

rows = []
for f in sorted(glob.glob('migrations/versions/*.py')):
    txt = open(f, encoding='utf-8').read()
    m = re.search(r"^revision\s*=\s*['\"]([^'\"]+)", txt, re.M)
    if m:
        rev = m.group(1)
        rows.append((len(rev), rev, os.path.basename(f)))

over = [r for r in rows if r[0] > 32]
print("total revisions:", len(rows))
print("max len:", max((r[0] for r in rows), default=0))
print(">32 chars (would break VARCHAR(32) on Postgres):")
for length, rev, fn in sorted(over):
    print(f"  {length:3d}  {rev}")

import glob, io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
rows = []
for f in glob.glob(r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-backend\migrations\versions\*.py"):
    t = io.open(f, encoding="utf-8", errors="ignore").read()
    r = re.search(r"^revision(?::\s*[^=]*)?\s*=\s*['\"]([^'\"]+)", t, re.M)
    d = re.search(r"^down_revision(?::\s*[^=]*)?\s*=\s*['\"]([^'\"]+)", t, re.M)
    if r:
        rows.append((r.group(1), d.group(1) if d else "NONE"))
rows.sort()
for rev, down in rows:
    if rev.split("_")[0] in ("100", "101", "102", "103", "104", "105", "106", "107"):
        print(f"{rev:40s} <- {down}")

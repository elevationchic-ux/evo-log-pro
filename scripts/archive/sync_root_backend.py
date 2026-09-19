import os, shutil, sys

sys.stdout.reconfigure(encoding='utf-8')

src = 'ERP-logistique-/evo-log-backend'
dst = 'evo-log-backend'

print(f"Syncing {src} -> {dst}...")

def ignore_patterns(d, files):
    ignored = []
    for f in files:
        if f in ['__pycache__', '.pytest_cache', '.git']:
            ignored.append(f)
    return ignored

if os.path.exists(dst):
    shutil.rmtree(dst)

shutil.copytree(src, dst, ignore=ignore_patterns)
print(f"Synced {dst} successfully! Total files: {len(os.listdir(dst))}")

import os, sys

sys.stdout.reconfigure(encoding='utf-8')

count = 0
for root, dirs, files in os.walk('evo-log-frontend/src'):
    for f in files:
        if f.endswith('.tsx') or f.endswith('.ts'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
            changed = False
            for old_pat in ["@/components/ui/card'", '@/components/ui/card"']:
                new_pat = old_pat.replace("/card", "/Card")
                if old_pat in content:
                    content = content.replace(old_pat, new_pat)
                    changed = True
            if changed:
                with open(fpath, 'w', encoding='utf-8') as fp:
                    fp.write(content)
                count += 1
                print(f"Updated: {fpath}")

print(f"Total files updated: {count}")

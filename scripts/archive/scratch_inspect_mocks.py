import os
import re
import json

frontend_dir = r"c:\Users\chris\Documents\Projet\Documents\evo-log\evo-log-frontend\src"
backend_dir = r"c:\Users\chris\Documents\Projet\Documents\evo-log\evo-log-backend\app"

mock_patterns = [
    r'\bmock[A-Za-z0-9_]*\b',
    r'\bMOCK_[A-Za-z0-9_]*\b',
    r'\bfake[A-Za-z0-9_]*\b',
    r'\bdummy[A-Za-z0-9_]*\b',
    r'\bplaceholder router\b',
    r'router\s*-\s*placeholder',
    r'\bSAMPLE_[A-Za-z0-9_]*\b'
]

findings = []

for base_dir in [frontend_dir, backend_dir]:
    for root, dirs, files in os.walk(base_dir):
        if 'node_modules' in root or '.next' in root or '__pycache__' in root:
            continue
        for f in files:
            if f.endswith(('.tsx', '.ts', '.py')) and not f.endswith('.d.ts'):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                        lines = fp.readlines()
                except Exception:
                    continue
                for idx, line in enumerate(lines):
                    # ignore common false positives like html placeholder="..." or lucide icons
                    if 'placeholder="' in line or "placeholder='" in line or 'placeholder:text' in line or 'placeholder-slate' in line:
                        continue
                    if 'lucide' in line or 'svg' in line:
                        continue
                    for pat in mock_patterns:
                        if re.search(pat, line, re.IGNORECASE):
                            findings.append({
                                'file': path.replace('\\', '/'),
                                'line': idx + 1,
                                'content': line.strip()[:140]
                            })
                            break

print(f"Total findings: {len(findings)}")
with open(r"c:\Users\chris\Documents\Projet\Documents\evo-log\scratch_all_mock_findings.json", "w", encoding="utf-8") as out:
    json.dump(findings, out, indent=2)

# Group by file
files_map = {}
for item in findings:
    f = item['file']
    files_map[f] = files_map.get(f, 0) + 1

sorted_files = sorted(files_map.items(), key=lambda x: x[1], reverse=True)
print("\nTop files with mock/dummy/placeholder occurrences:")
for f, count in sorted_files[:35]:
    print(f"  {f} ({count} occurrences)")

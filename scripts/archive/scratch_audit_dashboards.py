import os
import re
import json

app_pages_dir = r"c:\Users\chris\Documents\Projet\Documents\evo-log\evo-log-frontend\src\app\(app)"

page_reports = []

for root, dirs, files in os.walk(app_pages_dir):
    for f in files:
        if f == 'page.tsx':
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, app_pages_dir).replace('\\', '/')
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
            
            # Check for API fetching indicators
            has_api_call = bool(re.search(r'(apiClient|fetch\(|useQuery|useMutation|\b\w+API\.)', content))
            has_use_effect = bool(re.search(r'\buseEffect\b', content))
            has_hardcoded_arrays = bool(re.search(r'const\s+\[?\w+\]?\s*=\s*useState\s*<\s*\w+\[\]\s*>\s*\(\s*\[\s*\{', content)) or bool(re.search(r'const\s+[A-Z0-9_]+\s*:\s*\w+\[\]\s*=\s*\[\s*\{', content))
            
            # Check if there are hardcoded static data constants
            has_static_data = bool(re.search(r'const\s+(INITIAL_|DEFAULT_|STATIC_|MOCK_|[A-Z_]+_DATA)\s*=', content))
            
            page_reports.append({
                'page': rel_path,
                'has_api_call': has_api_call,
                'has_use_effect': has_use_effect,
                'has_hardcoded_arrays': has_hardcoded_arrays,
                'has_static_data': has_static_data,
                'size_lines': len(content.splitlines())
            })

no_api_pages = [p for p in page_reports if not p['has_api_call']]
print(f"Total pages in (app): {len(page_reports)}")
print(f"Pages WITHOUT any API call ({len(no_api_pages)}):")
for p in no_api_pages:
    print(f"  - {p['page']} ({p['size_lines']} lines)")

print(f"\nPages WITH API calls: {len(page_reports) - len(no_api_pages)}")

with open(r"c:\Users\chris\Documents\Projet\Documents\evo-log\scratch_pages_api_audit.json", "w", encoding="utf-8") as out:
    json.dump(page_reports, out, indent=2)

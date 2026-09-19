import os, sys

sys.stdout.reconfigure(encoding='utf-8')

for dc in ['docker-compose.yml', 'ERP-logistique-/docker-compose.yml', 'temp-repo/docker-compose.yml']:
    if os.path.exists(dc):
        print(f"=== {dc} ===")
        with open(dc, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'build:' in line or 'context:' in line or 'container_name:' in line or 'ports:' in line:
                    print(" ", line.strip())

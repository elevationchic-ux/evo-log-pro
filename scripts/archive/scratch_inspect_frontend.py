import os
import re

frontend_files = [
    "src/app/(app)/admin-saas/page.tsx",
    "src/app/(app)/admin-saas/tenants/page.tsx",
    "src/app/(app)/admin-saas/roles-permissions/page.tsx",
    "src/app/(app)/admin-saas/users/page.tsx",
    "src/app/(app)/admin-tenant/multi-tenant/page.tsx",
    "src/app/(app)/admin-tenant/audit-logs/page.tsx",
    "src/app/(app)/admin-tenant/users-rbac/page.tsx",
    "src/app/(app)/admin-tenant/system-admin/page.tsx",
    "src/app/(app)/admin/user-management/page.tsx",
    "src/app/(app)/admin/audit/page.tsx",
    "src/app/(app)/security/page.tsx",
    "src/app/(app)/security/notification-settings-escalation/page.tsx"
]

base = "evo-log-frontend"
for f in frontend_files:
    p = os.path.join(base, f)
    if os.path.exists(p):
        content = open(p, encoding="utf-8").read()
        fetches = re.findall(r'fetch\([`"\']([^`"\']*)', content)
        # also find const MOCK or hardcoded arrays
        mocks = re.findall(r'(?:const|let)\s+([A-Z0-9_]*(?:MOCK|DATA|SAMPLE|INITIAL)[A-Z0-9_]*)\s*=', content)
        print(f"=== {f} ({len(content.splitlines())} lines) ===")
        print(f"  Fetches: {fetches}")
        if mocks:
            print(f"  Mocks/Static: {mocks}")
    else:
        print(f"NOT FOUND: {p}")

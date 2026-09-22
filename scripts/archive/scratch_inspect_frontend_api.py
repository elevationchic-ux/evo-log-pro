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
    "src/app/(app)/admin-tenant/dashboard/page.tsx",
    "src/app/(app)/admin-tenant/global-settings/page.tsx",
    "src/app/(app)/admin/user-management/page.tsx",
    "src/app/(app)/admin/audit/page.tsx",
    "src/app/(app)/admin/subscriptions/page.tsx",
    "src/app/(app)/admin/companies/page.tsx",
    "src/app/(app)/admin/role-assignment/page.tsx",
    "src/app/(app)/security/page.tsx",
    "src/app/(app)/security/notification-settings-escalation/page.tsx",
    "src/app/(app)/security/alert-monitoring/page.tsx"
]

base = "evo-log-frontend"
for f in frontend_files:
    p = os.path.join(base, f)
    if os.path.exists(p):
        content = open(p, encoding="utf-8").read()
        api_calls = re.findall(r'(?:apiClient|adminAPI|authAPI)\.[a-zA-Z]+\([`"\']?([^`"\')\s]*)', content)
        fetches = re.findall(r'fetch\([`"\']([^`"\']*)', content)
        all_calls = list(set(api_calls + fetches))
        has_mock = "MOCK" in content or "INITIAL_" in content or "SAMPLE_" in content
        print(f"=== {f} ({len(content.splitlines())} lines) ===")
        print(f"  API Calls: {all_calls}")
        if has_mock:
            print(f"  Has Mock/Static keyword")
    else:
        print(f"NOT FOUND: {p}")

import os, shutil, sys

sys.stdout.reconfigure(encoding='utf-8')

src_fe = 'temp-repo/kamlog-frontend/src'
dst_fe = 'evo-log-frontend/src'

files_to_copy = [
    'lib/tcodes.ts',
    'lib/export.ts',
    'lib/offline/db.ts',
    'lib/offline/sync_manager.ts',
    'hooks/use-mobile.ts',
    'stores/authStore.ts',
    'stores/alertStores.ts',
    'i18n/dictionary.ts',
    'app/(app)/admin/security/mfa/page.tsx',
    'app/(app)/audit/dashboard/health/page.tsx',
    'app/(app)/bi/page.tsx',
    'app/(app)/bi/margins/page.tsx',
    'app/(app)/rh/conges/page.tsx',
    'app/(app)/transport/drivers/[id]/page.tsx',
    'app/(auth)/mfa/page.tsx',
    'app/(auth)/register/page.tsx',
    'app/(auth)/reset-password/page.tsx',
    'app/(auth)/session-expired/page.tsx'
]

print("=== Copying Frontend Modules ===")
for rel in files_to_copy:
    s = os.path.join(src_fe, rel)
    d = os.path.join(dst_fe, rel)
    if os.path.exists(s):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        print(f"Copied {rel}")
    else:
        print(f"NOT FOUND: {s}")

print("=== Copy Complete ===")

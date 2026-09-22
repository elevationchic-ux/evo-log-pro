import os, shutil, sys

sys.stdout.reconfigure(encoding='utf-8')

src_be = 'temp-repo/kamlog-backend'
dst_be = 'ERP-logistique-/evo-log-backend'

print("=== Starting Backend Fusion ===")

# 1. Models
for m in ['new_k_modules.py', 'organization.py']:
    src = os.path.join(src_be, 'app', 'models', m)
    dst = os.path.join(dst_be, 'app', 'models', m)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied model: {m}")

# 2. Routers v1
v1_routers = [
    'ai_assistant.py', 'ai_predictive.py', 'bi_advanced.py', 'crm.py',
    'digital_twin.py', 'e_invoicing.py', 'fixed_assets.py', 'freight_exchange.py',
    'gamification.py', 'ged.py', 'marketplace.py', 'new_k_modules.py',
    'ohada_accounting.py', 'onboarding.py', 'privacy.py', 'projects.py',
    'sectoral_features.py', 'status.py', 'subscription.py', 'superadmin.py'
]

for r in v1_routers:
    src = os.path.join(src_be, 'app', 'routers', 'v1', r)
    dst = os.path.join(dst_be, 'app', 'routers', 'v1', r)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied router v1: {r}")

# Root routers
for r in ['blockchain.py', 'collaboration.py', 'webhook_whatsapp.py']:
    src = os.path.join(src_be, 'app', 'routers', r)
    dst = os.path.join(dst_be, 'app', 'routers', r)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied root router: {r}")

# 3. Services & Utils
src_sms = os.path.join(src_be, 'app', 'services', 'sms_fallback.py')
dst_sms = os.path.join(dst_be, 'app', 'services', 'sms_fallback.py')
if os.path.exists(src_sms):
    shutil.copy2(src_sms, dst_sms)
    print("Copied service: sms_fallback.py")

src_sec = os.path.join(src_be, 'app', 'utils', 'security_vault.py')
dst_sec = os.path.join(dst_be, 'app', 'utils', 'security_vault.py')
if os.path.exists(src_sec):
    shutil.copy2(src_sec, dst_sec)
    print("Copied util: security_vault.py")

# Also copy any missing utils
for u in ['cache.py', 'lockout.py', 'metering.py', 'retry.py']:
    src_u = os.path.join(src_be, 'app', 'utils', u)
    dst_u = os.path.join(dst_be, 'app', 'utils', u)
    if os.path.exists(src_u) and not os.path.exists(dst_u):
        shutil.copy2(src_u, dst_u)
        print(f"Copied util: {u}")

print("=== Backend Files Copied Successfully ===")

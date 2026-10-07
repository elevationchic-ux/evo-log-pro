from pathlib import Path
p = Path("evo-log-backend/app/models/__init__.py")
t = p.read_text(encoding="utf-8")
old = '''# <expansion:admin>
try:
    from app.models.admin_deep import (
        FeatureFlag,
        ApiQuota,
        WhiteLabel,
        TenantOnboarding,
        TenantApiKey,
        TenantWebhook,
        DataMigration,
        PlatformTicket,
        BillingEntry,
        UsageAnalytics,
        UptimeRecord,
    )
    __all__.extend(["FeatureFlag", "ApiQuota", "WhiteLabel", "TenantOnboarding", "TenantApiKey", "TenantWebhook", "DataMigration", "PlatformTicket", "BillingEntry", "UsageAnalytics", "UptimeRecord"])
except Exception:
    pass
# </expansion:admin>'''
new = '''# <expansion:admin>
from app.models.admin_deep import (
    FeatureFlag, ApiQuota, WhiteLabel, TenantOnboarding, TenantApiKey,
    TenantWebhook, DataMigration, PlatformTicket, BillingEntry, UsageAnalytics, UptimeRecord,
)
__all__.extend(["FeatureFlag", "ApiQuota", "WhiteLabel", "TenantOnboarding", "TenantApiKey", "TenantWebhook", "DataMigration", "PlatformTicket", "BillingEntry", "UsageAnalytics", "UptimeRecord"])
# </expansion:admin>'''
assert old in t, "marker block not found"
t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("unwrapped")

import re

txt = open("evo-log-frontend/src/config/navigationRegistry.ts", encoding="utf-8").read()
for p in [
    "/transit-douane/trader-registration",
    "/magasin-stock/consignment-stock",
    "/comptabilite-ohada/treasury-accounts",
    "/finance-ohada/credit-facilities",
    "/parc-vehicules/registration-tracking",
    "/superadmin-cadc/partner-network",
]:
    needle = 'path: "%s"' % p
    idxs = [m.start() for m in re.finditer(re.escape(needle), txt)]
    print(p, idxs)
    for i in idxs:
        line_no = txt.count("\n", 0, i) + 1
        print("  line", line_no)
        seg = txt[max(0, i - 150):i + 200]
        print("  " + seg.replace("\n", "\n  "))
    print("---")

import re
p = r"evo-log-frontend\node_modules\lucide-react\dist\lucide-react.d.ts"
try:
    t = open(p, encoding="utf-8", errors="replace").read()
except FileNotFoundError:
    import os
    for root, dirs, files in os.walk(r"evo-log-frontend\node_modules\lucide-react"):
        for f in files:
            if f.endswith(".d.ts"):
                print("found:", os.path.join(root, f))
    raise SystemExit

wanted = ["Pipeline","Snowflake","HardHat","Syringe","GitCommitHorizontal","Weight","Workflow","Link","ScanLine","Route","Construction","CircleDot","Ruler","Shuffle","ArrowDownUp","CalendarRange","Container","Landmark","Tag","BarChart3","AlertTriangle","Anchor","Ship","Upload","Radar","Activity","Gauge","Layers","Boxes","Package","Building2","Map","User","CheckCircle","Timer","Lock","Truck","Calculator","AlertOctagon","RefreshCcw","ClipboardList","FileSignature","Shield","Thermometer","LayoutDashboard","Wrench","Database","FileText","Zap","Map"]

# As of newer lucide-react versions, exports look like:
#   declare const Pipeline: lucide-react__Icon;  or
#   export { Pipeline, ... }
found = set(re.findall(r'\b([A-Z][A-Za-z0-9]+)\b', t))
missing = [w for w in wanted if w not in found]
print("MISSING:", missing)
print("total exports scanned:", len(found))

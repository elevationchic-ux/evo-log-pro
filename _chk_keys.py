import re,io
s=io.open(r"evo-log-frontend\src\config\domainLoadingConfig.ts",encoding="utf-8").read()
keys=re.findall(r"^  '([\w-]+)': \{",s,re.M)
print("KEYS:",keys)
idx=s.index("export function")
res=s[idx:]
refs=sorted(set(re.findall(r"DOMAIN_LOADING_CONFIGS\['([\w-]+)'\]",res)))
print("REFERENCED:",refs)
print("MISSING:",[r for r in refs if r not in keys])
print("UNUSED:",[k for k in keys if k not in refs and k!="comptabilite-ohada"])
g=re.findall(r"^  '([\w-]+)': \{",s,re.M)
print("gradientBg used in consumers?")

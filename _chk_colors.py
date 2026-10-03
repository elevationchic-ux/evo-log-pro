import re,io
p=r"evo-log-frontend\src\config\domainLoadingConfig.ts"
s=io.open(p,encoding="utf-8").read()
pal=io.open(r"evo-log-frontend\src\config\modulePalette.ts",encoding="utf-8").read()
hexes=dict((m.group(1),m.group(2).upper()) for m in re.finditer(r"^\s{2}'?([\w-]+)'?:\s*\{\s*\n\s*hex:\s*'(#[0-9A-Fa-f]{6})'",pal,re.M))
alias=dict((m.group(1),m.group(2)) for m in re.finditer(r"^\s+'?([\w-]+)'?:\s*'([\w-]+)',",pal[pal.index("LEGACY_ALIAS"):],re.M))
blocks=re.findall(r"^\s{2}'([\w-]+)':\s*\{([\s\S]*?)\n\s{2}\},\s*$",s,re.M)
out=[]
for k,body in blocks:
    m=re.search(r"primaryColor:\s*'(#[0-9A-Fa-f]{6})'",body)
    if not m: continue
    key=k.replace("Domain","") if False else k
    cand=[key]
    if key.endswith("-domain"): cand.append(key[:-7])
    a=alias.get(cand[0])
    if a: cand.append(a)
    hexp=None
    for c in cand:
        if c in hexes: hexp=hexes[c];break
    status="OK" if hexp and hexp.upper()==m.group(1).upper() else ("MISSING-IN-PAL" if hexp is None else "MISMATCH")
    out.append((k,m.group(1).upper(),str(hexp),status))
for r in out: print("%-34s %-9s %-9s %s"%r)
print("blocks:",len(blocks))

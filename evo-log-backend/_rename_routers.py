import re, pathlib

renames = {
    "comptabilite_deep.py": ("compta.", "comptabilite."),
    "finance_deep.py": ("finance.", "tresorerie."),
    "port_deep.py": ("port_ops.", "port."),
}
root = pathlib.Path("app/routers/v1")
for fn, (old, new) in renames.items():
    p = root / fn
    src = p.read_text(encoding="utf-8")
    # Ne toucher QUE les appels require_perm("prefix....")
    pat = re.compile(r'(require_perm\(\s*")' + re.escape(old))
    n = len(pat.findall(src))
    dst = pat.sub(r"\g<1>" + new, src)
    # sanity: aucun residu du préfixe invente dans un require_perm
    resid = len(re.findall(r'require_perm\(\s*"' + re.escape(old), dst))
    p.write_text(dst, encoding="utf-8")
    print(f"{fn}: replaced {n}, residual {resid}")

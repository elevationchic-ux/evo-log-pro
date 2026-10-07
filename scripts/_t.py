from pathlib import Path
p = Path("scripts/manifests/all_modules.py")
t = p.read_text(encoding="utf-8")
t = t.replace('"HandCoins"', '"DollarSign"')
t = t.replace('"Vault"', '"Lock"')
t = t.replace('"IdCard"', '"Contact"')
p.write_text(t, encoding="utf-8")
print("done")

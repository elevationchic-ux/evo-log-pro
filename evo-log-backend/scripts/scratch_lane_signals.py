import json

d = json.load(open("_fidelite_champs.json", encoding="utf-8"))
mine = [
    x for x in d
    if any(k in str(x.get("fichier", "")).replace("\\", "/") for k in ("magasin", "transport"))
    and "portail" not in str(x.get("fichier", ""))
]
print("total", len(d), "| lane magasin+transport", len(mine))
for x in mine:
    print(json.dumps(x, ensure_ascii=False))

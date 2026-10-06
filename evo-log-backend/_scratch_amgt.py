import json, re, pathlib
paths = json.loads(pathlib.Path("_openapi_paths.json").read_text(encoding="utf-8"))

def norm(p):
    return re.sub(r"\{[^}]+\}", "{p}", p).rstrip("/")

route_set = {norm(p) for p in paths}

subs = """autorisations
autorisations/{p}
autorisations/{p}/depot
concessions
concessions/{p}
concessions/{p}/obligations
concessions/{p}/reversaison
dragage
dragage/{p}
dragage/{p}/autorisation-rejet
dragage/{p}/bathymetrie
infrastructures
infrastructures/{p}
infrastructures/{p}/inspection
marches
marches/{p}
marches/{p}/attribution
marches/{p}/reception
marches/{p}/soumission-colife
nomenclatures
places
places/{p}
programmation
programmation/{p}
programmation/{p}/inscription-pip
programmation/{p}/notification-minfi
programmation/{p}/visa-controle-financier
programmation/{p}/visa-maturite
projets
projets/{p}
projets/{p}/avancement""".splitlines()

base = "/api/v1/amenagement-portuaire"
miss = []
for s in subs:
    full = norm(f"{base}/{s}")
    if full not in route_set:
        miss.append(full)
print("amenagement sub-calls:", len(subs), "MISSING:", len(miss))
for m in miss:
    print("  MISS", m)

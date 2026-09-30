import re, json, os

REG = os.path.join('evo-log-frontend', 'src', 'config', 'navigationRegistry.ts')
txt = open(REG, encoding='utf-8').read()

# clés de module de NIVEAU 1 = `key: '...'` (les subModules n'ont pas de `key:`)
keys = re.findall(r"""\n\s{4}key:\s*['"]([^'"]+)['"]""", txt)
print("MODULES NIVEAU-1 (", len(keys), ") :", keys)

# paths des subModules
subpaths = re.findall(r"path:\s*['\"`]([^'\"`]+)['\"`]", txt)
print("chemins references total:", len(set(subpaths)))

# Quels moduleKey de niveau-1 existent pour servir de cibles d'augmentation
have = set(keys)
want = ['dashboard','port-operations','transit-douane','transport-flotte','magasin-stock',
        'comptabilite-ohada','finance-ohada','parc-vehicules','rh-personnel','qhse-securite',
        'client-b2b','reports-bi','admin-saas','superadmin-cadc','admin-tenant','departement',
        'master-data','rh','chat','bi','security']
print("cibles presentes :", [w for w in want if w in have])
print("cibles ABSENTES  :", [w for w in want if w not in have])

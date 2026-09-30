import os, glob

APP = os.path.join('evo-log-frontend', 'src', 'app', '(app)')


def pages_of(root):
    out = []
    for fp in glob.glob(os.path.join(APP, root, '**', 'page.tsx'), recursive=True):
        rel = os.path.relpath(fp, APP).replace('\\', '/')
        rel = os.path.dirname(rel)
        parts = [s for s in rel.split('/') if s and not s.startswith('(')]
        u = '/' + '/'.join(parts)
        out.append((u, os.path.getsize(fp) // 1024))
    return sorted(out)


roots = ['acconage', 'acconage-avance', 'transit-avance', 'transport-avance',
         'magasin-avance', 'magasin-douane', 'maintenance', 'maintenance-gmao',
         'master-data', 'client-portal', 'portail-b2b', 'company', 'procurement',
         'purchase', 'cotations', 'auto-invoicing', 'paiement-local',
         'fiscalite-cameroun', 'integration-cameroun', 'compliance', 'tracking',
         'gps-tracking', 'fuel-guard', 'mobile-chauffeur', 'shift-planning',
         'container-lifecycle', 'bill-of-loading', 'real-customs', 'port-incidents',
         'port-performance', 'port-pricing', 'reports', 'reporting', 'goods',
         'transactions', 'documents', 'alerts', 'notifications', 'support',
         'integration', 'acquisition', 'reception-mag3', 'removal-slip',
         'transport-international', 'chauffeur']

for r in roots:
    ps = pages_of(r)
    if not ps:
        print(f'[{r}]  (AUCUNE PAGE)')
        continue
    land = [u for u, _ in ps if u == '/' + r]
    tag = land[0] if land else '(pas de page racine)'
    lst = ', '.join(f'{u}({k}K)' for u, k in ps[:8])
    print(f'[{r}] pages={len(ps)} landing={tag}')
    print(f'      {lst}')

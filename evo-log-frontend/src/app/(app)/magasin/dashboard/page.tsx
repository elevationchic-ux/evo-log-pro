'use client';

import { KPICard, StatCard, Card, CardHeader, CardContent, DataTable, StatusBadge, StatusBadges, PageHeader } from '@/components/ui';

export default function MagasinDashboardPage() {
  const receptions = [
    { id: 'REC-2024-0847', reference: 'BL-DLA-4521', supplier: 'Globex Cameroon', items: 147, status: 'RÉCEPTIONNÉ', date: '24/08/2024', warehouse: 'Zone A' },
    { id: 'REC-2024-0848', reference: 'BL-DLA-4522', supplier: 'SABC SARL', items: 89, status: 'EN_COURS', date: '24/08/2024', warehouse: 'Zone B' },
    { id: 'REC-2024-0849', reference: 'BL-DLA-4523', supplier: 'Alucam', items: 234, status: 'VALIDÉ', date: '23/08/2024', warehouse: 'Zone A' },
    { id: 'REC-2024-0850', reference: 'BL-DLA-4524', supplier: 'MTN Cameroon', items: 56, status: 'EN_ATTENTE', date: '23/08/2024', warehouse: 'Zone C' },
  ];

  const columns = [
    { key: 'id', header: 'N° Réception', sortable: true },
    { key: 'reference', header: 'Référence BL', sortable: true },
    { key: 'supplier', header: 'Fournisseur', sortable: true },
    { key: 'items', header: 'Colis', sortable: true },
    { key: 'status', header: 'Statut', render: (item: any) => StatusBadges.Magasin[item.status] || <StatusBadge label={item.status} /> },
    { key: 'date', header: 'Date', sortable: true },
    { key: 'warehouse', header: 'Zone' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="📦 K-Magasin WMS"
        description="Gestion d'entrepôt, réception, stockage, préparation commandes"
        breadcrumbs={[{ label: 'Magasin' }]}
        actions={
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nouvelle Réception
          </button>
        }
      />

      <div className="grid gap-4 md:grid-cols-4">
        <KPICard title="Articles en Stock" value="12,847" subtitle="Articles différents" icon={<span className="material-symbols-outlined text-2xl">inventory_2</span>} color="primary" />
        <KPICard title="Mouvements Jour" value="247" subtitle="Entrées/Sorties" icon={<span className="material-symbols-outlined text-2xl">swap_horiz</span>} color="emerald" trend={{ value: 18, isPositive: true }} />
        <KPICard title="Taux de Service" value="96%" subtitle="OTIF" icon={<span className="material-symbols-outlined text-2xl">verified</span>} color="blue" trend={{ value: 2, isPositive: true }} />
        <KPICard title="Alertes Stock" value="23" subtitle="Seuil bas" icon={<span className="material-symbols-outlined text-2xl">warning</span>} color="amber" trend={{ value: 5, isPositive: false }} />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Réceptions Jour" value="12" change={8} color="success" icon={<span className="material-symbols-outlined">move_to_inbox</span>} />
        <StatCard label="Expéditions Jour" value="18" change={12} color="primary" icon={<span className="material-symbols-outlined">outbox</span>} />
        <StatCard label="Taux Occupation" value="78%" change={3} color="warning" icon={<span className="material-symbols-outlined">pie_chart</span>} />
        <StatCard label="Précision Picking" value="99.2%" change={0.5} color="info" icon={<span className="material-symbols-outlined">checklist</span>} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader title="Réceptions du Jour" subtitle="Historique des dernières réceptions" icon={<span className="material-symbols-outlined text-xl">inbox</span>} action={<button className="text-sm text-primary hover:underline">Voir tout</button>} />
            <CardContent>
              <DataTable data={receptions} columns={columns} keyField="id" />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Occupation Entrepôt" icon={<span className="material-symbols-outlined text-xl">warehouse</span>} />
            <CardContent>
              <div className="space-y-4">
                {['Zone A (Conteneurs)', 'Zone B (Palette)', 'Zone C (Marchandises)', 'Zone D (Dangerux)'].map((zone, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1"><span>{zone}</span><span className="font-medium">{65 + i * 10}%</span></div>
                    <div className="h-2 bg-surface-container rounded-full overflow-hidden">
                      <div className="h-full bg-primary rounded-full" style={{ width: `${65 + i * 10}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="Alertes Importantes" icon={<span className="material-symbols-outlined text-xl text-red-500">notifications</span>} />
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 rounded border border-red-200 bg-red-500/5"><p className="font-medium text-sm">Stock critique</p><p className="text-xs text-on-surface-variant">Pièces détachées X-450 - 3 unités</p></div>
                <div className="p-3 rounded border border-amber-200 bg-amber-500/5"><p className="font-medium text-sm"> Péremption proche</p><p className="text-xs text-on-surface-variant">12 articles < 30 jours</p></div>
                <div className="p-3 rounded border border-blue-200 bg-blue-500/5"><p className="font-medium text-sm">Réception prévue</p><p className="text-xs text-on-surface-variant">SABC - 14h00</p></div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
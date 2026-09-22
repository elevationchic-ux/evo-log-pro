'use client';

import { KPICard, StatCard, Card, CardHeader, CardContent, DataTable, StatusBadge, StatusBadges, PageHeader } from '@/components/ui';

export default function TransportFlottePage() {
  const vehicles: Array<any> = [];

  const columns = [
    { key: 'id', header: 'Immatriculation', sortable: true },
    { key: 'type', header: 'Type', sortable: true },
    { key: 'brand', header: 'Marque' },
    { key: 'model', header: 'Modèle' },
    { key: 'year', header: 'Année', sortable: true },
    { key: 'status', header: 'Statut', render: (item: any) => <StatusBadge label={item.status} variant={item.status === 'ACTIF' ? 'success' : item.status === 'MAINTENANCE' ? 'warning' : 'default'} /> },
    { key: 'mileage', header: 'Kilométrage', sortable: true },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="🚚 Gestion de la Flotte"
        description="Camions, tracteurs, remorques, engins de manutention - Suivi complet parc véhicule"
        breadcrumbs={[{ label: 'Transport', href: '/transport' }, { label: 'Flotte' }]}
        actions={
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">add</span>
            Ajouter Véhicule
          </button>
        }
      />

      <div className="grid gap-4 md:grid-cols-4">
        <KPICard title="Parc Total" value="—" subtitle="Données indisponibles" icon={<span className="material-symbols-outlined text-2xl">directions_car</span>} color="blue" />
        <KPICard title="En Service" value="—" subtitle="Données indisponibles" icon={<span className="material-symbols-outlined text-2xl">check_circle</span>} color="emerald" />
        <KPICard title="En Maintenance" value="—" subtitle="Données indisponibles" icon={<span className="material-symbols-outlined text-2xl">build</span>} color="amber" />
        <KPICard title="Kilométrage Moyen" value="—" subtitle="Données indisponibles" icon={<span className="material-symbols-outlined text-2xl">speed</span>} color="blue" />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Camions 10T" value="34" color="primary" icon={<span className="material-symbols-outlined">local_shipping</span>} />
        <StatCard label="Camions 20T" value="28" color="success" icon={<span className="material-symbols-outlined">local_shipping</span>} />
        <StatCard label="Tracteurs" value="42" color="info" icon={<span className="material-symbols-outlined">agriculture</span>} />
        <StatCard label="Semi-remorques" value="23" color="warning" icon={<span className="material-symbols-outlined">archive</span>} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader title="Inventaire Flotte" subtitle="Tous véhicules enregistrés" icon={<span className="material-symbols-outlined text-xl">inventory_2</span>} action={<button className="text-sm text-primary hover:underline">Exporter</button>} />
            <CardContent>
              <DataTable data={vehicles} columns={columns} keyField="id" onRowClick={(item) => console.log('View:', item.id)} />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Répartition par Statut" icon={<span className="material-symbols-outlined text-xl">pie_chart</span>} />
            <CardContent>
              <div className="space-y-3">
                <div className="rounded-lg bg-slate-500/10 p-3 text-sm text-slate-500">Aucune donnée de flotte persistée disponible.</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="Prochaines Révisions" icon={<span className="material-symbols-outlined text-xl">event</span>} />
            <CardContent>
              <div className="space-y-3">
                <div className="rounded border border-slate-700 bg-slate-500/5 p-3 text-sm text-slate-500">Aucune révision persistée disponible.</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
'use client';

import { KPICard, StatCard, Card, CardHeader, CardContent, DataTable, StatusBadge, StatusBadges, PageHeader } from '@/components/ui';

export default function TransportFlottePage() {
  const vehicles = [
    { id: 'CMR-T-4521', type: 'Camion 20T', brand: 'Mercedes', model: 'Actros', year: 2022, status: 'ACTIF', mileage: '145,200 km', lastMaintenance: '15/08/2024' },
    { id: 'CMR-T-4518', type: 'Tracteur', brand: 'Volvo', model: 'FH16', year: 2021, status: 'ACTIF', mileage: '198,500 km', lastMaintenance: '01/08/2024' },
    { id: 'CMR-T-4532', type: 'Semi-remorque', brand: 'Scania', model: 'R500', year: 2023, status: 'MAINTENANCE', mileage: '45,800 km', lastMaintenance: '20/08/2024' },
    { id: 'CMR-T-4509', type: 'Camion 10T', brand: 'Isuzu', model: 'NPR', year: 2020, status: 'ACTIF', mileage: '267,100 km', lastMaintenance: '10/07/2024' },
    { id: 'CMR-T-4545', type: 'Camion 20T', brand: 'MAN', model: 'TGA', year: 2022, status: 'HORS_SERVICE', mileage: '178,900 km', lastMaintenance: '05/06/2024' },
  ];

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
        <KPICard title="Parc Total" value="127" subtitle="Véhicules" icon={<span className="material-symbols-outlined text-2xl">directions_car</span>} color="blue" trend={{ value: 5, isPositive: true }} />
        <KPICard title="En Service" value="89" subtitle="Actifs" icon={<span className="material-symbols-outlined text-2xl">check_circle</span>} color="emerald" />
        <KPICard title="En Maintenance" value="23" subtitle="Atelier" icon={<span className="material-symbols-outlined text-2xl">build</span>} color="amber" />
        <KPICard title="Kilométrage Moyen" value="156K km" subtitle="Par véhicule" icon={<span className="material-symbols-outlined text-2xl">speed</span>} color="blue" />
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
                <div className="flex justify-between items-center p-3 rounded-lg bg-emerald-500/10"><span className="text-sm">Actifs</span><span className="font-bold text-emerald-600">89</span></div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-amber-500/10"><span className="text-sm">En Maintenance</span><span className="font-bold text-amber-600">23</span></div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-slate-500/10"><span className="text-sm">En Attente</span><span className="font-bold text-slate-600">8</span></div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-red-500/10"><span className="text-sm">Hors Service</span><span className="font-bold text-red-600">7</span></div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="Prochaines Révisions" icon={<span className="material-symbols-outlined text-xl">event</span>} />
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 rounded border border-amber-200 bg-amber-500/5"><p className="font-medium">CMR-T-4521</p><p className="text-xs text-on-surface-variant">Révision 150K km - Dans 4,800 km</p></div>
                <div className="p-3 rounded border border-red-200 bg-red-500/5"><p className="font-medium">CMR-T-4509</p><p className="text-xs text-on-surface-variant">Contrôle technique - Expire dans 15j</p></div>
                <div className="p-3 rounded border border-amber-200 bg-amber-500/5"><p className="font-medium">CMR-T-4532</p><p className="text-xs text-on-surface-variant">Vidange - Dans 2,500 km</p></div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
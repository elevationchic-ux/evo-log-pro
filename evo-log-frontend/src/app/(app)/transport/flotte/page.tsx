'use client';

import { useState, useEffect } from 'react';
import { KPICard, StatCard, Card, CardHeader, CardContent, DataTable, StatusBadge, StatusBadges, PageHeader } from '@/components/ui';
import { transportAPI } from '@/lib/api-client';
import { EmptyStates } from '@/components/design-system/EmptyState';

export default function TransportFlottePage() {
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVehicles();
  }, []);

  const loadVehicles = async () => {
    try {
      const res = await transportAPI.getCamions();
      const d = res.data;
      const list = Array.isArray(d) ? d : (d?.items || (Array.isArray(res) ? res : []));
      const transformed = list.map((c: any) => ({
        id: c.immatriculation || c.id,
        type: c.type || 'Camion',
        brand: c.marque || 'N/A',
        model: c.modele || 'N/A',
        year: c.annee || new Date().getFullYear(),
        status: c.statut || 'DISPONIBLE',
        mileage: c.kilometrage ? `${c.kilometrage.toLocaleString()} km` : '0 km',
        lastMaintenance: c.derniere_maintenance || 'N/A'
      }));
      setVehicles(transformed);
    } catch (err) {
      console.error('Error loading vehicles:', err);
      setVehicles([]);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: 'id', header: 'Immatriculation', sortable: true },
    { key: 'type', header: 'Type', sortable: true },
    { key: 'brand', header: 'Marque' },
    { key: 'model', header: 'Modèle' },
    { key: 'year', header: 'Année', sortable: true },
    { key: 'status', header: 'Statut', render: (item: any) => <StatusBadge label={item.status} variant={item.status === 'ACTIF' || item.status === 'DISPONIBLE' ? 'success' : item.status === 'MAINTENANCE' ? 'warning' : 'default'} /> },
    { key: 'mileage', header: 'Kilométrage', sortable: true },
  ];

  const kpis = [
    { title: 'Parc Total', value: vehicles.length.toString(), subtitle: 'Véhicules', icon: <span className="material-symbols-outlined text-2xl">directions_car</span>, color: 'blue' as const },
    { title: 'En Service', value: vehicles.filter(v => v.status === 'ACTIF' || v.status === 'DISPONIBLE').length.toString(), subtitle: 'Actifs', icon: <span className="material-symbols-outlined text-2xl">check_circle</span>, color: 'emerald' as const },
    { title: 'Maintenance', value: vehicles.filter(v => v.status === 'MAINTENANCE').length.toString(), subtitle: 'En atelier', icon: <span className="material-symbols-outlined text-2xl">build</span>, color: 'amber' as const },
    { title: 'Hors Service', value: vehicles.filter(v => v.status === 'HORS_SERVICE').length.toString(), subtitle: 'Indisponibles', icon: <span className="material-symbols-outlined text-2xl">block</span>, color: 'red' as const },
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
        {kpis.map((kpi, i) => (
          <KPICard key={i} title={kpi.title} value={kpi.value} subtitle={kpi.subtitle} icon={kpi.icon} color={kpi.color} />
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Camions 10T" value={vehicles.filter(v => v.type?.includes('10T')).length.toString()} color="primary" icon={<span className="material-symbols-outlined">local_shipping</span>} />
        <StatCard label="Camions 20T" value={vehicles.filter(v => v.type?.includes('20T')).length.toString()} color="success" icon={<span className="material-symbols-outlined">local_shipping</span>} />
        <StatCard label="Tracteurs" value={vehicles.filter(v => v.type?.includes('Tracteur')).length.toString()} color="info" icon={<span className="material-symbols-outlined">agriculture</span>} />
        <StatCard label="Semi-remorques" value={vehicles.filter(v => v.type?.includes('Semi')).length.toString()} color="warning" icon={<span className="material-symbols-outlined">archive</span>} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader title="Inventaire Flotte" subtitle="Tous véhicules enregistrés" icon={<span className="material-symbols-outlined text-xl">inventory_2</span>} action={<button className="text-sm text-primary hover:underline">Exporter</button>} />
            <CardContent>
              {loading ? (
                <div className="p-8 text-center text-slate-400">Chargement...</div>
              ) : vehicles.length === 0 ? (
                <EmptyStates.NoData
                  description="Aucun véhicule enregistré dans la flotte."
                  action={{
                    label: 'Rafraîchir',
                    onClick: loadVehicles
                  }}
                />
              ) : (
                <DataTable data={vehicles} columns={columns} keyField="id" onRowClick={(item) => console.log('View:', item.id)} />
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Répartition par Statut" icon={<span className="material-symbols-outlined text-xl">pie_chart</span>} />
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 rounded-lg bg-emerald-500/10"><span className="text-sm">Actifs</span><span className="font-bold text-emerald-600">{vehicles.filter(v => v.status === 'ACTIF' || v.status === 'DISPONIBLE').length}</span></div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-amber-500/10"><span className="text-sm">En Maintenance</span><span className="font-bold text-amber-600">{vehicles.filter(v => v.status === 'MAINTENANCE').length}</span></div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-slate-500/10"><span className="text-sm">En Attente</span><span className="font-bold text-slate-600">{vehicles.filter(v => v.status === 'EN_ATTENTE').length}</span></div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-red-500/10"><span className="text-sm">Hors Service</span><span className="font-bold text-red-600">{vehicles.filter(v => v.status === 'HORS_SERVICE').length}</span></div>
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
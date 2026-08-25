'use client';

import { KPICard, StatCard, Card, CardHeader, CardContent, DataTable, StatusBadge, StatusBadges, PageHeader } from '@/components/ui';

export default function TransportDispatchPage() {
  const missions = [
    { id: 'DISP-001', client: 'SABC', cargo: 'Marchandises', weight: '12.5T', origin: 'Port Douala', destination: 'Yaoundé', priority: 'HIGH', vehicle: 'CMR-T-4521', driver: 'M. Kamdem' },
    { id: 'DISP-002', client: 'Alucam', cargo: 'Conteneurs', weight: '18.2T', origin: 'Zone Franche', destination: 'Bafoussam', priority: 'MEDIUM', vehicle: 'CMR-T-4518', driver: 'M. Ondoua' },
    { id: 'DISP-003', client: 'MTN Cameroon', cargo: 'Équipements', weight: '8.7T', origin: 'Magasin Central', destination: 'Douala', priority: 'HIGH', vehicle: 'À affecter', driver: 'À affecter' },
    { id: 'DISP-004', client: 'Nexttel', cargo: 'Marchandises', weight: '15.3T', origin: 'Port', destination: 'Garoua', priority: 'LOW', vehicle: 'CMR-T-4532', driver: 'M. Nguimdjeu' },
    { id: 'DISP-005', client: 'Port Authority', cargo: 'Divers', weight: '22.1T', origin: 'Zone Port', destination: 'Kribi', priority: 'MEDIUM', vehicle: 'CMR-T-4509', driver: 'M. Talla' },
  ];

  const columns = [
    { key: 'id', header: 'N° Dispatch', sortable: true },
    { key: 'client', header: 'Client', sortable: true },
    { key: 'cargo', header: 'Cargaison' },
    { key: 'weight', header: 'Poids', sortable: true },
    { key: 'origin', header: 'Origine' },
    { key: 'destination', header: 'Destination' },
    { 
      key: 'priority', 
      header: 'Priorité',
      render: (item: any) => {
        const colors: Record<string, string> = { HIGH: 'error', MEDIUM: 'warning', LOW: 'default' };
        return <StatusBadge label={item.priority} variant={colors[item.priority] as any} icon />;
      }
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="📋 Dispatch & Planification"
        description="Affectation missions, optimisation tournées, planification journaux"
        breadcrumbs={[{ label: 'Transport', href: '/transport' }, { label: 'Dispatch' }]}
        actions={
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nouvelle Planification
          </button>
        }
      />

      <div className="grid gap-4 md:grid-cols-4">
        <KPICard title="Missions à Planifier" value="23" subtitle="Aujourd'hui" icon={<span className="material-symbols-outlined text-2xl">event_note</span>} color="amber" trend={{ value: 15, isPositive: false }} />
        <KPICard title="Véhicules Disponibles" value="38" subtitle="Sur 45" icon={<span className="material-symbols-outlined text-2xl">local_shipping</span>} color="emerald" />
        <KPICard title="Chauffeurs Disponibles" value="12" subtitle="Aujourd'hui" icon={<span className="material-symbols-outlined text-2xl">badge</span>} color="blue" />
        <KPICard title="Taux Occupation" value="87%" subtitle="Objectif: 90%" icon={<span className="material-symbols-outlined text-2xl">pie_chart</span>} color="violet" trend={{ value: 3, isPositive: true }} />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Tonnages Jour" value="142T" change={8} color="primary" icon={<span className="material-symbols-outlined">scale</span>} />
        <StatCard label="Coût/Mission" value="45,000 CFA" change={-5} changeLabel="vs mois dernier" color="success" icon={<span className="material-symbols-outlined">payments</span>} />
        <StatCard label="Distance Totale" value="2,450 km" change={12} color="info" icon={<span className="material-symbols-outlined">straighten</span>} />
        <StatCard label="Retards Aujourd'hui" value="3" change={2} changeLabel="vs hier" color="danger" icon={<span className="material-symbols-outlined">schedule</span>} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader title="Missions à Affecter" subtitle="Priorisation par ordre de priorité" icon={<span className="material-symbols-outlined text-xl">list</span>} />
            <CardContent>
              <DataTable data={missions} columns={columns} keyField="id" onRowClick={(item) => console.log('Assign:', item.id)} />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Disponibilité Véhicules" icon={<span className="material-symbols-outlined text-xl">directions_car</span>} />
            <CardContent>
              <div className="space-y-3">
                {['Camions 10T', 'Camions 20T', 'Tracteurs', 'Semi-remorques'].map((type, i) => (
                  <div key={i} className="flex justify-between items-center p-2 rounded border border-outline">
                    <span className="text-sm">{type}</span>
                    <span className="font-bold text-primary">{5 + i * 2}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="Planification Jour" icon={<span className="material-symbols-outlined text-xl">calendar_today</span>} />
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-on-surface-variant">Matin (6h-12h)</span><span className="font-medium">45 missions</span></div>
                <div className="flex justify-between"><span className="text-on-surface-variant">Après-midi (12h-18h)</span><span className="font-medium">38 missions</span></div>
                <div className="flex justify-between"><span className="text-on-surface-variant">Soir (18h-22h)</span><span className="font-medium">12 missions</span></div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
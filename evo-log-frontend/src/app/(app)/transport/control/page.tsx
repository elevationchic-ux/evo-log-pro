'use client';

import { useState } from 'react';
import { KPICard, StatCard, Card, CardHeader, CardContent, DataTable, StatusBadge, StatusBadges, PageHeader } from '@/components/ui';

export default function TransportControlPage() {
  const [loading, setLoading] = useState(false);

  // Mock data for KPIs
  const kpis = [
    { title: 'Véhicules Actifs', value: '45', subtitle: 'En mission', icon: <span className="material-symbols-outlined text-2xl">local_shipping</span>, color: 'primary' as const, trend: { value: 8, isPositive: true } },
    { title: 'Missions du Jour', value: '128', subtitle: 'Livraisons', icon: <span className="material-symbols-outlined text-2xl">route</span>, color: 'success' as const, trend: { value: 12, isPositive: true } },
    { title: 'Taux Ponctualité', value: '94%', subtitle: 'Objectif: 95%', icon: <span className="material-symbols-outlined text-2xl">schedule</span>, color: 'warning' as const },
    { title: 'Alertes Today', value: '7', subtitle: 'À traiter', icon: <span className="material-symbols-outlined text-2xl">warning</span>, color: 'danger' as const, trend: { value: 3, isPositive: false } },
  ];

  // Mock data for missions table
  const missions = [
    { id: 'TR-2024-0847', vehicle: 'CMR-T-4521', driver: 'M. Kamdem', client: 'SABC', origin: 'Port Douala', destination: 'Yaoundé', status: 'EN_ROUTE', eta: '3h15', progress: 65 },
    { id: 'TR-2024-0848', vehicle: 'CMR-T-4518', driver: 'M. Ondoua', client: 'Alucam', origin: 'Magasin A', destination: 'Bafoussam', status: 'CHARGEMENT', eta: 'En cours', progress: 20 },
    { id: 'TR-2024-0849', vehicle: 'CMR-T-4532', driver: 'M. Nguimdjeu', client: 'Port Authority', origin: 'Zone Port', destination: 'Kribi', status: 'LIVRÉ', eta: 'Terminé', progress: 100 },
    { id: 'TR-2024-0850', vehicle: 'CMR-T-4509', driver: 'M. Talla', client: 'MTN Cameroon', origin: 'Entrepôt', destination: 'Douala', status: 'ATTENTE', eta: '14:00', progress: 0 },
    { id: 'TR-2024-0851', vehicle: 'CMR-T-4525', driver: 'M. Fouda', client: 'Nexttel', origin: 'Port', destination: 'Garoua', status: 'EN_ROUTE', eta: '8h30', progress: 45 },
  ];

  const columns = [
    { key: 'id', header: 'N° Mission', sortable: true },
    { key: 'vehicle', header: 'Véhicule', sortable: true },
    { key: 'driver', header: 'Chauffeur', sortable: true },
    { key: 'client', header: 'Client', sortable: true },
    { key: 'origin', header: 'Origine' },
    { key: 'destination', header: 'Destination' },
    { 
      key: 'status', 
      header: 'Statut',
      render: (item: any) => {
        const statusMap: Record<string, any> = {
          EN_ROUTE: StatusBadges.Transport.EN_ROUTE,
          CHARGEMENT: StatusBadges.Transport.CHARGEMENT,
          LIVRÉ: StatusBadges.Transport.LIVRÉ,
          ATTENTE: StatusBadges.Transport.ATTENTE,
        };
        return statusMap[item.status] || <StatusBadge label={item.status} />;
      }
    },
    { key: 'eta', header: 'ETA', sortable: true },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="🚛 Control Tower Transport"
        description="Centre de contrôle transport temps réel - Suivi des missions et fleet management"
        breadcrumbs={[
          { label: 'Transport', href: '/transport' },
          { label: 'Control Tower' }
        ]}
        actions={
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nouvelle Mission
          </button>
        }
      />

      {/* KPIs Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi, index) => (
          <KPICard key={index} {...kpi} loading={loading} />
        ))}
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Camions en Service" value="42" change={5} color="primary" icon={<span className="material-symbols-outlined">local_shipping</span>} />
        <StatCard label="Chauffeurs Actifs" value="38" change={2} color="success" icon={<span className="material-symbols-outlined">person</span>} />
        <StatCard label="Kilomètres Jour" value="2,847 km" change={15} color="info" icon={<span className="material-symbols-outlined">speed</span>} />
        <StatCard label="Consommation Moyenne" value="32.5 L/100km" change={-3} changeLabel="vs cible" color="warning" icon={<span className="material-symbols-outlined">local_gas_station</span>} />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Missions Table */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader 
              title="Missions en Cours" 
              subtitle="5 dernières missions"
              icon={<span className="material-symbols-outlined text-xl">route</span>}
              action={
                <button className="text-sm text-primary hover:underline">Voir tout</button>
              }
            />
            <CardContent>
              <DataTable 
                data={missions} 
                columns={columns} 
                keyField="id"
                onRowClick={(item) => console.log('Navigate to mission:', item.id)}
              />
            </CardContent>
          </Card>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Fleet Status */}
          <Card>
            <CardHeader title="État de la Flotte" icon={<span className="material-symbols-outlined text-xl">directions_car</span>} />
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 rounded-lg bg-emerald-500/10">
                  <span className="text-sm text-on-surface">Disponibles</span>
                  <span className="font-bold text-emerald-600">42</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-amber-500/10">
                  <span className="text-sm text-on-surface">En Mission</span>
                  <span className="font-bold text-amber-600">38</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-red-500/10">
                  <span className="text-sm text-on-surface">En Maintenance</span>
                  <span className="font-bold text-red-600">12</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-slate-500/10">
                  <span className="text-sm text-on-surface">Hors Service</span>
                  <span className="font-bold text-slate-600">5</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alerts */}
          <Card>
            <CardHeader title="Alertes en Attente" icon={<span className="material-symbols-outlined text-xl text-red-500">warning</span>} />
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 rounded-lg border border-red-200 bg-red-500/5">
                  <p className="text-sm font-medium text-on-surface">Retard mission TR-0847</p>
                  <p className="text-xs text-on-surface-variant">+45 min - Trafic Routes</p>
                </div>
                <div className="p-3 rounded-lg border border-amber-200 bg-amber-500/5">
                  <p className="text-sm font-medium text-on-surface">Contrôle technique expiré</p>
                  <p className="text-xs text-on-surface-variant">CMR-T-4512 - À traiter</p>
                </div>
                <div className="p-3 rounded-lg border border-red-200 bg-red-500/5">
                  <p className="text-sm font-medium text-on-surface">Alerte carburant</p>
                  <p className="text-xs text-on-surface-variant">CMR-T-4538 - Réservoir bas</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
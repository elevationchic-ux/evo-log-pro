'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transportAPI } from '@/lib/api-client';
import { KPICard, StatCard, Card, CardHeader, CardContent, DataTable, StatusBadge, StatusBadges, PageHeader } from '@/components/ui';
import { toast } from 'sonner';

export default function TransportControlPage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Fetch live missions
  const { data: missionsData, isLoading: loadingMissions } = useQuery({
    queryKey: ['transport-missions'],
    queryFn: async () => {
      try {
        const res = await transportAPI.getMissions();
        return res.data?.items || res.data || (Array.isArray(res) ? res : []);
      } catch (e) {
        return [];
      }
    },
    enabled: mounted,
  });

  // Fetch live CEMAC corridors
  const { data: corridorsData } = useQuery({
    queryKey: ['transport-corridors'],
    queryFn: async () => {
      try {
        const res = await transportAPI.getCorridorsCEMAC();
        return res.data || res;
      } catch (e) {
        return null;
      }
    },
    enabled: mounted,
  });

  // Fetch live Fleet TCO
  const { data: tcoData } = useQuery({
    queryKey: ['transport-tco'],
    queryFn: async () => {
      try {
        const res = await transportAPI.getFleetTCO();
        return res.data || res;
      } catch (e) {
        return null;
      }
    },
    enabled: mounted,
  });

  // VRP Optimization mutation
  const vrpMutation = useMutation({
    mutationFn: async () => {
      const res = await transportAPI.optimizeVRP({});
      return res.data || res;
    },
    onSuccess: (data: any) => {
      toast.success(`Optimisation VRP réussie : ${data?.kms_a_vide_economises ?? 0} km économisés.`);
      queryClient.invalidateQueries({ queryKey: ['transport-missions'] });
    },
    onError: () => {
      toast.error("Erreur lors du calcul d'optimisation de tournée.");
    }
  });

  const defaultMissions: Array<any> = [];

  const missions = Array.isArray(missionsData) && missionsData.length > 0
    ? missionsData.map((m: any) => ({
        id: m.reference || `TR-${m.id || '2026'}`,
        vehicle: m.immatriculation || m.camion || '—',
        driver: m.conducteur || '—',
        client: m.client || '—',
        origin: m.origine || '—',
        destination: m.destination || '—',
        status: m.statut || '—',
        eta: m.eta || '—',
        progress: m.progression ?? 0
      }))
    : defaultMissions;

  const kpis = [
    { title: 'Véhicules Flotte', value: String(tcoData?.flotte_totale_vehicules ?? '—'), subtitle: 'Tracteurs & Plateaux', icon: <span className="material-symbols-outlined text-2xl">local_shipping</span>, color: 'blue' as const },
    { title: 'Missions Actives', value: String(missions.length), subtitle: 'En cours d\'acheminement', icon: <span className="material-symbols-outlined text-2xl">route</span>, color: 'emerald' as const, trend: { value: 12, isPositive: true } },
    { title: 'Corridors CEMAC', value: corridorsData?.total_camions_en_transit == null ? '—' : `${corridorsData.total_camions_en_transit} convois`, subtitle: "Douala - N'Djamena & Bangui", icon: <span className="material-symbols-outlined text-2xl">public</span>, color: 'amber' as const },
    { title: 'TCO Moyen Flotte', value: tcoData?.cout_global_moyen_km_xaf == null ? '—' : `${tcoData.cout_global_moyen_km_xaf} XAF`, subtitle: 'Coût au km parcouru', icon: <span className="material-symbols-outlined text-2xl">paid</span>, color: 'violet' as const },
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

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement de la Tour de Contrôle TMS...</div>;

  return (
    <div className="space-y-6">
      <PageHeader 
        title="🚛 Control Tower Transport (TMS & Flotte)"
        description="Centre de contrôle transport temps réel - Tournées optimisées VRP, Corridors CEMAC et TCO flotte"
        breadcrumbs={[
          { label: 'Transport', href: '/transport' },
          { label: 'Control Tower' }
        ]}
        actions={
          <div className="flex gap-2">
            <button
              onClick={() => vrpMutation.mutate()}
              disabled={vrpMutation.isPending}
              className="rounded-xl bg-amber-500 hover:bg-amber-600 px-4 py-2 text-xs font-bold text-slate-950 flex items-center gap-2 shadow-lg shadow-amber-500/20"
            >
              <span className="material-symbols-outlined text-[16px]">alt_route</span>
              {vrpMutation.isPending ? 'Optimisation en cours...' : 'Optimiser Tournées VRP'}
            </button>
            <button
              onClick={() => toast.info('Formulaire de création de mission de transport')}
              className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:opacity-90 flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[16px]">add</span>
              Nouvelle Mission
            </button>
          </div>
        }
      />

      {/* KPIs Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi, index) => (
          <KPICard key={index} {...kpi} loading={loadingMissions} />
        ))}
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Camions en Service" value="42" change={5} color="primary" icon={<span className="material-symbols-outlined">local_shipping</span>} />
        <StatCard label="Chauffeurs Actifs" value="38" change={2} color="success" icon={<span className="material-symbols-outlined">person</span>} />
        <StatCard label="Kilomètres Jour" value="3,150 km" change={15} color="info" icon={<span className="material-symbols-outlined">speed</span>} />
        <StatCard label="Consommation Moyenne" value="31.8 L/100km" change={-4} changeLabel="vs cible" color="warning" icon={<span className="material-symbols-outlined">local_gas_station</span>} />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Missions Table */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader 
              title="Missions en Cours (Live API)" 
              subtitle={`${missions.length} missions sous surveillance GPS`}
              icon={<span className="material-symbols-outlined text-xl">route</span>}
              action={
                <button onClick={() => queryClient.invalidateQueries({ queryKey: ['transport-missions'] })} className="text-xs text-primary hover:underline">
                  Actualiser
                </button>
              }
            />
            <CardContent>
              <DataTable 
                data={missions} 
                columns={columns} 
                keyField="id"
                onRowClick={(item) => toast.info(`Mission sélectionnée : ${item.id} • Chauffeur : ${item.driver}`)}
              />
            </CardContent>
          </Card>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Corridors CEMAC Status */}
          <Card>
            <CardHeader title="Corridors Internationaux CEMAC" icon={<span className="material-symbols-outlined text-xl text-amber-500">public</span>} />
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/60">
                  <div className="text-xs font-bold text-white flex justify-between">
                    <span>Axe Douala - N'Djamena (1 850 km)</span>
                    <span className="text-emerald-400 font-mono">14 convois</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Carnet TRIE Inter-États • Escorte Ngaoundéré-Kousseri active.</p>
                </div>
                <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/60">
                  <div className="text-xs font-bold text-white flex justify-between">
                    <span>Axe Douala - Bangui (1 430 km)</span>
                    <span className="text-cyan-400 font-mono">9 convois</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Poste frontière Garoua-Boulaï • Caution apurée à 100%.</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Maintenance & TCO Alerts */}
          <Card>
            <CardHeader title="Alertes Maintenance Prédictive Flotte" icon={<span className="material-symbols-outlined text-xl text-red-500">warning</span>} />
            <CardContent>
              <div className="space-y-3">
                {(tcoData?.alertes_maintenance_predictive || [
                  { immatriculation: 'LT-TR-4021', type: 'Tracteur Actros', alerte: 'VIDANGE_MOTEUR_IMMINENTE', echeance_km: 500, priorite: 'HAUTE' },
                  { immatriculation: 'LT-TR-8812', type: 'Plateau 40ft', alerte: 'CONTROLE_PNEUMATIQUES', echeance_km: 1200, priorite: 'MOYENNE' }
                ]).map((alt: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-xl border border-red-500/20 bg-red-500/5 flex justify-between items-center">
                    <div>
                      <div className="text-xs font-bold text-red-400 font-mono">{alt.immatriculation}</div>
                      <div className="text-[11px] text-slate-400">{alt.alerte} • {alt.type}</div>
                    </div>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-300">
                      -{alt.echeance_km} km
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
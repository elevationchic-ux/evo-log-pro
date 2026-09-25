'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transportAPI } from '@/lib/api-client';
import { KPICard, StatCard, Card, CardHeader, CardContent, DataTable, StatusBadge, PageHeader } from '@/components/ui';
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

  // Flotte et chauffeurs reels : MissionResponse n'expose que camion_id /
  // conducteur_id (schemas/transport.py MissionBase). Sans ces jointures, les
  // colonnes Vehicule et Chauffeur ne pouvaient rien afficher : l'ancien code
  // lisait m.immatriculation / m.conducteur / m.client, champs qui n'existent
  // dans aucun schema.
  const { data: camionsData } = useQuery({
    queryKey: ['transport-camions'],
    queryFn: async () => {
      try {
        const res = await transportAPI.getCamions();
        return res.data?.items || res.data || [];
      } catch (e) {
        return [];
      }
    },
    enabled: mounted,
  });

  const { data: chauffeursData } = useQuery({
    queryKey: ['transport-chauffeurs'],
    queryFn: async () => {
      try {
        const res = await transportAPI.getChauffeurs();
        return res.data?.items || res.data || [];
      } catch (e) {
        return [];
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

  const immatriculations = new Map((camionsData || []).map((c: any) => [c.id, c.immatriculation]));
  const nomsChauffeurs = new Map((chauffeursData || []).map((d: any) => [d.id, `${d.nom || ''} ${d.prenom || ''}`.trim()]));

  const defaultMissions: Array<any> = [];

  const missions = Array.isArray(missionsData) && missionsData.length > 0
    ? missionsData.map((m: any) => ({
        id: m.reference || `TR-${m.id || '2026'}`,
        // Jointures reelles par cles etrangeres ; pas de champ invente.
        vehicle: immatriculations.get(m.camion_id) || '',
        driver: nomsChauffeurs.get(m.conducteur_id) || '',
        client: m.client_id ? `Client #${m.client_id}` : '',
        // MissionResponse expose point_depart / point_arrivee (pas origine / destination).
        origin: m.point_depart || '',
        destination: m.point_arrivee || '',
        status: m.statut || '',
        // Pas de champ `eta` dans le contrat : l'heure de fin prevue est le seul
        // repere reel disponible.
        eta: m.date_fin_prevue ? new Date(m.date_fin_prevue).toLocaleDateString('fr-FR') : '',
        distance_km: m.distance_km ?? null
      }))
    : defaultMissions;

  const kpis = [
    { title: 'Véhicules Flotte', value: String(tcoData?.flotte_totale_vehicules ?? ''), subtitle: 'Tracteurs & Plateaux', icon: <span className="material-symbols-outlined text-2xl">local_shipping</span>, color: 'blue' as const },
    { title: 'Missions Actives', value: String(missions.length), subtitle: 'En cours d\'acheminement', icon: <span className="material-symbols-outlined text-2xl">route</span>, color: 'emerald' as const },
    { title: 'Corridors CEMAC', value: corridorsData?.total_camions_en_transit == null ? '' : `${corridorsData.total_camions_en_transit} convois`, subtitle: "Douala - N'Djamena & Bangui", icon: <span className="material-symbols-outlined text-2xl">public</span>, color: 'amber' as const },
    { title: 'TCO Moyen Flotte', value: tcoData?.cout_global_moyen_km_xaf == null ? '' : `${tcoData.cout_global_moyen_km_xaf} XAF`, subtitle: 'Coût au km parcouru', icon: <span className="material-symbols-outlined text-2xl">paid</span>, color: 'violet' as const },
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
        // Cles = valeurs reelles de MissionStatus (minuscules, sans accent).
        // L'ancien statusMap testait EN_ROUTE / CHARGEMENT / LIVRE / ATTENTE :
        // aucune mission ne porte ces valeurs, chaque ligne tombait donc dans
        // le fallback avec le code technique brut comme libelle.
        const parStatut: Record<string, JSX.Element> = {
          planifiee: <StatusBadge label="Planifiée" variant="pending" icon />,
          en_cours: <StatusBadge label="En Route" variant="transit" icon pulse />,
          terminee: <StatusBadge label="Terminée" variant="delivered" icon />,
          annulee: <StatusBadge label="Annulée" variant="error" icon />,
          en_retard: <StatusBadge label="En Retard" variant="error" icon pulse />,
        };
        return parStatut[item.status] || <StatusBadge label={item.status || '—'} />;
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

      {/* Stats Overview — calculees depuis les donnees API deja chargees.
          Les valeurs precedentes (42, 38, « 3,150 km », « 31.8 L/100km »)
          etaient des litteraux inventes dans le JSX, presents quelle que soit
          la base. */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Camions Actifs" value={String((camionsData || []).filter((c: any) => c.status === 'active').length)} color="primary" icon={<span className="material-symbols-outlined">local_shipping</span>} />
        <StatCard label="Chauffeurs Actifs" value={String((chauffeursData || []).filter((d: any) => d.is_active).length)} color="success" icon={<span className="material-symbols-outlined">person</span>} />
        <StatCard label="Missions en Cours" value={String(missions.filter((m: any) => m.status === 'en_cours').length)} color="info" icon={<span className="material-symbols-outlined">route</span>} />
        <StatCard
          label="Distance Planifiée"
          value={(() => {
            const km = missions.map((m: any) => m.distance_km).filter((v: any) => typeof v === 'number').reduce((a: number, b: number) => a + b, 0);
            return missions.some((m: any) => typeof m.distance_km === 'number') ? `${km.toLocaleString('fr-FR')} km` : '—';
          })()}
          color="warning"
          icon={<span className="material-symbols-outlined">speed</span>}
        />
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
              {/* Avant : « 14 convois » / « 9 convois » en dur dans le JSX.
                  Maintenant : rendu depuis corridorsData.corridors, et un etat
                  vide honnete si l'API ne repond pas. */}
              <div className="space-y-3">
                {(corridorsData?.corridors || []).length === 0 ? (
                  <p className="text-xs text-slate-500 py-2">Aucun corridor remonté par l'API.</p>
                ) : (
                  corridorsData.corridors.map((c: any, idx: number) => (
                    <div key={idx} className="p-3 rounded-xl border border-slate-800 bg-slate-900/60">
                      <div className="text-xs font-bold text-white flex justify-between">
                        <span>{c.axe} ({c.distance_km} km)</span>
                        <span className="text-emerald-400 font-mono">{c.convois_actifs} convois</span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1">{c.regime_douane}</p>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Maintenance & TCO Alerts */}
          <Card>
            <CardHeader title="Alertes Maintenance Prédictive Flotte" icon={<span className="material-symbols-outlined text-xl text-red-500">warning</span>} />
            <CardContent>
              <div className="space-y-3">
                {/* Pas de fallback invente : quand l'endpoint ne repond pas, on
                    le dit au lieu d'afficher des immatriculations fictives. */}
                {(tcoData?.alertes_maintenance_predictive || []).length === 0 ? (
                  <p className="text-xs text-slate-500 py-2">Aucune alerte remontee par l'API TCO.</p>
                ) : (
                  tcoData.alertes_maintenance_predictive.map((alt: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-xl border border-red-500/20 bg-red-500/5 flex justify-between items-center">
                    <div>
                      <div className="text-xs font-bold text-red-400 font-mono">{alt.immatriculation}</div>
                      <div className="text-[11px] text-slate-400">{alt.alerte} • {alt.type}</div>
                    </div>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-300">
                      -{alt.echeance_km} km
                    </span>
                  </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Anchor, Activity, Ship, Gauge, Clock, ArrowUpRight,
  TrendingUp, RefreshCw, BarChart2, CheckCircle2, AlertTriangle, Layers
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function PortPerformancePage() {
  const [data, setData] = useState<any>(null);
  const [kpis, setKpis] = useState<any>({
    taux_occupation_quais_pourcent: 78.5,
    temps_moyen_attente_rade_heures: 6.2,
    delai_sejour_moyen_conteneurs_jours: 8.4,
    productivite_portiques_mouvements_heure: 24.8,
  });
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resOverview, resKpis] = await Promise.allSettled([
        apiClient.get('/api/v1/port-performance'),
        apiClient.get('/api/v1/port-performance/kpis')
      ]);

      if (resOverview.status === 'fulfilled' && resOverview.value.data) {
        setData(resOverview.value.data);
      }
      if (resKpis.status === 'fulfilled' && resKpis.value.data) {
        setKpis(resKpis.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement performances portuaires:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Anchor className="w-3.5 h-3.5" /> Performance Opérationnelle Maritime • PAD & PAK
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Tableau de Bord de Performance Portuaire
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Cadencement des portiques, temps d'attente sur rade, cadences de manutention et délai de franchise séjour.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchData()}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Occupation des Quais</span>
            <Ship className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {kpis.taux_occupation_quais_pourcent || 78.5}%
          </div>
          <div className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> Fluide (&lt; 85% seuil de saturation)
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Attente Moyenne sur Rade</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            {kpis.temps_moyen_attente_rade_heures || 6.2} h
          </div>
          <div className="text-xs text-slate-500 mt-1">Pilotage et marée Douala Wouri</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Délai Séjour Conteneur</span>
            <Gauge className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {kpis.delai_sejour_moyen_conteneurs_jours || 8.4} Jours
          </div>
          <div className="text-xs text-slate-500 mt-1">Franchise magasin 11 jours</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Cadence Portiques STS</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {kpis.productivite_portiques_mouvements_heure || 24.8} Mvts/h
          </div>
          <div className="text-xs text-slate-500 mt-1">Norme internationale ISO 25</div>
        </div>
      </div>

      {/* Berth & Quai Operations Monitoring */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Ship className="w-5 h-5 text-cyan-400" /> Postes à Quai en Opération (Douala & Kribi)
          </h3>
          <div className="space-y-3">
            {[
              { quai: 'Quai 14 - Terminal Conteneurs RTC (PAD)', navire: 'CMA CGM MONTE CARLO', statut: 'DÉCHARGEMENT', avancement: 68, teu: 1420 },
              { quai: 'Quai 15 - Terminal Minéralier', navire: 'BULK CAMEROON', statut: 'CHARGEMENT BAUXITE', avancement: 82, teu: 0 },
              { quai: 'Quai 16 - Roulier Ro-Ro', navire: 'GRIMALDI GRANDE NIGERIA', statut: 'DÉBARQUEMENT VÉHICULES', avancement: 45, teu: 350 },
              { quai: 'Quai Kribi Deep Sea 1', navire: 'MAERSK TEMA', statut: 'OPÉRATIONS EN COURS', avancement: 91, teu: 2850 }
            ].map((p, i) => (
              <div key={i} className="p-4 rounded-2xl bg-slate-800/40 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white">{p.quai}</span>
                  <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-[10px] font-bold">
                    {p.statut}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Navire : <strong className="text-slate-200">{p.navire}</strong></span>
                  <span>{p.teu > 0 ? `${p.teu} EVP` : 'Vrac solide'}</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-cyan-500 h-full rounded-full transition-all" style={{ width: `${p.avancement}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-emerald-400" /> Cadences Horaires par Équipe (Shift Dockers)
          </h3>
          <div className="space-y-4">
            {[
              { shift: 'Shift 1 (06h - 14h) Équipe Matin', cadence: 26.2, rendement: '104% objectif', portiques: 4 },
              { shift: 'Shift 2 (14h - 22h) Équipe Après-Midi', cadence: 24.8, rendement: '99% objectif', portiques: 4 },
              { shift: 'Shift 3 (22h - 06h) Équipe Nuit', cadence: 23.4, rendement: '94% objectif', portiques: 3 },
            ].map((s, i) => (
              <div key={i} className="p-4 rounded-2xl bg-slate-800/40 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="font-bold text-white text-sm">{s.shift}</div>
                  <div className="text-xs text-slate-400 mt-1">{s.portiques} portiques en service simultané</div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-black font-mono text-emerald-400">{s.cadence} mvts/h</div>
                  <div className="text-xs text-slate-500">{s.rendement}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

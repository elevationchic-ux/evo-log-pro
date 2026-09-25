'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { Map, Activity, MapPin, Search } from 'lucide-react';
import { transportAPI } from '@/lib/api-client';

// Dynamic import with SSR false is REQUIRED for react-leaflet
const MapControlTower = dynamic(() => import('@/components/transport/MapControlTower'), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-slate-900 rounded-2xl animate-pulse flex items-center justify-center">
      <p className="text-slate-400 font-bold flex items-center gap-2">
        <Map className="w-5 h-5 animate-spin" />
        Initialisation de la tour de contrôle...
      </p>
    </div>
  )
});

export default function GPSControlTowerPage() {
  const [missions, setMissions] = useState<any[]>([]);
  const [camions, setCamions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const [mRes, cRes] = await Promise.all([
          transportAPI.getMissions().catch(() => ({ data: [] })),
          transportAPI.getCamions().catch(() => ({ data: [] }))
        ]);
        setMissions(mRes.data || []);
        setCamions(cRes.data || []);
      } catch (e) {
        console.error("Failed to load map data", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredMissions = missions.filter(m => 
    (m.reference && m.reference.toLowerCase().includes(search.toLowerCase())) ||
    (m.camion_immatriculation && m.camion_immatriculation.toLowerCase().includes(search.toLowerCase()))
  );

  // CamionResponse expose `status` (valeurs reelles de l'enum CamionStatus :
  // active / in_maintenance / out_of_service / reserved) et non `statut`.
  // Les trois compteurs ci-dessous testaient `c.statut` contre EN_ROUTE,
  // DISPONIBLE, EN_MAINTENANCE et `!c.actif` : aucune de ces cles n'existe,
  // donc « En Mouvement » et « En Arret » restaient a 0 pendant que
  // « Hors Ligne » avalait 100 % de la flotte. Le passage en mission se lit
  // sur les missions reellement en cours, via la cle etrangere camion_id.
  const camionsEnMission = new Set(
    missions.filter(m => m.statut === 'en_cours' && m.camion_id != null)
      .map(m => m.camion_id)
  );
  const enMouvement = camions.filter(c => camionsEnMission.has(c.id)).length;
  const enArret = camions.filter(c => c.status === 'active' && !camionsEnMission.has(c.id)).length;
  const horsLigne = camions.filter(c => c.status === 'in_maintenance' || c.status === 'out_of_service').length;

  const total = enMouvement + enArret + horsLigne || 1;
  const pctMouvement = Math.round((enMouvement / total) * 100);
  const pctArret = Math.round((enArret / total) * 100);
  const pctHorsLigne = Math.round((horsLigne / total) * 100);

  return (
    <ModuleLayout module="transport">
      <div className="h-[calc(100vh-theme(spacing.16))] flex flex-col p-4 animate-in fade-in duration-500">
        
        {/* Header Compact */}
        <div className="flex justify-between items-center mb-4 shrink-0">
          <div>
            <h1 className="text-2xl font-black text-slate-200 flex items-center gap-2">
              <Map className="w-6 h-6 text-blue-600" />
              Tour de Contrôle GPS
            </h1>
            <p className="text-slate-500 text-sm">Suivi télématique en temps réel de la flotte.</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                type="text" 
                placeholder="Rechercher OT, Camion..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="pl-9 pr-4 py-2 border border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 outline-none w-64"
              />
            </div>
            <div className="bg-emerald-500/10 text-emerald-600 px-3 py-2 rounded-xl text-sm font-bold flex items-center gap-2 border border-emerald-500/30 shadow-sm">
              <Activity className="w-4 h-4" />
              Système En Ligne
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div className="flex-1 rounded-2xl shadow-sm border border-slate-700 overflow-hidden relative z-0">
          {loading ? (
            <div className="h-full w-full bg-slate-900 animate-pulse flex items-center justify-center">Chargement de la carte...</div>
          ) : (
            <MapControlTower vehicles={filteredMissions} />
          )}
          
          {/* Overlay Stats Card */}
          <div className="absolute top-4 right-4 z-[400] w-72 bg-slate-900/90 backdrop-blur-md p-4 rounded-2xl shadow-xl border border-slate-700">
            <h3 className="font-bold text-slate-200 mb-3 text-sm flex items-center gap-2">
              <MapPin className="w-4 h-4 text-blue-600" />
              Statut Flotte ({camions.length} Véhicules)
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs font-semibold text-slate-500">En mission</span>
                <span className="text-sm font-black text-emerald-600">{enMouvement}</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-1.5"><div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${pctMouvement}%` }}></div></div>
              
              <div className="flex justify-between items-center">
                <span className="text-xs font-semibold text-slate-500">En Arrêt / Quai</span>
                <span className="text-sm font-black text-amber-600">{enArret}</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-1.5"><div className="bg-amber-500 h-1.5 rounded-full" style={{ width: `${pctArret}%` }}></div></div>
              
              <div className="flex justify-between items-center">
                <span className="text-xs font-semibold text-slate-500">Hors Ligne / Maintenance</span>
                <span className="text-sm font-black text-red-600">{horsLigne}</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-1.5"><div className="bg-red-500 h-1.5 rounded-full" style={{ width: `${pctHorsLigne}%` }}></div></div>
            </div>
          </div>
        </div>
        
      </div>
    </ModuleLayout>
  );
}

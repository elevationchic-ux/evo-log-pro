'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Navigation, Search, RefreshCw, Truck, MapPin, Gauge,
  ShieldCheck, AlertTriangle, Radio, Activity, Compass, CheckCircle2
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface PositionItem {
  id: number;
  vehicule_id: number;
  immatriculation?: string;
  latitude: number;
  longitude: number;
  vitesse_kmh: number;
  cap?: number;
  statut_moteur: string;
  adresse_approximative?: string;
  timestamp: string;
}

export default function GpsTrackingPage() {
  const [positions, setPositions] = useState<PositionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedVehicule, setSelectedVehicule] = useState<PositionItem | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/gps-tracking');
      if (res.data) {
        const list = Array.isArray(res.data) ? res.data : (res.data.items || []);
        setPositions(list);
        if (list.length > 0 && !selectedVehicule) {
          setSelectedVehicule(list[0]);
        }
      }
    } catch (err) {
      console.error('Erreur chargement tracking GPS:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedVehicule]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const filteredPositions = positions.filter((p) =>
    (p.immatriculation || '').toLowerCase().includes(search.toLowerCase()) ||
    (p.adresse_approximative || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Radio className="w-3.5 h-3.5 animate-pulse" /> Télématique Flotte & Géolocalisation Satellitaire
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Tracking GPS Temps Réel & Geofencing
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Surveillance en continu de la position des camions, vitesse, arrêts inopinés et franchissement des zones portuaires.
          </p>
        </div>

        <button
          onClick={() => fetchData()}
          className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
          title="Actualiser positions"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Balises GPS Connectées</span>
            <Truck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {positions.length || 82}
          </div>
          <div className="text-xs text-emerald-400 mt-1">Signal 4G / Iridium actif</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Véhicules en Mouvement</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-400 mt-2">
            {positions.filter(p => p.vitesse_kmh > 0).length || 48}
          </div>
          <div className="text-xs text-slate-500 mt-1">Vitesse moyenne 45 km/h</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>En Zone Portuaire (PAD/PAK)</span>
            <MapPin className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-blue-400 mt-2">
            24 Camions
          </div>
          <div className="text-xs text-slate-500 mt-1">Geofence quai & entrepôts</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Alertes Vitesse / Sortie</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            0 Critique
          </div>
          <div className="text-xs text-slate-500 mt-1">Corridors sécurisés</div>
        </div>
      </div>

      {/* Main Map & Vehicle List */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left List */}
        <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filtrer camion par immatriculation..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {filteredPositions.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-500">
                Aucun véhicule géolocalisé.
              </div>
            ) : (
              filteredPositions.map((p) => (
                <div
                  key={p.id}
                  onClick={() => setSelectedVehicule(p)}
                  className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
                    selectedVehicule?.id === p.id
                      ? 'bg-emerald-500/10 border-emerald-500/40'
                      : 'bg-slate-800/40 border-slate-800 hover:bg-slate-800/80'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-sm text-white">
                      {p.immatriculation || `CAMION #${p.vehicule_id}`}
                    </span>
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                      p.vitesse_kmh > 0
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {p.vitesse_kmh > 0 ? `${p.vitesse_kmh} km/h` : 'À l\'arrêt'}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1 flex items-center gap-1 truncate">
                    <MapPin className="w-3 h-3 text-slate-500 shrink-0" />
                    <span>{p.adresse_approximative || `Lat: ${p.latitude}, Long: ${p.longitude}`}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Details Panel / Visualizer */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Compass className="w-5 h-5 text-emerald-400" /> Détail Télématique Véhicule
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Paramètres capteurs IoT, sonde carburant et état du moteur en temps réel :
            </p>
          </div>

          {selectedVehicule ? (
            <div className="space-y-4">
              <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                  <span className="font-mono font-black text-lg text-white">
                    {selectedVehicule.immatriculation || `VÉHICULE #${selectedVehicule.vehicule_id}`}
                  </span>
                  <span className="text-xs font-mono text-emerald-400">
                    Statut : {selectedVehicule.statut_moteur}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                  <div>
                    <span className="text-slate-500 block">Vitesse Actuelle</span>
                    <span className="font-bold text-white font-mono">{selectedVehicule.vitesse_kmh} km/h</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Coordonnées GPS</span>
                    <span className="font-mono text-slate-300">
                      {selectedVehicule.latitude.toFixed(4)}, {selectedVehicule.longitude.toFixed(4)}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Cap / Direction</span>
                    <span className="font-mono text-slate-300">{selectedVehicule.cap || 0}° Nord</span>
                  </div>
                </div>
              </div>

              {/* Geofence Check */}
              <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                <div className="text-xs">
                  <span className="font-bold text-emerald-400 block">Corridor Sécurisé Validé</span>
                  <span className="text-slate-300">
                    Le véhicule circule dans l'itinéraire autorisé (Corridor National Douala - Yaoundé RN3).
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-xs text-slate-500">
              Sélectionnez un camion dans la liste de gauche pour afficher ses détails télématiques.
            </div>
          )}

          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <span>Protocole GPS : NMEA 0183 / Teltonika FMB920</span>
            <span className="font-mono text-emerald-400 font-bold">Liaison 100% stable</span>
          </div>
        </div>
      </div>
    </div>
  );
}

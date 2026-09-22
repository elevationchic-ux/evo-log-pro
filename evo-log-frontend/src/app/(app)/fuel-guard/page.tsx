'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fuelGuardAPI } from '@/lib/api-client';
import { Fuel, AlertTriangle, ShieldCheck, Search, Zap } from 'lucide-react';
import Link from 'next/link';

export default function FuelGuardPage() {
  const [mounted, setMounted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['fuel-sensors'],
    queryFn: async () => {
      const res = await fuelGuardAPI.getSensors();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-FuelGuard...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.immatriculation_camion || '') + ' ' + String(i.derniere_station || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 text-orange-400 text-xs font-semibold mb-2 border border-orange-500/20">
            <Fuel className="w-3.5 h-3.5" />
            K-FuelGuard • Télémétrie Reservoirs & Anti-Fraude IoT
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Télémétrie Carburant & Protection Vol</h1>
          <p className="text-slate-400 text-sm mt-1">Surveillance continue des niveaux de diesel et prévention des siphonnages.</p>
        </div>

        <Link
          href="/fuel-guard/alerts"
          className="inline-flex items-center justify-center gap-2 bg-orange-600 hover:bg-orange-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-orange-600/30 transition-all hover:scale-[1.02]"
        >
          <Zap className="w-4 h-4" />
          Alertes Anomales IoT
        </Link>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Capteurs de Niveau Réservoir Flotte en Temps Réel
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par immatriculation..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-orange-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Camion Immatriculation</th>
                <th className="px-6 py-4">Niveau Réservoir (Litres)</th>
                <th className="px-6 py-4">Dernière Station Partenaire</th>
                <th className="px-6 py-4 text-right">Statut Télémétrie</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={4} className="p-12 text-center text-slate-400">Chargement des capteurs K-FuelGuard...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucun capteur actif enregistré.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 font-mono">
                      {item.immatriculation_camion || 'LT-802-AA'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      <span className="font-mono text-orange-400 font-bold">{item.niveau_actuel_litres || 340} L</span> / {item.capacite_totale_litres || 400} L
                    </td>
                    <td className="px-6 py-4 text-slate-300 text-xs">
                      {item.derniere_station || 'TotalEnergies Douala Port'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <ShieldCheck className="w-3 h-3" /> NORMALE
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

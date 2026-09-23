'use client';

import React, { useState } from 'react';
import {
  Fuel, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Gauge, Droplet, TrendingDown, TrendingUp, ShieldAlert
} from 'lucide-react';
import { toast } from 'sonner';

interface FuelRecord {
  id: string;
  immatriculation: string;
  driver: string;
  tankCapacity: number;
  currentLevel: number;
  consumptionAvg: number;
  lastRefuelLitres: number;
  lastRefuelDate: string;
  anomaliesDetected: boolean;
  status: 'NORMAL' | 'ALERTE_SIPHONNAGE' | 'SURCONSOMMATION';
}

const FUEL_DATA: FuelRecord[] = [];

export default function TransportFlotteFuelTelematics() {
  const [data, setData] = useState<FuelRecord[]>(FUEL_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = data.filter(d =>
    d.immatriculation.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.driver.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-blue-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Fuel Guard & Télématique CanBus
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KTRN_FUEL
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Fuel className="w-8 h-8 text-blue-400" />
            Télématique Carburant & Anti-Siphonnage
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Sondes de réservoir en temps réel, analyse de la consommation L/100km et détection automatique des anomalies.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.success('Rapport télématique carburant exporté')}
            className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-blue-500/25 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" /> Rapport Carburant
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Consommation Moyenne Flotte</div>
          <div className="text-2xl font-black text-slate-100 font-mono">
             <span className="text-xs text-slate-400 font-normal">L / 100 km</span>
          </div>
          <div className="text-[11px] text-emerald-400 mt-2">Conforme aux standards constructeurs</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Carburant Consommé (Août 2026)</div>
          <div className="text-2xl font-black text-blue-400 font-mono">
             <span className="text-xs font-normal">Litres</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Gasoil TotalEnergies</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Alertes Vols / Chutes Sondes</div>
          <div className="text-2xl font-black text-red-400 font-mono">
             <span className="text-xs font-normal text-slate-400">incident</span>
          </div>
          <div className="text-[11px] text-red-300/80 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Aucune alerte persistée disponible
          </div>
        </div>
      </div>

      {/* Table Télématique */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher véhicule ou chauffeur..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Véhicule & Chauffeur</th>
                <th className="py-3.5 px-4 text-right">Capacité Réservoir</th>
                <th className="py-3.5 px-4 text-right">Niveau Actuel</th>
                <th className="py-3.5 px-4 text-right">Conso Moyenne</th>
                <th className="py-3.5 px-4">Dernier Plein</th>
                <th className="py-3.5 px-4 text-center">Statut Sonde</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(item => (
                <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-blue-400 text-sm">{item.immatriculation}</div>
                    <div className="font-sans text-slate-300 text-xs">{item.driver}</div>
                  </td>
                  <td className="py-3.5 px-4 text-right text-slate-400">{item.tankCapacity} L</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-100">{item.currentLevel} L</td>
                  <td className="py-3.5 px-4 text-right font-bold text-blue-300">{item.consumptionAvg} L/100km</td>
                  <td className="py-3.5 px-4">
                    <div className="text-slate-200 font-bold">{item.lastRefuelLitres} L</div>
                    <div className="text-[11px] text-slate-400">{item.lastRefuelDate}</div>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.status === 'NORMAL' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      'bg-red-500/10 text-red-400 border border-red-500/20 animate-pulse'
                    }`}>
                      {item.status === 'NORMAL' ? '✓ Normal' : '🚨 Siphonnage Détecté'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

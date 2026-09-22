'use client';

import React, { useState } from 'react';
import {
  Truck, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, MapPin, Calendar, Clock, User, ShieldCheck, ArrowRight
} from 'lucide-react';
import { toast } from 'sonner';

interface Mission {
  id: string;
  code: string;
  corridor: string;
  client: string;
  driver: string;
  truckPlate: string;
  trailerPlate: string;
  cargo: string;
  departureDate: string;
  status: 'EN_ROUTE' | 'AFFECTE' | 'LIVRE' | 'ATTENTE_CHARGEMENT';
  progress: number;
}

const MISSIONS: Mission[] = [];

export default function TransportFlotteMissionsDispatch() {
  const [missions, setMissions] = useState<Mission[]>(MISSIONS);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const filtered = missions.filter(m => {
    const matchStatus = filterStatus === 'ALL' || m.status === filterStatus;
    const matchSearch = m.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        m.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        m.driver.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        m.corridor.toLowerCase().includes(searchQuery.toLowerCase());
    return matchStatus && matchSearch;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-blue-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
              TMS & Dispatch Intelligent Corridors
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KTRN_DSP / TR01
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Truck className="w-8 h-8 text-blue-400" />
            Dispatching des Tournées & Missions
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Affectation optimisée des chauffeurs, tracteurs et remorques pour les corridors CEMAC et livraisons locales.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Ouverture de l assistant de dispatch intelligent (Affectation IA)')}
            className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-blue-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Créer Ordre de Transport
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Missions en Transit Actif</div>
          <div className="text-2xl font-black text-blue-400 font-mono">18 <span className="text-xs font-normal text-slate-400">convois</span></div>
          <div className="text-[11px] text-slate-400 mt-2">12 corridors inter-États</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Taux d Utilisation Flotte</div>
          <div className="text-2xl font-black text-emerald-400 font-mono">92.4%</div>
          <div className="text-[11px] text-emerald-300/80 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> 38 tracteurs mobilisés
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ponctualité (OTD)</div>
          <div className="text-2xl font-black text-slate-100 font-mono">96.8%</div>
          <div className="text-[11px] text-slate-400 mt-2">Respect des fenêtres horaires</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Alertes Géolocalisation</div>
          <div className="text-2xl font-black text-amber-400 font-mono">2 <span className="text-xs font-normal text-slate-400">arrêts prolongés</span></div>
          <div className="text-[11px] text-amber-300/80 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Corridor N&apos;Djamena
          </div>
        </div>
      </div>

      {/* Barre de Recherche et Filtres */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher mission, corridor, chauffeur, camion..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          {['ALL', 'EN_ROUTE', 'AFFECTE', 'LIVRE'].map(st => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all border ${
                filterStatus === st
                  ? 'bg-blue-600/30 text-blue-300 border-blue-500'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Table des Missions */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Code Mission</th>
                <th className="py-3.5 px-4">Corridor & Destination</th>
                <th className="py-3.5 px-4">Client</th>
                <th className="py-3.5 px-4">Chauffeur & Véhicules</th>
                <th className="py-3.5 px-4">Marchandise / Conteneur</th>
                <th className="py-3.5 px-4 text-center">Progression</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(m => (
                <tr key={m.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-blue-400">{m.code}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-100 font-medium flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-red-400 shrink-0" /> {m.corridor}
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{m.client}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-sans font-bold text-slate-200">{m.driver}</div>
                    <div className="text-[11px] text-slate-400 font-mono">Tracteur: {m.truckPlate} • Rem: {m.trailerPlate}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{m.cargo}</td>
                  <td className="py-3.5 px-4 text-center">
                    <div className="w-24 bg-slate-950 rounded-full h-2 mx-auto overflow-hidden border border-slate-800">
                      <div className="bg-gradient-to-r from-blue-500 to-emerald-400 h-full" style={{ width: `${m.progress}%` }} />
                    </div>
                    <span className="text-[10px] text-slate-400 mt-1 block">{m.progress}%</span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      m.status === 'EN_ROUTE' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      m.status === 'LIVRE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {m.status}
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

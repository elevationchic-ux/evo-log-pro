'use client';

import React, { useState } from 'react';
import {
  Compass, Search, Filter, Download, CheckCircle2,
  AlertTriangle, MapPin, Radio, ShieldCheck, Clock, Navigation
} from 'lucide-react';
import { toast } from 'sonner';

interface Checkpoint {
  name: string;
  country: string;
  trucksInQueue: number;
  avgWaitHours: number;
  status: 'FLUIDE' | 'RALENTI' | 'BLOQUE';
}

const CHECKPOINTS: Checkpoint[] = [
  { name: 'Kousseri / N\'Djamena (Pont N\'Gueli)', country: 'Cameroun ➔ Tchad', trucksInQueue: 14, avgWaitHours: 4.5, status: 'FLUIDE' },
  { name: 'Garoua-Boulaï / Cantonnier', country: 'Cameroun ➔ RCA', trucksInQueue: 28, avgWaitHours: 12.0, status: 'RALENTI' },
  { name: 'Touboro / Mbere', country: 'Cameroun ➔ Tchad Sud', trucksInQueue: 6, avgWaitHours: 2.0, status: 'FLUIDE' },
  { name: 'Poste de Pesage d Edéa', country: 'Cameroun Axe Lourd', trucksInQueue: 8, avgWaitHours: 0.5, status: 'FLUIDE' },
];

export default function TransportFlotteControlTower() {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>(CHECKPOINTS);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-blue-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Tour de Contrôle & ETA Frontières
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KTRN_RTE
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Compass className="w-8 h-8 text-blue-400" />
            Tour de Contrôle des Corridors CEMAC
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Supervision 24/7 des flux routiers, temps d attente aux frontières et calcul dynamique des heures estimées d arrivée (ETA).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.success('Cartographie radar des convois rafraîchie')}
            className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-blue-500/25 transition-all cursor-pointer"
          >
            <Radio className="w-4 h-4" /> Radar Flotte Live
          </button>
        </div>
      </div>

      {/* Grid: État des Frontières & Corridors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {checkpoints.map(cp => (
          <div key={cp.name} className="bg-slate-900/90 border border-slate-800 p-5 rounded-3xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5 font-bold text-slate-100">
                <MapPin className="w-5 h-5 text-red-400" />
                <span>{cp.name}</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                cp.status === 'FLUIDE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                cp.status === 'RALENTI' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}>
                {cp.status}
              </span>
            </div>

            <div className="text-xs text-slate-400 font-mono">{cp.country}</div>

            <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800 text-xs font-mono">
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-850">
                <div className="text-slate-500 text-[10px] uppercase">Camions en Attente</div>
                <div className="font-bold text-slate-200 text-base">{cp.trucksInQueue} camions</div>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-850">
                <div className="text-slate-500 text-[10px] uppercase">Attente Moyenne</div>
                <div className="font-bold text-amber-400 text-base">{cp.avgWaitHours} heures</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
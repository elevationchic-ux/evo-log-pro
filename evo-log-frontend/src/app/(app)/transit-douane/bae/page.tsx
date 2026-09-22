'use client';

import React, { useState } from 'react';
import {
  Globe, Plus, Search, Download, CheckCircle2, AlertTriangle, Printer, Clock
} from 'lucide-react';
import { toast } from 'sonner';

type BaeStatus = 'EN_TRANSIT' | 'ARRIVE' | 'APURE' | 'CONTENTIEUX';

interface BaeRecord {
  id: string;
  baeNumber: string;
  declarant: string;
  destinataire: string;
  corridor: string;
  marchandise: string;
  poidsKg: number;
  cautionXaf: number;
  dateDepart: string;
  dateEcheance: string;
  status: BaeStatus;
}

const BAE_DATA: BaeRecord[] = [];

const STATUS_COLORS: Record<BaeStatus, string> = {
  EN_TRANSIT: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  ARRIVE: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
  APURE: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  CONTENTIEUX: 'bg-red-500/10 text-red-400 border border-red-500/20',
};

export default function TransitDouaneBae() {
  const [records] = useState<BaeRecord[]>(BAE_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = records.filter(r =>
    r.baeNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.destinataire.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.corridor.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-cyan-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Bulletins de Transit CEMAC
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KDOU_BAE
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Globe className="w-8 h-8 text-cyan-400" />
            BAE  Transit Communautaire CEMAC
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Gestion des Bulletins d Analyse et d Expédition (BAE), cautionnements, apurement et contentieux.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Création d un nouveau dossier BAE de transit CEMAC')}
            className="px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-teal-500 text-white font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Ouvrir BAE
          </button>
        </div>
      </div>

      {/* Table BAE */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher n° BAE, destinataire ou corridor..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">N° BAE & Déclarant</th>
                <th className="py-3.5 px-4">Destinataire Final</th>
                <th className="py-3.5 px-4">Corridor CEMAC</th>
                <th className="py-3.5 px-4">Marchandise</th>
                <th className="py-3.5 px-4 text-right">Poids Net</th>
                <th className="py-3.5 px-4 text-right">Caution (XAF)</th>
                <th className="py-3.5 px-4">Échéance Apurement</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(r => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-cyan-400">{r.baeNumber}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{r.declarant}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-100 font-semibold">{r.destinataire}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{r.corridor}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{r.marchandise}</td>
                  <td className="py-3.5 px-4 text-right text-slate-200">{r.poidsKg.toLocaleString()} kg</td>
                  <td className="py-3.5 px-4 text-right font-bold text-amber-400">{r.cautionXaf.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-slate-300">{r.dateEcheance}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${STATUS_COLORS[r.status]}`}>
                      {r.status}
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

'use client';

import React, { useState } from 'react';
import {
  ArrowUpRight, ArrowDownLeft, Search, Plus, Download, Filter
} from 'lucide-react';
import { toast } from 'sonner';

type MvtType = 'ENTREE' | 'SORTIE' | 'TRANSFERT' | 'REGULARISATION';

interface Movement {
  id: string;
  date: string;
  sku: string;
  designation: string;
  type: MvtType;
  qtyMoved: number;
  fromLocation: string;
  toLocation: string;
  reference: string;
  operator: string;
}

const MOVEMENTS_DATA: Movement[] = [];

const MVT_COLORS: Record<MvtType, string> = {
  ENTREE: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  SORTIE: 'bg-red-500/10 text-red-400 border border-red-500/20',
  TRANSFERT: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  REGULARISATION: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
};

export default function MagasinStockMovements() {
  const [movements, setMovements] = useState<Movement[]>(MOVEMENTS_DATA);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<MvtType | 'ALL'>('ALL');

  const filtered = movements.filter(m => {
    const matchQuery =
      m.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.designation.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.reference.toLowerCase().includes(searchQuery.toLowerCase());
    const matchType = filterType === 'ALL' || m.type === filterType;
    return matchQuery && matchType;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Journal des Mouvements WMS
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KMAG_MVM
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <ArrowUpRight className="w-8 h-8 text-amber-400" />
            Mouvements de Stock (Entrées / Sorties)
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Traçabilité complète des flux physiques : entrées quai, sorties picking, transferts et régularisations d inventaire.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.success('Export des mouvements de stock en CSV (période sélectionnée)')}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" /> Exporter Journal
          </button>
        </div>
      </div>

      {/* Filtres par type */}
      <div className="flex flex-wrap gap-2">
        {(['ALL', 'ENTREE', 'SORTIE', 'TRANSFERT', 'REGULARISATION'] as const).map(t => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold font-mono transition-all cursor-pointer ${
              filterType === t
                ? 'bg-amber-500 text-slate-950 shadow-lg'
                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:border-amber-500/50'
            }`}
          >
            {t === 'ALL' ? 'Tous les mouvements' : t}
          </button>
        ))}
      </div>

      {/* Table des mouvements */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher SKU, désignation ou référence..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Date & Heure</th>
                <th className="py-3.5 px-4">SKU & Désignation</th>
                <th className="py-3.5 px-4 text-center">Type</th>
                <th className="py-3.5 px-4 text-right">Quantité</th>
                <th className="py-3.5 px-4">Origine</th>
                <th className="py-3.5 px-4">Destination</th>
                <th className="py-3.5 px-4">Référence</th>
                <th className="py-3.5 px-4">Opérateur</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(m => (
                <tr key={m.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 text-slate-400 whitespace-nowrap">{m.date}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-amber-400">{m.sku}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{m.designation}</div>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${MVT_COLORS[m.type]}`}>
                      {m.type}
                    </span>
                  </td>
                  <td className={`py-3.5 px-4 text-right font-bold text-base ${
                    m.qtyMoved > 0 ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {m.qtyMoved > 0 ? `+${m.qtyMoved}` : m.qtyMoved}
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">{m.fromLocation}</td>
                  <td className="py-3.5 px-4 text-slate-300">{m.toLocation}</td>
                  <td className="py-3.5 px-4 font-bold text-blue-400">{m.reference}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{m.operator}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

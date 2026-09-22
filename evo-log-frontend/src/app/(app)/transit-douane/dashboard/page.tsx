'use client';

import React, { useState } from 'react';
import {
  FileText, Search, Plus, Filter, Eye, CheckCircle2, AlertTriangle,
  Clock, Calculator, ChevronRight, Download, Stamp, TrendingUp, Package
} from 'lucide-react';
import { toast } from 'sonner';

export default function TransitDouaneDashboardPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const kpis: Array<any> = [];

  const circuits: Array<any> = [];

  const circuitColors: Record<string, string> = {
    'VERT': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'JAUNE': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    'ROUGE': 'bg-red-500/10 text-red-400 border-red-500/30',
  };

  const filteredCircuits = circuits.filter(c =>
    !searchQuery ||
    c.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.conteneur.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white">Transit & Douane CEMAC</h1>
          <p className="text-xs text-slate-400 mt-0.5">Gestion DUM · Circuits GUCE · BAE · Titres Transit T1 · Taxation CEMAC</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => toast.info('Ouvrir formulaire nouvelle DUM  Démos disponibles en section Déclarations')}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg"
          >
            <Plus className="w-4 h-4" /> Nouvelle DUM
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        {kpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div key={i} className={`${kpi.bg} border rounded-2xl p-4 shadow-lg`}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${kpi.color}`} />
                <span className="text-xs font-medium text-slate-400 truncate">{kpi.label}</span>
              </div>
              <div className={`text-2xl font-black ${kpi.color} font-mono`}>{kpi.value}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">{kpi.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Declarations Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
          <h2 className="text-sm font-bold text-white">Déclarations DUM en Cours</h2>
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="DUM, Client, Conteneur..."
              className="h-9 pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono w-60"
            />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-left">
                <th className="px-4 py-3 text-slate-400 font-semibold uppercase">N° DUM</th>
                <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Client</th>
                <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden md:table-cell">Marchandise</th>
                <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Circuit</th>
                <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden lg:table-cell">Valeur Déclarée</th>
                <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Statut BAE</th>
                <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Agent</th>
                <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredCircuits.map((row) => (
                <tr key={row.code} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 font-mono font-bold text-amber-300">{row.code}</td>
                  <td className="px-4 py-3 text-slate-200 font-medium">{row.client}</td>
                  <td className="px-4 py-3 text-slate-400 hidden md:table-cell max-w-48 truncate">{row.marchandise}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-black border ${circuitColors[row.circuit]}`}>
                      ● {row.circuit}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-slate-300 hidden lg:table-cell">
                    {(row.valeur / 1000000).toFixed(1)} M XAF
                  </td>
                  <td className="px-4 py-3 text-slate-400">{row.bae}</td>
                  <td className="px-4 py-3 text-slate-400">{row.agent}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toast.info(`Ouvrir dossier ${row.code}`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5 text-amber-400" />
                    </button>
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

'use client';

import React, { useState } from 'react';
import {
  FileText, Plus, Search, Download, CheckCircle2,
  AlertTriangle, Clock, DollarSign, Printer
} from 'lucide-react';
import { toast } from 'sonner';

type DumStatus = 'BROUILLON' | 'DEPOSEE' | 'EN_LIQUIDATION' | 'LIQUIDEE' | 'CONTESTEE';
type DumType = 'IM4' | 'IM7' | 'EX1' | 'T1';

interface DumDeclaration {
  id: string;
  dumNumber: string;
  type: DumType;
  importateur: string;
  marchandise: string;
  valeurCifXaf: number;
  droitsTaxes: number;
  tvaXaf: number;
  depositDate: string;
  status: DumStatus;
  regime: string;
}

const DUM_DATA: DumDeclaration[] = [];

const STATUS_COLORS: Record<DumStatus, string> = {
  BROUILLON: 'bg-slate-800 text-slate-400 border border-slate-700',
  DEPOSEE: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  EN_LIQUIDATION: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
  LIQUIDEE: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  CONTESTEE: 'bg-red-500/10 text-red-400 border border-red-500/20',
};

export default function TransitDouaneDeclarations() {
  const [declarations] = useState<DumDeclaration[]>(DUM_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = declarations.filter(d =>
    d.dumNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.importateur.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.marchandise.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-cyan-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Déclarations en Douane SYDONIA World
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KDOU_DUM
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <FileText className="w-8 h-8 text-cyan-400" />
            Déclarations DUM Import / Export / Transit
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Saisie des DUM SYDONIA, calcul automatique droits TEC CEMAC (Cat. 4), TVA 19.25%, visa et liquidation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Ouverture du formulaire de saisie d une nouvelle DUM')}
            className="px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-cyan-500 hover:to-teal-400 text-white font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Nouvelle DUM
          </button>
        </div>
      </div>

      {/* Table DUM */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher n° DUM, importateur ou marchandise..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">N° DUM & Régime</th>
                <th className="py-3.5 px-4">Importateur</th>
                <th className="py-3.5 px-4">Marchandise (SH)</th>
                <th className="py-3.5 px-4 text-right">Valeur CIF (XAF)</th>
                <th className="py-3.5 px-4 text-right">Droits & Taxes</th>
                <th className="py-3.5 px-4 text-right">TVA 19.25%</th>
                <th className="py-3.5 px-4">Date Dépôt</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(d => (
                <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-cyan-400">{d.dumNumber}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{d.regime}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-100 font-semibold">{d.importateur}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-300 max-w-[200px] truncate">{d.marchandise}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-200">{d.valeurCifXaf.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-red-400">{d.droitsTaxes.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-amber-400">{d.tvaXaf.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-slate-400">{d.depositDate}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${STATUS_COLORS[d.status]}`}>
                      {d.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => toast.success(`Impression DUM ${d.dumNumber}`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
                    >
                      <Printer className="w-3.5 h-3.5" />
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

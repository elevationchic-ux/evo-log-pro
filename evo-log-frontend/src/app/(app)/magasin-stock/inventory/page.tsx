'use client';

import React, { useState } from 'react';
import {
  Boxes, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Calculator, Calendar, FileText, Check
} from 'lucide-react';
import { toast } from 'sonner';

interface InventoryItem {
  id: string;
  sku: string;
  designation: string;
  location: string;
  stockTheorique: number;
  stockPhysique: number;
  ecart: number;
  valeurUnitaire: number;
  ecartValeur: number;
  status: 'VALIDE' | 'EN_REVISION' | 'ECART_DETECTE';
}

const INVENTORY_DATA: InventoryItem[] = [
  { id: '1', sku: 'ART-LUB-001', designation: 'Huile Moteur Synthétique 15W40 (Fût 200L)', location: 'Allée B - Rack 04 - Niv 2', stockTheorique: 45, stockPhysique: 45, ecart: 0, valeurUnitaire: 320000, ecartValeur: 0, status: 'VALIDE' },
  { id: '2', sku: 'ART-PNEU-225', designation: 'Pneu Poids Lourd 315/80 R22.5 Michelin', location: 'Allée D - Rack 01 - Sol', stockTheorique: 24, stockPhysique: 22, ecart: -2, valeurUnitaire: 280000, ecartValeur: -560000, status: 'ECART_DETECTE' },
  { id: '3', sku: 'ART-FLT-OIL', designation: 'Filtre à Huile Tracteur Actros', location: 'Allée A - Bac 12', stockTheorique: 80, stockPhysique: 80, ecart: 0, valeurUnitaire: 25000, ecartValeur: 0, status: 'VALIDE' },
  { id: '4', sku: 'ART-CTN-PIEC', designation: 'Batterie 12V 220Ah Poids Lourd', location: 'Allée C - Rack 02 - Niv 1', stockTheorique: 15, stockPhysique: 16, ecart: +1, valeurUnitaire: 145000, ecartValeur: +145000, status: 'ECART_DETECTE' },
];

export default function MagasinStockInventory() {
  const [items, setItems] = useState<InventoryItem[]>(INVENTORY_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const totalEcartValeur = items.reduce((acc, curr) => acc + curr.ecartValeur, 0);

  const handleRegularize = () => {
    toast.success('PV de régularisation comptable OHADA généré et transmis au module Comptabilité (Écritures 603/703)');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Contrôle Physique & Valorisation OHADA
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KMAG_INV
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Boxes className="w-8 h-8 text-amber-400" />
            Inventaires Tournants & Écarts de Stock
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Comptage physique des références, détection des écarts et intégration automatique dans le Grand Livre (Classe 3).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRegularize}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all cursor-pointer"
          >
            <Check className="w-4 h-4" /> Générer PV de Régularisation
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Références Contrôlées</div>
          <div className="text-2xl font-black text-slate-100 font-mono">164 <span className="text-xs text-slate-400 font-normal">SKUs</span></div>
          <div className="text-[11px] text-slate-400 mt-2">Campagne d inventaire Août 2026</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Taux de Fiabilité des Stocks</div>
          <div className="text-2xl font-black text-emerald-400 font-mono">98.2%</div>
          <div className="text-[11px] text-emerald-300/80 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Objectif &gt; 98% atteint
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Impact Net des Écarts (XAF)</div>
          <div className="text-2xl font-black text-amber-400 font-mono">
            {totalEcartValeur.toLocaleString()} <span className="text-xs font-normal">XAF</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Écart global à régulariser</div>
        </div>
      </div>

      {/* Table Inventaire */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par référence SKU ou désignation..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Code SKU</th>
                <th className="py-3.5 px-4">Désignation de l Article</th>
                <th className="py-3.5 px-4">Emplacement MAG3</th>
                <th className="py-3.5 px-4 text-right">Stock Théorique</th>
                <th className="py-3.5 px-4 text-right">Stock Physique</th>
                <th className="py-3.5 px-4 text-right">Écart Qté</th>
                <th className="py-3.5 px-4 text-right">Impact Valeur (XAF)</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {items.map(item => (
                <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-amber-400">{item.sku}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-100 font-medium">{item.designation}</td>
                  <td className="py-3.5 px-4 text-slate-400">{item.location}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-200">{item.stockTheorique}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-100">{item.stockPhysique}</td>
                  <td className={`py-3.5 px-4 text-right font-bold ${
                    item.ecart === 0 ? 'text-slate-400' : item.ecart < 0 ? 'text-red-400' : 'text-emerald-400'
                  }`}>
                    {item.ecart > 0 ? `+${item.ecart}` : item.ecart}
                  </td>
                  <td className={`py-3.5 px-4 text-right font-bold ${
                    item.ecartValeur === 0 ? 'text-slate-400' : item.ecartValeur < 0 ? 'text-red-400' : 'text-emerald-400'
                  }`}>
                    {item.ecartValeur !== 0 ? item.ecartValeur.toLocaleString() : '-'}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.status === 'VALIDE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {item.status === 'VALIDE' ? '✓ Conforme' : '⚠️ Écart'}
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

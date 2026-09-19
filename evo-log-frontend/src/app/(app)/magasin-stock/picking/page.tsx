'use client';

import React, { useState } from 'react';
import {
  Layers, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Package, MapPin, User, ArrowRight, Printer
} from 'lucide-react';
import { toast } from 'sonner';

interface PickingOrder {
  id: string;
  orderNumber: string;
  client: string;
  destination: string;
  itemsCount: number;
  totalWeightKg: number;
  priority: 'URGENT' | 'NORMAL' | 'BASSE';
  status: 'A_PREPARER' | 'EN_COURS' | 'TERMINE';
  picker: string;
  rule: 'FIFO' | 'FEFO';
}

const PICKING_DATA: PickingOrder[] = [
  { id: '1', orderNumber: 'PC-2026-0412', client: 'TOTAL Cameroun S.A.', destination: 'Dépôt N\'Djamena', itemsCount: 12, totalWeightKg: 14500, priority: 'URGENT', status: 'EN_COURS', picker: 'Moïse Talla', rule: 'FIFO' },
  { id: '2', orderNumber: 'PC-2026-0411', client: 'SABC Boissons', destination: 'Usine Koumassi', itemsCount: 4, totalWeightKg: 8200, priority: 'NORMAL', status: 'A_PREPARER', picker: 'Non Assigné', rule: 'FEFO' },
  { id: '3', orderNumber: 'PC-2026-0410', client: 'CIMENCAM', destination: 'Site Bonabéri', itemsCount: 8, totalWeightKg: 24000, priority: 'NORMAL', status: 'TERMINE', picker: 'Samuel Eto', rule: 'FIFO' },
];

export default function MagasinStockPicking() {
  const [orders, setOrders] = useState<PickingOrder[]>(PICKING_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = orders.filter(o =>
    o.orderNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.picker.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Préparation de Commandes & Vagues WMS
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KMAG_PIK
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Layers className="w-8 h-8 text-amber-400" />
            Ordres de Picking & Sorties FIFO
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Génération des bordereaux de prélèvement, guidage cariste dans les allées et allotissement quai expédition.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Génération d une nouvelle vague de préparation')}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Nouvelle Vague Picking
          </button>
        </div>
      </div>

      {/* Table Picking */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher ordre, client, préparateur..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">N° Ordre</th>
                <th className="py-3.5 px-4">Client & Destination</th>
                <th className="py-3.5 px-4 text-center">Colis / Lignes</th>
                <th className="py-3.5 px-4 text-right">Poids Total</th>
                <th className="py-3.5 px-4">Règle</th>
                <th className="py-3.5 px-4">Préparateur</th>
                <th className="py-3.5 px-4 text-center">Priorité</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(o => (
                <tr key={o.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-amber-400">{o.orderNumber}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-sans text-slate-100 font-bold">{o.client}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{o.destination}</div>
                  </td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-200">{o.itemsCount} lignes</td>
                  <td className="py-3.5 px-4 text-right text-slate-300">{o.totalWeightKg.toLocaleString()} kg</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 border border-slate-700 text-amber-300">
                      {o.rule}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{o.picker}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      o.priority === 'URGENT' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {o.priority}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      o.status === 'TERMINE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      o.status === 'EN_COURS' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {o.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => toast.success(`Impression de la fiche de prélèvement ${o.orderNumber}`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg mx-auto"
                      title="Imprimer Fiche"
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

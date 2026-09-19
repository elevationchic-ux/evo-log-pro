'use client';

import React, { useState } from 'react';
import { Wrench, Plus, Search, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import { toast } from 'sonner';

interface MaintenanceOrder {
  id: string;
  orderCode: string;
  vehiclePlate: string;
  vehicleType: string;
  orderType: 'PREVENTIF' | 'CORRECTIF';
  operations: string[];
  technicien: string;
  plannedDate: string;
  currentKm: number;
  targetKm: number;
  status: 'PLANIFIE' | 'EN_COURS' | 'TERMINE';
}

const MAINTENANCE_ORDERS: MaintenanceOrder[] = [
  {
    id: '1', orderCode: 'OT-PREV-2026-0841', vehiclePlate: 'CMR-TK-4521', vehicleType: 'Tracteur SCANIA R540',
    orderType: 'PREVENTIF', operations: ['Vidange huile moteur 10W40 + filtre', 'Contrôle pression pneumatiques', 'Graissage cardan et croisillons'],
    technicien: 'Jean-Paul Bekono', plannedDate: '28/08/2026', currentKm: 289500, targetKm: 290000, status: 'PLANIFIE'
  },
  {
    id: '2', orderCode: 'OT-CORR-2026-0839', vehiclePlate: 'CMR-TK-4518', vehicleType: 'Remorque FRUEHAUF 40T',
    orderType: 'CORRECTIF', operations: ['Remplacement plateau de frein (rupture)', 'Réglage timonerie de frein'],
    technicien: 'Thierry Ndzengue', plannedDate: '27/08/2026', currentKm: 157200, targetKm: 157200, status: 'EN_COURS'
  },
  {
    id: '3', orderCode: 'OT-PREV-2026-0835', vehiclePlate: 'CMR-TK-4509', vehicleType: 'Tracteur MERCEDES Actros',
    orderType: 'PREVENTIF', operations: ['Vidange + filtre à air', 'Remplacement courroie de distribution', 'Contrôle embrayage'],
    technicien: 'Jean-Paul Bekono', plannedDate: '25/08/2026', currentKm: 420000, targetKm: 420000, status: 'TERMINE'
  },
];

export default function ParcVehiculesPreventiveMaintenance() {
  return <div className="p-8 text-center text-slate-400">La maintenance préventive attend un endpoint GMAO persistant. Les ordres de démonstration sont désactivés.</div>;
  /*
  const [orders] = useState<MaintenanceOrder[]>(MAINTENANCE_ORDERS);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = orders.filter(o =>
    o.vehiclePlate.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.orderCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.technicien.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header * /}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              GMAO - Maintenance Préventive & Corrective
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KVEH_MNT
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Wrench className="w-8 h-8 text-amber-400" />
            Ordres de Travail GMAO
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Planification des entretiens préventifs par seuils kilométriques, gestion des pannes et suivi en temps réel de l atelier mécanique.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.success('Génération automatique des OT préventifs du mois')}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-600 to-orange-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Générer OT Préventifs
          </button>
        </div>
      </div>

      {/* Table OT * /}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par véhicule, code OT ou technicien..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Code OT & Véhicule</th>
                <th className="py-3.5 px-4">Opérations</th>
                <th className="py-3.5 px-4">Technicien</th>
                <th className="py-3.5 px-4">Date Planifiée</th>
                <th className="py-3.5 px-4 text-center">Type</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(o => (
                <tr key={o.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-amber-400">{o.orderCode}</div>
                    <div className="font-sans font-bold text-slate-100 mt-0.5">{o.vehiclePlate}</div>
                    <div className="text-[11px] text-slate-400 font-sans">{o.vehicleType}</div>
                    <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                      {o.currentKm.toLocaleString()} km / Seuil: {o.targetKm.toLocaleString()} km
                    </div>
                  </td>
                  <td className="py-3.5 px-4 max-w-[240px]">
                    <ul className="space-y-0.5">
                      {o.operations.map((op, i) => (
                        <li key={i} className="text-[11px] text-slate-300 font-sans flex items-start gap-1">
                          <span className="text-amber-400 mt-0.5 shrink-0">•</span> {op}
                        </li>
                      ))}
                    </ul>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{o.technicien}</td>
                  <td className="py-3.5 px-4 text-slate-400">{o.plannedDate}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      o.orderType === 'PREVENTIF' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      'bg-red-500/10 text-red-400 border border-red-500/20'
                    }`}>
                      {o.orderType}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      o.status === 'TERMINE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      o.status === 'EN_COURS' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {o.status}
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
  */
}

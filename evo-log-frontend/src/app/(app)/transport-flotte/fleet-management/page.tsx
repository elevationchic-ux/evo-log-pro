'use client';

import React, { useState } from 'react';
import {
  Truck, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, Wrench, Calendar, Gauge, ShieldCheck, DollarSign
} from 'lucide-react';
import { toast } from 'sonner';

interface Vehicle {
  id: string;
  immatriculation: string;
  type: 'TRACTEUR' | 'SEMI_REMORQUE' | 'PORTEUR' | 'REACHSTACKER';
  brandModel: string;
  year: number;
  odometer: number;
  technicalInspectionDate: string;
  insuranceDate: string;
  tcoMonthly: number;
  status: 'OPERATIONNEL' | 'EN_MAINTENANCE' | 'IMMOBILISE';
}

const FLEET_DATA: Vehicle[] = [];

export default function TransportFlotteFleetManagement() {
  const [fleet, setFleet] = useState<Vehicle[]>(FLEET_DATA);
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = fleet.filter(v =>
    v.immatriculation.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.brandModel.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-blue-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Gestion de Parc & Fiche Véhicule
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KTRN_FLT
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Truck className="w-8 h-8 text-blue-400" />
            Parc Véhicules & Suivi TCO
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Inventaire des tracteurs, remorques, visites techniques, coûts de détention (TCO) et planification GMAO.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Formulaire d ajout d un véhicule à la flotte')}
            className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-blue-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Ajouter Véhicule
          </button>
        </div>
      </div>

      {/* Table Flotte */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par immatriculation ou modèle..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Immatriculation</th>
                <th className="py-3.5 px-4">Type & Marque/Modèle</th>
                <th className="py-3.5 px-4 text-right">Kilométrage</th>
                <th className="py-3.5 px-4">Visite Technique</th>
                <th className="py-3.5 px-4">Assurance</th>
                <th className="py-3.5 px-4 text-right">TCO Moyen / Mois</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(v => (
                <tr key={v.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-blue-400 text-sm">{v.immatriculation}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-100">
                    <div className="font-bold">{v.brandModel}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{v.type} • Année {v.year}</div>
                  </td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-200">{v.odometer.toLocaleString()} km</td>
                  <td className="py-3.5 px-4 text-slate-300">{v.technicalInspectionDate}</td>
                  <td className="py-3.5 px-4 text-slate-300">{v.insuranceDate}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-emerald-400">{v.tcoMonthly.toLocaleString()} XAF</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      v.status === 'OPERATIONNEL' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      v.status === 'EN_MAINTENANCE' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-red-500/10 text-red-400 border border-red-500/20'
                    }`}>
                      {v.status}
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

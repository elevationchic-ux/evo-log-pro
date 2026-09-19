'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Fuel, ArrowLeft, Download, Search, RefreshCw,
  TrendingDown, TrendingUp, AlertTriangle, CheckCircle2, Truck
} from 'lucide-react';

interface FuelHistoryRecord {
  id: number;
  camion: string;
  periode: string;
  litres_totaux: number;
  km_parcourus: number;
  conso_moyenne_l100: number;
  cout_total_xaf: number;
  statut: 'NORMAL' | 'SURCONSOMMATION';
}

export default function TransportFuelHistoryPage() {
  const [records, setRecords] = useState<FuelHistoryRecord[]>([
    {
      id: 1,
      camion: 'LT 912 AB (Mercedes Actros 3340)',
      periode: 'Août 2026',
      litres_totaux: 2450,
      km_parcourus: 6800,
      conso_moyenne_l100: 36.0,
      cout_total_xaf: 2028600,
      statut: 'NORMAL'
    },
    {
      id: 2,
      camion: 'LT 842 BC (Volvo FH16 540)',
      periode: 'Août 2026',
      litres_totaux: 3100,
      km_parcourus: 6200,
      conso_moyenne_l100: 50.0,
      cout_total_xaf: 2566800,
      statut: 'SURCONSOMMATION'
    },
    {
      id: 3,
      camion: 'LT 319 DE (Renault Kerax 440)',
      periode: 'Août 2026',
      litres_totaux: 1890,
      km_parcourus: 5100,
      conso_moyenne_l100: 37.1,
      cout_total_xaf: 1564920,
      statut: 'NORMAL'
    }
  ]);
  const [search, setSearch] = useState('');

  const filtered = records.filter(r =>
    r.camion.toLowerCase().includes(search.toLowerCase()) ||
    r.periode.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/transport-flotte" className="hover:text-amber-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Transport & Flotte
        </Link>
        <span>/</span>
        <span className="text-white">Historique & Analyse des Consommations Carburant</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Fuel className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Historique Carburant & Télémétrie FuelGuard
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-mono">
                KTRN_HST
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Analyse mensuelle de la consommation par tracteur, détection des siphonnages et optimisation des coûts d'énergie
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => alert('Exportation du rapport de consommation mensuel au format Excel...')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-sm shadow-lg shadow-amber-600/30 transition"
          >
            <Download className="w-4 h-4" />
            Exporter Rapport Carburant
          </button>
        </div>
      </div>

      {/* Main Table card */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Rechercher par véhicule ou période..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="py-3 px-4 rounded-l-xl">Véhicule Flotte</th>
                <th className="py-3 px-4">Période</th>
                <th className="py-3 px-4">Litrages Pompés</th>
                <th className="py-3 px-4">Kilométrage</th>
                <th className="py-3 px-4">Moyenne L/100km</th>
                <th className="py-3 px-4">Coût Total (XAF)</th>
                <th className="py-3 px-4 rounded-r-xl">Diagnostic FuelGuard</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filtered.map(r => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 px-4 font-semibold text-white">
                    {r.camion}
                  </td>
                  <td className="py-3.5 px-4 text-xs text-slate-300">
                    {r.periode}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs text-white">
                    {r.litres_totaux.toLocaleString()} L
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs text-slate-400">
                    {r.km_parcourus.toLocaleString()} km
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs font-bold text-white">
                    {r.conso_moyenne_l100} L/100km
                  </td>
                  <td className="py-3.5 px-4 font-mono text-xs text-amber-400 font-bold">
                    {r.cout_total_xaf.toLocaleString()} XAF
                  </td>
                  <td className="py-3.5 px-4">
                    {r.statut === 'SURCONSOMMATION' ? (
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20 flex items-center gap-1 w-fit">
                        <AlertTriangle className="w-3 h-3" />
                        Alerte Surconsommation (+38%)
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                        <CheckCircle2 className="w-3 h-3" />
                        Conforme Norme Constructeur
                      </span>
                    )}
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

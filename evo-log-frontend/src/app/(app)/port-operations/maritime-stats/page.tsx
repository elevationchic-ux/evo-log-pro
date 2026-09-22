'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  BarChart3, ArrowLeft, Download, RefreshCw, Calendar,
  Ship, Anchor, Clock, ArrowUpRight, CheckCircle2
} from 'lucide-react';

export default function PortOperationsMaritimeStatsPage() {
  const [periode, setPeriode] = useState('CE_MOIS');
  const [portFiltre, setPortFiltre] = useState('ALL');

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Opérations Portuaires
        </Link>
        <span>/</span>
        <span className="text-white">Statistiques de Rendement & Cadences</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-violet-500/10 text-violet-400 rounded-xl border border-violet-500/20">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Statistiques Maritimes & Ratios de Manutention
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/30 font-mono">
                KACC_STA
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Analyse des cadences horaires portiques, temps d'attente en rade, séjour à quai et tonnage
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={portFiltre}
            onChange={e => setPortFiltre(e.target.value)}
            className="px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-violet-500"
          >
            <option value="ALL">Tous les terminaux (PAD & PAK)</option>
            <option value="DOUALA">Douala - Quai 14</option>
            <option value="KRIBI">Kribi - Port Mboro</option>
          </select>
          <button
            onClick={() => alert('Export du rapport analytique maritime sous format Excel / PDF généré avec succès.')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium text-sm shadow-lg shadow-violet-600/30 transition"
          >
            <Download className="w-4 h-4" />
            Exporter Rapport
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Cadence Moyenne Grues</span>
          <p className="text-2xl font-bold text-white mt-1">24.6 <span className="text-sm font-normal text-slate-400">mvts/h</span></p>
          <span className="text-xs text-emerald-400 mt-1 block">Objectif contractuel : 22 mvts/h</span>
        </div>
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Attente Rade Moyenne</span>
          <p className="text-2xl font-bold text-amber-400 mt-1">14.2 <span className="text-sm font-normal text-slate-400">heures</span></p>
          <span className="text-xs text-slate-400 mt-1 block">Rade de Douala / Kribi</span>
        </div>
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Temps Séjour à Quai</span>
          <p className="text-2xl font-bold text-blue-400 mt-1">36.8 <span className="text-sm font-normal text-slate-400">heures</span></p>
          <span className="text-xs text-emerald-400 mt-1 block">-12% par rapport au mois passé</span>
        </div>
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Volume EVP Traité</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1">18,450 <span className="text-sm font-normal text-slate-400">EVP</span></p>
          <span className="text-xs text-slate-400 mt-1 block">72% Pleins • 28% Vides</span>
        </div>
      </div>

      {/* Grid Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
          <h3 className="text-base font-semibold text-white mb-4 flex items-center justify-between">
            <span>Rendement par Poste d'Accostage</span>
            <span className="text-xs text-slate-400">Derniers 30 jours</span>
          </h3>
          <div className="space-y-4">
            {[
              { quai: 'Quai 14 - Terminal Conteneurs Douala', cadence: '26.2 mvts/h', pct: 88, navires: 14 },
              { quai: 'Quai 13 - Polyvalent Douala', cadence: '18.4 mvts/h', pct: 62, navires: 8 },
              { quai: 'Poste Mboro 01 - Eau Profonde Kribi', cadence: '29.5 mvts/h', pct: 95, navires: 11 },
              { quai: 'Poste Mboro 02 - Polyvalent Kribi', cadence: '21.0 mvts/h', pct: 70, navires: 6 },
            ].map((item, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="font-medium text-white">{item.quai}</span>
                  <span className="text-violet-400 font-mono font-bold">{item.cadence} ({item.navires} navires)</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-violet-500 rounded-full" style={{ width: `${item.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
          <h3 className="text-base font-semibold text-white mb-4 flex items-center justify-between">
            <span>Répartition par Ligne Maritime</span>
            <span className="text-xs text-slate-400">Parts de marché</span>
          </h3>
          <div className="space-y-3">
            {[
              { ligne: 'CMA CGM', volume: '7,200 EVP', share: '39%' },
              { ligne: 'MAERSK LINE', volume: '5,100 EVP', share: '28%' },
              { ligne: 'MSC (Mediterranean Shipping Co)', volume: '3,800 EVP', share: '21%' },
              { ligne: 'GRIMALDI LINES', volume: '1,450 EVP', share: '8%' },
              { ligne: 'HAPAG-LLOYD', volume: '900 EVP', share: '4%' },
            ].map((l, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/40 rounded-xl border border-slate-800">
                <div>
                  <p className="font-semibold text-white text-sm">{l.ligne}</p>
                  <p className="text-xs text-slate-400">{l.volume}</p>
                </div>
                <span className="text-sm font-bold text-violet-400 font-mono">{l.share}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
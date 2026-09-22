'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  BarChart3, ArrowLeft, Download, RefreshCw, Filter,
  Ship, Truck, Box, CheckCircle2, Clock, Activity, ArrowRight
} from 'lucide-react';

export default function ReportsBiOperationalAnalyticsPage() {
  const [corridor, setCorridor] = useState('ALL');

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/reports-bi" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> BI & Tableaux de Bord
        </Link>
        <span>/</span>
        <span className="text-white">Analytique Opérationnelle End-to-End</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Analytique Opérationnelle Pipeline Navire → Client
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 font-mono">
                KBI_OPS
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Mesure des délais de passage portuaire, transit des corridors CEMAC et productivité logistique globale
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={corridor}
            onChange={e => setCorridor(e.target.value)}
            className="px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">Tous les corridors</option>
            <option value="DLA_NDJ">Corridor Douala → N'Djamena (Tchad)</option>
            <option value="DLA_BGF">Corridor Douala → Bangui (RCA)</option>
            <option value="KRI_HINT">Corridor Kribi → Yaoundé / Hinterland</option>
          </select>
          <button
            onClick={() => alert('Génération du rapport de performance opérationnelle en cours...')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm shadow-lg shadow-indigo-600/30 transition"
          >
            <Download className="w-4 h-4" />
            Exporter
          </button>
        </div>
      </div>

      {/* KPI Pipeline End to End */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Temps Séjour Quai (Dwell Time)</span>
          <p className="text-3xl font-extrabold text-white mt-1 font-mono">5.2 <span className="text-sm font-normal text-slate-400">jours</span></p>
          <span className="text-xs text-emerald-400 mt-1 block">-1.1 jour vs moyenne PAD</span>
        </div>
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Dédouanement CAMCIS Moyen</span>
          <p className="text-3xl font-extrabold text-emerald-400 mt-1 font-mono">48 <span className="text-sm font-normal text-slate-400">heures</span></p>
          <span className="text-xs text-slate-400 mt-1 block">Du dépôt au BAE douane</span>
        </div>
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Délai Acheminement Corridor</span>
          <p className="text-3xl font-extrabold text-blue-400 mt-1 font-mono">8.4 <span className="text-sm font-normal text-slate-400">jours</span></p>
          <span className="text-xs text-blue-400 mt-1 block">Douala → N'Djamena (1 850 km)</span>
        </div>
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Taux de Service Client (OTIF)</span>
          <p className="text-3xl font-extrabold text-purple-400 mt-1 font-mono">96.8%</p>
          <span className="text-xs text-purple-400 mt-1 block">On-Time In-Full</span>
        </div>
      </div>

      {/* Operational Flow Pipeline */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <h2 className="text-lg font-semibold text-white mb-2">Cycle Logistique End-to-End • Navire → Client</h2>
        <p className="text-xs text-slate-400 mb-6">Suivi chronologique des étapes d'exécution et taux de conformité</p>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[
            { step: '1. Débarquement Quai', icon: Ship, time: '24-36h', status: 'Optimal', count: '14 Navires' },
            { step: '2. Dédouanement Douane', icon: Box, time: '48h', status: 'Conforme', count: '128 Dossiers' },
            { step: '3. Entreposage MAD', icon: Activity, time: '3-5 jours', status: 'En cours', count: '450 TC en stock' },
            { step: '4. Transport Routier', icon: Truck, time: '2-8 jours', status: 'Actif', count: '38 Convois' },
            { step: '5. e-POD & Clôture', icon: CheckCircle2, time: 'Immédiat', status: '98% OTIF', count: '342 BLs signés' },
          ].map((s, idx) => {
            const Icon = s.icon;
            return (
              <div key={idx} className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-indigo-400">{s.step}</span>
                    <Icon className="w-4 h-4 text-slate-400" />
                  </div>
                  <p className="text-lg font-bold text-white mt-2">{s.count}</p>
                </div>
                <div className="mt-4 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <span>Délai : {s.time}</span>
                  <span className="text-emerald-400 font-semibold">{s.status}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

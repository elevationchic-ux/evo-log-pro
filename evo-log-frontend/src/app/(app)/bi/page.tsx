'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { biAnalyticsAPI } from '@/lib/api-client';
import { BarChart3, TrendingUp, DollarSign, Package, Truck, Percent, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function BiAnalyticsPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['bi-summary'],
    queryFn: async () => {
      const res = await biAnalyticsAPI.getSummary();
      return res.data;
    },
    enabled: mounted,
  });

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Analytics BI...</div>;

  const summary = data || {
    chiffre_affaires_cumule_xaf: 142500000.0,
    marge_brute_globale_pct: 22.4,
    volume_fret_evp: 1280,
    taux_livraison_ponctuel_pct: 97.8,
    economie_carburant_xaf: 8400000.0
  };

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-fuchsia-500/10 text-fuchsia-400 text-xs font-semibold mb-2 border border-fuchsia-500/20">
            <BarChart3 className="w-3.5 h-3.5" />
            K-Analytics • Business Intelligence Executive C-Level
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Tableaux de Bord Décisionnels BI</h1>
          <p className="text-slate-400 text-sm mt-1">Analyse de rentabilité, marge contributive et KPIs opérationnels en temps réel.</p>
        </div>

        <Link
          href="/bi/margins"
          className="inline-flex items-center justify-center gap-2 bg-fuchsia-600 hover:bg-fuchsia-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-fuchsia-600/30 transition-all hover:scale-[1.02]"
        >
          <TrendingUp className="w-4 h-4" />
          Analyse des Marges
        </Link>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-2xl flex items-center justify-center mb-3">
            <DollarSign className="w-6 h-6" />
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Chiffre d'Affaires Cumulé</p>
          <h2 className="text-2xl font-black text-slate-100 font-mono">
            {Number(summary.chiffre_affaires_cumule_xaf).toLocaleString()} XAF
          </h2>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div className="w-12 h-12 bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20 rounded-2xl flex items-center justify-center mb-3">
            <Percent className="w-6 h-6" />
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Marge Brute Globale</p>
          <h2 className="text-2xl font-black text-fuchsia-400 font-mono">
            {summary.marge_brute_globale_pct}%
          </h2>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div className="w-12 h-12 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded-2xl flex items-center justify-center mb-3">
            <Package className="w-6 h-6" />
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Volume Fret Traité</p>
          <h2 className="text-2xl font-black text-slate-100 font-mono">
            {summary.volume_fret_evp} EVP
          </h2>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div className="w-12 h-12 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-2xl flex items-center justify-center mb-3">
            <Truck className="w-6 h-6" />
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Économie Carburant IoT</p>
          <h2 className="text-2xl font-black text-emerald-400 font-mono">
            +{Number(summary.economie_carburant_xaf).toLocaleString()} XAF
          </h2>
        </div>
      </div>
    </div>
  );
}

'use client';

import React from 'react';
import { BarChart3, TrendingUp, Activity, Globe, DollarSign, Package, Truck } from 'lucide-react';
import { toast } from 'sonner';

export default function ReportsBIExecutiveDashboard() {
  const kpiCards = [
    { label: "Chiffre d'Affaires Mensuel", value: '1,284,500,000 XAF', trend: '+12.4%', positive: true, icon: DollarSign },
    { label: 'Tonnage Manutentionné', value: '84,200 T', trend: '+8.1%', positive: true, icon: Package },
    { label: 'Taux de Service OTIF', value: '94.8%', trend: '+1.2 pts', positive: true, icon: Activity },
    { label: 'DSO Délai Règlement Client', value: '42 jours', trend: '-3 jours', positive: true, icon: TrendingUp },
    { label: 'Missions Transport Effectuées', value: '1,847', trend: '+15.7%', positive: true, icon: Truck },
    { label: 'Taux d Occupation MAG3', value: '78.4%', trend: '-2.1%', positive: false, icon: BarChart3 },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="bg-slate-900/90 border border-indigo-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            Direction Générale & Pilotage Stratégique
          </span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
            T-Code : KBI_DSH
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-indigo-400" />
          Executive Dashboard  Direction Générale EVO-LOG
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Tableau de bord de pilotage stratégique consolidant les KPIs de tous les pôles métiers (Finance, Transport, Magasin, Transit).
        </p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {kpiCards.map((kpi, i) => {
          const IconCmp = kpi.icon;
          return (
            <div key={i} className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{kpi.label}</div>
                  <div className="text-xl font-black text-slate-100 font-mono">{kpi.value}</div>
                </div>
                <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <IconCmp className="w-5 h-5" />
                </div>
              </div>
              <div className={`text-xs font-bold mt-2 ${kpi.positive ? 'text-emerald-400' : 'text-red-400'}`}>
                {kpi.positive ? '▲' : '▼'} {kpi.trend} vs mois précédent
              </div>
            </div>
          );
        })}
      </div>

      {/* Table Activité par Module */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Activité Consolidée par Pôle Métier  Août 2026
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Pôle Métier</th>
                <th className="py-3.5 px-4 text-right">CA Réalisé (XAF)</th>
                <th className="py-3.5 px-4 text-right">Budget Mensuel (XAF)</th>
                <th className="py-3.5 px-4 text-right">Taux de Réalisation</th>
                <th className="py-3.5 px-4 text-center">Tendance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {[
                { pole: '🚢 Opérations Portuaires', ca: 542000000, budget: 500000000, rate: 108.4, trend: '▲' },
                { pole: '🚛 Transport & Corridors CEMAC', ca: 384000000, budget: 400000000, rate: 96.0, trend: '◇' },
                { pole: '🛃 Transit & Douane', ca: 198000000, budget: 180000000, rate: 110.0, trend: '▲' },
                { pole: '📦 Magasin WMS MAG3', ca: 87500000, budget: 90000000, rate: 97.2, trend: '◇' },
                { pole: '💰 Finance & Comptabilité', ca: 73000000, budget: 70000000, rate: 104.3, trend: '▲' },
              ].map((row, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-sans font-bold text-slate-100">{row.pole}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-emerald-400">{row.ca.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right text-slate-300">{row.budget.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right">
                    <span className={`font-bold ${row.rate >= 100 ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {row.rate}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center text-lg">
                    <span className={row.trend === '▲' ? 'text-emerald-400' : 'text-amber-400'}>{row.trend}</span>
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

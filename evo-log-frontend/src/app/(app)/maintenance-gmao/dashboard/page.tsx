'use client';

import React, { useState } from 'react';
import {
  Wrench, AlertTriangle, CheckCircle2, Clock, BarChart3,
  Truck, Zap, Calendar, Plus, Eye, Activity, TrendingDown,
  Shield, RefreshCw, FileText, Settings
} from 'lucide-react';
import { toast } from 'sonner';

export default function MaintenanceGMAODashboardPage() {
  const [selectedEngin, setSelectedEngin] = useState<string | null>(null);
  const [tab, setTab] = useState<'dashboard' | 'preventive' | 'corrective'>('dashboard');

  const fleet: Array<any> = [];

  const preventivePlans: Array<any> = [];

  const correctiveOrders: Array<any> = [];

  const selected = fleet.find(f => f.id === selectedEngin);

  const statutColors: Record<string, string> = {
    'BON ÉTAT': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'ALERTE': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    'CRITIQUE': 'bg-red-500/10 text-red-400 border-red-500/30',
    'PLANIFIÉ': 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    'URGENT': 'bg-red-500/10 text-red-400 border-red-500/30',
    'EN COURS': 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    'EN ATTENTE PIÈCES': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  };

  const globalKpis = [
    { label: 'Flotte Disponible', value: `${fleet.filter(f => f.statut === 'BON ÉTAT').length}/${fleet.length}`, icon: Truck, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
    { label: 'OT Ouverts', value: correctiveOrders.length, icon: Wrench, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
    { label: 'PM Planifiés (30j)', value: preventivePlans.length, icon: Calendar, color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
    { label: 'TCO Global', value: '—', icon: TrendingDown, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Wrench className="w-6 h-6 text-amber-400" /> Maintenance GMAO  Parc Véhicules & Engins
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Préventive planifiée · Corrective OT · MTBF/MTTR · TCO · Certification MINTT/MINTP</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => toast.info('Créer Ordre de Travail corrective')} className="px-4 py-2.5 bg-slate-800 border border-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2">
            <Plus className="w-4 h-4" /> Ordre de Travail
          </button>
          <button onClick={() => toast.info('Planifier maintenance préventive')} className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg">
            <Calendar className="w-4 h-4" /> Planifier PM
          </button>
        </div>
      </div>

      {/* Global KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        {globalKpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div key={i} className={`${kpi.bg} border rounded-2xl p-4`}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${kpi.color}`} />
                <span className="text-xs text-slate-400 truncate">{kpi.label}</span>
              </div>
              <div className={`text-2xl font-black font-mono ${kpi.color}`}>{kpi.value}</div>
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: 'dashboard', label: 'État de la Flotte' },
          { id: 'preventive', label: 'Plans Maintenance' },
          { id: 'corrective', label: 'Ordres de Travail' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id as any)} className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${tab === t.id ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30' : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Fleet Tab */}
      {tab === 'dashboard' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* List */}
          <div className="space-y-2">
            {fleet.map(v => (
              <button key={v.id} onClick={() => setSelectedEngin(v.id)} className={`w-full text-left p-4 rounded-2xl border transition-all ${selectedEngin === v.id ? 'bg-amber-500/10 border-amber-500/40' : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-black text-white font-mono">{v.immat}</span>
                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${statutColors[v.statut]}`}>{v.statut}</span>
                </div>
                <div className="text-[11px] text-slate-400">{v.model}</div>
                {v.alertes.length > 0 && (
                  <div className="mt-1 flex items-center gap-1 text-[10px] text-amber-400">
                    <AlertTriangle className="w-3 h-3" /> {v.alertes.length} alerte{v.alertes.length > 1 ? 's' : ''}
                  </div>
                )}
                {/* Availability bar */}
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div className={`h-full rounded-full ${v.disponibilite > 90 ? 'bg-emerald-500' : v.disponibilite > 80 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${v.disponibilite}%` }}></div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">{v.disponibilite}%</span>
                </div>
              </button>
            ))}
          </div>

          {/* Detail */}
          <div className="lg:col-span-2">
            {selected ? (
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl space-y-5">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-black text-white font-mono">{selected.immat}</h2>
                    <p className="text-xs text-slate-400">{selected.model}</p>
                  </div>
                  <span className={`text-[11px] font-bold px-3 py-1 rounded-full border ${statutColors[selected.statut]}`}>{selected.statut}</span>
                </div>

                {/* KPIs */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { label: 'Km Total', value: selected.km.toLocaleString() + ' km', icon: Activity },
                    { label: 'MTBF', value: selected.mtbf + ' h', icon: Shield },
                    { label: 'MTTR', value: selected.mttr + ' h', icon: Wrench },
                    { label: 'Disponibilité', value: selected.disponibilite + '%', icon: CheckCircle2 },
                  ].map((m, i) => {
                    const Icon = m.icon;
                    return (
                      <div key={i} className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-center">
                        <Icon className="w-4 h-4 text-amber-400 mx-auto mb-1" />
                        <div className="text-sm font-black text-white font-mono">{m.value}</div>
                        <div className="text-[10px] text-slate-500">{m.label}</div>
                      </div>
                    );
                  })}
                </div>

                {/* Alerts */}
                {selected.alertes.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-xs font-bold text-slate-300 uppercase">Alertes Maintenance</div>
                    {selected.alertes.map((alert: string, i: number) => (
                      <div key={i} className="flex items-center gap-2 p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl text-xs text-amber-300">
                        <AlertTriangle className="w-4 h-4 shrink-0" /> {alert}
                      </div>
                    ))}
                  </div>
                )}

                {/* Upcoming maintenance */}
                <div className="p-4 bg-blue-500/5 border border-blue-500/20 rounded-xl">
                  <div className="text-xs font-bold text-blue-300 mb-1">Prochaines Échéances</div>
                  {selected.km > 0 && (
                    <div className="text-[11px] text-slate-300">
                      Prochaine vidange : à <strong className="font-mono text-amber-300">{selected.prochaineVidange.toLocaleString()} km</strong> (dans {(selected.prochaineVidange - selected.km).toLocaleString()} km)
                    </div>
                  )}
                  <div className="text-[11px] text-slate-300 mt-0.5">
                    Contrôle Technique MINTT : <strong className="font-mono text-amber-300">{selected.prochainCT}</strong>
                  </div>
                  <div className="text-[11px] text-slate-300 mt-0.5">
                    TCO Total : <strong className="font-mono text-amber-300">{(selected.tco / 1000000).toFixed(2)} M XAF</strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center justify-center h-full">
                <div className="text-center text-slate-500 py-12">
                  <Wrench className="w-10 h-10 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">Sélectionnez un engin</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Preventive Plans */}
      {tab === 'preventive' && (
        <div className="space-y-3">
          {preventivePlans.map((pm: any) => (
            <div key={pm.ref} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs font-black text-amber-300">{pm.ref}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${statutColors[pm.statut]}`}>{pm.statut}</span>
                  </div>
                  <div className="text-sm font-bold text-white">{pm.type}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Engin : <strong className="text-slate-200">{pm.engin}</strong> • Planifié : {pm.planifie} • Durée : {pm.duree} • Tech : {pm.technicien}
                  </div>
                  {pm.pieces.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {pm.pieces.map((p: string, i: number) => (
                        <span key={i} className="text-[10px] font-mono bg-slate-800 border border-slate-700 text-slate-400 px-2 py-0.5 rounded">{p}</span>
                      ))}
                    </div>
                  )}
                </div>
                <button onClick={() => toast.success(`OT Maintenance ${pm.ref} validé`)} className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs rounded-xl hover:bg-emerald-500/20 shrink-0">
                  Valider PM
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Corrective OTs */}
      {tab === 'corrective' && (
        <div className="space-y-3">
          {correctiveOrders.map((ot: any) => (
            <div key={ot.ref} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs font-black text-amber-300">{ot.ref}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${statutColors[ot.statut]}`}>{ot.statut}</span>
                  </div>
                  <div className="text-sm font-bold text-white">{ot.panne}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Engin : <strong className="text-slate-200">{ot.engin}</strong> • Signalé : {ot.signale} • Immobilisé : {ot.tempsImmo}j • Tech : {ot.technicien}
                  </div>
                  {ot.pieces.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {ot.pieces.map((p: string, i: number) => (
                        <span key={i} className="text-[10px] font-mono bg-red-500/5 border border-red-500/20 text-red-400 px-2 py-0.5 rounded">{p}</span>
                      ))}
                    </div>
                  )}
                </div>
                <button onClick={() => toast.success(`OT ${ot.ref} clôturé`)} className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs rounded-xl hover:bg-emerald-500/20 shrink-0">
                  Clôturer OT
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

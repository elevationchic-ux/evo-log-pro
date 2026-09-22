'use client';

import React, { useState } from 'react';
import {
  Wrench, AlertTriangle, CheckCircle2, Clock, BarChart3,
  Truck, Zap, Calendar, Plus, Eye, Activity, TrendingDown,
  Shield, RefreshCw, FileText, Settings
} from 'lucide-react';
import { toast } from 'sonner';

export default function MaintenanceGMAODashboardPage() {
  const [selectedEngin, setSelectedEngin] = useState<string | null>('TRK-CM-001');
  const [tab, setTab] = useState<'dashboard' | 'preventive' | 'corrective'>('dashboard');

  const fleet = [
    {
      id: 'TRK-CM-001', immat: 'LT 2291 B', model: 'VOLVO FH 460 (2022)',
      km: 189420, prochaineVidange: 195000, prochainCT: '12/2026',
      mtbf: 1240, mttr: 3.2, tco: 4850000, disponibilite: 94.2,
      alertes: [], statut: 'BON ÉTAT',
    },
    {
      id: 'TRK-CM-002', immat: 'LT 8840 A', model: 'MAN TGX 18.440 (2021)',
      km: 267310, prochaineVidange: 270000, prochainCT: '03/2027',
      mtbf: 980, mttr: 4.1, tco: 6240000, disponibilite: 87.1,
      alertes: ['Vidange huile moteur dans 2,690 km', 'Plaquettes frein avant à contrôler'],
      statut: 'ALERTE',
    },
    {
      id: 'TRK-CM-003', immat: 'LT 4421 C', model: 'IVECO STRALIS (2023)',
      km: 145820, prochaineVidange: 150000, prochainCT: '06/2027',
      mtbf: 1580, mttr: 2.1, tco: 3420000, disponibilite: 97.8,
      alertes: [], statut: 'BON ÉTAT',
    },
    {
      id: 'TRK-CM-004', immat: 'LT 1109 B', model: 'MERCEDES ACTROS (2020)',
      km: 312890, prochaineVidange: 315000, prochainCT: '09/2026',
      mtbf: 720, mttr: 6.5, tco: 9800000, disponibilite: 78.3,
      alertes: ['CONTRÔLE TECHNIQUE EXPIRÉ  Renouvellement urgent !', 'Pneumatique AR droit à remplacer', 'Suspension cabine à inspecter'],
      statut: 'CRITIQUE',
    },
    {
      id: 'GRU-001', immat: 'CM GRU 01', model: 'Grue Mobile LIEBHERR LTM 1050 (2019)',
      km: 0, prochaineVidange: 0, prochainCT: '01/2027',
      mtbf: 2100, mttr: 8.4, tco: 15600000, disponibilite: 82.0,
      alertes: ['Certification levage à renouveler (MINTP) dans 45j'],
      statut: 'ALERTE',
    },
  ];

  const preventivePlans = [
    { ref: 'PM-2026-089', engin: 'LT 8840 A', type: 'Vidange & Filtres Moteur', planifie: '05/09/2026', duree: '4h', technicien: 'M. Bello Maintenance', statut: 'PLANIFIÉ', pieces: ['Huile 15W40  18L', 'Filtre huile', 'Filtre air', 'Filtre carburant'] },
    { ref: 'PM-2026-087', engin: 'LT 1109 B', type: 'Contrôle Technique MINTT (Urgent)', planifie: '02/09/2026', duree: '1 jour', technicien: 'Centre MINTT Douala', statut: 'URGENT', pieces: [] },
    { ref: 'PM-2026-085', engin: 'LT 2291 B', type: 'Révision 190,000 km (Complète)', planifie: '15/09/2026', duree: '2 jours', technicien: 'M. Bello + M. Manga', statut: 'PLANIFIÉ', pieces: ['Plaquettes frein', 'Disques AV', 'Courroie distribution', 'Batterie 24V'] },
    { ref: 'PM-2026-082', engin: 'CM GRU 01', type: 'Certification Levage MINTP + Épreuve Charge', planifie: '20/09/2026', duree: '1 jour', technicien: 'Bureau Véritas + MINTP', statut: 'PLANIFIÉ', pieces: [] },
  ];

  const correctiveOrders = [
    { ref: 'OT-2026-041', engin: 'LT 1109 B', panne: 'Fuite circuit hydraulique freinage AV', signale: '28/08/2026', technicien: 'M. Bello', statut: 'EN COURS', tempsImmo: 2.5, pieces: ['Joint hydraulique 18mm', 'Flexible frein AV G'] },
    { ref: 'OT-2026-039', engin: 'LT 8840 A', panne: 'Climatisation cabine en panne (compresseur)', signale: '25/08/2026', technicien: 'Prestataire Autocool DLA', statut: 'EN ATTENTE PIÈCES', tempsImmo: 5, pieces: ['Compresseur clim AC', 'Courroie AC'] },
  ];

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
    { label: 'TCO Global', value: '39.9 M XAF', icon: TrendingDown, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
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
          <button onClick={() => toast.error("La création d'ordres de travail n'est pas encore raccordée à l'API.")} className="px-4 py-2.5 bg-slate-800 border border-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2">
            <Plus className="w-4 h-4" /> Ordre de Travail
          </button>
          <button onClick={() => toast.error("La planification de maintenance préventive n'est pas encore raccordée à l'API.")} className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg">
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
                    {selected.alertes.map((alert, i) => (
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
          {preventivePlans.map(pm => (
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
                      {pm.pieces.map((p, i) => (
                        <span key={i} className="text-[10px] font-mono bg-slate-800 border border-slate-700 text-slate-400 px-2 py-0.5 rounded">{p}</span>
                      ))}
                    </div>
                  )}
                </div>
                <button onClick={() => toast.error("La validation des OT préventifs n'est pas encore raccordée à l'API.")} className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs rounded-xl hover:bg-emerald-500/20 shrink-0">
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
          {correctiveOrders.map(ot => (
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
                      {ot.pieces.map((p, i) => (
                        <span key={i} className="text-[10px] font-mono bg-red-500/5 border border-red-500/20 text-red-400 px-2 py-0.5 rounded">{p}</span>
                      ))}
                    </div>
                  )}
                </div>
                <button onClick={() => toast.error("La clôture des OT correctifs n'est pas encore raccordée à l'API.")} className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs rounded-xl hover:bg-emerald-500/20 shrink-0">
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

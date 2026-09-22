'use client';

import React, { useState } from 'react';
import {
  Users, UserPlus, TrendingUp, Clock, CalendarDays, FileText,
  Search, Eye, Edit3, Download, ChevronRight, Award, Phone,
  AlertTriangle, CheckCircle2, Briefcase, BarChart3
} from 'lucide-react';
import { toast } from 'sonner';

export default function RHDashboardPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'effectifs' | 'conges' | 'performances'>('effectifs');

  const kpis: Array<any> = [];

  const employees: Array<any> = [];

  const congesEnAttente: Array<any> = [];

  const deptRepartition: Array<any> = [];

  const filteredEmps = employees.filter(e =>
    !searchQuery ||
    e.nom.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.poste.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.dept.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const statutColors: Record<string, string> = {
    'ACTIF': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'CONGE': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    'SUSPENDU': 'bg-red-500/10 text-red-400 border-red-500/30',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Users className="w-6 h-6 text-amber-400" /> Ressources Humaines & Paie
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Gestion effectifs · Congés · Paie IRPP/CNPS/CAC/FNE · Bulletins · Déclarations DIPE</p>
        </div>
        <button
          onClick={() => toast.info('Formulaire recrutement / nouvel employé')}
          className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg"
        >
          <UserPlus className="w-4 h-4" /> Nouvel Employé
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        {kpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div key={i} className={`${kpi.bg} border rounded-2xl p-4 shadow`}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${kpi.color}`} />
                <span className="text-xs text-slate-400 truncate">{kpi.label}</span>
              </div>
              <div className={`text-xl font-black font-mono ${kpi.color}`}>{kpi.value}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">{kpi.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Dept Repartition */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow">
        <h2 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-blue-400" /> Répartition par Département
        </h2>
        <div className="space-y-2.5">
          {deptRepartition.map((d, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="w-40 text-[11px] text-slate-400 shrink-0 truncate">{d.dept}</div>
              <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className={`h-full ${d.color} rounded-full`} style={{ width: `${d.pct}%` }}></div>
              </div>
              <span className="text-[11px] font-mono text-slate-300 w-12 text-right">{d.count} emp.</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: 'effectifs', label: 'Annuaire Employés' },
          { id: 'conges', label: 'Demandes Congés en Attente' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${activeTab === tab.id ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30' : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'}`}
          >
            {tab.label} {tab.id === 'conges' && <span className="ml-1 bg-amber-500 text-slate-950 rounded-full px-1.5 py-0.5 text-[9px] font-black">{congesEnAttente.length}</span>}
          </button>
        ))}
      </div>

      {/* Employee Table */}
      {activeTab === 'effectifs' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800">
            <div className="relative max-w-xs">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Nom, poste ou département..."
                className="w-full h-9 pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-left">
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Matricule</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Nom & Prénom</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden md:table-cell">Poste</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden lg:table-cell">Département</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Contrat</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden md:table-cell">Salaire Brut</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Statut</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredEmps.map(emp => (
                  <tr key={emp.matricule} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-amber-300">{emp.matricule}</td>
                    <td className="px-4 py-3 font-bold text-slate-200">{emp.nom}</td>
                    <td className="px-4 py-3 text-slate-400 hidden md:table-cell">{emp.poste}</td>
                    <td className="px-4 py-3 text-slate-400 hidden lg:table-cell">{emp.dept}</td>
                    <td className="px-4 py-3">
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${emp.contrat === 'CDI' ? 'text-blue-400 bg-blue-500/10' : 'text-amber-400 bg-amber-500/10'}`}>{emp.contrat}</span>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300 hidden md:table-cell">{emp.salaire.toLocaleString()} XAF</td>
                    <td className="px-4 py-3">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${statutColors[emp.statut]}`}>{emp.statut}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button onClick={() => toast.info(`Fiche employé ${emp.matricule}`)} className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg">
                          <Eye className="w-3.5 h-3.5 text-amber-400" />
                        </button>
                        <button onClick={() => toast.info(`Générer bulletin ${emp.matricule}`)} className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg">
                          <FileText className="w-3.5 h-3.5 text-blue-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Leave requests */}
      {activeTab === 'conges' && (
        <div className="space-y-3">
          {congesEnAttente.map((req, i) => (
            <div key={i} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="text-sm font-bold text-white">{req.emp}</div>
                  <div className="text-xs text-amber-300 mt-0.5">{req.type}</div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    Du <strong className="text-slate-200">{req.debut}</strong> au <strong className="text-slate-200">{req.fin}</strong> ({req.duree}) • Solde acquis: {req.solde}j • Demande le {req.demande}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => toast.success(`Congé de ${req.emp} refusé`)}
                    className="px-3 py-2 bg-red-500/10 border border-red-500/30 text-red-400 font-bold text-xs rounded-xl hover:bg-red-500/20"
                  >
                    Refuser
                  </button>
                  <button
                    onClick={() => toast.success(`Congé de ${req.emp} approuvé ✓`)}
                    className="px-3 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs rounded-xl hover:bg-emerald-500/20"
                  >
                    Approuver
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

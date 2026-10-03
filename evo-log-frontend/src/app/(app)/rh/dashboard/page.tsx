'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  Users, UserPlus, Clock, CalendarDays, AlertTriangle, CheckCircle2,
  Search, BarChart3
} from 'lucide-react';
import { toast } from 'sonner';
import { rhAPI } from '@/lib/api-client';

interface Employe {
  id: number;
  full_name: string;
  matricule: string | null;
  poste: string | null;
  departement: string | null;
  type_contrat: string | null;
  salaire_base: number | null;
  statut: string | null;
  en_conge: boolean;
}

interface Conge {
  id: number;
  employe_id: number | null;
  employe_nom: string | null;
  type_conge: string | null;
  date_debut: string | null;
  date_fin: string | null;
  nombre_jours: number | null;
  motif: string | null;
  statut: string;
  date_demande: string | null;
}

// Statuts tels que les renvoie le backend (enum contrats / conges en minuscules).
const CONGE_LABELS: Record<string, string> = {
  conge_annuel: 'Congé annuel',
  conge_maladie: 'Congé maladie',
  conge_maternite: 'Congé maternité',
  conge_paternite: 'Congé paternité',
  conge_exceptionnel: 'Congé exceptionnel',
  conge_sans_solde: 'Congé sans solde',
  absence_autorisee: 'Absence autorisée',
};

export default function RHDashboardPage() {
  const [employes, setEmployes] = useState<Employe[]>([]);
  const [totalEmployes, setTotalEmployes] = useState(0);
  const [conges, setConges] = useState<Conge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'effectifs' | 'conges'>('effectifs');
  const [deciding, setDeciding] = useState<number | null>(null);

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [empRes, congeRes] = await Promise.all([
        rhAPI.getEmployes(),
        rhAPI.getConges(),
      ]);
      const data = empRes.data;
      setEmployes(Array.isArray(data?.items) ? data.items : []);
      setTotalEmployes(typeof data?.total === 'number' ? data.total : 0);
      setConges(Array.isArray(congeRes.data) ? congeRes.data : []);
    } catch {
      setError(
        'Impossible de charger les données RH : le serveur n\'a pas répondu. ' +
        'Aucune donnée n\'est affichée tant qu\'elle n\'a pas été récupérée.'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const congesEnAttente = useMemo(
    () => conges.filter(c => c.statut === 'en_attente'),
    [conges]
  );

  const kpis = useMemo(() => {
    const enCongte = employes.filter(e => e.en_conge).length;
    const actifs = employes.filter(e => e.statut === 'actif').length;
    return [
      { label: 'Effectif enregistré', value: totalEmployes, sub: `${employes.length} fiche(s) chargée(s)`, icon: Users, color: 'text-amber-400', bg: 'bg-slate-900/80 border-slate-800' },
      { label: 'Contrats actifs', value: actifs, sub: 'selon le contrat de référence', icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-slate-900/80 border-slate-800' },
      { label: 'En congé maintenant', value: enCongte, sub: 'conges approuvés en cours', icon: CalendarDays, color: 'text-blue-400', bg: 'bg-slate-900/80 border-slate-800' },
      { label: 'Demandes en attente', value: congesEnAttente.length, sub: 'à trancher par la DRH', icon: Clock, color: 'text-amber-300', bg: 'bg-slate-900/80 border-slate-800' },
    ];
  }, [employes, totalEmployes, congesEnAttente]);

  const deptRepartition = useMemo(() => {
    const counts = new Map<string, number>();
    employes.forEach(e => {
      const d = e.departement || 'Non renseigné';
      counts.set(d, (counts.get(d) || 0) + 1);
    });
    const max = Math.max(...counts.values(), 1);
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([dept, count]) => ({ dept, count, pct: Math.round((count / max) * 100) }));
  }, [employes]);

  const filteredEmps = employes.filter(e =>
    !searchQuery ||
    (e.full_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (e.poste || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (e.departement || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  async function deciderConge(conge: Conge, approuver: boolean) {
    setDeciding(conge.id);
    try {
      if (approuver) {
        await rhAPI.deciderConge(conge.id, true, 'Approuvé depuis le tableau de bord RH');
        toast.success(`Congé de ${conge.employe_nom ?? 'collaborateur'} approuvé`);
      } else {
        const motif = window.prompt('Motif du refus (obligatoire côté serveur) :');
        if (!motif) { setDeciding(null); return; }
        await rhAPI.deciderConge(conge.id, false, motif);
        toast.success(`Congé de ${conge.employe_nom ?? 'collaborateur'} refusé`);
      }
      await charger();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Décision impossible : vérifiez les droits RH.');
    } finally {
      setDeciding(null);
    }
  }

  const statutColors: Record<string, string> = {
    actif: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    inactif: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
    expire: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    resilie: 'bg-red-500/10 text-red-400 border-red-500/30',
    suspendu: 'bg-red-500/10 text-red-400 border-red-500/30',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Users className="w-6 h-6 text-amber-400" /> Ressources Humaines & Paie
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Effectifs enregistrés · Demandes de congé réelles · Décisions DRH</p>
        </div>
        <Link
          href="/rh/employes"
          className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg"
        >
          <UserPlus className="w-4 h-4" /> Nouvel Employé
        </Link>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="text-xs font-bold text-red-300">Données RH indisponibles</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{error}</div>
          </div>
          <button onClick={charger} className="px-3 py-1.5 bg-red-500/20 border border-red-500/40 text-red-300 text-[11px] font-bold rounded-lg">
            Réessayer
          </button>
        </div>
      )}

      {/* KPIs  déduits des données réelles, jamais préremplis */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        {kpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div key={i} className={`${kpi.bg} border rounded-2xl p-4 shadow`}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${kpi.color}`} />
                <span className="text-xs text-slate-400 truncate">{kpi.label}</span>
              </div>
              <div className={`text-xl font-black font-mono ${kpi.color}`}>{loading ? '…' : kpi.value}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">{kpi.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Dept Repartition  comptée sur l'annuaire reel */}
      {deptRepartition.length > 0 && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow">
          <h2 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-400" /> Répartition par Département
          </h2>
          <div className="space-y-2.5">
            {deptRepartition.map((d, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-40 text-[11px] text-slate-400 shrink-0 truncate">{d.dept}</div>
                <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className="h-full bg-amber-500 rounded-full" style={{ width: `${d.pct}%` }}></div>
                </div>
                <span className="text-[11px] font-mono text-slate-300 w-12 text-right">{d.count} emp.</span>
              </div>
            ))}
          </div>
        </div>
      )}

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
            {tab.label} {tab.id === 'conges' && <span className="ml-1 bg-amber-500 text-slate-950 rounded-full px-1.5 py-0.5 text-[11px] font-black">{congesEnAttente.length}</span>}
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
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Nom complet</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden md:table-cell">Poste</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden lg:table-cell">Département</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Contrat</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden md:table-cell">Salaire de base</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {loading ? (
                  <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-500">Chargement de l'annuaire…</td></tr>
                ) : filteredEmps.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                      {employes.length === 0
                        ? 'Aucun collaborateur enregistré. Les effectifs apparaîtront ici dès que des fiches auront été créées.'
                        : 'Aucun résultat pour cette recherche.'}
                    </td>
                  </tr>
                ) : filteredEmps.map(emp => (
                  <tr key={emp.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-amber-300">{emp.matricule || ''}</td>
                    <td className="px-4 py-3 font-bold text-slate-200">{emp.full_name}</td>
                    <td className="px-4 py-3 text-slate-400 hidden md:table-cell">{emp.poste || ''}</td>
                    <td className="px-4 py-3 text-slate-400 hidden lg:table-cell">{emp.departement || ''}</td>
                    <td className="px-4 py-3">
                      <span className={`text-[11px] px-2 py-0.5 rounded font-bold ${emp.type_contrat === 'CDI' ? 'text-blue-400 bg-blue-500/10' : 'text-amber-400 bg-amber-500/10'}`}>
                        {emp.type_contrat || 'Sans contrat'}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300 hidden md:table-cell">
                      {emp.salaire_base != null ? `${Math.round(emp.salaire_base).toLocaleString()} XAF` : ''}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${statutColors[emp.statut ?? ''] || statutColors.inactif}`}>
                        {emp.en_conge ? 'en congé' : (emp.statut || 'inactif')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Leave requests  decisions reelles via le backend */}
      {activeTab === 'conges' && (
        <div className="space-y-3">
          {loading ? (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center text-slate-500 text-xs">Chargement des demandes…</div>
          ) : congesEnAttente.length === 0 ? (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center text-slate-500 text-xs">
              Aucune demande de congé en attente.
            </div>
          ) : congesEnAttente.map(req => (
            <div key={req.id} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="text-sm font-bold text-white">{req.employe_nom || `Employe #${req.employe_id}`}</div>
                  <div className="text-xs text-amber-300 mt-0.5">{CONGE_LABELS[req.type_conge ?? ''] || req.type_conge || 'Type non précisé'}</div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    Du <strong className="text-slate-200">{req.date_debut || '?'}</strong> au <strong className="text-slate-200">{req.date_fin || '?'}</strong>
                    {req.nombre_jours != null ? ` (${req.nombre_jours} jour(s)` : ''}
                    {req.date_demande ? `) · Déposée le ${req.date_demande.slice(0, 10)}` : ''}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    disabled={deciding === req.id}
                    onClick={() => deciderConge(req, false)}
                    className="px-3 py-2 bg-red-500/10 border border-red-500/30 text-red-400 font-bold text-xs rounded-xl hover:bg-red-500/20 disabled:opacity-50"
                  >
                    Refuser
                  </button>
                  <button
                    disabled={deciding === req.id}
                    onClick={() => deciderConge(req, true)}
                    className="px-3 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs rounded-xl hover:bg-emerald-500/20 disabled:opacity-50"
                  >
                    {deciding === req.id ? '…' : 'Approuver'}
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

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Users, Plus, Search, AlertTriangle, Phone, Download } from 'lucide-react';
import { rhAPI } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';

// Champs reellement renvoyes par GET /api/v1/rh/employes (_employee_dict).
interface Employe {
  id: number;
  full_name: string;
  matricule: string | null;
  email: string | null;
  phone: string | null;
  poste: string | null;
  departement: string | null;
  type_contrat: string | null;
  date_embauche: string | null;
  salaire_base: number | null;
  statut: string | null;
  en_conge: boolean;
}

export default function RhPersonnelEmployees() {
  const [employees, setEmployees] = useState<Employe[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await rhAPI.getEmployes();
      setEmployees(Array.isArray(res.data?.items) ? res.data.items : []);
      setTotal(typeof res.data?.total === 'number' ? res.data.total : 0);
    } catch {
      setError('Annuaire indisponible : le serveur n\'a pas répondu. Aucun collaborateur n\'est affiché par défaut.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const filtered = employees.filter(e => {
    const q = searchQuery.toLowerCase();
    return !q ||
      (e.full_name || '').toLowerCase().includes(q) ||
      (e.matricule || '').toLowerCase().includes(q) ||
      (e.departement || '').toLowerCase().includes(q) ||
      (e.poste || '').toLowerCase().includes(q);
  });

  function exporterCSV() {
    if (filtered.length === 0) return;
    exportToCSV(
      filtered.map(e => ({
        matricule: e.matricule ?? '',
        nom: e.full_name,
        poste: e.poste ?? '',
        departement: e.departement ?? '',
        contrat: e.type_contrat ?? '',
        embauche: e.date_embauche ? e.date_embauche.slice(0, 10) : '',
        telephone: e.phone ?? '',
        statut: e.en_conge ? 'en_conge' : (e.statut ?? ''),
      })),
      'annuaire_collaborateurs'
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Gestion Administrative du Personnel
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_EMP
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Users className="w-8 h-8 text-pink-400" />
            Fiches Collaborateurs & Contrats
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {total} collaborateur(s) enregistré(s) — type de contrat, date d&apos;embauche et salaire issues du contrat portant.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={exporterCSV} className="px-3 py-2.5 bg-slate-800 border border-slate-700 text-slate-300 font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-slate-700">
            <Download className="w-4 h-4" /> Exporter
          </button>
          <Link
            href="/rh/employes"
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all"
          >
            <Plus className="w-4 h-4" /> Nouveau Collaborateur
          </Link>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="text-xs font-bold text-red-300">Annuaire indisponible</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{error}</div>
          </div>
          <button onClick={charger} className="px-3 py-1.5 bg-red-500/20 border border-red-500/40 text-red-300 text-[11px] font-bold rounded-lg">
            Réessayer
          </button>
        </div>
      )}

      {/* Table Collaborateurs */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par nom, matricule, département..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Matricule & Nom</th>
                <th className="py-3.5 px-4">Département & Poste</th>
                <th className="py-3.5 px-4">Type Contrat</th>
                <th className="py-3.5 px-4">Date d&apos;Embauche</th>
                <th className="py-3.5 px-4">Contact</th>
                <th className="py-3.5 px-4 text-right">Salaire de base</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr><td colSpan={7} className="py-8 text-center text-slate-500 font-sans">Chargement de l&apos;annuaire…</td></tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 font-sans">
                    {employees.length === 0
                      ? 'Aucun collaborateur enregistré. La table s\'remplit dès que des fiches sont créées via le module RH.'
                      : 'Aucun résultat pour cette recherche.'}
                  </td>
                </tr>
              ) : filtered.map(e => (
                <tr key={e.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-pink-400">{e.matricule || '—'}</div>
                    <div className="font-sans text-slate-100 font-bold text-sm">{e.full_name}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans">
                    <div className="text-slate-100 font-medium">{e.poste || '—'}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{e.departement || '—'}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 border border-slate-700 text-slate-300">
                      {e.type_contrat || 'Sans contrat'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300">{e.date_embauche ? e.date_embauche.slice(0, 10) : '—'}</td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2 text-slate-400">
                      {e.phone ? <Phone className="w-3 h-3" /> : null}
                      <span className="truncate max-w-[140px]">{e.phone || e.email || '—'}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-right text-slate-200">
                    {e.salaire_base != null ? `${Math.round(e.salaire_base).toLocaleString()} XAF` : '—'}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      e.en_conge
                        ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                        : e.statut === 'actif'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {e.en_conge ? 'en congé' : (e.statut || 'inactif')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-[10px] text-slate-500">
        La visite médicale est suivie via les documents du collaborateur (module Documents RH), pas dans cet annuaire :
        aucune date n&apos;est affichée sans enregistrement réel.
      </p>
    </div>
  );
}

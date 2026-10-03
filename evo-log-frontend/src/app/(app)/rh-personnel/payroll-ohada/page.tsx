'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  Banknote, Search, AlertTriangle, Download, Calculator
} from 'lucide-react';
import { rhAPI } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';

// Bulletin tel que renvoye GET /api/v1/rh/paie/bulletin.
interface Bulletin {
  id: number;
  reference: string;
  employe_id: number;
  periode: string | null;
  salaire_base: number;
  heures_supplementaires: number;
  indemnite_heures_sup: number;
  primes: number;
  salaire_brut: number;
  cotisations_cnps: number;
  retenues_fiscales: number;
  autres_deductions: number;
  net_a_payer: number;
  statut: string;
  date_paiement: string | null;
}

function fmt(n: number | null | undefined): string {
  return n == null ? '' : Math.round(n).toLocaleString();
}

export default function RhPersonnelPayrollOhada() {
  const [payrolls, setPayrolls] = useState<Bulletin[]>([]);
  const [noms, setNoms] = useState<Map<number, string>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [periode, setPeriode] = useState('');

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, unknown> = {};
      if (periode) {
        const [a, m] = periode.split('-');
        if (a) params.annee = Number(a);
        if (m) params.mois = Number(m);
      }
      const [paieRes, empRes] = await Promise.all([
        rhAPI.getPaie(params),
        rhAPI.getEmployes(),
      ]);
      setPayrolls(Array.isArray(paieRes.data) ? paieRes.data : []);
      const map = new Map<number, string>();
      (Array.isArray(empRes.data?.items) ? empRes.data.items : []).forEach(
        (e: { id: number; full_name: string; matricule: string | null }) => {
          map.set(e.id, e.full_name);
        }
      );
      setNoms(map);
    } catch {
      setError('Livre de paie indisponible : le serveur n\'a pas répondu. Aucun montant n\'est simulé.');
    } finally {
      setLoading(false);
    }
  }, [periode]);

  useEffect(() => { charger(); }, [charger]);

  const periodes = useMemo(() => {
    const set = new Set<string>();
    payrolls.forEach(p => { if (p.periode) set.add(p.periode); });
    return Array.from(set).sort().reverse();
  }, [payrolls]);

  const filtered = payrolls.filter(p => {
    const q = searchQuery.toLowerCase();
    const nom = noms.get(p.employe_id) || '';
    return !q || nom.toLowerCase().includes(q) || p.reference.toLowerCase().includes(q);
  });

  // Totaux : somme des fiches reellement enregistrees (jamais un solde de gestion).
  const totalNet = payrolls.reduce((acc, p) => acc + (p.net_a_payer || 0), 0);
  const totalCnps = payrolls.reduce((acc, p) => acc + (p.cotisations_cnps || 0), 0);
  const totalIrgm = payrolls.reduce((acc, p) => acc + (p.retenues_fiscales || 0), 0);

  function exporterCSV() {
    if (filtered.length === 0) return;
    exportToCSV(
      filtered.map(p => ({
        reference: p.reference,
        employe: noms.get(p.employe_id) || p.employe_id,
        periode: p.periode ?? '',
        salaire_base: p.salaire_base,
        brut: p.salaire_brut,
        cnps: p.cotisations_cnps,
        irgm: p.retenues_fiscales,
        net: p.net_a_payer,
        statut: p.statut,
      })),
      'livre_paie_enregistre'
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Livre de Paie & Fiscalité Cameroun
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_PAY
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Banknote className="w-8 h-8 text-pink-400" />
            Livre de Paie OHADA & Bulletins de Salaire
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Fiches réellement enregistrées ; CNPS et IRGM calculés par le moteur serveur (PaieService), aucun taux appliqué ici.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={exporterCSV} className="px-3 py-2.5 bg-slate-800 border border-slate-700 text-slate-300 font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-slate-700">
            <Download className="w-4 h-4" /> Export CSV
          </button>
          <Link
            href="/rh/paie"
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all"
          >
            <Calculator className="w-4 h-4" /> Saisir une fiche
          </Link>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="text-xs font-bold text-red-300">Livre de paie indisponible</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{error}</div>
          </div>
          <button onClick={charger} className="px-3 py-1.5 bg-red-500/20 border border-red-500/40 text-red-300 text-[11px] font-bold rounded-lg">
            Réessayer
          </button>
        </div>
      )}

      {/* KPI Cards  sommes des fiches chargees */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Total Net enregistré (XAF)</div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            {loading ? '…' : totalNet.toLocaleString()} <span className="text-xs font-normal text-slate-400">XAF</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Somme des {payrolls.length} fiche(s) affichée(s).</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Cotisations CNPS retenues</div>
          <div className="text-2xl font-black text-pink-400 font-mono">
            {loading ? '…' : totalCnps.toLocaleString()} <span className="text-xs font-normal text-slate-400">XAF</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Telles que calculées par le serveur sur chaque fiche.</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Retenues IRGM / Impôts</div>
          <div className="text-2xl font-black text-amber-400 font-mono">
            {loading ? '…' : totalIrgm.toLocaleString()} <span className="text-xs font-normal text-slate-400">XAF</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">Barème appliqué côté serveur, pas par cet écran.</div>
        </div>
      </div>

      {/* Table Paie */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[220px] max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher un collaborateur ou une référence…"
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
          <select
            value={periode}
            onChange={e => setPeriode(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-pink-500"
          >
            <option value="">Toutes périodes</option>
            {Array.from(new Set(
              periodes.concat(periode ? [periode] : [])
            )).sort().reverse().map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Réf. & Collaborateur</th>
                <th className="py-3.5 px-4">Période</th>
                <th className="py-3.5 px-4 text-right">Salaire Base</th>
                <th className="py-3.5 px-4 text-right">Heures Sup / Primes</th>
                <th className="py-3.5 px-4 text-right">Salaire Brut</th>
                <th className="py-3.5 px-4 text-right">CNPS</th>
                <th className="py-3.5 px-4 text-right">IRGM</th>
                <th className="py-3.5 px-4 text-right">Net à Payer</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr><td colSpan={9} className="py-8 text-center text-slate-500 font-sans">Chargement du livre de paie…</td></tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-500 font-sans">
                    {payrolls.length === 0
                      ? 'Aucune fiche de paie enregistrée. Aucun bulletin fictif n\'est affiché en attendant la première saisie.'
                      : 'Aucune fiche pour cette recherche.'}
                  </td>
                </tr>
              ) : filtered.map(p => (
                <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-pink-400">{p.reference}</div>
                    <div className="font-sans text-slate-100 font-bold">{noms.get(p.employe_id) || `Employé #${p.employe_id}`}</div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300">{p.periode ?? ''}</td>
                  <td className="py-3.5 px-4 text-right text-slate-200">{fmt(p.salaire_base)}</td>
                  <td className="py-3.5 px-4 text-right text-slate-300">{fmt(p.indemnite_heures_sup + p.primes)}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-100">{fmt(p.salaire_brut)}</td>
                  <td className="py-3.5 px-4 text-right text-pink-400">-{fmt(p.cotisations_cnps)}</td>
                  <td className="py-3.5 px-4 text-right text-amber-400">-{fmt(p.retenues_fiscales)}</td>
                  <td className="py-3.5 px-4 text-right font-black text-emerald-400 text-sm">
                    {fmt(p.net_a_payer)} XAF
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${p.statut === 'paye' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : p.statut === 'annule' ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>{p.statut}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-[10px] text-slate-500">
        Statuts gérés par le backend : en_attente · paye · annule. La clôture mensuelle et les ordres de
        virement ne sont pas exécutés par cet écran : il n&apos;affiche que ce qui a été enregistré.
      </p>
    </div>
  );
}

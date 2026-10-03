'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  FileCheck, Search, AlertTriangle, Download, Info
} from 'lucide-react';
import { rhAPI } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';

interface Bulletin {
  id: number;
  periode: string | null;
  salaire_brut: number;
  cotisations_cnps: number;
  retenues_fiscales: number;
  statut: string;
}

// Brouillon de declaration, agregat calcule a partir des bulletins reels.
interface BrouillonPeriode {
  periode: string;
  nbFiches: number;
  baseBrute: number;
  cnps: number;
  irgm: number;
  totalReverser: number;
}

export default function RhPersonnelSocialDeclarations() {
  const [bulletins, setBulletins] = useState<Bulletin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await rhAPI.getPaie();
      setBulletins(Array.isArray(res.data) ? res.data : []);
    } catch {
      setError('Impossible de charger les bulletins de paie : aucun chiffre de déclaration n\'est affiché sans source réelle.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  // Agregat par periode des cotisations reellement retenues sur les fiches
  // enregistrees. Ce n'est PAS une declaration teletransmise : la plateforme
  // ne gere ni depot DGI/CNPS ni numero de recepisse.
  const brouillons = useMemo<BrouillonPeriode[]>(() => {
    const byPeriode = new Map<string, BrouillonPeriode>();
    bulletins.forEach(b => {
      if (!b.periode) return;
      const cur = byPeriode.get(b.periode) || {
        periode: b.periode, nbFiches: 0, baseBrute: 0, cnps: 0, irgm: 0, totalReverser: 0,
      };
      if (b.statut !== 'annule') {
        cur.nbFiches += 1;
        cur.baseBrute += b.salaire_brut || 0;
        cur.cnps += b.cotisations_cnps || 0;
        cur.irgm += b.retenues_fiscales || 0;
      }
      cur.totalReverser = cur.cnps + cur.irgm;
      byPeriode.set(b.periode, cur);
    });
    return Array.from(byPeriode.values()).sort((a, b) => b.periode.localeCompare(a.periode));
  }, [bulletins]);

  const filtered = brouillons.filter(b =>
    !searchQuery || b.periode.includes(searchQuery)
  );

  function exporterBrouillon() {
    if (brouillons.length === 0) return;
    exportToCSV(
      brouillons.map(b => ({
        periode: b.periode,
        fiches: b.nbFiches,
        base_brute_xaf: Math.round(b.baseBrute),
        cnps_xaf: Math.round(b.cnps),
        irgm_xaf: Math.round(b.irgm),
        total_a_reverser_xaf: Math.round(b.totalReverser),
      })),
      'brouillon_declarations_sociales'
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Conformité Fiscale & Sociale Cameroun
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_DIP
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <FileCheck className="w-8 h-8 text-pink-400" />
            Déclarations Sociales & DIPE — Brouillons
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Cotisations agrégées à partir des bulletins de paie réellement enregistrés.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={exporterBrouillon}
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all"
          >
            <Download className="w-4 h-4" /> Exporter le brouillon (CSV)
          </button>
        </div>
      </div>

      {/* Avertissement de perimetre : pas de teletransmission, pas de recu */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-2xl p-4 flex items-start gap-3">
        <Info className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
        <p className="text-[11px] text-slate-300 leading-relaxed">
          Cet écran établit des <strong>brouillons calculés</strong> (base brute, CNPS, IRGM par période) à partir
          des fiches de paie enregistrées. La plateforme ne <strong>télétransmet rien</strong> à la DGI ni à la CNPS
          et ne délivre <strong>aucun récépissé</strong> : le dépôt officiel (format EDI-DIPE, bordereaux CNPS)
          reste une démarche externe. Aucun statut « déposé / conforme » n&apos;est affiché faute de source vérifiable.
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="text-xs font-bold text-red-300">Données indisponibles</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{error}</div>
          </div>
          <button onClick={charger} className="px-3 py-1.5 bg-red-500/20 border border-red-500/40 text-red-300 text-[11px] font-bold rounded-lg">
            Réessayer
          </button>
        </div>
      )}

      {/* Table Brouillons */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-xs">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Période (ex : 2026-09)…"
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Période</th>
                <th className="py-3.5 px-4 text-right">Fiches retenues</th>
                <th className="py-3.5 px-4 text-right">Masse salariale brute</th>
                <th className="py-3.5 px-4 text-right">CNPS retenue</th>
                <th className="py-3.5 px-4 text-right">IRGM retenu</th>
                <th className="py-3.5 px-4 text-right">Total à reverser (brouillon)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr><td colSpan={6} className="py-8 text-center text-slate-500 font-sans">Chargement des bulletins…</td></tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 font-sans">
                    {bulletins.length === 0
                      ? 'Aucune fiche de paie enregistrée : aucune cotisation ne peut être agrégée.'
                      : 'Aucune période pour cette recherche.'}
                  </td>
                </tr>
              ) : filtered.map(b => (
                <tr key={b.periode} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-pink-400">{b.periode}</td>
                  <td className="py-3.5 px-4 text-right text-slate-300">{b.nbFiches}</td>
                  <td className="py-3.5 px-4 text-right text-slate-200">{Math.round(b.baseBrute).toLocaleString()} XAF</td>
                  <td className="py-3.5 px-4 text-right text-pink-400">{Math.round(b.cnps).toLocaleString()} XAF</td>
                  <td className="py-3.5 px-4 text-right text-amber-400">{Math.round(b.irgm).toLocaleString()} XAF</td>
                  <td className="py-3.5 px-4 text-right font-black text-emerald-400">
                    {Math.round(b.totalReverser).toLocaleString()} XAF
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

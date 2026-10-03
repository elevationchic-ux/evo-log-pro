'use client';

import React, { useCallback, useEffect, useState } from 'react';
import {
  Clock, Search, AlertTriangle, Download, CheckCircle2
} from 'lucide-react';
import { rhAPI } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';

// Emargement reel (PointageVacation) tel que renvoie
// GET /api/v1/chef-personnel/pointages.
interface Pointage {
  id: number;
  employe_id: number;
  employe_nom: string;
  employe_role: string;
  date_pointage: string;
  heure_arrivee: string | null;
  heure_depart: string | null;
  heures_effectives: number;
  droit_panier_nuit: boolean;
  montant_panier: number;
  est_valide: boolean;
  remarques: string | null;
}

export default function RhPersonnelTimeAttendance() {
  const [records, setRecords] = useState<Pointage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filtreDate, setFiltreDate] = useState('');

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await rhAPI.getPointages(filtreDate || undefined);
      setRecords(Array.isArray(res.data) ? res.data : []);
    } catch (err: any) {
      const status = err?.response?.status;
      if (status === 403) {
        setError(
          'Registre réservé : seul le Chef du Personnel, la DRH ou la Direction ' +
          'peut consulter les émargements.'
        );
      } else {
        setError('Registre de pointage indisponible : le serveur n\'a pas répondu. Aucun émargement n\'est simulé.');
      }
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, [filtreDate]);

  useEffect(() => { charger(); }, [charger]);

  const filtered = records.filter(r => {
    const q = searchQuery.toLowerCase();
    return !q ||
      (r.employe_nom || '').toLowerCase().includes(q) ||
      (r.employe_role || '').toLowerCase().includes(q);
  });

  function exporterCSV() {
    if (filtered.length === 0) return;
    exportToCSV(
      filtered.map(r => ({
        date: r.date_pointage,
        agent: r.employe_nom,
        role: r.employe_role,
        arrivee: r.heure_arrivee ?? '',
        depart: r.heure_depart ?? '',
        heures_effectives: r.heures_effectives,
        panier_nuit: r.droit_panier_nuit ? r.montant_panier : 0,
        valide: r.est_valide ? 'oui' : 'non',
        remarques: r.remarques ?? '',
      })),
      'registre_pointages'
    );
  }

  const valideCount = records.filter(r => r.est_valide).length;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Pointage & Temps de Travail
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_ATT
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Clock className="w-8 h-8 text-pink-400" />
            Temps, Présences & Heures Supplémentaires
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {records.length} émargement(s) enregistré(s) · {valideCount} certifié(s) par le Chef du Personnel
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={exporterCSV}
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all"
          >
            <Download className="w-4 h-4" /> Export du registre
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="text-xs font-bold text-red-300">Registre indisponible</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{error}</div>
          </div>
          <button onClick={charger} className="px-3 py-1.5 bg-red-500/20 border border-red-500/40 text-red-300 text-[11px] font-bold rounded-lg">
            Réessayer
          </button>
        </div>
      )}

      {/* Table Pointages */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[220px] max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher un collaborateur ou une fonction…"
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
          <input
            type="date"
            value={filtreDate}
            onChange={e => setFiltreDate(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-pink-500"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Collaborateur</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4 text-center">Arrivée</th>
                <th className="py-3.5 px-4 text-center">Départ</th>
                <th className="py-3.5 px-4 text-right">Heures effectives</th>
                <th className="py-3.5 px-4 text-right">Panier de nuit</th>
                <th className="py-3.5 px-4 text-center">Certification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr><td colSpan={7} className="py-8 text-center text-slate-500 font-sans">Chargement du registre…</td></tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 font-sans">
                    {records.length === 0
                      ? 'Aucun émargement enregistré pour cette période. Le registre se remplit par le module Chef du Personnel (pointage / certification).'
                      : 'Aucun résultat pour cette recherche.'}
                  </td>
                </tr>
              ) : filtered.map(r => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-sans text-slate-100 font-bold">{r.employe_nom}</div>
                    <div className="text-[11px] text-slate-400">{r.employe_role}</div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300">{r.date_pointage}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-emerald-400">{r.heure_arrivee || '—'}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-blue-400">{r.heure_depart || '—'}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-200">{r.heures_effectives} h</td>
                  <td className="py-3.5 px-4 text-right">
                    {r.droit_panier_nuit
                      ? <span className="text-amber-400 font-bold">{r.montant_panier.toLocaleString()} XAF</span>
                      : <span className="text-slate-500">—</span>}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    {r.est_valide ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> certifié
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-500/10 text-slate-400 border border-slate-500/20">
                        en attente
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-[10px] text-slate-500">
        Le registre affiche les émargements enregistrés et certifiés côté serveur (100 plus récents, filtrable
        par date). Les majorations d&apos;heures supplémentaires sont calculées sur la fiche de paie par le moteur
        serveur, pas par cet écran.
      </p>
    </div>
  );
}

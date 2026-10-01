'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  Users, Banknote, FileCheck, Clock, Award, AlertTriangle
} from 'lucide-react';
import { rhAPI } from '@/lib/api-client';

interface Employe {
  id: number;
  full_name: string;
  type_contrat: string | null;
  statut: string | null;
  en_conge: boolean;
}

interface Bulletin {
  id: number;
  periode: string | null;
  salaire_brut: number;
  net_a_payer: number;
  statut: string;
}

interface Conge {
  id: number;
  statut: string;
}

export default function RhPersonnelDashboard() {
  const [employes, setEmployes] = useState<Employe[]>([]);
  const [totalEffectif, setTotalEffectif] = useState(0);
  const [bulletins, setBulletins] = useState<Bulletin[]>([]);
  const [conges, setConges] = useState<Conge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [empRes, paieRes, congeRes] = await Promise.all([
        rhAPI.getEmployes(),
        rhAPI.getPaie(),
        rhAPI.getConges(),
      ]);
      setEmployes(Array.isArray(empRes.data?.items) ? empRes.data.items : []);
      setTotalEffectif(typeof empRes.data?.total === 'number' ? empRes.data.total : 0);
      setBulletins(Array.isArray(paieRes.data) ? paieRes.data : []);
      setConges(Array.isArray(congeRes.data) ? congeRes.data : []);
    } catch {
      setError(
        'Indicateurs indisponibles : le serveur n\'a pas répondu. ' +
        'Aucun chiffre n\'est affiché sans avoir été lu en base — ni effectif, ni masse salariale.'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const contratsParType = useMemo(() => {
    const counts = new Map<string, number>();
    employes.forEach(e => {
      const t = e.type_contrat || 'Sans contrat';
      counts.set(t, (counts.get(t) || 0) + 1);
    });
    return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
  }, [employes]);

  const effectifEnConge = employes.filter(e => e.en_conge).length;
  const demandesEnAttente = conges.filter(c => c.statut === 'en_attente').length;

  const periodesPaie = useMemo(() => {
    const set = new Set<string>();
    bulletins.forEach(b => { if (b.periode) set.add(b.periode); });
    return Array.from(set).sort().reverse();
  }, [bulletins]);

  const [periodeSel, setPeriodeSel] = useState('');
  useEffect(() => {
    if (periodesPaie.length > 0 && !periodesPaie.includes(periodeSel)) {
      setPeriodeSel(periodesPaie[0]);
    }
  }, [periodesPaie, periodeSel]);

  const masseSalarialePeriode = useMemo(() => {
    const fiches = bulletins.filter(b => b.periode === periodeSel);
    return {
      brut: fiches.reduce((acc, b) => acc + (b.salaire_brut || 0), 0),
      net: fiches.reduce((acc, b) => acc + (b.net_a_payer || 0), 0),
      count: fiches.length,
    };
  }, [bulletins, periodeSel]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Direction des Ressources Humaines & Paie OHADA
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_DSH
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Users className="w-8 h-8 text-pink-400" />
            Supervision RH & Capital Humain
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Effectifs, contrats et paie : uniquement des données réellement enregistrées.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/rh-personnel/payroll-ohada"
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all"
          >
            <Banknote className="w-4 h-4" /> Voir le livre de paie
          </Link>
        </div>
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

      {/* KPI Cards — deduites des enregistrements reels */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Effectif enregistré</div>
          <div className="text-2xl font-black text-pink-400 font-mono">
            {loading ? '…' : totalEffectif} <span className="text-xs font-normal text-slate-400">collaborateurs</span>
          </div>
          {contratsParType.length > 0 && (
            <div className="text-[11px] text-slate-400 mt-2">
              {contratsParType.map(([t, n]) => `${n} ${t}`).join(' • ')}
            </div>
          )}
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Masse salariale {periodeSel || '(aucune période payée)'}
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            {loading ? '…' : `${masseSalarialePeriode.brut.toLocaleString()}`} <span className="text-xs font-normal text-slate-400">XAF brut</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">
            {masseSalarialePeriode.count > 0
              ? `Net versé : ${masseSalarialePeriode.net.toLocaleString()} XAF — ${masseSalarialePeriode.count} fiche(s) enregistrée(s)`
              : 'Aucune fiche de paie enregistrée : somme = 0, rien n\'est estimé.'}
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">En congé actuellement</div>
          <div className="text-2xl font-black text-blue-400 font-mono">{loading ? '…' : effectifEnConge}</div>
          <div className="text-[11px] text-slate-400 mt-2">D\'après les conges approuves couvrant la date du jour.</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Demandes de congé en attente</div>
          <div className="text-2xl font-black text-amber-400 font-mono">{loading ? '…' : demandesEnAttente}</div>
          <div className="text-[11px] text-slate-400 mt-2">À trancher dans le tableau de bord RH.</div>
        </div>
      </div>

      {periodesPaie.length > 1 && (
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="font-bold uppercase text-[11px]">Période de paie :</span>
          <select
            value={periodeSel}
            onChange={e => setPeriodeSel(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-xs text-slate-200 font-mono focus:outline-none focus:border-pink-500"
          >
            {periodesPaie.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
      )}

      {/* Raccourcis Sous-Modules */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link
          href="/rh-personnel/payroll-ohada"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-pink-500/50 rounded-2xl transition-all group"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
              <Banknote className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KRH_PAY
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-pink-400 transition-colors">
            Paie OHADA & Bulletins de Salaire
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Fiches réellement enregistrées ; cotisations CNPS et IRGM calculées par le moteur serveur.
          </p>
        </Link>

        <Link
          href="/rh-personnel/social-declarations"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-pink-500/50 rounded-2xl transition-all group"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
              <FileCheck className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KRH_DIP
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-pink-400 transition-colors">
            Déclarations Sociales & DIPE
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Brouillons de cotisations agrégés à partir des bulletins enregistrés (télétransmission non gérée).
          </p>
        </Link>

        <Link
          href="/rh/dashboard"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-pink-500/50 rounded-2xl transition-all group"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
              <Clock className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KRH_CGE
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-pink-400 transition-colors">
            Congés & Décisions DRH
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Demandes déposées par les collaborateurs, à approuver ou refuser.
          </p>
        </Link>
      </div>

      {/* Formation/habilitations : pas de donnees reelles exploitees ici */}
      <div className="flex items-start gap-3 bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
        <Award className="w-4 h-4 text-slate-500 mt-0.5 shrink-0" />
        <p className="text-[11px] text-slate-500">
          Les habilitations et Visites médicales ne sont pas agrégées sur cet écran : aucune donnée
          probante n&apos;est disponible sans requête dédiée, et ce tableau de bord n&apos;affiche aucun indicateur invérifiable.
        </p>
      </div>
    </div>
  );
}

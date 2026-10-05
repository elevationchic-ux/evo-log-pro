'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Lock, Calendar, AlertTriangle, ShieldCheck,
  Clock, Check, RefreshCw, Loader2, FileWarning
} from 'lucide-react';
import { toast } from 'sonner';

/**
 * Page Clôtures mensuelles & annuelles SYSCOHADA.
 *
 * HONNETETE DES DONNEES : la liste des periodes n'est plus fabriquee depuis la
 * date du jour (l'ancienne version inventait les statuts CLOTURE/EN_COURS,
 * codait des cases "Validé" en dur et affichait un faux toast pour la cloture
 * annuelle). Tout est desormais derive de l'etat reel calcule cote serveur via
 * GET /comptabilite-avance/cloture/etats : une periode n'est dite « cloturee »
 * que si une balance de verification equilibree a reellement ete generee.
 */

const AUTH = () => ({ 'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('access_token') || '' : ''}` });
const NOM_OPE_RATEUR = (): string => {
  if (typeof window === 'undefined') return 'Opérateur';
  try {
    const u = localStorage.getItem('user');
    if (u) { const p = JSON.parse(u); return p.full_name || p.username || p.email || 'Opérateur'; }
  } catch { /* ignore */ }
  return localStorage.getItem('user_email') || 'Opérateur';
};

interface Periode {
  periode: string;      // "2026-05"
  label: string;        // "Mai 2026"
  entries_count: number;
  closed: boolean;
  balance_statut: string | null;
  balance_date: string | null;
}

interface Etats {
  exercice_id: number;
  annee: number;
  exercice_statut: string;
  periodes: Periode[];
}

export default function ComptabiliteOhadaMonthlyClosing() {
  const [etats, setEtats] = useState<Etats | null>(null);
  const [selected, setSelected] = useState<Periode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [closing, setClosing] = useState(false);
  const [closingAnnual, setClosingAnnual] = useState(false);

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/comptabilite-avance/cloture/etats', { headers: AUTH() });
      if (!res.ok) {
        const corps = await res.json().catch(() => ({}));
        setError(corps.detail || `Erreur ${res.status}`);
        setEtats(null);
        return;
      }
      const data: Etats = await res.json();
      setEtats(data);
      // Garder la meme periode si elle existe toujours, sinon premiere non cloturee.
      setSelected(prev => {
        const trouve = prev && data.periodes.find(p => p.periode === prev.periode);
        return (trouve as Periode) || data.periodes.find(p => !p.closed) || data.periodes[0] || null;
      });
    } catch {
      setError('Connexion impossible avec le serveur comptable.');
      setEtats(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { charger(); }, [charger]);

  const handleRunClosing = async () => {
    if (!etats || !selected || selected.closed) return;
    setClosing(true);
    try {
      const res = await fetch('/api/v1/comptabilite-avance/cloture/mensuelle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...AUTH() },
        body: JSON.stringify({
          exercice_id: etats.exercice_id,
          periode: selected.periode,
          cloture_par: NOM_OPE_RATEUR(),
        }),
      });
      const corps = await res.json().catch(() => ({}));
      if (!res.ok) {
        toast.error(corps.detail || `La clôture de ${selected.label} a échoué.`);
        return;
      }
      toast.success(`Période ${selected.label} clôturée : balance de vérification générée et équilibrée.`);
      await charger();
    } catch {
      toast.error('Connexion serveur interrompue. Aucun état local n’a été modifié.');
    } finally {
      setClosing(false);
    }
  };

  const handleRunAnnualClosing = async () => {
    if (!etats || etats.exercice_statut === 'cloture') return;
    if (!confirm(`Confirmer la clôture ANNUELLE de l'exercice ${etats.annee} ? Cette opération génère bilan, compte de résultat et TAFIRE, puis verrouille l'exercice.`)) return;
    setClosingAnnual(true);
    try {
      const res = await fetch('/api/v1/comptabilite-avance/cloture/annuelle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...AUTH() },
        body: JSON.stringify({ exercice_id: etats.exercice_id, cloture_par: NOM_OPE_RATEUR() }),
      });
      const corps = await res.json().catch(() => ({}));
      if (!res.ok) {
        toast.error(corps.detail || 'La clôture annuelle a échoué.');
        return;
      }
      toast.success(`Exercice ${etats.annee} clôturé. Résultat net : ${Number(corps.resultat_net ?? 0).toLocaleString('fr-FR')} XAF.`);
      await charger();
    } catch {
      toast.error('Connexion serveur interrompue. Aucun état local n’a été modifié.');
    } finally {
      setClosingAnnual(false);
    }
  };

  // Checklist derivee de l'etat REEL de la periode selectionnee (aucun "Validé"
  // code en dur) ; les controles purement manuels restent explicitement a
  // attester, sans pretendre qu'ils sont faits.
  const controls = selected ? [
    { label: 'Pièces comptabilisées sur la période', value: `${selected.entries_count} écriture(s)`, done: selected.entries_count > 0, auto: true },
    { label: 'Balance de vérification générée et équilibrée', value: selected.balance_statut || 'aucune balance', done: selected.closed, auto: true },
    { label: 'Rapprochement bancaire mensuel', value: 'À attester manuellement', done: false, auto: false },
    { label: 'Dotations aux amortissements comptabilisées', value: 'À attester manuellement', done: false, auto: false },
    { label: 'Apurement des comptes d’attente (471)', value: 'À attester manuellement', done: false, auto: false },
  ] : [];

  return (
    <div className="space-y-6 animate-in fade-in duration-300 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
            Arrêtés des Comptes & Verrouillage
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3 mt-2">
            <Lock className="w-8 h-8 text-violet-400" />
            Clôtures Mensuelles & Annuelles SYSCOHADA
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Génération de la balance de vérification, contrôle d’équilibre Débit=Crédit et verrouillage des périodes.
          </p>
          {etats && (
            <div className="text-[11px] text-slate-500 font-mono mt-1">
              Exercice {etats.annee} (id {etats.exercice_id}) — statut : {etats.exercice_statut}
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button onClick={charger} disabled={loading}
            className="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2 transition-all disabled:opacity-50">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button
            onClick={handleRunAnnualClosing}
            disabled={closingAnnual || !etats || etats.exercice_statut === 'cloture'}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 disabled:opacity-50 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
          >
            {closingAnnual ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
            {etats?.exercice_statut === 'cloture' ? 'Exercice clôturé' : 'Clôture Annuelle'}
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-2xl p-4 text-sm">
          <FileWarning className="w-5 h-5" /> {error}
        </div>
      )}

      {loading && !etats && (
        <div className="flex items-center justify-center gap-3 py-20 text-slate-400">
          <Loader2 className="w-5 h-5 animate-spin text-violet-400" /> Chargement des états de clôture…
        </div>
      )}

      {etats && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Liste des periodes REELLES */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-3">
            <h2 className="text-sm font-black text-white uppercase tracking-tight flex items-center gap-2 pb-2 border-b border-slate-800">
              <Calendar className="w-4 h-4 text-violet-400" /> Périodes Comptables ({etats.annee})
            </h2>

            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {etats.periodes.map(p => {
                const isSel = selected?.periode === p.periode;
                return (
                  <button
                    key={p.periode}
                    onClick={() => setSelected(p)}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all flex items-center justify-between ${
                      isSel
                        ? 'bg-violet-600/20 border-violet-500 text-white shadow-md'
                        : 'bg-slate-950 border-slate-800/80 text-slate-400 hover:text-white'
                    }`}
                  >
                    <div>
                      <div className="font-black text-xs">{p.label}</div>
                      <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                        {p.closed ? `Clôturé le ${p.balance_date}` : `${p.entries_count} écriture(s)`}
                      </div>
                    </div>
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-black uppercase ${
                      p.closed
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}>
                      {p.closed ? 'CLOTURE' : 'OUVERT'}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Detail & Procedure */}
          <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6 flex flex-col justify-between">
            {selected ? (
              <>
                <div className="space-y-5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800">
                    <div>
                      <h3 className="text-lg font-black text-white">{selected.label}</h3>
                      <p className="text-xs text-slate-400 font-mono">
                        Statut : <b className="text-violet-400">{selected.closed ? 'CLOTURE' : 'OUVERT'}</b> •{' '}
                        {selected.entries_count} écriture(s) comptabilisée(s)
                      </p>
                    </div>
                    {selected.closed ? (
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-bold font-mono">
                        <Lock className="w-4 h-4" /> Période clôturée
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-bold font-mono">
                        <Clock className="w-4 h-4" /> En cours d’imputation
                      </div>
                    )}
                  </div>

                  {selected.entries_count === 0 && !selected.closed && (
                    <div className="flex items-center gap-2 text-amber-300 text-xs bg-amber-500/10 border border-amber-500/20 rounded-xl p-3">
                      <AlertTriangle className="w-4 h-4" />
                      Aucune écriture validée sur cette période : la clôture est impossible tant qu’aucune pièce n’y est comptabilisée.
                    </div>
                  )}

                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Contrôles de Clôture OHADA
                    </h4>
                    <div className="space-y-2 text-xs">
                      {controls.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800/80">
                          <span className="text-slate-300">{item.label}</span>
                          <span className={`px-2 py-0.5 rounded text-[11px] font-bold flex items-center gap-1 ${
                            item.done
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : item.auto
                              ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30'
                              : 'bg-slate-800 text-slate-400 border border-slate-700'
                          }`}>
                            {item.done ? <Check className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                            {item.value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
                  <div className="text-[11px] text-slate-500 font-mono">
                    {selected.closed ? `Clôture générée le ${selected.balance_date}` : 'Action soumise aux habilitations DAF / Chef Comptable'}
                  </div>
                  {!selected.closed && (
                    <button
                      onClick={handleRunClosing}
                      disabled={closing || selected.entries_count === 0}
                      className="px-6 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:opacity-50 text-white font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-violet-500/25 transition-all"
                    >
                      {closing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                      {closing ? 'Verrouillage…' : `Clôturer ${selected.label}`}
                    </button>
                  )}
                </div>
              </>
            ) : (
              <div className="text-sm text-slate-400 py-10 text-center">Aucune période disponible.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

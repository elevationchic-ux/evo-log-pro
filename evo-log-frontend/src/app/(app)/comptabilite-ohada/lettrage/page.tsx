'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  CheckCheck, Search, RefreshCw, AlertCircle, Wand2, Undo2,
  Link2, ListChecks, Plus,
} from 'lucide-react';
import { toast } from 'sonner';

const API = '/api/v1/comptabilite-avance';
const AUTH = () => ({
  'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('access_token') || '' : ''}`,
  'Content-Type': 'application/json',
});

const OPERATEUR = (): string => {
  if (typeof window === 'undefined') return 'Opérateur';
  try {
    const u = localStorage.getItem('user');
    if (u) { const p = JSON.parse(u); return p.full_name || p.username || p.email || 'Opérateur'; }
  } catch { /* stockage illisible */ }
  return localStorage.getItem('user_email') || 'Opérateur';
};

const num = (v: unknown): number => {
  const n = typeof v === 'string' ? parseFloat(v) : (v as number);
  return Number.isFinite(n) ? n : 0;
};
const fmt = (n: number) => Math.round(n).toLocaleString('fr-FR');
const fmtDate = (iso: string | null) => {
  if (!iso) return '—';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString('fr-FR');
};

interface CompteOuvert {
  compteId: number;
  numero: string;
  intitule: string;
  soldeOuvert: number;
}

interface LigneOuverte {
  ligne_id: number;
  ecriture_id: number;
  date_ecriture: string;
  libelle: string | null;
  journal: string | null;
  periode: string | null;
  debit: number;
  credit: number;
}

interface Suggestions {
  compte_id: number;
  compte_numero: string;
  compte_intitule: string;
  lignes: LigneOuverte[];
  total_debit: number;
  total_credit: number;
  solde_ouvert: number;
}

interface Lettrage {
  id: number;
  compte_id: number;
  numero_lettrage: string;
  type_lettrage: string;
  date_lettrage: string;
  montant_lettre: number;
  reference_lettrage: string | null;
  effectue_par: string | null;
  notes: string | null;
  date_annulation: string | null;
  motif_annulation: string | null;
}

const aujourdHui = () => new Date().toISOString().slice(0, 10);

export default function ComptabiliteOhadaLettrage() {
  // ---- Comptes à lettrer ----
  const [comptes, setComptes] = useState<CompteOuvert[]>([]);
  const [loadingComptes, setLoadingComptes] = useState(true);
  const [erreurComptes, setErreurComptes] = useState<string | null>(null);
  const [recherche, setRecherche] = useState('');
  const [compteActif, setCompteActif] = useState<number | null>(null);

  // ---- Items ouverts du compte sélectionné ----
  const [suggestions, setSuggestions] = useState<Suggestions | null>(null);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [erreurSuggestions, setErreurSuggestions] = useState<string | null>(null);
  const [selection, setSelection] = useState<Set<number>>(new Set());
  const [reference, setReference] = useState('');
  const [dateLettrage, setDateLettrage] = useState(aujourdHui());
  const [enCour, setEnCour] = useState(false);

  // ---- Lettrages existants ----
  const [lettrages, setLettrages] = useState<Lettrage[]>([]);
  const [onglet, setOnglet] = useState<'OUVERTS' | 'LETTRAGES'>('OUVERTS');

  const chargerComptes = useCallback(async () => {
    setLoadingComptes(true); setErreurComptes(null);
    try {
      const res = await fetch(`${API}/balances/verification`, { headers: AUTH() });
      if (!res.ok) {
        const b = await res.json().catch(() => ({}));
        setErreurComptes(b.detail || `Erreur ${res.status}`);
        setComptes([]);
        return;
      }
      const data = await res.json();
      const items = data?.lignes || (Array.isArray(data) ? data : []);
      // Seuls les comptes de TIERS (classe 4) se lettrrent : stocks, tiers
      // financiers… Les classes 6/7 sont soldées en fin d'exercice, pas par
      // rapprochement. On n'invente rien : solde ouvert = débit - crédit réel.
      const ouverts: CompteOuvert[] = items
        .map((i: Record<string, unknown>) => {
          const numero = String(i.compte_numero ?? i.compte ?? '');
          return {
            compteId: Number(i.compte_id),
            numero,
            intitule: String(i.compte_intitule ?? i.intitule ?? ''),
            soldeOuvert: num(i.solde_final_debit) - num(i.solde_final_credit),
          };
        })
        .filter((c: CompteOuvert) => Number.isFinite(c.compteId) && c.numero.startsWith('4'));
      setComptes(ouverts);
      setCompteActif(prev => {
        const actif = prev !== null && ouverts.some(c => c.compteId === prev) ? prev : (ouverts[0]?.compteId ?? null);
        return actif;
      });
    } catch {
      setErreurComptes('Serveur comptable injoignable.');
      setComptes([]);
    } finally {
      setLoadingComptes(false);
    }
  }, []);

  const chargerSuggestions = useCallback(async (compteId: number) => {
    setLoadingSuggestions(true); setErreurSuggestions(null); setSuggestions(null);
    setSelection(new Set());
    try {
      const res = await fetch(`${API}/lettrage/suggestions/${compteId}`, { headers: AUTH() });
      if (!res.ok) {
        const b = await res.json().catch(() => ({}));
        setErreurSuggestions(b.detail || `Erreur ${res.status}`);
        return;
      }
      const data = await res.json();
      setSuggestions({
        ...data,
        lignes: (data.lignes || []).map((l: Record<string, unknown>) => ({
          ...l,
          debit: num(l.debit),
          credit: num(l.credit),
        })),
        total_debit: num(data.total_debit),
        total_credit: num(data.total_credit),
        solde_ouvert: num(data.solde_ouvert),
      });
    } catch {
      setErreurSuggestions('Serveur comptable injoignable.');
    } finally {
      setLoadingSuggestions(false);
    }
  }, []);

  const chargerLettrages = useCallback(async (compteId: number) => {
    try {
      const res = await fetch(`${API}/lettrages?compte_id=${compteId}`, { headers: AUTH() });
      if (!res.ok) { setLettrages([]); return; }
      const data = await res.json();
      setLettrages(Array.isArray(data) ? data : []);
    } catch {
      setLettrages([]);
    }
  }, []);

  useEffect(() => { chargerComptes(); }, [chargerComptes]);

  useEffect(() => {
    if (compteActif === null) { setSuggestions(null); setLettrages([]); return; }
    chargerSuggestions(compteActif);
    chargerLettrages(compteActif);
  }, [compteActif, chargerSuggestions, chargerLettrages]);

  const comptesFiltres = useMemo(
    () => comptes.filter(c => c.numero.includes(recherche) || c.intitule.toLowerCase().includes(recherche.toLowerCase())),
    [comptes, recherche]
  );

  const lignesSelectionnees = useMemo(
    () => (suggestions?.lignes || []).filter(l => selection.has(l.ligne_id)),
    [suggestions, selection]
  );
  const selDebit = lignesSelectionnees.reduce((s, l) => s + l.debit, 0);
  const selCredit = lignesSelectionnees.reduce((s, l) => s + l.credit, 0);
  const selEcart = selDebit - selCredit;
  const selectionSoldee = selection.size >= 2 && Math.abs(selEcart) < 0.005;

  const basculerLigne = (id: number) => {
    setSelection(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const toutCocher = () => {
    if (!suggestions) return;
    setSelection(prev => prev.size === suggestions.lignes.length
      ? new Set()
      : new Set(suggestions.lignes.map(l => l.ligne_id)));
  };

  const rechargerCompte = async () => {
    if (compteActif === null) return;
    await Promise.all([chargerSuggestions(compteActif), chargerLettrages(compteActif), chargerComptes()]);
  };

  const lettrerManuellement = async () => {
    if (compteActif === null || !selectionSoldee) return;
    setEnCour(true);
    try {
      const res = await fetch(`${API}/lettrage/manuel`, {
        method: 'POST',
        headers: AUTH(),
        body: JSON.stringify({
          compte_id: compteActif,
          lignes_ids: [...selection],
          date_lettrage: dateLettrage,
          effectue_par: OPERATEUR(),
          reference: reference || null,
        }),
      });
      const b = await res.json().catch(() => ({}));
      if (!res.ok) { toast.error(b.detail || `Le lettrage a échoué (${res.status})`); return; }
      toast.success(`Lettrage ${b.numero_lettrage} enregistré (${fmt(selDebit)} XAF rapprochés)`);
      setReference('');
      await rechargerCompte();
    } catch {
      toast.error('Serveur comptable injoignable.');
    } finally {
      setEnCour(false);
    }
  };

  const lettrerAutomatiquement = async () => {
    if (compteActif === null) return;
    setEnCour(true);
    try {
      const res = await fetch(
        `${API}/lettrage/automatique/${compteActif}?date_reference=${aujourdHui()}`,
        { method: 'POST', headers: AUTH() }
      );
      const b = await res.json().catch(() => ({}));
      if (!res.ok) { toast.error(b.detail || `Lettrage automatique impossible (${res.status})`); return; }
      toast.success(`${b.numero_lettrage} : ${fmt(num(b.montant_lettre))} XAF soldés automatiquement`);
      await rechargerCompte();
    } catch {
      toast.error('Serveur comptable injoignable.');
    } finally {
      setEnCour(false);
    }
  };

  const annuler = async (l: Lettrage) => {
    const motif = window.prompt(`Motif d'annulation du lettrage ${l.numero_lettrage} :`);
    if (!motif || !motif.trim()) return;
    setEnCour(true);
    try {
      const res = await fetch(
        `${API}/lettrage/${l.id}/annuler?motif=${encodeURIComponent(motif.trim())}`,
        { method: 'POST', headers: AUTH() }
      );
      const b = await res.json().catch(() => ({}));
      if (!res.ok) { toast.error(b.detail || `Annulation impossible (${res.status})`); return; }
      toast.success('Lettrage annulé — les écritures sont de nouveau ouvertes');
      await rechargerCompte();
    } catch {
      toast.error('Serveur comptable injoignable.');
    } finally {
      setEnCour(false);
    }
  };

  const actif = comptes.find(c => c.compteId === compteActif) || null;

  return (
    <div className="space-y-6 animate-in fade-in duration-300 font-sans">
      {/* Entête */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              Rapprochement comptable SYSCOHADA
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <CheckCheck className="w-8 h-8 text-violet-400" />
            Lettrage des comptes de tiers
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Source : lignes réelles du grand livre. Un lettrage n&apos;est accepté que si le
            solde de la sélection est nul (règle du rapprochement).
          </p>
        </div>
        <button onClick={chargerComptes}
          className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl flex items-center gap-2 border border-slate-700 transition-all self-start">
          <RefreshCw className={`w-3.5 h-3.5 ${loadingComptes ? 'animate-spin' : ''}`} /> Recharger
        </button>
      </div>

      {erreurComptes && (
        <div className="flex items-center gap-3 px-4 py-3 bg-red-950/60 border border-red-800/40 rounded-2xl text-xs text-red-300">
          <AlertCircle className="w-4 h-4 shrink-0" />{erreurComptes}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Colonne des comptes */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl flex flex-col">
          <div className="px-4 py-3 border-b border-slate-800 text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Link2 className="w-4 h-4 text-violet-400" /> Comptes de tiers ({comptesFiltres.length})
          </div>
          <div className="p-3 border-b border-slate-800">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input value={recherche} onChange={e => setRecherche(e.target.value)}
                placeholder="Filtrer 401 Clients, 402 Fournisseurs…"
                className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500 font-mono" />
            </div>
          </div>
          <div className="overflow-y-auto max-h-[520px] divide-y divide-slate-800/60">
            {loadingComptes ? (
              <div className="p-6 text-center text-slate-500 text-xs">Chargement…</div>
            ) : comptesFiltres.length === 0 ? (
              <div className="p-6 text-center text-slate-500 text-xs">
                Aucun compte de classe 4 avec des mouvements. Saisissez d&apos;abord des écritures
                d&apos;achat, de vente ou de règlement au journal.
              </div>
            ) : (
              comptesFiltres.map(c => (
                <button key={c.compteId} onClick={() => setCompteActif(c.compteId)}
                  className={`w-full text-left px-4 py-2.5 transition-colors ${compteActif === c.compteId ? 'bg-violet-600/20 border-l-2 border-violet-500' : 'hover:bg-slate-800/40 border-l-2 border-transparent'}`}>
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs font-bold text-violet-400">{c.numero}</span>
                    <span className={`font-mono text-[11px] ${c.soldeOuvert > 0 ? 'text-emerald-400' : c.soldeOuvert < 0 ? 'text-blue-400' : 'text-slate-500'}`}>
                      {c.soldeOuvert > 0 ? `${fmt(c.soldeOuvert)} D` : c.soldeOuvert < 0 ? `${fmt(-c.soldeOuvert)} C` : 'soldé'}
                    </span>
                  </div>
                  <div className="text-slate-300 text-xs truncate mt-0.5">{c.intitule}</div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Détail */}
        <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          {compteActif === null ? (
            <div className="p-12 text-center text-slate-500 text-sm">
              <Link2 className="w-10 h-10 mx-auto mb-3 text-slate-600" />
              Sélectionnez un compte pour afficher ses items ouverts.
            </div>
          ) : (
            <>
              <div className="px-5 py-4 border-b border-slate-800">
                <div className="text-sm font-black text-white font-mono">
                  {actif?.numero} — {actif?.intitule}
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  {suggestions ? `${suggestions.lignes.length} item(s) ouvert(s) · solde ${fmt(suggestions.solde_ouvert)} XAF` : 'Chargement…'}
                </div>
                <div className="flex items-center gap-2 mt-3">
                  <button onClick={() => setOnglet('OUVERTS')}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${onglet === 'OUVERTS' ? 'bg-violet-600 text-white' : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-white'}`}>
                    Items à lettrer
                  </button>
                  <button onClick={() => setOnglet('LETTRAGES')}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${onglet === 'LETTRAGES' ? 'bg-violet-600 text-white' : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-white'}`}>
                    Lettrages ({lettrages.length})
                  </button>
                  <div className="ml-auto flex items-center gap-2">
                    <button onClick={lettrerAutomatiquement} disabled={enCour || loadingSuggestions}
                      className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl flex items-center gap-2 transition-all">
                      <Wand2 className="w-3.5 h-3.5" /> Lettrage automatique FIFO
                    </button>
                  </div>
                </div>
              </div>

              {onglet === 'OUVERTS' && (
                erreurSuggestions ? (
                  <div className="m-4 flex items-center gap-3 px-4 py-3 bg-red-950/60 border border-red-800/40 rounded-2xl text-xs text-red-300">
                    <AlertCircle className="w-4 h-4 shrink-0" />{erreurSuggestions}
                  </div>
                ) : loadingSuggestions ? (
                  <div className="p-10 text-center text-slate-400 text-xs">Chargement des items ouverts…</div>
                ) : !suggestions || suggestions.lignes.length === 0 ? (
                  <div className="p-10 text-center text-slate-500 text-xs">
                    <CheckCheck className="w-10 h-10 mx-auto mb-3 text-emerald-500/60" />
                    Aucun item ouvert : ce compte est entièrement lettré.
                  </div>
                ) : (
                  <>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-slate-950/90 border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                          <tr>
                            <th className="py-2.5 px-3 w-10">
                              <input type="checkbox"
                                checked={selection.size === suggestions.lignes.length && selection.size > 0}
                                onChange={toutCocher}
                                className="accent-violet-600 bg-slate-950" aria-label="Tout cocher" />
                            </th>
                            <th className="py-2.5 px-3">Date</th>
                            <th className="py-2.5 px-3">Journal</th>
                            <th className="py-2.5 px-3">Libellé</th>
                            <th className="py-2.5 px-3 text-right text-emerald-400">Débit</th>
                            <th className="py-2.5 px-3 text-right text-blue-400">Crédit</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 text-slate-300">
                          {suggestions.lignes.map(l => (
                            <tr key={l.ligne_id} onClick={() => basculerLigne(l.ligne_id)}
                              className={`cursor-pointer transition-colors ${selection.has(l.ligne_id) ? 'bg-violet-600/15' : 'hover:bg-slate-800/40'}`}>
                              <td className="py-2 px-3">
                                <input type="checkbox" checked={selection.has(l.ligne_id)} onChange={() => basculerLigne(l.ligne_id)}
                                  onClick={e => e.stopPropagation()} className="accent-violet-600 bg-slate-950"
                                  aria-label={`Sélection ligne ${l.ligne_id}`} />
                              </td>
                              <td className="py-2 px-3 text-slate-400 whitespace-nowrap">{fmtDate(l.date_ecriture)}</td>
                              <td className="py-2 px-3">
                                <span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px]">{l.journal ?? '—'}</span>
                              </td>
                              <td className="py-2 px-3 font-sans max-w-[240px] truncate" title={l.libelle ?? ''}>{l.libelle ?? '—'}</td>
                              <td className="py-2 px-3 text-right text-emerald-400">{l.debit > 0 ? fmt(l.debit) : '-'}</td>
                              <td className="py-2 px-3 text-right text-blue-400">{l.credit > 0 ? fmt(l.credit) : '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Barre de rapprochement */}
                    <div className="px-4 py-3 border-t border-slate-800 bg-slate-950/60">
                      <div className="flex flex-wrap items-center gap-3 text-[11px] font-mono">
                        <span className="text-slate-400">{selection.size} ligne(s) cochée(s)</span>
                        <span className="text-emerald-400">Débit {fmt(selDebit)}</span>
                        <span className="text-blue-400">Crédit {fmt(selCredit)}</span>
                        <span className={selectionSoldee ? 'text-emerald-400 font-black' : 'text-amber-400 font-black'}>
                          {selection.size === 0 ? 'Sélectionnez un ensemble à solder'
                            : selectionSoldee ? '✓ Solde nul — lettrage possible'
                            : `⚠ Écart ${fmt(Math.abs(selEcart))} XAF — lettrage refusé`}
                        </span>
                      </div>

                      <div className="flex flex-wrap items-end gap-3 mt-3">
                        <label className="flex flex-col gap-1">
                          <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Date de lettrage</span>
                          <input type="date" value={dateLettrage} onChange={e => setDateLettrage(e.target.value)}
                            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 font-mono focus:outline-none focus:border-violet-500" />
                        </label>
                        <label className="flex flex-col gap-1 flex-1 min-w-[180px]">
                          <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Référence (facultative)</span>
                          <input value={reference} onChange={e => setReference(e.target.value)}
                            placeholder="N° de chèque, virement…"
                            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-violet-500" />
                        </label>
                        <button onClick={lettrerManuellement}
                          disabled={!selectionSoldee || enCour}
                          title={selectionSoldee ? 'Lettrer la sélection' : 'La sélection doit être soldée (débit = crédit)'}
                          className="px-4 py-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl flex items-center gap-2 transition-all">
                          <Plus className="w-3.5 h-3.5" /> Lettrer la sélection
                        </button>
                      </div>
                    </div>
                  </>
                )
              )}

              {onglet === 'LETTRAGES' && (
                lettrages.length === 0 ? (
                  <div className="p-10 text-center text-slate-500 text-xs">
                    <ListChecks className="w-10 h-10 mx-auto mb-3 text-slate-600" />
                    Aucun lettrage enregistré pour ce compte.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950/90 border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                        <tr>
                          <th className="py-2.5 px-3">N° lettrage</th>
                          <th className="py-2.5 px-3">Type</th>
                          <th className="py-2.5 px-3">Date</th>
                          <th className="py-2.5 px-3 text-right">Montant lettré</th>
                          <th className="py-2.5 px-3">Référence</th>
                          <th className="py-2.5 px-3">Par</th>
                          <th className="py-2.5 px-3 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 text-slate-300">
                        {lettrages.map(l => {
                          const annule = l.date_annulation !== null;
                          return (
                            <tr key={l.id} className={annule ? 'opacity-50' : ''}>
                              <td className="py-2 px-3 text-violet-400 font-bold whitespace-nowrap">{l.numero_lettrage}</td>
                              <td className="py-2 px-3">
                                <span className={`px-1.5 py-0.5 rounded text-[10px] border ${l.type_lettrage === 'automatique' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'}`}>
                                  {l.type_lettrage}
                                </span>
                              </td>
                              <td className="py-2 px-3 text-slate-400 whitespace-nowrap">{fmtDate(l.date_lettrage)}</td>
                              <td className="py-2 px-3 text-right text-slate-200">{fmt(num(l.montant_lettre))}</td>
                              <td className="py-2 px-3 text-slate-400">{l.reference_lettrage || '—'}</td>
                              <td className="py-2 px-3 text-slate-400">{l.effectue_par || '—'}</td>
                              <td className="py-2 px-3 text-right">
                                {annule ? (
                                  <span className="text-[10px] text-red-400" title={l.motif_annulation || ''}>annulé</span>
                                ) : (
                                  <button onClick={() => annuler(l)} disabled={enCour}
                                    className="px-2 py-1 bg-slate-800 hover:bg-red-900/60 disabled:opacity-40 text-red-300 text-[11px] font-bold rounded-lg flex items-center gap-1.5 border border-slate-700 transition-all ml-auto">
                                    <Undo2 className="w-3 h-3" /> Annuler
                                  </button>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Layers, Search, BookOpen, ChevronLeft, Printer, RefreshCw,
  AlertCircle, Building2,
} from 'lucide-react';
import CompanyDocumentHeader, { CompanyDocumentFooter } from '@/components/documents/CompanyDocumentHeader';

const AUTH = () => ({ 'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('access_token') || '' : ''}` });

export interface AccountSummary {
  compte_id: number;
  compte: string;
  intitule: string;
  classe: string;
  soldeInitialDebit: number;
  soldeInitialCredit: number;
  mouvementsDebit: number;
  mouvementsCredit: number;
  soldeFinalDebit: number;
  soldeFinalCredit: number;
}

interface LedgerLine {
  id: number;
  date_ecriture: string;
  libelle: string | null;
  journal: string | null;
  periode: string | null;
  debit: number;
  credit: number;
  statut_lettrage: string | null;
}

interface LedgerRow extends LedgerLine {
  soldeDebit: number;
  soldeCredit: number;
}

const num = (v: unknown): number => {
  const n = typeof v === 'string' ? parseFloat(v) : (v as number);
  return Number.isFinite(n) ? (n as number) : 0;
};
const fmt = (n: number) => Math.round(n).toLocaleString('fr-FR');
const fmtDate = (iso: string | null) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString('fr-FR');
};

export default function ComptabiliteOhadaGeneralLedger() {
  const [viewMode, setViewMode] = useState<'BALANCE' | 'GRAND_LIVRE'>('BALANCE');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClasse, setSelectedClasse] = useState<string>('ALL');
  const [accounts, setAccounts] = useState<AccountSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [equilibree, setEquilibree] = useState<boolean | null>(null);

  // Grand livre auxiliaire (par compte)
  const [selectedCompteId, setSelectedCompteId] = useState<number | null>(null);
  const [ledger, setLedger] = useState<LedgerRow[]>([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerError, setLedgerError] = useState<string | null>(null);

  const fetchAccountsAndBalance = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetch('/api/v1/comptabilite-avance/balances/verification', { headers: AUTH() });
      if (res.ok) {
        const data = await res.json();
        const items = data?.lignes || (Array.isArray(data) ? data : []);
        setEquilibree(typeof data?.equilibree === 'boolean' ? data.equilibree : null);
        setAccounts(items.map((item: Record<string, unknown>) => {
          const numero = String(item.compte_numero ?? item.compte ?? '');
          return {
            compte_id: Number(item.compte_id),
            compte: numero,
            intitule: String(item.compte_intitule ?? item.intitule ?? ''),
            classe: `Classe ${numero.charAt(0)}`,
            soldeInitialDebit: num(item.solde_initial_debit),
            soldeInitialCredit: num(item.solde_initial_credit),
            mouvementsDebit: num(item.debit),
            mouvementsCredit: num(item.credit),
            soldeFinalDebit: num(item.solde_final_debit),
            soldeFinalCredit: num(item.solde_final_credit),
          };
        }));
      } else {
        const b = await res.json().catch(() => ({}));
        setError(b.detail || `Erreur ${res.status}`);
        setAccounts([]);
      }
    } catch {
      setError('Serveur comptable injoignable.');
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAccountsAndBalance(); }, [fetchAccountsAndBalance]);

  const chargerGrandLivre = useCallback(async (compteId: number) => {
    setLedgerLoading(true); setLedgerError(null); setLedger([]);
    try {
      // Large plage : tout l'historique réellement comptabilisé pour ce compte.
      const res = await fetch(
        `/api/v1/comptabilite-avance/grand-livre/auxiliaire/${compteId}?date_debut=1970-01-01&date_fin=2999-12-31`,
        { headers: AUTH() }
      );
      if (res.ok) {
        const data = await res.json();
        const lignes: LedgerLine[] = Array.isArray(data) ? data : [];
        // Solde cours cumulatif calculé sur les lignes réelles (dérivé, jamais inventé).
        let net = 0;
        setLedger(lignes.map(l => {
          net += num(l.debit) - num(l.credit);
          return { ...l, soldeDebit: net > 0 ? net : 0, soldeCredit: net < 0 ? -net : 0 };
        }));
      } else {
        const b = await res.json().catch(() => ({}));
        setLedgerError(b.detail || `Erreur ${res.status}`);
      }
    } catch {
      setLedgerError('Serveur comptable injoignable.');
    } finally {
      setLedgerLoading(false);
    }
  }, []);

  const selectionnerCompte = (compteId: number) => {
    setSelectedCompteId(compteId);
    chargerGrandLivre(compteId);
  };

  const filtered = accounts.filter(a => {
    const matchClasse = selectedClasse === 'ALL' || a.classe.includes(selectedClasse);
    const matchSearch = a.compte.includes(searchQuery) || a.intitule.toLowerCase().includes(searchQuery.toLowerCase());
    return matchClasse && matchSearch;
  });

  const totaux = filtered.reduce((acc, a) => ({
    debInit: acc.debInit + a.soldeInitialDebit,
    credInit: acc.credInit + a.soldeInitialCredit,
    mouvDeb: acc.mouvDeb + a.mouvementsDebit,
    mouvCred: acc.mouvCred + a.mouvementsCredit,
    debFin: acc.debFin + a.soldeFinalDebit,
    credFin: acc.credFin + a.soldeFinalCredit,
  }), { debInit: 0, credInit: 0, mouvDeb: 0, mouvCred: 0, debFin: 0, credFin: 0 });

  const ledgerTotaux = ledger.reduce((acc, l) => ({
    deb: acc.deb + num(l.debit), cred: acc.cred + num(l.credit),
  }), { deb: 0, cred: 0 });

  const selectedAccount = accounts.find(a => a.compte_id === selectedCompteId) || null;

  return (
    <div className="space-y-6 animate-in fade-in duration-300 font-sans">
      {/* Official Header for Print */}
      <div className="hidden print:block">
        <CompanyDocumentHeader
          documentTitle={viewMode === 'BALANCE' ? "BALANCE GÉNÉRALE DES COMPTES À 6 COLONNES" : `GRAND LIVRE — ${selectedAccount?.compte || ''} ${selectedAccount?.intitule || ''}`}
          documentNumber={`ETAT-OHADA-${new Date().getFullYear()}-${viewMode}`}
          documentDate={new Date().toLocaleDateString('fr-FR')}
          documentReference="ETATS-SYSCOHADA-OFFICIEL"
        />
      </div>

      {/* Screen Header Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl print:hidden">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              Grand Livre &amp; Balances SYSCOHADA
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Layers className="w-8 h-8 text-violet-400" />
            {viewMode === 'BALANCE' ? 'Balance de Vérification (6 Colonnes)' : 'Grand Livre des Comptes'}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Source : grand livre réel (pièces en partie double). Aucune valeur simulée.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-slate-950 p-1 rounded-2xl border border-slate-800 flex items-center">
            <button onClick={() => setViewMode('BALANCE')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${viewMode === 'BALANCE' ? 'bg-violet-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}>
              Balance 6 Colonnes
            </button>
            <button onClick={() => { setViewMode('GRAND_LIVRE'); if (selectedCompteId === null && filtered[0]) selectionnerCompte(filtered[0].compte_id); }}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${viewMode === 'GRAND_LIVRE' ? 'bg-violet-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}>
              Grand Livre
            </button>
          </div>
          <button onClick={fetchAccountsAndBalance} className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl flex items-center gap-2 border border-slate-700 transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Recharger
          </button>
          <button onClick={() => window.print()} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-xs rounded-xl flex items-center gap-2 transition-all">
            <Printer className="w-4 h-4 text-slate-400" /> Imprimer État
          </button>
        </div>
      </div>

      {/* Barre de Recherche & Sélecteur de Classes OHADA */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 print:hidden">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input type="text" placeholder="Filtrer par N° de compte ou intitulé..." value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500 font-mono" />
        </div>
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 scrollbar-none">
          {[
            { id: 'ALL', label: 'Toutes' }, { id: 'Classe 1', label: 'Cl. 1 Capitaux' },
            { id: 'Classe 2', label: 'Cl. 2 Immob.' }, { id: 'Classe 3', label: 'Cl. 3 Stocks' },
            { id: 'Classe 4', label: 'Cl. 4 Tiers' }, { id: 'Classe 5', label: 'Cl. 5 Tréso' },
            { id: 'Classe 6', label: 'Cl. 6 Charges' }, { id: 'Classe 7', label: 'Cl. 7 Produits' },
          ].map(c => (
            <button key={c.id} onClick={() => setSelectedClasse(c.id)}
              className={`px-3 py-1.5 rounded-lg text-[11px] font-bold whitespace-nowrap transition-all ${selectedClasse === c.id ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40' : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-white'}`}>
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-3 px-4 py-3 bg-red-950/60 border border-red-800/40 rounded-2xl text-xs text-red-300 print:hidden">
          <AlertCircle className="w-4 h-4 shrink-0" />{error}
        </div>
      )}

      {/* ============ VUE BALANCE ============ */}
      {viewMode === 'BALANCE' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/90 border-b border-slate-800 text-[11px] uppercase tracking-wider font-mono text-slate-400">
                <tr>
                  <th rowSpan={2} className="py-3 px-4 border-r border-slate-800">Compte</th>
                  <th rowSpan={2} className="py-3 px-4 border-r border-slate-800">Intitulé SYSCOHADA</th>
                  <th colSpan={2} className="py-2 px-4 text-center border-b border-r border-slate-800 bg-slate-900/50">Soldes d&apos;Ouverture</th>
                  <th colSpan={2} className="py-2 px-4 text-center border-b border-r border-slate-800 bg-slate-900/80">Mouvements Période</th>
                  <th colSpan={2} className="py-2 px-4 text-center bg-slate-900/50">Soldes de Clôture</th>
                </tr>
                <tr>
                  <th className="py-2 px-3 text-right border-r border-slate-800 text-emerald-400">Débit</th>
                  <th className="py-2 px-3 text-right border-r border-slate-800 text-blue-400">Crédit</th>
                  <th className="py-2 px-3 text-right border-r border-slate-800 text-emerald-400">Débit</th>
                  <th className="py-2 px-3 text-right border-r border-slate-800 text-blue-400">Crédit</th>
                  <th className="py-2 px-3 text-right border-r border-slate-800 text-emerald-400">Débiteur</th>
                  <th className="py-2 px-3 text-right text-blue-400">Créditeur</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr><td colSpan={8} className="py-12 text-center text-slate-500">Chargement de la balance…</td></tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-500">
                      <Layers className="w-10 h-10 mx-auto mb-2 text-slate-400" />
                      Aucun compte avec mouvements pour ce filtre. Saisissez des écritures au journal pour générer la balance.
                    </td>
                  </tr>
                ) : (
                  filtered.map(a => (
                    <tr key={a.compte_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-2.5 px-4 font-bold text-violet-400 border-r border-slate-800/60">{a.compte}</td>
                      <td className="py-2.5 px-4 text-slate-200 font-sans border-r border-slate-800/60 font-medium">{a.intitule}</td>
                      <td className="py-2.5 px-3 text-right border-r border-slate-800/60 text-slate-300">{a.soldeInitialDebit > 0 ? fmt(a.soldeInitialDebit) : '-'}</td>
                      <td className="py-2.5 px-3 text-right border-r border-slate-800/60 text-slate-300">{a.soldeInitialCredit > 0 ? fmt(a.soldeInitialCredit) : '-'}</td>
                      <td className="py-2.5 px-3 text-right border-r border-slate-800/60 font-bold text-emerald-400">{a.mouvementsDebit > 0 ? fmt(a.mouvementsDebit) : '-'}</td>
                      <td className="py-2.5 px-3 text-right border-r border-slate-800/60 font-bold text-blue-400">{a.mouvementsCredit > 0 ? fmt(a.mouvementsCredit) : '-'}</td>
                      <td className="py-2.5 px-3 text-right border-r border-slate-800/60 font-black text-emerald-400 bg-emerald-950/10">{a.soldeFinalDebit > 0 ? fmt(a.soldeFinalDebit) : '-'}</td>
                      <td className="py-2.5 px-3 text-right font-black text-blue-400 bg-blue-950/10">{a.soldeFinalCredit > 0 ? fmt(a.soldeFinalCredit) : '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
              {filtered.length > 0 && (
                <tfoot className="bg-slate-950 border-t-2 border-slate-700 font-mono font-black text-xs text-white">
                  <tr>
                    <td colSpan={2} className="py-3 px-4 uppercase text-slate-400 border-r border-slate-800">TOTAUX CONSOLIDÉS (XAF)</td>
                    <td className="py-3 px-3 text-right border-r border-slate-800 text-emerald-400">{fmt(totaux.debInit)}</td>
                    <td className="py-3 px-3 text-right border-r border-slate-800 text-blue-400">{fmt(totaux.credInit)}</td>
                    <td className="py-3 px-3 text-right border-r border-slate-800 text-emerald-400">{fmt(totaux.mouvDeb)}</td>
                    <td className="py-3 px-3 text-right border-r border-slate-800 text-blue-400">{fmt(totaux.mouvCred)}</td>
                    <td className="py-3 px-3 text-right border-r border-slate-800 text-emerald-300 bg-emerald-950/20">{fmt(totaux.debFin)}</td>
                    <td className="py-3 px-3 text-right text-blue-300 bg-blue-950/20">{fmt(totaux.credFin)}</td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
          {equilibree !== null && filtered.length > 0 && (
            <div className={`px-4 py-2 text-[11px] font-mono border-t border-slate-800 ${equilibree ? 'text-emerald-400' : 'text-amber-400'}`}>
              {equilibree ? '✓ Balance équilibrée (total débit = total crédit)' : '⚠ Balance déséquilibrée : à contrôler'}
            </div>
          )}
        </div>
      )}

      {/* ============ VUE GRAND LIVRE (forreal) ============ */}
      {viewMode === 'GRAND_LIVRE' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Sélecteur de compte */}
          <div className="lg:col-span-1 bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl flex flex-col">
            <div className="px-4 py-3 border-b border-slate-800 text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-violet-400" /> Comptes ({filtered.length})
            </div>
            <div className="overflow-y-auto max-h-[560px] divide-y divide-slate-800/60">
              {loading ? (
                <div className="p-6 text-center text-slate-500 text-xs">Chargement…</div>
              ) : filtered.length === 0 ? (
                <div className="p-6 text-center text-slate-500 text-xs">Aucun compte avec mouvements. Saisissez des écritures au journal.</div>
              ) : (
                filtered.map(a => (
                  <button key={a.compte_id} onClick={() => selectionnerCompte(a.compte_id)}
                    className={`w-full text-left px-4 py-2.5 transition-colors ${selectedCompteId === a.compte_id ? 'bg-violet-600/20 border-l-2 border-violet-500' : 'hover:bg-slate-800/40 border-l-2 border-transparent'}`}>
                    <div className="font-mono text-xs font-bold text-violet-400">{a.compte}</div>
                    <div className="text-slate-300 text-xs truncate">{a.intitule}</div>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Détail du grand livre auxiliaire */}
          <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
            {!selectedCompteId ? (
              <div className="p-12 text-center text-slate-500 text-sm">
                <BookOpen className="w-10 h-10 mx-auto mb-3 text-slate-600" />
                Sélectionnez un compte pour afficher son grand livre auxiliaire.
              </div>
            ) : (
              <>
                <div className="px-5 py-4 border-b border-slate-800 flex items-center gap-3 print:border-slate-300">
                  <button onClick={() => setViewMode('BALANCE')} className="text-slate-500 hover:text-white print:hidden"><ChevronLeft className="w-4 h-4" /></button>
                  <div>
                    <div className="text-sm font-black text-white font-mono">{selectedAccount?.compte} — {selectedAccount?.intitule}</div>
                    <div className="text-[11px] text-slate-400">Grand livre auxiliaire {ledger.length} écriture(s)</div>
                  </div>
                </div>

                {ledgerError ? (
                  <div className="m-4 flex items-center gap-3 px-4 py-3 bg-red-950/60 border border-red-800/40 rounded-2xl text-xs text-red-300">
                    <AlertCircle className="w-4 h-4 shrink-0" />{ledgerError}
                  </div>
                ) : ledgerLoading ? (
                  <div className="p-10 text-center text-slate-400 text-xs">Chargement du grand livre…</div>
                ) : ledger.length === 0 ? (
                  <div className="p-10 text-center text-slate-500 text-xs">Aucune écriture pour ce compte.</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950/90 border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                        <tr>
                          <th className="py-2.5 px-3">Date</th>
                          <th className="py-2.5 px-3">Journal</th>
                          <th className="py-2.5 px-3">Libellé</th>
                          <th className="py-2.5 px-3 text-right text-emerald-400">Débit</th>
                          <th className="py-2.5 px-3 text-right text-blue-400">Crédit</th>
                          <th className="py-2.5 px-3 text-right">Solde Déb.</th>
                          <th className="py-2.5 px-3 text-right">Solde Créd.</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 text-slate-300">
                        {ledger.map(l => (
                          <tr key={l.id} className="hover:bg-slate-800/40">
                            <td className="py-2 px-3 text-slate-400 whitespace-nowrap">{fmtDate(l.date_ecriture)}</td>
                            <td className="py-2 px-3"><span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px]">{l.journal ?? '—'}</span></td>
                            <td className="py-2 px-3 font-sans max-w-[260px] truncate" title={l.libelle ?? ''}>{l.libelle ?? ''}</td>
                            <td className="py-2 px-3 text-right text-emerald-400">{num(l.debit) > 0 ? fmt(num(l.debit)) : '-'}</td>
                            <td className="py-2 px-3 text-right text-blue-400">{num(l.credit) > 0 ? fmt(num(l.credit)) : '-'}</td>
                            <td className="py-2 px-3 text-right text-emerald-300">{l.soldeDebit > 0 ? fmt(l.soldeDebit) : '-'}</td>
                            <td className="py-2 px-3 text-right text-blue-300">{l.soldeCredit > 0 ? fmt(l.soldeCredit) : '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot className="bg-slate-950 border-t-2 border-slate-700 font-black text-white">
                        <tr>
                          <td colSpan={3} className="py-2.5 px-3 uppercase text-slate-400 text-[11px]">Totaux</td>
                          <td className="py-2.5 px-3 text-right text-emerald-400">{fmt(ledgerTotaux.deb)}</td>
                          <td className="py-2.5 px-3 text-right text-blue-400">{fmt(ledgerTotaux.cred)}</td>
                          <td colSpan={2} className="py-2.5 px-3 text-right text-slate-300">
                            {fmt(Math.abs(ledgerTotaux.deb - ledgerTotaux.cred))} {ledgerTotaux.deb >= ledgerTotaux.cred ? 'D' : 'C'}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Official Footer for Print */}
      <div className="hidden print:block"><CompanyDocumentFooter /></div>
    </div>
  );
}

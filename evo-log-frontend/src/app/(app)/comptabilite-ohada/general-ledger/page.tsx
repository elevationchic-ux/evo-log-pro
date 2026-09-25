'use client';

import React, { useState, useEffect } from 'react';
import {
  Layers, Search, Filter, Download, ArrowUpDown,
  BookOpen, Calculator, CheckCircle2, FileText, ChevronRight,
  Printer, RefreshCw, AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import CompanyDocumentHeader, { CompanyDocumentFooter } from '@/components/documents/CompanyDocumentHeader';

export interface AccountSummary {
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

export default function ComptabiliteOhadaGeneralLedger() {
  const [viewMode, setViewMode] = useState<'BALANCE' | 'GRAND_LIVRE'>('BALANCE');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClasse, setSelectedClasse] = useState<string>('ALL');
  const [accounts, setAccounts] = useState<AccountSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAccountsAndBalance = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/comptabilite-avance/balances/verification', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}` }
      });
      if (res.ok) {
        const data = await res.json();
        const items = data?.lignes || (Array.isArray(data) ? data : []);
        if (items.length > 0) {
          setAccounts(items.map((item: any) => ({
            compte: item.compte_numero || item.compte,
            intitule: item.compte_intitule || item.intitule,
            classe: `Classe ${String(item.compte_numero || item.compte).charAt(0)}`,
            soldeInitialDebit: parseFloat(item.solde_initial_debit || 0),
            soldeInitialCredit: parseFloat(item.solde_initial_credit || 0),
            mouvementsDebit: parseFloat(item.debit || item.mouvementsDebit || 0),
            mouvementsCredit: parseFloat(item.credit || item.mouvementsCredit || 0),
            soldeFinalDebit: parseFloat(item.solde_final_debit || 0),
            soldeFinalCredit: parseFloat(item.solde_final_credit || 0),
          })));
        } else {
          setAccounts([]);
        }
      } else {
        setAccounts([]);
      }
    } catch {
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccountsAndBalance();
  }, []);

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

  const handlePrint = () => {
    toast.success(
      viewMode === 'BALANCE'
        ? 'Impression de la Balance Générale à 6 Colonnes...'
        : 'Impression du Grand Livre Général des Comptes...'
    );
    window.print();
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300 font-sans">
      {/* Official Header for Print */}
      <div className="hidden print:block">
        <CompanyDocumentHeader
          documentTitle={viewMode === 'BALANCE' ? "BALANCE GÉNÉRALE DES COMPTES À 6 COLONNES" : "GRAND LIVRE GÉNÉRAL SYSCOHADA"}
          documentNumber={`ETAT-OHADA-${new Date().getFullYear()}-${viewMode}`}
          documentDate={new Date().toLocaleDateString('fr-FR')}
          documentReference="ETATS-SYSCOHADA-OFFICIEL"
        />
      </div>

      {/* Screen Header Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl print:hidden">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              Grand Livre & Balances SYSCOHADA
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KOHA_GLB
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Layers className="w-8 h-8 text-violet-400" />
            {viewMode === 'BALANCE' ? 'Balance de Vérification (6 Colonnes)' : 'Grand Livre des Comptes'}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Soldes d&apos;ouverture, mouvements de la période et soldes finaux conformes aux 8 classes SYSCOHADA.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Mode Switcher */}
          <div className="bg-slate-950 p-1 rounded-2xl border border-slate-800 flex items-center">
            <button
              onClick={() => setViewMode('BALANCE')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                viewMode === 'BALANCE'
                  ? 'bg-violet-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Balance 6 Colonnes
            </button>
            <button
              onClick={() => setViewMode('GRAND_LIVRE')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                viewMode === 'GRAND_LIVRE'
                  ? 'bg-violet-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Grand Livre
            </button>
          </div>

          <button
            onClick={handlePrint}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-xs rounded-xl flex items-center gap-2 transition-all"
          >
            <Printer className="w-4 h-4 text-slate-400" /> Imprimer État
          </button>
        </div>
      </div>

      {/* Barre de Recherche & Sélecteur de Classes OHADA */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 print:hidden">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Filtrer par N° de compte ou intitulé..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500 font-mono"
          />
        </div>

        {/* Classes OHADA */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 scrollbar-none">
          {[
            { id: 'ALL', label: 'Toutes' },
            { id: 'Classe 1', label: 'Cl. 1 Capitaux' },
            { id: 'Classe 2', label: 'Cl. 2 Immob.' },
            { id: 'Classe 3', label: 'Cl. 3 Stocks' },
            { id: 'Classe 4', label: 'Cl. 4 Tiers' },
            { id: 'Classe 5', label: 'Cl. 5 Tréso' },
            { id: 'Classe 6', label: 'Cl. 6 Charges' },
            { id: 'Classe 7', label: 'Cl. 7 Produits' },
          ].map(c => (
            <button
              key={c.id}
              onClick={() => setSelectedClasse(c.id)}
              className={`px-3 py-1.5 rounded-lg text-[11px] font-bold whitespace-nowrap transition-all ${
                selectedClasse === c.id
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40'
                  : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-white'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table Balance à 6 Colonnes */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/90 border-b border-slate-800 text-[10px] uppercase tracking-wider font-mono text-slate-400">
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
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    <Layers className="w-10 h-10 mx-auto mb-2 text-slate-400" />
                    Aucun compte avec mouvements pour ce filtre. Saisissez des écritures au journal pour générer la balance.
                  </td>
                </tr>
              ) : (
                filtered.map(a => (
                  <tr key={a.compte} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-4 font-bold text-violet-400 border-r border-slate-800/60">{a.compte}</td>
                    <td className="py-2.5 px-4 text-slate-200 font-sans border-r border-slate-800/60 font-medium">{a.intitule}</td>
                    <td className="py-2.5 px-3 text-right border-r border-slate-800/60 text-slate-300">
                      {a.soldeInitialDebit > 0 ? a.soldeInitialDebit.toLocaleString() : '-'}
                    </td>
                    <td className="py-2.5 px-3 text-right border-r border-slate-800/60 text-slate-300">
                      {a.soldeInitialCredit > 0 ? a.soldeInitialCredit.toLocaleString() : '-'}
                    </td>
                    <td className="py-2.5 px-3 text-right border-r border-slate-800/60 font-bold text-emerald-400">
                      {a.mouvementsDebit > 0 ? a.mouvementsDebit.toLocaleString() : '-'}
                    </td>
                    <td className="py-2.5 px-3 text-right border-r border-slate-800/60 font-bold text-blue-400">
                      {a.mouvementsCredit > 0 ? a.mouvementsCredit.toLocaleString() : '-'}
                    </td>
                    <td className="py-2.5 px-3 text-right border-r border-slate-800/60 font-black text-emerald-400 bg-emerald-950/10">
                      {a.soldeFinalDebit > 0 ? a.soldeFinalDebit.toLocaleString() : '-'}
                    </td>
                    <td className="py-2.5 px-3 text-right font-black text-blue-400 bg-blue-950/10">
                      {a.soldeFinalCredit > 0 ? a.soldeFinalCredit.toLocaleString() : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
            {filtered.length > 0 && (
              <tfoot className="bg-slate-950 border-t-2 border-slate-700 font-mono font-black text-xs text-white">
                <tr>
                  <td colSpan={2} className="py-3 px-4 uppercase text-slate-400 border-r border-slate-800">
                    TOTAUX CONSOLIDÉS (XAF)
                  </td>
                  <td className="py-3 px-3 text-right border-r border-slate-800 text-emerald-400">
                    {totaux.debInit.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right border-r border-slate-800 text-blue-400">
                    {totaux.credInit.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right border-r border-slate-800 text-emerald-400">
                    {totaux.mouvDeb.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right border-r border-slate-800 text-blue-400">
                    {totaux.mouvCred.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right border-r border-slate-800 text-emerald-300 bg-emerald-950/20">
                    {totaux.debFin.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right text-blue-300 bg-blue-950/20">
                    {totaux.credFin.toLocaleString()}
                  </td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      </div>

      {/* Official Footer for Print */}
      <div className="hidden print:block">
        <CompanyDocumentFooter />
      </div>
    </div>
  );
}

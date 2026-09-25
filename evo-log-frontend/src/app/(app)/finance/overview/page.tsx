'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  DollarSign, TrendingUp, ArrowUpRight, ArrowDownRight, Building2,
  Plus, FileText, Banknote, AlertCircle
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { financeAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

interface FinanceKpis {
  chiffre_affaires: number;
  total_factures: number;
  total_encaisse: number;
  montant_impaye: number;
  taux_recouvrement: number;
  creances_douteuses: number;
  tresorerie_disponible: number;
}

interface AgeeRow {
  client: string;
  en_cours: number;
  j60: number;
  j90: number;
  statut: 'OK' | 'RISQUE' | 'CRITIQUE';
}

interface JournalRow {
  date: string;
  libelle: string;
  compte: string;
  statut: string;
  montant: number;
  type: 'RECETTE' | 'DEPENSE';
}

const fmtM = (n: number) => (n / 1_000_000).toFixed(1);

export default function FinanceOverviewPage() {
  const router = useRouter();
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const [kpis, setKpis] = useState<FinanceKpis | null>(null);
  const [balanceAgee, setBalanceAgee] = useState<AgeeRow[]>([]);
  const [recentEntries, setRecentEntries] = useState<JournalRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setErreur(null);
    try {
      const [kpisRes, facturesRes, encaissementsRes] = await Promise.all([
        financeAPI.getKpis(),
        financeAPI.getFactures(),
        financeAPI.getEncaissements(),
      ]);
      setKpis(kpisRes.data as FinanceKpis);

      const factures: any[] = Array.isArray(facturesRes.data) ? facturesRes.data : [];
      const encaissements: any[] = Array.isArray(encaissementsRes.data) ? encaissementsRes.data : [];

      // ── Balance âgée : agrégation réelle par client, buckets d'ancienneté ──
      const now = Date.now();
      const byClient = new Map<string, AgeeRow>();
      for (const f of factures) {
        const impaye = Number(f.montant_ttc || 0); // approx: payé retranché globalement ci-dessous
        if (['payee', 'annulee', 'brouillon'].includes(String(f.statut))) continue;
        const echeance = f.date_echeance ? new Date(f.date_echeance).getTime() : now;
        const jours = Math.max(0, Math.floor((now - echeance) / 86_400_000));
        const nom = f.client_nom || `Client #${f.client_id ?? '?'}`;
        const row = byClient.get(nom) || { client: nom, en_cours: 0, j60: 0, j90: 0, statut: 'OK' };
        if (jours > 90) row.j90 += impaye;
        else if (jours > 30) row.j60 += impaye;
        else row.en_cours += impaye;
        byClient.set(nom, row);
      }
      const rows = Array.from(byClient.values()).map((r) => ({
        ...r,
        statut: (r.j90 > 0 ? 'CRITIQUE' : r.j60 > 0 ? 'RISQUE' : 'OK') as AgeeRow['statut'],
      })).sort((a, b) => (b.j90 + b.j60 + b.en_cours) - (a.j90 + a.j60 + a.en_cours));
      setBalanceAgee(rows);

      // ── Journal de trésorerie récent : encaissements réels ──
      setRecentEntries(
        encaissements.slice(0, 12).map((p: any) => ({
          date: p.date_paiement ? new Date(p.date_paiement).toLocaleDateString('fr-FR') : '',
          libelle: `Encaissement facture #${p.facture_id ?? '?'}`,
          compte: p.mode_paiement || 'banque',
          statut: p.statut || 'confirme',
          montant: Number(p.montant || 0),
          type: 'RECETTE' as const,
        }))
      );
    } catch (e) {
      setErreur('Les données financières n\'ont pas pu être chargées. Vérifiez votre connexion et réessayez.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const statusColors: Record<string, string> = {
    OK: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    RISQUE: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    CRITIQUE: 'bg-red-500/10 text-red-400 border-red-500/30',
  };

  const k = kpis;
  const cashKpis = [
    { label: 'Trésorerie Globale', value: k ? fmtM(k.tresorerie_disponible) : '0.0', sub: 'Comptes de classe 5 (banque/caisse)', icon: Banknote, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
    { label: 'Encaissé (cumul)', value: k ? fmtM(k.total_encaisse) : '0.0', sub: 'Règlements clients perçus', icon: ArrowUpRight, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
    { label: 'Impayés', value: k ? fmtM(k.montant_impaye) : '0.0', sub: 'Facturé non réglé', icon: ArrowDownRight, color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
    { label: 'Taux Recouvrement', value: k ? `${k.taux_recouvrement}%` : '0%', sub: `CA facturé: ${k ? fmtM(k.chiffre_affaires) : '0.0'} M XAF`, icon: TrendingUp, color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <DollarSign className="w-6 h-6 text-amber-400" /> Finance & Trésorerie OHADA
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Données réelles agrégées depuis la base (factures, encaissements, plan comptable)
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} className="px-3 py-2 border border-slate-700 rounded-xl text-xs text-slate-300 hover:bg-slate-800">{t('Actualiser', 'Refresh')}</button>
          <button onClick={() => router.push('/comptabilite-ohada/journal')} className="px-4 py-2 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg">
            <Plus className="w-4 h-4" /> {t('Écriture Comptable', 'Accounting Entry')}
          </button>
        </div>
      </div>

      {erreur && (
        <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4" /> {erreur}
        </div>
      )}

      {/* Cash Flow KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        {cashKpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div key={i} className={`${kpi.bg} border rounded-2xl p-4 shadow-lg`}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${kpi.color}`} />
                <span className="text-xs text-slate-400 truncate">{kpi.label}</span>
              </div>
              <div className={`text-2xl font-black font-mono ${kpi.color}`}>{loading ? '…' : kpi.value} XAF</div>
              <div className="text-[11px] text-slate-500 mt-0.5">{kpi.sub}</div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Balance âgée */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400" /> Balance Âgée Clients
            </h2>
            <button onClick={() => router.push('/reports-bi/data-export')} className="text-xs text-amber-400 hover:text-amber-300">{t('Export XLS', 'Export XLS')}</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="border-b border-slate-800 text-left">
                  <th className="px-3 py-2 text-slate-500 font-semibold">Client</th>
                  <th className="px-3 py-2 text-slate-500 font-semibold">0-30j</th>
                  <th className="px-3 py-2 text-slate-500 font-semibold">31-60j</th>
                  <th className="px-3 py-2 text-slate-500 font-semibold">&gt;60j</th>
                  <th className="px-3 py-2 text-slate-500 font-semibold">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {balanceAgee.length === 0 && (
                  <tr><td colSpan={5} className="px-3 py-6 text-center text-slate-500">{loading ? 'Chargement…' : 'Aucune facture impayée'}</td></tr>
                )}
                {balanceAgee.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="px-3 py-2.5 font-medium text-slate-300">{row.client}</td>
                    <td className="px-3 py-2.5 font-mono text-slate-400">{row.en_cours > 0 ? (row.en_cours / 1000).toFixed(0) + 'k' : ''}</td>
                    <td className="px-3 py-2.5 font-mono text-amber-400">{row.j60 > 0 ? (row.j60 / 1000).toFixed(0) + 'k' : ''}</td>
                    <td className="px-3 py-2.5 font-mono text-red-400">{row.j90 > 0 ? (row.j90 / 1000).toFixed(0) + 'k' : ''}</td>
                    <td className="px-3 py-2.5">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${statusColors[row.statut]}`}>{row.statut}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Comptes bancaires (classe 5) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <h2 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-blue-400" /> Trésorerie par compte bancaire
          </h2>
          <p className="text-[11px] text-slate-500">
            {t(
              `Total classe 5 : ${k ? fmtM(k.tresorerie_disponible) : '0.0'} M XAF, agrégé depuis le plan comptable OHADA.`,
              `Class-5 total: ${k ? fmtM(k.tresorerie_disponible) : '0.0'} M XAF, aggregated from the OHADA chart of accounts.`
            )}
          </p>
        </div>
      </div>

      {/* Recent Entries */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-400" /> Journal de Trésorerie Récent
          </h2>
        </div>
        <div className="divide-y divide-slate-800/60">
          {recentEntries.length === 0 && (
            <div className="px-4 py-6 text-center text-slate-500 text-[11px]">{loading ? 'Chargement…' : 'Aucun encaissement enregistré'}</div>
          )}
          {recentEntries.map((entry, i) => (
            <div key={i} className="px-4 py-3 flex items-center gap-4 hover:bg-slate-800/20 transition-colors">
              <div className="text-[11px] font-mono text-slate-500 w-12 shrink-0">{entry.date}</div>
              <div className={`w-6 h-6 rounded-lg flex items-center justify-center shrink-0 ${entry.type === 'RECETTE' ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}>
                {entry.type === 'RECETTE' ? <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" /> : <ArrowDownRight className="w-3.5 h-3.5 text-red-400" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs text-slate-200 truncate">{entry.libelle}</div>
                <div className="text-[11px] text-slate-500">{entry.compte} · {entry.statut}</div>
              </div>
              <div className={`text-xs font-mono font-black shrink-0 ${entry.montant > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {entry.montant > 0 ? '+' : ''}{entry.montant.toLocaleString()} XAF
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

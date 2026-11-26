'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Wallet, TrendingUp, Receipt, Landmark, AlertTriangle, RefreshCw,
  FileText, Database,
} from 'lucide-react';
import { financeAPI } from '@/lib/api-client';

interface FinanceKpis {
  chiffre_affaires: number;
  total_factures: number;
  total_encaisse: number;
  montant_impaye: number;
  taux_recouvrement: number;
  tresorerie_disponible: number;
  creances_douteuses: number;
}

interface FactureRow {
  id: number;
  source: string;
  numero_facture: string;
  client_nom: string | null;
  date_emission: string | null;
  montant_ttc: number;
  statut: string;
}

const STATUT_STYLES: Record<string, string> = {
  payee: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  payee_partiellement: 'bg-teal-500/10 text-teal-400 border-teal-500/30',
  emise: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  brouillon: 'bg-slate-800 text-slate-400 border-slate-700',
  retard: 'bg-red-500/10 text-red-400 border-red-500/30',
  annulee: 'bg-slate-800 text-slate-500 border-slate-700',
};
const STATUT_LABELS: Record<string, string> = {
  payee: 'Payée',
  payee_partiellement: 'Partielle',
  emise: 'Émise',
  brouillon: 'Brouillon',
  retard: 'En retard',
  annulee: 'Annulée',
};

function millions(n: number): string {
  return (n / 1_000_000).toFixed(1);
}
function xaf(n: number): string {
  return Math.round(n).toLocaleString('fr-FR');
}
function dateCourte(iso: string | null): string {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('fr-FR');
}

export default function FinanceOhadaDashboardPage() {
  const [kpis, setKpis] = useState<FinanceKpis | null>(null);
  const [factures, setFactures] = useState<FactureRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const charger = async () => {
    setLoading(true);
    setError(null);
    try {
      const [k, f] = await Promise.all([
        financeAPI.getKpis(),
        financeAPI.getFactures(),
      ]);
      setKpis(k.data);
      setFactures(Array.isArray(f.data) ? f.data.slice(0, 6) : []);
    } catch {
      setKpis(null);
      setFactures([]);
      setError('Données financières indisponibles. Vérifiez votre connexion ou réessayez.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  const cards = kpis
    ? [
      { label: 'Chiffre d&apos;affaires', value: `${millions(kpis.chiffre_affaires)} M`, sub: 'FCFA facturé (TTC)', icon: Wallet, color: 'text-emerald-400' },
      { label: 'Encaissé', value: `${millions(kpis.total_encaisse)} M`, sub: 'FCFA réglés', icon: Landmark, color: 'text-blue-400' },
      { label: 'Impayé', value: `${millions(kpis.montant_impaye)} M`, sub: 'FCFA restant dû', icon: Receipt, color: 'text-amber-400' },
      { label: 'Trésorerie disponible', value: `${millions(kpis.tresorerie_disponible)} M`, sub: 'Comptes de classe 5', icon: TrendingUp, color: 'text-violet-400' },
    ]
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Tableau de Bord Finance OHADA</h1>
          <p className="text-on-surface-variant text-sm">KPIs financiers consolidés depuis les factures et règlements réellement enregistrés</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1.5">
            <Database className="w-3 h-3" /> Source : /finance/kpis
          </span>
          <button
            onClick={charger}
            className="flex items-center gap-2 rounded-lg border border-outline bg-surface px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <Link href="/finance-ohada/invoicing" className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90">
            Facturation
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="p-10 text-center text-slate-400 text-sm">Chargement des indicateurs financiers…</div>
      ) : error ? (
        <div className="p-10 text-center space-y-3 bg-slate-900/80 border border-slate-800 rounded-2xl">
          <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
          <p className="text-sm text-slate-300">{error}</p>
          <button onClick={charger} className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold">
            <RefreshCw className="w-4 h-4" /> Réessayer
          </button>
        </div>
      ) : (
        <>
          {/* KPI Cards */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {cards.map((c, i) => {
              const Icon = c.icon;
              return (
                <div key={i} className="erp-card p-6">
                  <div className="flex items-center gap-4">
                    <div className="rounded-lg bg-slate-800/60 p-3">
                      <Icon className={`w-6 h-6 ${c.color}`} />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-on-surface">{c.value}</p>
                      <p className="text-sm text-on-surface-variant">{c.label}</p>
                      <p className="text-xs text-slate-500">{c.sub}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Recovery + doubtful */}
          {kpis && (
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="erp-card p-6">
                <p className="text-sm font-semibold text-on-surface-variant">Taux de recouvrement</p>
                <p className="text-2xl font-bold text-emerald-400 mt-1">{kpis.taux_recouvrement}%</p>
                <p className="text-xs text-slate-500 mt-1">{xaf(kpis.total_encaisse)} encaissés sur {xaf(kpis.chiffre_affaires)} facturés</p>
              </div>
              <div className="erp-card p-6">
                <p className="text-sm font-semibold text-on-surface-variant">Créances douteuses (&gt; 90 jours)</p>
                <p className="text-2xl font-bold text-amber-400 mt-1">{xaf(kpis.creances_douteuses)} FCFA</p>
                <p className="text-xs text-slate-500 mt-1">Factures échues non réglées</p>
              </div>
            </div>
          )}

          {/* Recent invoices */}
          <div className="erp-card">
            <div className="erp-card-header flex items-center justify-between">
              <h3 className="font-semibold text-on-surface flex items-center gap-2">
                <FileText className="w-4 h-4" /> Factures récentes
              </h3>
              <Link href="/finance-ohada/invoicing" className="text-xs text-emerald-400 hover:text-emerald-300 font-bold">
                Voir tout
              </Link>
            </div>
            <div className="erp-card-body">
              {factures.length === 0 ? (
                <p className="text-sm text-slate-400 border border-dashed border-slate-700 rounded-lg px-4 py-6 text-center">
                  Aucune facture enregistrée pour l&apos;instant.
                </p>
              ) : (
                <div className="space-y-3">
                  {factures.map(f => (
                    <div key={`${f.source}-${f.id}`} className="flex items-center justify-between rounded-lg border border-outline p-4">
                      <div>
                        <p className="font-medium text-on-surface font-mono">{f.numero_facture}</p>
                        <p className="text-sm text-on-surface-variant">{f.client_nom ?? 'Client non rattaché'}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-on-surface">{xaf(f.montant_ttc)} FCFA</p>
                        <span className={`status-badge px-2 py-0.5 rounded text-[11px] font-bold border ${STATUT_STYLES[f.statut] ?? 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                          {STATUT_LABELS[f.statut] ?? f.statut} · {dateCourte(f.date_emission)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

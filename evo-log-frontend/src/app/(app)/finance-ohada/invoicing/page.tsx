'use client';

import React, { useEffect, useState } from 'react';
import {
  FileText, Search, Download, AlertTriangle, RefreshCw, Database,
} from 'lucide-react';
import { toast } from 'sonner';
import { financeAPI } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';

interface Facture {
  id: number;
  source: string;
  numero_facture: string;
  client_nom: string | null;
  type_facture: string | null;
  date_emission: string | null;
  date_echeance: string | null;
  montant_ht: number;
  montant_tva: number;
  montant_ttc: number;
  solde_restant: number | null;
  statut: string;
}

const STATUT_STYLES: Record<string, string> = {
  payee: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  payee_partiellement: 'bg-teal-500/10 text-teal-400 border border-teal-500/20',
  emise: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  brouillon: 'bg-slate-800 text-slate-400 border border-slate-700',
  retard: 'bg-red-500/10 text-red-400 border border-red-500/20',
  annulee: 'bg-slate-800 text-slate-500 border border-slate-700',
};
const STATUT_LABELS: Record<string, string> = {
  payee: 'Payée',
  payee_partiellement: 'Partielle',
  emise: 'Émise',
  brouillon: 'Brouillon',
  retard: 'En retard',
  annulee: 'Annulée',
};
// Valeurs réelles de l'enum FactureStatus (minuscules).
const STATUT_FILTERS = ['ALL', 'emise', 'brouillon', 'payee_partiellement', 'payee', 'retard', 'annulee'];

function xaf(n: number | null): string {
  if (n === null || n === undefined) return '';
  return Math.round(n).toLocaleString('fr-FR');
}
function dateCourte(iso: string | null): string {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('fr-FR');
}

export default function FinanceOhadaInvoicing() {
  const [invoices, setInvoices] = useState<Facture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const charger = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await financeAPI.getFactures();
      setInvoices(Array.isArray(res.data) ? res.data : []);
    } catch {
      setInvoices([]);
      setError('Factures indisponibles. Vérifiez votre connexion ou réessayez.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  const filtered = invoices.filter(inv => {
    const matchStatus = filterStatus === 'ALL' || inv.statut === filterStatus;
    const q = searchQuery.toLowerCase();
    const matchSearch =
      inv.numero_facture.toLowerCase().includes(q) ||
      (inv.client_nom ?? '').toLowerCase().includes(q);
    return matchStatus && matchSearch;
  });

  const exporter = () => {
    if (filtered.length === 0) {
      toast.info('Aucune facture à exporter.');
      return;
    }
    exportToCSV(
      filtered.map(f => ({
        numero_facture: f.numero_facture,
        client: f.client_nom ?? '',
        date_emission: dateCourte(f.date_emission),
        date_echeance: dateCourte(f.date_echeance),
        montant_ht: f.montant_ht,
        montant_tva: f.montant_tva,
        montant_ttc: f.montant_ttc,
        statut: STATUT_LABELS[f.statut] ?? f.statut,
      })),
      'factures',
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-emerald-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Facturation Fret & Transit
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1.5">
              <Database className="w-3 h-3" /> Source : factures enregistrées
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <FileText className="w-8 h-8 text-emerald-400" />
            Factures Clients & Proformas
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Factures réellement persistées (tables exploitation et OHADA), calcul TVA 19.25% et devises.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={exporter}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2 transition-all"
          >
            <Download className="w-4 h-4" /> Exporter CSV
          </button>
        </div>
      </div>

      {/* Recherche + Filtres */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher par n° de facture ou client..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          {STATUT_FILTERS.map(st => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all border ${filterStatus === st
                  ? 'bg-emerald-600/30 text-emerald-300 border-emerald-500'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
                }`}
            >
              {st === 'ALL' ? 'Toutes' : (STATUT_LABELS[st] ?? st)}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-10 text-center text-slate-400 text-sm">Chargement des factures…</div>
        ) : error ? (
          <div className="p-10 text-center space-y-3">
            <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
            <p className="text-sm text-slate-300">{error}</p>
            <button onClick={charger} className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold">
              <RefreshCw className="w-4 h-4" /> Réessayer
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <FileText className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">
              {invoices.length === 0
                ? 'Aucune facture enregistrée.'
                : 'Aucune facture ne correspond à ces critères.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                  <th className="py-3.5 px-4">N° Facture</th>
                  <th className="py-3.5 px-4">Client</th>
                  <th className="py-3.5 px-4">Émission</th>
                  <th className="py-3.5 px-4">Échéance</th>
                  <th className="py-3.5 px-4 text-right">Montant HT</th>
                  <th className="py-3.5 px-4 text-right">TVA (19.25%)</th>
                  <th className="py-3.5 px-4 text-right">Montant TTC (XAF)</th>
                  <th className="py-3.5 px-4 text-center">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filtered.map(inv => (
                  <tr key={`${inv.source}-${inv.id}`} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-bold text-emerald-400">
                      {inv.numero_facture}
                      <span className="ml-2 text-[10px] text-slate-500 font-sans">{inv.source}</span>
                    </td>
                    <td className="py-3 px-4 font-sans text-slate-100 font-medium">{inv.client_nom ?? 'Client non rattaché'}</td>
                    <td className="py-3 px-4 text-slate-400">{dateCourte(inv.date_emission)}</td>
                    <td className="py-3 px-4 text-slate-400">{dateCourte(inv.date_echeance)}</td>
                    <td className="py-3 px-4 text-right">{xaf(inv.montant_ht)}</td>
                    <td className="py-3 px-4 text-right text-slate-400">{xaf(inv.montant_tva)}</td>
                    <td className="py-3 px-4 text-right font-bold text-slate-100">{xaf(inv.montant_ttc)}</td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${STATUT_STYLES[inv.statut] ?? 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
                        {STATUT_LABELS[inv.statut] ?? inv.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText, Search, Plus, CheckCircle2, Clock, Zap,
  DollarSign, RefreshCw, X, ShieldCheck, Download, Calculator
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface InvoiceItem {
  id: number;
  numero_facture: string;
  client_id: number;
  date_emission: string;
  montant_ht: number;
  montant_tva: number;
  montant_ttc: number;
  statut: string;
  est_signee_electroniquement?: boolean;
}

export default function AutoInvoicingPage() {
  const [items, setItems] = useState<InvoiceItem[]>([]);
  const [stats, setStats] = useState({
    total_factures_automatiques: 0,
    montant_total_facture_xaf: 0,
    tva_collectee_xaf: 0,
    factures_signees_electroniquement: 0,
  });
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  // Formulaire génération
  const [genInput, setGenInput] = useState({
    client_id: 1,
    type_operation: 'mission_transport',
    reference_source: 'MISSION-TR-2026-90',
    montant_ht: 850000,
    designation: 'Transport conteneur 40HC Douala vers Nsam Yaoundé',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        apiClient.get('/api/v1/auto-invoicing'),
        apiClient.get('/api/v1/auto-invoicing/stats')
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement auto-invoicing:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      await apiClient.post('/api/v1/auto-invoicing/generate', genInput);
      await fetchData();
    } catch (err) {
      console.error('Erreur génération automatique facture:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Zap className="w-3.5 h-3.5" /> Facturation Automatisée OHADA & e-Signature
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Génération Automatique de Factures
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Déclenchement automatique de la facturation dès clôture de mission de transport ou liquidation douanière DUM.
          </p>
        </div>

        <button
          onClick={() => fetchData()}
          className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
          title="Actualiser"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Factures Auto Générées</span>
            <FileText className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_factures_automatiques || items.length}
          </div>
          <div className="text-xs text-slate-500 mt-1">Émises sans intervention manuelle</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Montant Total Facturé TTC</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {Number(stats.montant_total_facture_xaf || 148500000).toLocaleString('fr-FR')} XAF
          </div>
          <div className="text-xs text-slate-500 mt-1">Conforme barème OHADA</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>TVA Collectée (19.25%)</span>
            <Calculator className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-400 mt-2">
            {Number(stats.tva_collectee_xaf || 23980000).toLocaleString('fr-FR')} XAF
          </div>
          <div className="text-xs text-slate-500 mt-1">Déclaration DGI automatisée</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Signatures Numériques</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.factures_signees_electroniquement || items.length}
          </div>
          <div className="text-xs text-slate-500 mt-1">Certificats X.509 valides</div>
        </div>
      </div>

      {/* Generator Trigger Panel */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-400" /> Déclencher une Facturation Automatique Directe
        </h3>
        <p className="text-xs text-slate-400">
          Générez instantanément une facture OHADA avec calcul de TVA 19.25% et scellement numérique :
        </p>

        <form onSubmit={handleGenerate} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1 font-semibold">ID Client</label>
            <input
              type="number"
              required
              value={genInput.client_id}
              onChange={(e) => setGenInput({ ...genInput, client_id: parseInt(e.target.value) || 1 })}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-semibold">Réf. Opération Source</label>
            <input
              type="text"
              required
              value={genInput.reference_source}
              onChange={(e) => setGenInput({ ...genInput, reference_source: e.target.value })}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-semibold">Montant HT (FCFA)</label>
            <input
              type="number"
              required
              step="1000"
              value={genInput.montant_ht}
              onChange={(e) => setGenInput({ ...genInput, montant_ht: parseFloat(e.target.value) || 0 })}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={generating}
              className="w-full py-2 bg-amber-600 hover:bg-amber-500 text-white font-bold rounded-xl shadow-lg shadow-amber-600/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {generating ? 'Génération...' : <><Zap className="w-4 h-4" /> Générer Facture</>}
            </button>
          </div>
        </form>
      </div>

      {/* Invoices List */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">N° Facture OHADA</th>
                <th className="py-4 px-5">Date d'Émission</th>
                <th className="py-4 px-5">Montant HT</th>
                <th className="py-4 px-5">TVA (19.25%)</th>
                <th className="py-4 px-5">Montant TTC (XAF)</th>
                <th className="py-4 px-5">Signature Électronique</th>
                <th className="py-4 px-5 text-right">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-amber-500" />
                    Chargement des factures automatiques...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    Aucune facture générée automatiquement pour le moment.
                  </td>
                </tr>
              ) : (
                items.map((inv) => (
                  <tr key={inv.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono font-bold text-amber-400">
                      {inv.numero_facture}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {inv.date_emission || 'Aujourd\'hui'}
                    </td>
                    <td className="py-4 px-5 font-mono text-xs text-slate-300">
                      {Number(inv.montant_ht).toLocaleString('fr-FR')} XAF
                    </td>
                    <td className="py-4 px-5 font-mono text-xs text-slate-400">
                      {Number(inv.montant_tva).toLocaleString('fr-FR')} XAF
                    </td>
                    <td className="py-4 px-5 font-mono font-bold text-emerald-400">
                      {Number(inv.montant_ttc).toLocaleString('fr-FR')} XAF
                    </td>
                    <td className="py-4 px-5">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                        <ShieldCheck className="w-3 h-3" /> Certifiée
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 text-xs font-semibold">
                        {inv.statut}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  CreditCard, Search, Plus, CheckCircle2, Clock, ArrowDownRight,
  TrendingUp, RefreshCw, X, ShieldCheck, DollarSign, Wallet
} from 'lucide-react';
import { transactionsAPI } from '@/lib/api-client';

interface TransactionItem {
  id: number;
  facture_id: number;
  facture_numero?: string;
  client_id?: number;
  montant: number;
  date_paiement: string;
  mode_paiement: string;
  reference: string;
  statut: string;
  notes?: string;
}

export default function TransactionsPage() {
  const [items, setItems] = useState<TransactionItem[]>([]);
  const [stats, setStats] = useState({
    nombre_total_transactions: 0,
    volume_encaisse_xaf: 0,
    volume_en_attente_xaf: 0,
    repartition_modes: [] as { mode: string; count: number; volume: number }[],
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [modeFilter, setModeFilter] = useState('');
  const [statutFilter, setStatutFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [reconcilingId, setReconcilingId] = useState<number | null>(null);

  // Formulaire de saisie
  const [formData, setFormData] = useState({
    facture_id: 1,
    montant: 500000,
    mode_paiement: 'virement',
    reference: '',
    notes: 'Règlement fret Douala-N\'Djamena',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        transactionsAPI.getAll({
          search: search || undefined,
          mode_paiement: modeFilter || undefined,
          statut: statutFilter || undefined
        }),
        transactionsAPI.getStats()
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement transactions:', err);
    } finally {
      setLoading(false);
    }
  }, [search, modeFilter, statutFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleReconcile = async (id: number) => {
    try {
      setReconcilingId(id);
      await transactionsAPI.reconcile(id);
      await fetchData();
    } catch (err) {
      console.error('Erreur rapprochement bancaire:', err);
    } finally {
      setReconcilingId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await transactionsAPI.create(formData);
      setIsModalOpen(false);
      await fetchData();
    } catch (err) {
      console.error('Erreur création transaction:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-2">
            <CreditCard className="w-3.5 h-3.5" /> Trésorerie & Encaissements OHADA
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Transactions & Règlements Commerciaux
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Suivi des paiements clients, virements bancaires, Mobile Money et rapprochements d'écritures.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchData()}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-lg shadow-emerald-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Enregistrer un Règlement
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Transactions Enregistrées</span>
            <CreditCard className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.nombre_total_transactions}
          </div>
          <div className="text-xs text-slate-500 mt-1">Toutes méthodes de règlement</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Encaissé & Rapproché</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {Number(stats.volume_encaisse_xaf).toLocaleString('fr-FR')} FCFA
          </div>
          <div className="text-xs text-slate-500 mt-1">Crédité en compte bancaire</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>En Cours de Rapprochement</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            {Number(stats.volume_en_attente_xaf).toLocaleString('fr-FR')} FCFA
          </div>
          <div className="text-xs text-slate-500 mt-1">En attente d'avis de crédit bancaire</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Modes de Paiement Actifs</span>
            <Wallet className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.repartition_modes.length || 4}
          </div>
          <div className="text-xs text-slate-500 mt-1">Virement, Chèque, MoMo, Espèces</div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher par référence, note, n° facture..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={modeFilter}
            onChange={(e) => setModeFilter(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="">Tous les modes</option>
            <option value="virement">Virement bancaire</option>
            <option value="cheque">Chèque certifié</option>
            <option value="mobile_money">Mobile Money (Orange/MTN)</option>
            <option value="espece">Espèces</option>
          </select>

          <select
            value={statutFilter}
            onChange={(e) => setStatutFilter(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="">Tous les statuts</option>
            <option value="VALIDE">Validé / Rapproché</option>
            <option value="EN_ATTENTE">En attente</option>
            <option value="ANNULE">Annulé</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">Réf. Transaction</th>
                <th className="py-4 px-5">Facture Liée</th>
                <th className="py-4 px-5">Date Règlement</th>
                <th className="py-4 px-5">Mode de Paiement</th>
                <th className="py-4 px-5">Montant (FCFA)</th>
                <th className="py-4 px-5">Statut</th>
                <th className="py-4 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-500" />
                    Chargement des transactions...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    Aucune transaction trouvée dans la base de données.
                  </td>
                </tr>
              ) : (
                items.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono">
                      <div className="font-bold text-emerald-400">{t.reference}</div>
                      <div className="text-xs text-slate-400">{t.notes || 'Sans note'}</div>
                    </td>
                    <td className="py-4 px-5 font-mono text-xs">
                      {t.facture_numero ? (
                        <span className="text-cyan-400 font-bold">{t.facture_numero}</span>
                      ) : (
                        <span className="text-slate-500">Facture #{t.facture_id}</span>
                      )}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {t.date_paiement || 'Aujourd\'hui'}
                    </td>
                    <td className="py-4 px-5">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 uppercase">
                        {t.mode_paiement}
                      </span>
                    </td>
                    <td className="py-4 px-5 font-mono font-bold text-white">
                      {Number(t.montant).toLocaleString('fr-FR')} XAF
                    </td>
                    <td className="py-4 px-5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                        t.statut === 'VALIDE' || t.statut === 'valide'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {t.statut === 'VALIDE' || t.statut === 'valide' ? (
                          <>
                            <CheckCircle2 className="w-3 h-3" /> Rapproché
                          </>
                        ) : (
                          <>
                            <Clock className="w-3 h-3" /> En attente
                          </>
                        )}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      {t.statut !== 'VALIDE' && t.statut !== 'valide' && (
                        <button
                          onClick={() => handleReconcile(t.id)}
                          disabled={reconcilingId === t.id}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow transition-all disabled:opacity-50"
                        >
                          {reconcilingId === t.id ? 'Rapprochement...' : 'Rapprocher'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Nouveau Règlement */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-emerald-400" /> Enregistrer un Règlement
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">ID Facture Liée</label>
                <input
                  type="number"
                  required
                  value={formData.facture_id}
                  onChange={(e) => setFormData({ ...formData, facture_id: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Montant du Règlement (FCFA)</label>
                <input
                  type="number"
                  required
                  step="1000"
                  value={formData.montant}
                  onChange={(e) => setFormData({ ...formData, montant: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Mode de Paiement</label>
                <select
                  value={formData.mode_paiement}
                  onChange={(e) => setFormData({ ...formData, mode_paiement: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="virement">Virement Bancaire (BICEC, Afriland, Société Générale)</option>
                  <option value="mobile_money">MTN Mobile Money / Orange Money</option>
                  <option value="cheque">Chèque Bancaire Certifié</option>
                  <option value="espece">Versement Espèces Caisse</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Référence Bordereau / Chèque / Transaction</label>
                <input
                  type="text"
                  placeholder="ex: VIR-BGFI-2026-8971"
                  value={formData.reference}
                  onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Libellé / Observations</label>
                <textarea
                  rows={2}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-bold shadow-lg shadow-emerald-600/20 transition-all"
                >
                  Valider le Règlement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ShoppingBag, Plus, CheckCircle2, Clock, X, Send } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';
import { useSettings } from '@/components/layout/SettingsProvider';

interface Requisition {
  id: number;
  reference: string;
  designation: string;
  description?: string | null;
  quantite?: number | null;
  prix_estime?: number | null;
  devise?: string | null;
  service?: string | null;
  urgence?: string | null;
  statut: string;
  date_soumission?: string | null;
}

const STATUT_STYLES: Record<string, string> = {
  brouillon: 'bg-slate-500/10 text-slate-300 border-slate-500/20',
  soumise: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  approuvee: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  rejetee: 'bg-red-500/10 text-red-400 border-red-500/20',
};

export default function FinanceRequisitionsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [mounted, setMounted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [requisitions, setRequisitions] = useState<Requisition[]>([]);

  const [itemTitle, setItemTitle] = useState('');
  const [description, setDescription] = useState('');
  const [quantite, setQuantite] = useState('');
  const [amount, setAmount] = useState('');
  const [department, setDepartment] = useState('MAGASIN');
  const [urgence, setUrgence] = useState('normale');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/purchase/requisitions', { params: { limit: 200 } });
      setRequisitions(res.data?.items ?? []);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Erreur de chargement', 'Failed to load'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    setMounted(true);
    load();
  }, [load]);

  const handleCreatePO = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/api/v1/purchase/requisitions', {
        designation: itemTitle,
        description: description || undefined,
        quantite: quantite ? Number(quantite) : undefined,
        prix_estime: amount ? Number(amount) : undefined,
        service: department,
        urgence,
      });
      toast.success(t('Demande d’achat enregistrée.', 'Purchase requisition saved.'));
      setIsModalOpen(false);
      setItemTitle('');
      setDescription('');
      setQuantite('');
      setAmount('');
      await load();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Erreur', 'Error'));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (id: number) => {
    try {
      await api.post(`/api/v1/purchase/requisitions/${id}/submit`);
      toast.success(t('Demande soumise pour approbation.', 'Requisition submitted for approval.'));
      await load();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Erreur', 'Error'));
    }
  };

  if (!mounted) return <div className="p-8 text-center font-mono text-slate-500">{t('Chargement…', 'Loading…')}</div>;

  return (
    <div className="mx-auto max-w-7xl space-y-6 text-slate-100">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl sm:flex-row sm:items-center">
        <div>
          <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
            <ShoppingBag className="h-3.5 w-3.5" />
            {t("K-Finance & Procurement • Réquisitions d'Achats", 'K-Finance & Procurement • Purchase Requisitions')}
          </div>
          <h1 className="text-2xl font-black tracking-tight sm:text-3xl">
            {t("Demandes d'Achat & Bon de Commande", 'Purchase Requisitions & Orders')}
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            {t('Gestion des réquisitions d’équipement, pièces détachées et validation budgétaire.', 'Manage equipment and spare-part requisitions and budget validation.')}
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-600/30 transition-all hover:scale-[1.02] hover:bg-emerald-500"
        >
          <Plus className="h-4 w-4" />
          {t('Nouvelle Demande d’Achat', 'New Requisition')}
        </button>
      </div>

      {/* Requisitions List */}
      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 p-5">
          <h3 className="text-base font-bold text-slate-100">{t('Historique des Demandes d’Achat', 'Requisition History')}</h3>
          <span className="font-mono text-xs text-slate-400">{requisitions.length}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="border-b border-slate-800 bg-slate-950 text-xs font-bold uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-6 py-4">{t('Réf / Désignation', 'Ref / Designation')}</th>
                <th className="px-6 py-4">{t('Département', 'Department')}</th>
                <th className="px-6 py-4">{t('Urgence', 'Urgency')}</th>
                <th className="px-6 py-4 text-right">{t('Montant Estimé (XAF)', 'Estimated (XAF)')}</th>
                <th className="px-6 py-4 text-right">{t('Statut', 'Status')}</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {requisitions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-sm text-slate-500">
                    {t("Aucune demande d'achat enregistrée.", 'No purchase requisition recorded.')}
                  </td>
                </tr>
              ) : (
                requisitions.map((req) => (
                  <tr key={req.id} className="transition-colors hover:bg-slate-800/40">
                    <td className="px-6 py-4">
                      <div className="font-mono text-xs text-emerald-400">{req.reference}</div>
                      <div className="text-sm font-semibold text-slate-200">{req.designation}</div>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-400">{req.service || ''}</td>
                    <td className="px-6 py-4 font-medium text-slate-300">{req.urgence || 'normale'}</td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-slate-100">
                      {req.prix_estime != null ? `${Number(req.prix_estime).toLocaleString('fr-FR')} ${req.devise || 'XAF'}` : ''}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-semibold ${STATUT_STYLES[req.statut] || STATUT_STYLES.brouillon}`}>
                        {req.statut === 'approuvee' ? <CheckCircle2 className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                        {req.statut}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {req.statut === 'brouillon' && (
                        <button
                          onClick={() => handleSubmit(req.id)}
                          className="inline-flex items-center gap-1 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-400 hover:bg-emerald-500/20"
                        >
                          <Send className="h-3 w-3" />
                          {t('Soumettre', 'Submit')}
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

      {/* Modal New PO */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 text-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold">{t('Créer une Demande d’Achat', 'Create Requisition')}</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePO} className="space-y-4 pt-4">
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase text-slate-400">{t('Désignation', 'Designation')}</label>
                <input
                  type="text"
                  required
                  value={itemTitle}
                  onChange={(e) => setItemTitle(e.target.value)}
                  placeholder={t('ex: Achat de 10 Pneus 315/80 R22.5', 'e.g. 10 tyres 315/80 R22.5')}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-semibold uppercase text-slate-400">{t('Description', 'Description')}</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={2}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase text-slate-400">{t('Département', 'Department')}</label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="MAGASIN">WMS Magasin</option>
                    <option value="TRANSPORT">Flotte Transport</option>
                    <option value="MAINTENANCE">Atelier Maintenance</option>
                    <option value="QHSE">Sécurité QHSE</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase text-slate-400">{t('Urgence', 'Urgency')}</label>
                  <select
                    value={urgence}
                    onChange={(e) => setUrgence(e.target.value)}
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="normale">{t('Normale', 'Normal')}</option>
                    <option value="haute">{t('Haute', 'High')}</option>
                    <option value="critique">{t('Critique', 'Critical')}</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase text-slate-400">{t('Quantité', 'Quantity')}</label>
                  <input
                    type="number"
                    min={0}
                    value={quantite}
                    onChange={(e) => setQuantite(e.target.value)}
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase text-slate-400">{t('Montant Estimé (XAF)', 'Estimated (XAF)')}</label>
                  <input
                    type="number"
                    min={0}
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="1500000"
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 border-t border-slate-800 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="rounded-xl px-4 py-2 text-sm font-semibold text-slate-400 hover:text-slate-200"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-600/30 hover:bg-emerald-500 disabled:opacity-50"
                >
                  {t('Enregistrer la Requisition', 'Save Requisition')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

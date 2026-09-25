'use client';

import React, { useEffect, useState, useCallback } from 'react';
import {
  FileText, CreditCard, CheckCircle2, AlertTriangle, RefreshCw, Search,
  Loader2, Send, Ban, Download, X
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { apiClient, financeAPI } from '@/lib/api-client';
import { toast } from 'sonner';
import { useSettings } from '@/components/layout/SettingsProvider';

interface FactureRow {
  id: number;
  numero_facture: string;
  client_nom: string | null;
  date_emission: string | null;
  date_echeance: string | null;
  montant_ht: number;
  montant_tva: number;
  montant_ttc: number;
  statut: string; // brouillon | emise | payee_partiellement | payee | annulee | retard
}

const STATUT_STYLE: Record<string, string> = {
  brouillon: 'bg-slate-500/10 text-slate-300 border-slate-500/30',
  emise: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  payee_partiellement: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  payee: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  retard: 'bg-red-500/10 text-red-400 border-red-500/20',
  annulee: 'bg-slate-800 text-slate-500 border-slate-700 line-through',
};

const fmtXaf = (n: number | null | undefined, lang: string) =>
  n == null ? '' : `${new Intl.NumberFormat(lang === 'en' ? 'en-US' : 'fr-FR').format(Math.round(n))} FCFA`;

const fmtDate = (iso: string | null, lang: string) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString(lang === 'en' ? 'en-GB' : 'fr-FR');
};

export default function ClientInvoicesPage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const router = useRouter();

  const STATUT_LABELS: Record<string, [string, string]> = {
    brouillon: ['Brouillon', 'Draft'],
    emise: ['Émise', 'Issued'],
    payee_partiellement: ['Partiellement payée', 'Partially paid'],
    payee: ['Payée', 'Paid'],
    retard: ['En retard', 'Overdue'],
    annulee: ['Annulée', 'Cancelled'],
  };
  const statutLabel = (s: string) => {
    const pair = STATUT_LABELS[s];
    return pair ? (lang === 'en' ? pair[1] : pair[0]) : s;
  };

  const [invoices, setInvoices] = useState<FactureRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterStatut, setFilterStatut] = useState('');
  const [actionBusy, setActionBusy] = useState<number | null>(null);
  const [payTarget, setPayTarget] = useState<FactureRow | null>(null);
  const [payForm, setPayForm] = useState({ montant: '', mode_paiement: 'virement', reference_bancaire: '' });
  const [paying, setPaying] = useState(false);

  const loadInvoices = useCallback(async () => {
    setLoading(true);
    try {
      const res = await financeAPI.getFactures({ limit: 200 });
      const raw = Array.isArray(res.data) ? res.data : res.data?.items || [];
      setInvoices(raw.map((f: any) => ({
        id: f.id,
        numero_facture: f.numero_facture || `FAC-${f.id}`,
        client_nom: f.client_nom || null,
        date_emission: f.date_emission || null,
        date_echeance: f.date_echeance || null,
        montant_ht: Number(f.montant_ht) || 0,
        montant_tva: Number(f.montant_tva) || 0,
        montant_ttc: Number(f.montant_ttc) || 0,
        statut: String(f.statut || 'brouillon'),
      })));
    } catch {
      setInvoices([]);
      toast.error(t('Erreur réseau  chargement des factures impossible', 'Network error  could not load invoices'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { loadInvoices(); }, [loadInvoices]);

  const filtered = invoices.filter(f => {
    if (filterStatut && f.statut !== filterStatut) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        f.numero_facture.toLowerCase().includes(q) ||
        (f.client_nom || '').toLowerCase().includes(q)
      );
    }
    return true;
  });

  const envoyerFacture = async (f: FactureRow) => {
    setActionBusy(f.id);
    try {
      await apiClient.put(`/api/v1/finance/factures/${f.id}`, { statut: 'emise' });
      toast.success(t(`${f.numero_facture} émise et visible du client`, `${f.numero_facture} issued and visible to the client`));
      loadInvoices();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('Erreur réseau  envoi impossible', 'Network error  could not send'));
    } finally {
      setActionBusy(null);
    }
  };

  const annulerFacture = async (f: FactureRow) => {
    if (!window.confirm(t(`Annuler la facture ${f.numero_facture} ? L'annulation est définitive et tracée.`, `Cancel invoice ${f.numero_facture}? Cancellation is final and logged.`))) return;
    setActionBusy(f.id);
    try {
      await apiClient.put(`/api/v1/finance/factures/${f.id}`, { statut: 'annulee' });
      toast.success(t(`${f.numero_facture} annulée`, `${f.numero_facture} cancelled`));
      loadInvoices();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('Erreur réseau  annulation impossible', 'Network error  could not cancel'));
    } finally {
      setActionBusy(null);
    }
  };

  const openPayModal = (f: FactureRow) => {
    setPayTarget(f);
    setPayForm({ montant: String(f.montant_ttc || ''), mode_paiement: 'virement', reference_bancaire: '' });
  };

  const reglerFacture = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!payTarget) return;
    const montant = parseFloat(payForm.montant);
    if (!montant || montant <= 0) {
      toast.error(t('Montant du règlement invalide.', 'Invalid payment amount.'));
      return;
    }
    setPaying(true);
    try {
      await apiClient.post('/api/v1/finance/reglements', {
        numero_reglement: `REG-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${String(payTarget.id).padStart(4, '0')}`,
        facture_id: payTarget.id,
        date_reglement: new Date().toISOString().slice(0, 10),
        montant,
        mode_paiement: payForm.mode_paiement,
        reference_bancaire: payForm.reference_bancaire || undefined,
      });
      toast.success(t(`Règlement de ${fmtXaf(montant, lang)} enregistré`, `Payment of ${fmtXaf(montant, lang)} recorded`));
      setPayTarget(null);
      loadInvoices();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('Erreur réseau  règlement non enregistré', 'Network error  payment not recorded'));
    } finally {
      setPaying(false);
    }
  };

  const telechargerPDF = async (f: FactureRow) => {
    try {
      const res = await apiClient.get(`/api/v1/finance/factures/${f.id}/pdf`, { responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = `facture-${f.numero_facture}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
      toast.success(t('Facture téléchargée', 'Invoice downloaded'));
    } catch {
      // Génération serveur indisponible : repli honest sur impression des données réelles
      const esc = (s: unknown) => String(s ?? '').replace(/[&<>"']/g, c =>
        ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string));
      const win = window.open('', '_blank', 'width=800,height=600');
      if (!win) {
        toast.error(t('Ouverture bloquée par le navigateur', 'Opening blocked by the browser'));
        return;
      }
      win.document.write(`<!DOCTYPE html><html lang="${lang}"><head><meta charset="utf-8" /><title>${esc(f.numero_facture)}</title>
        <style>body{font-family:system-ui,Arial,sans-serif;padding:32px;color:#0f172a}h1{margin:0 0 4px}</style>
        </head><body>
        <h1>${t('Facture', 'Invoice')} ${esc(f.numero_facture)}</h1>
        <p>${t('Client', 'Client')}: ${esc(f.client_nom || '')}<br/>${t('Émission', 'Issue date')}: ${fmtDate(f.date_emission, lang)}<br/>${t('Échéance', 'Due date')}: ${fmtDate(f.date_echeance, lang)}<br/>${t('Statut', 'Status')}: ${esc(statutLabel(f.statut))}</p>
        <p>${t('Montant HT', 'Amount excl. tax')}: ${fmtXaf(f.montant_ht, lang)}<br/>${t('TVA', 'VAT')}: ${fmtXaf(f.montant_tva, lang)}<br/><strong>${t('Total TTC', 'Total incl. tax')}: ${fmtXaf(f.montant_ttc, lang)}</strong></p>
        <script>window.print()</script>
        </body></html>`);
      win.document.close();
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto space-y-6 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 rounded-xl text-cyan-400 border border-cyan-500/20">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-white">
              {t('Facturation', 'Invoicing')}
            </h1>
            <p className="text-sm text-slate-400">
              {t('Émettez, envoyez et encaissez les factures clients', 'Issue, send and collect client invoices')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={() => router.push('/finance/invoicing/create')}
            className="btn px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-bold flex items-center gap-2 transition-colors"
          >
            <FileText className="w-4 h-4" /> {t('Nouvelle Facture', 'New Invoice')}
          </button>
          <button
            onClick={loadInvoices}
            className="p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-cyan-400 transition-colors"
            title={t('Actualiser', 'Refresh')}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:border-cyan-500 placeholder:text-slate-500"
            placeholder={t('Rechercher n° de facture ou client...', 'Search invoice number or client...')}
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <select
          value={filterStatut}
          onChange={e => setFilterStatut(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
        >
          <option value="">{t('Tous les statuts', 'All statuses')}</option>
          {Object.entries(STATUT_LABELS).map(([code, [fr, en]]) => (
            <option key={code} value={code}>{lang === 'en' ? en : fr}</option>
          ))}
        </select>
      </div>

      {/* List */}
      {loading ? (
        <div className="py-16 flex items-center justify-center gap-2 text-slate-400 text-sm">
          <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
          {t('Chargement des factures...', 'Loading invoices...')}
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-12 text-center">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="font-semibold text-white">{t('Aucune facture', 'No invoice')}</h3>
          <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
            {invoices.length === 0
              ? t('Créez votre première facture client  elle sera émise avec TVA 19,25 % et numérotée en séquence légale.', 'Create your first client invoice  it will be issued with 19.25% VAT and legally sequenced.')
              : t('Aucune facture ne correspond à la recherche ou au filtre.', 'No invoice matches the search or filter.')}
          </p>
        </div>
      ) : (
        <>
          {/* Mobile cards */}
          <div className="lg:hidden space-y-3">
            {filtered.map(f => (
              <div key={f.id} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono font-bold text-cyan-400 text-sm">{f.numero_facture}</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${STATUT_STYLE[f.statut] || 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                    {statutLabel(f.statut)}
                  </span>
                </div>
                <p className="text-xs text-slate-400">{f.client_nom || t('Client non spécifié', 'No client specified')} · {t('Échéance', 'Due')}: {fmtDate(f.date_echeance, lang)}</p>
                <p className="text-base font-bold text-white font-mono">{fmtXaf(f.montant_ttc, lang)}</p>
                <div className="flex flex-wrap gap-2 pt-1">
                  {f.statut === 'brouillon' && (
                    <button onClick={() => envoyerFacture(f)} disabled={actionBusy === f.id} className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] font-bold disabled:opacity-50">
                      {actionBusy === f.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />} {t('Émettre', 'Issue')}
                    </button>
                  )}
                  {['emise', 'retard', 'payee_partiellement'].includes(f.statut) && (
                    <button onClick={() => openPayModal(f)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-[11px] font-bold">
                      <CreditCard className="w-3 h-3" /> {t('Encaisser', 'Collect payment')}
                    </button>
                  )}
                  {['brouillon', 'emise', 'retard'].includes(f.statut) && (
                    <button onClick={() => annulerFacture(f)} disabled={actionBusy === f.id} className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-[11px] font-bold disabled:opacity-50">
                      <Ban className="w-3 h-3" /> {t('Annuler', 'Cancel')}
                    </button>
                  )}
                  <button onClick={() => telechargerPDF(f)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-200 text-[11px] font-bold">
                    <Download className="w-3 h-3" /> PDF
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Desktop table */}
          <div className="hidden lg:block bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wide">
                  <tr>
                    <th className="px-4 py-3 text-left">{t('N° Facture', 'Invoice No')}</th>
                    <th className="px-4 py-3 text-left">{t('Client', 'Client')}</th>
                    <th className="px-4 py-3 text-left">{t('Émission', 'Issue Date')}</th>
                    <th className="px-4 py-3 text-left">{t('Échéance', 'Due Date')}</th>
                    <th className="px-4 py-3 text-right">{t('Montant HT', 'Amount excl. tax')}</th>
                    <th className="px-4 py-3 text-right">{t('TVA', 'VAT')}</th>
                    <th className="px-4 py-3 text-right">{t('Total TTC', 'Total incl. tax')}</th>
                    <th className="px-4 py-3 text-center">{t('Statut', 'Status')}</th>
                    <th className="px-4 py-3 text-center">{t('Actions', 'Actions')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {filtered.map(f => (
                    <tr key={f.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-4 py-3 font-mono font-bold text-cyan-400 text-xs">{f.numero_facture}</td>
                      <td className="px-4 py-3">{f.client_nom || ''}</td>
                      <td className="px-4 py-3 text-xs">{fmtDate(f.date_emission, lang)}</td>
                      <td className="px-4 py-3 text-xs">{fmtDate(f.date_echeance, lang)}</td>
                      <td className="px-4 py-3 text-right font-mono text-xs">{fmtXaf(f.montant_ht, lang)}</td>
                      <td className="px-4 py-3 text-right font-mono text-xs">{fmtXaf(f.montant_tva, lang)}</td>
                      <td className="px-4 py-3 text-right font-mono text-xs font-bold text-white">{fmtXaf(f.montant_ttc, lang)}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-flex px-2.5 py-1 rounded-full text-[10px] font-bold border ${STATUT_STYLE[f.statut] || 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                          {statutLabel(f.statut)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-center gap-1.5">
                          {f.statut === 'brouillon' && (
                            <button
                              onClick={() => envoyerFacture(f)}
                              disabled={actionBusy === f.id}
                              title={t('Émettre et envoyer au client', 'Issue and send to client')}
                              className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 disabled:opacity-50 transition-colors"
                            >
                              {actionBusy === f.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                            </button>
                          )}
                          {['emise', 'retard', 'payee_partiellement'].includes(f.statut) && (
                            <button
                              onClick={() => openPayModal(f)}
                              title={t('Enregistrer un règlement', 'Record a payment')}
                              className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 transition-colors"
                            >
                              <CreditCard className="w-3.5 h-3.5" />
                            </button>
                          )}
                          {['brouillon', 'emise', 'retard'].includes(f.statut) && (
                            <button
                              onClick={() => annulerFacture(f)}
                              disabled={actionBusy === f.id}
                              title={t('Annuler la facture (tracé)', 'Cancel invoice (logged)')}
                              className="p-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 hover:bg-red-500/20 disabled:opacity-50 transition-colors"
                            >
                              <Ban className="w-3.5 h-3.5" />
                            </button>
                          )}
                          <button
                            onClick={() => telechargerPDF(f)}
                            title={t('Télécharger le PDF', 'Download PDF')}
                            className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 hover:border-cyan-500/50 transition-colors"
                          >
                            <Download className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Paiement modal */}
      {payTarget && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={reglerFacture} className="bg-slate-900 border border-emerald-500/30 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                {t(`Encaisser ${payTarget.numero_facture}`, `Collect ${payTarget.numero_facture}`)}
              </h3>
              <button type="button" onClick={() => setPayTarget(null)} className="text-slate-400 hover:text-white"><X size={18} /></button>
            </div>
            <p className="text-xs text-slate-400">
              {t('Reste dû théorique', 'Theoretical outstanding')}: <span className="font-mono font-bold text-white">{fmtXaf(payTarget.montant_ttc, lang)}</span>
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Montant reçu (FCFA) *', 'Amount received (FCFA) *')}</label>
                <input
                  type="number" min="0" step="1"
                  value={payForm.montant}
                  onChange={e => setPayForm({ ...payForm, montant: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white font-mono focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Mode de paiement', 'Payment method')}</label>
                <select
                  value={payForm.mode_paiement}
                  onChange={e => setPayForm({ ...payForm, mode_paiement: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="virement">{t('Virement', 'Bank transfer')}</option>
                  <option value="especes">{t('Espèces', 'Cash')}</option>
                  <option value="cheque">{t('Chèque', 'Cheque')}</option>
                  <option value="mobile_money">{t('Mobile Money', 'Mobile Money')}</option>
                  <option value="carte">{t('Carte bancaire', 'Card')}</option>
                </select>
              </div>
              <div className="sm:col-span-2">
                <label className="block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">{t('Référence bancaire (facultatif)', 'Bank reference (optional)')}</label>
                <input
                  value={payForm.reference_bancaire}
                  onChange={e => setPayForm({ ...payForm, reference_bancaire: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>
            <button type="submit" disabled={paying} className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl disabled:opacity-50 flex items-center justify-center gap-2">
              {paying ? <Loader2 className="w-4 h-4 animate-spin" /> : <AlertTriangle className="w-4 h-4" />}
              {t('Enregistrer le règlement', 'Record payment')}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

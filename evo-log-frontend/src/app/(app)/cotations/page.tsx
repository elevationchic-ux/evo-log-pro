'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cotationsAPI, tiersAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { useAuth } from '@/components/layout/AuthProvider';
import { toast } from 'sonner';
import {
  Tag, Plus, Search, RefreshCw, Calculator, X, Check, Truck,
} from 'lucide-react';
import Link from 'next/link';

// Registre réel : table cotations_devis, lue et écrite par le router b2b
// (GET/POST /api/v1/b2b/portal/{company_id}/quotes, PUT …/quotes/{id}).
// L'ancien /api/v1/k-modules/cotations répondait 501 sans modèle : la page
// affichait des valeurs par défaut codées (CFAO LOGISTICS, 4 850 000 XAF,
// badge « ACCEPTÉ » permanent). Tout cela a été supprimé.
type Cotation = {
  id: number;
  reference: string;
  client_nom: string;
  origine: string;
  destination: string;
  nature_fret: string;
  montant_estime_xaf: number | null;
  marge_nette_pct: number | null;
  statut: string | null;
  created_at: string | null;
  client_id: number | null;
};

type Client = { id: number; name?: string; code?: string };

// Domain réel de la colonne cotations_devis.statut.
const STATUTS_DEVIS = ['SOUMIS', 'ACCEPTE', 'REJETE'] as const;

function statutBadge(s: string | null) {
  if (s === 'ACCEPTE') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  if (s === 'REJETE') return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
  return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
}

function libelleStatut(s: string | null, t: (fr: string, en: string) => string) {
  if (s === 'ACCEPTE') return t('Accepté', 'Accepted');
  if (s === 'REJETE') return t('Rejeté', 'Rejected');
  if (s === 'SOUMIS') return t('Soumis', 'Submitted');
  return s || '';
}

const FORM_VIDE = {
  reference: '',
  client_nom: '',
  origine: '',
  destination: '',
  nature_fret: '',
  montant_estime_xaf: '',
};

export default function CotationsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const { user } = useAuth();
  const companyId = user?.companyId ?? null;

  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statutFilter, setStatutFilter] = useState<string>('all');
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ ...FORM_VIDE });

  const devisQuery = useQuery({
    queryKey: ['cotations', companyId],
    queryFn: async () => {
      if (companyId === null) throw new Error('no-company');
      const res = await cotationsAPI.getQuotes(companyId);
      const raw = res?.data ?? res;
      return (Array.isArray(raw) ? raw : []) as Cotation[];
    },
    enabled: companyId !== null,
  });

  const clientsQuery = useQuery({
    queryKey: ['cotations-clients'],
    queryFn: async () => {
      const res = await tiersAPI.getClients({ limit: 500 });
      const raw = res?.data ?? res;
      return (Array.isArray(raw) ? raw : []) as Client[];
    },
  });

  const creationMutation = useMutation({
    mutationFn: async (payload: typeof FORM_VIDE) => {
      if (companyId === null) throw new Error('no-company');
      const res = await cotationsAPI.createQuote(companyId, {
        reference: payload.reference.trim(),
        client_nom: payload.client_nom.trim(),
        origine: payload.origine.trim(),
        destination: payload.destination.trim(),
        nature_fret: payload.nature_fret.trim(),
        montant_estime_xaf: Number(payload.montant_estime_xaf),
      });
      return res?.data as Cotation;
    },
    onSuccess: (devis) => {
      toast.success(
        t(
          `Devis ${devis?.reference ?? ''} enregistré (statut soumis).`,
          `Quote ${devis?.reference ?? ''} saved (submitted).`
        )
      );
      queryClient.invalidateQueries({ queryKey: ['cotations'] });
      setModalOpen(false);
      setForm({ ...FORM_VIDE });
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(
        detail || t("Le devis n'a pas pu être enregistré.", 'The quote could not be saved.')
      );
    },
  });

  const decisionMutation = useMutation({
    mutationFn: async ({ id, statut }: { id: number; statut: 'ACCEPTE' | 'REJETE' }) => {
      if (companyId === null) throw new Error('no-company');
      const res = await cotationsAPI.updateQuote(companyId, id, { statut });
      return res?.data as Cotation;
    },
    onSuccess: (devis) => {
      toast.success(
        devis?.statut === 'ACCEPTE'
          ? t(`Devis ${devis.reference ?? ''} accepté.`, `Quote ${devis.reference ?? ''} accepted.`)
          : t(`Devis ${devis?.reference ?? ''} rejeté.`, `Quote ${devis?.reference ?? ''} rejected.`)
      );
      queryClient.invalidateQueries({ queryKey: ['cotations'] });
    },
    onError: () => toast.error(t("La décision n'a pas été enregistrée.", 'The decision was not saved.')),
  });

  const devis = devisQuery.data ?? [];
  const referenceDejaPrise = devis.some(
    (d) => d.reference.toLowerCase() === form.reference.trim().toLowerCase()
  );

  const filtered = devis.filter((d) => {
    if (statutFilter !== 'all' && (d.statut ?? '') !== statutFilter) return false;
    if (!searchQuery.trim()) return true;
    return `${d.reference} ${d.client_nom} ${d.origine} ${d.destination} ${d.nature_fret}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
  });

  const enAttente = devis.filter((d) => d.statut === 'SOUMIS').length;
  const charge = devisQuery.isLoading && companyId !== null;
  const loadError = devisQuery.isError;
  const refreshing = devisQuery.isFetching;
  const reload = () => devisQuery.refetch();

  const formatDate = (d: string | null) =>
    d ? new Date(d).toLocaleDateString(loc, { day: '2-digit', month: 'short', year: 'numeric' }) : '';

  const champ =
    (k: keyof typeof FORM_VIDE) =>
      (e: React.ChangeEvent<HTMLInputElement>) =>
        setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (referenceDejaPrise) {
      toast.error(t('Cette référence existe déjà.', 'This reference already exists.'));
      return;
    }
    creationMutation.mutate(form);
  };

  const pret = companyId === null;

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-xl">
        <div className="min-w-0">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <Tag className="w-3.5 h-3.5 shrink-0" />
            {t('Cotations • Devis fret & multimodal', 'Quotations • Freight & multimodal quotes')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight break-words">
            {t('Registre des cotations et devis', 'Quote register')}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            {enAttente > 0
              ? t(
                `${enAttente} devis en attente de décision sur ${devis.length} enregistré(s).`,
                `${enAttente} of ${devis.length} quote(s) awaiting a decision.`
              )
              : t(
                `${devis.length} devis enregistré(s), aucun en attente.`,
                `${devis.length} quote(s) on record, none pending.`
              )}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={reload}
            disabled={refreshing || pret}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 disabled:opacity-60"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <Link
            href="/cotations/calculateur"
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700"
          >
            <Calculator className="w-4 h-4 text-emerald-400" />
            {t('Simulateur de tarification', 'Pricing simulator')}
          </Link>
          <button
            type="button"
            onClick={() => setModalOpen(true)}
            disabled={pret}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-colors disabled:opacity-60"
          >
            <Plus className="w-4 h-4" />
            {t('Nouveau devis', 'New quote')}
          </button>
        </div>
      </div>

      {pret ? (
        <p className="rounded-2xl border border-amber-500/30 bg-amber-500/10 text-amber-400 px-4 py-3 text-sm">
          {t(
            "Aucune société n'est rattachée à votre compte : les devis ne peuvent pas être chargés.",
            'No company is attached to your account: quotes cannot be loaded.'
          )}
        </p>
      ) : null}

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            {t('Devis émis', 'Issued quotes')}
            <span className="ml-2 text-xs font-mono text-slate-400">({filtered.length})</span>
          </h3>

          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-3.5 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t('Référence, client, tracé…', 'Reference, client, route…')}
                aria-label={t('Rechercher un devis', 'Search a quote')}
                className="min-h-[44px] w-full pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>
            <select
              value={statutFilter}
              onChange={(e) => setStatutFilter(e.target.value)}
              aria-label={t('Filtrer par statut', 'Filter by status')}
              className="min-h-[44px] w-full sm:w-auto px-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="all">{t('Tous les statuts', 'All statuses')}</option>
              {STATUTS_DEVIS.map((s) => (
                <option key={s} value={s}>{libelleStatut(s, t)}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">{t('Référence / Client', 'Reference / Client')}</th>
                <th className="px-6 py-4">{t('Tracé', 'Route')}</th>
                <th className="px-6 py-4">{t('Nature du fret', 'Cargo')}</th>
                <th className="px-6 py-4 text-right whitespace-nowrap">{t('Montant estimé', 'Quoted amount')}</th>
                <th className="px-6 py-4 text-right whitespace-nowrap">{t('Marge', 'Margin')}</th>
                <th className="px-6 py-4">{t('Statut', 'Status')}</th>
                <th className="px-6 py-4 text-right">{t('Décision', 'Decision')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {charge ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-slate-400">
                    {t('Chargement des devis…', 'Loading quotes…')}
                  </td>
                </tr>
              ) : loadError ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-red-400">
                    {t(
                      'Le registre des devis na pas pu être chargé. Vérifiez votre connexion puis réessayez.',
                      'The quote register could not be loaded. Check your connection and try again.'
                    )}
                    <button
                      type="button"
                      onClick={reload}
                      className="block mx-auto mt-3 min-h-[44px] px-4 py-2 rounded-xl border border-slate-700 text-xs font-bold text-slate-200 hover:bg-slate-800"
                    >
                      {t('Réessayer', 'Retry')}
                    </button>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500">
                    {devis.length === 0
                      ? t(
                        'Aucun devis enregistré. Émettez le premier avec « Nouveau devis ».',
                        'No quote on record. Issue the first one with “New quote”.'
                      )
                      : t('Aucun devis ne correspond à la recherche.', 'No quote matches your search.')}
                  </td>
                </tr>
              ) : (
                filtered.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 font-mono whitespace-nowrap">
                      {d.reference || `#${d.id}`}
                      <div className="text-xs font-normal text-slate-400 truncate max-w-[220px]" title={d.client_nom}>
                        <Truck className="w-3 h-3 inline mr-1 -mt-0.5" />
                        {d.client_nom || ''}
                      </div>
                      <div className="text-xs font-normal text-slate-500">{formatDate(d.created_at)}</div>
                    </td>
                    <td className="px-6 py-4 max-w-[260px]">
                      <span className="block truncate" title={`${d.origine} → ${d.destination}`}>
                        {d.origine || ''} → {d.destination || ''}
                      </span>
                    </td>
                    <td className="px-6 py-4 max-w-[200px] truncate" title={d.nature_fret}>
                      {d.nature_fret || ''}
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold whitespace-nowrap text-emerald-400">
                      {d.montant_estime_xaf != null
                        ? `${Number(d.montant_estime_xaf).toLocaleString(loc)} XAF`
                        : ''}
                    </td>
                    <td className="px-6 py-4 text-right font-mono whitespace-nowrap">
                      {d.marge_nette_pct != null ? `${Number(d.marge_nette_pct).toLocaleString(loc)} %` : ''}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${statutBadge(d.statut)}`}>
                        {libelleStatut(d.statut, t)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {d.statut === 'SOUMIS' ? (
                        <div className="flex justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => decisionMutation.mutate({ id: d.id, statut: 'ACCEPTE' })}
                            disabled={decisionMutation.isPending}
                            className="min-h-[44px] inline-flex items-center gap-1 px-3 rounded-xl border border-emerald-500/40 bg-emerald-500/10 text-xs font-bold text-emerald-400 hover:bg-emerald-500/20 disabled:opacity-60"
                          >
                            <Check className="w-3.5 h-3.5" /> {t('Accepter', 'Accept')}
                          </button>
                          <button
                            type="button"
                            onClick={() => decisionMutation.mutate({ id: d.id, statut: 'REJETE' })}
                            disabled={decisionMutation.isPending}
                            className="min-h-[44px] inline-flex items-center gap-1 px-3 rounded-xl border border-slate-700 bg-slate-800 text-xs font-bold text-slate-300 hover:bg-slate-700 disabled:opacity-60"
                          >
                            <X className="w-3.5 h-3.5" /> {t('Rejeter', 'Reject')}
                          </button>
                        </div>
                      ) : (
                        <p className="text-right text-xs text-slate-600"></p>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de création */}
      {modalOpen && (
        <div className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg my-8 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold">{t('Émettre un devis', 'Issue a quote')}</h3>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                aria-label={t('Fermer', 'Close')}
                className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Référence *', 'Reference *')}
                  </label>
                  <input
                    type="text"
                    required
                    value={form.reference}
                    onChange={champ('reference')}
                    placeholder="DEV-2026-001"
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                  {referenceDejaPrise ? (
                    <p className="text-xs text-rose-400 mt-1">{t('Référence déjà utilisée.', 'Reference already used.')}</p>
                  ) : null}
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Client *', 'Client *')}
                  </label>
                  <input
                    type="text"
                    required
                    list="cotations-clients-list"
                    value={form.client_nom}
                    onChange={champ('client_nom')}
                    placeholder={t('Raison sociale du destinataire', 'Recipient company name')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                  <datalist id="cotations-clients-list">
                    {(clientsQuery.data ?? []).map((c) => (
                      <option key={c.id} value={c.name ?? ''} />
                    ))}
                  </datalist>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Origine *', 'Origin *')}
                  </label>
                  <input
                    type="text"
                    required
                    value={form.origine}
                    onChange={champ('origine')}
                    placeholder={t('Port de Douala', 'Douala port')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Destination *', 'Destination *')}
                  </label>
                  <input
                    type="text"
                    required
                    value={form.destination}
                    onChange={champ('destination')}
                    placeholder={t("N'Djamena", 'N’Djamena')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Nature du fret *', 'Cargo *')}
                  </label>
                  <input
                    type="text"
                    required
                    value={form.nature_fret}
                    onChange={champ('nature_fret')}
                    placeholder={t('Conteneur 40HC', '40HC container')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Montant estimé (XAF) *', 'Quoted amount (XAF) *')}
                  </label>
                  <input
                    type="number"
                    required
                    min="0"
                    step="0.01"
                    value={form.montant_estime_xaf}
                    onChange={champ('montant_estime_xaf')}
                    placeholder="0"
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <p className="text-xs text-slate-500">
                {t(
                  'La marge et le statut sont initialisés par la base (15 %, soumis) puis ajustés depuis la liste.',
                  'Margin and status are initialised by the database (15 %, submitted) then adjusted from the list.'
                )}
              </p>

              <div className="flex flex-col-reverse sm:flex-row justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="min-h-[44px] px-4 rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={
                    creationMutation.isPending ||
                    !form.reference.trim() ||
                    !form.client_nom.trim() ||
                    !form.origine.trim() ||
                    !form.destination.trim() ||
                    !form.nature_fret.trim() ||
                    form.montant_estime_xaf === '' ||
                    referenceDejaPrise
                  }
                  className="min-h-[44px] px-5 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30 disabled:opacity-60"
                >
                  {creationMutation.isPending ? t('Enregistrement…', 'Saving…') : t('Enregistrer le devis', 'Save quote')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useSession } from 'next-auth/react';
import {
  LifeBuoy,
  Plus,
  Search,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  X,
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { supportAPI } from '@/lib/api-client';
import { useI18n } from '@/hooks/useI18n';

/*
 * Console support : table support_tickets, contrat reel du router
 * /api/v1/support (TicketCreate / TicketUpdate / TicketResponse).
 *
 * Les deux colonnes derivees (statut, priorite) sont des String libres en
 * base ; le domaine est celui rappele par le backend. Aucune valeur n'est
 * inventee : un ticket sans module precise ni assignation affiche « non
 * renseigne », pas un remplissage par defaut.
 */
const STATUTS = ['ouvert', 'en_cours', 'resolu', 'ferme'] as const;
const PRIORITES = ['basse', 'normale', 'haute', 'urgente'] as const;

// Le slate est l'identite du module Administration (support y est rattache) :
// les badges d'etat utilisent donc d'autres teintes pour rester lisibles.
function statutBadge(statut?: string): string {
  const s = String(statut || '').toLowerCase();
  if (s === 'ouvert') return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
  if (s === 'en_cours') return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  if (s === 'resolu') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  if (s === 'ferme') return 'bg-slate-600/20 text-slate-300 border-slate-500/30';
  return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
}

function prioriteBadge(priorite?: string): string {
  const p = String(priorite || '').toLowerCase();
  if (p === 'urgente') return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
  if (p === 'haute') return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
  return 'bg-slate-500/10 text-slate-400 border-slate-600/40';
}

// Valeurs de module_concerne = cles de routage reelles de l'ERP.
const MODULES: { value: string; labelKey: keyof ReturnType<typeof useI18n>['support'] }[] = [
  { value: 'transit-douane', labelKey: 'modTransit' },
  { value: 'transport-flotte', labelKey: 'modTransport' },
  { value: 'finance-ohada', labelKey: 'modFinance' },
  { value: 'magasin-stock', labelKey: 'modMagasin' },
  { value: 'port-operations', labelKey: 'modPort' },
  { value: 'comptabilite-ohada', labelKey: 'modCompta' },
  { value: 'rh-personnel', labelKey: 'modRH' },
  { value: 'qhse-securite', labelKey: 'modQHSE' },
  { value: 'admin-tenant', labelKey: 'modPlateforme' },
];

export default function SupportPage() {
  const t = useI18n();
  const { data: session } = useSession();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTicket, setNewTicket] = useState({
    sujet: '',
    module_concerne: 'admin-tenant',
    priorite: 'normale',
    description: '',
  });

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['support-tickets'],
    queryFn: async () => {
      const res = await supportAPI.getTickets({ limit: 200 });
      const raw = res.data?.items ?? res.data ?? [];
      return Array.isArray(raw) ? raw : [];
    },
  });

  const tickets = Array.isArray(data) ? data : [];

  const statutLabel = (s?: string) => {
    const key = String(s || '').toLowerCase();
    if (key === 'en_cours') return t.support.statutEnCours;
    if (key === 'resolu') return t.support.statutResolu;
    if (key === 'ferme') return t.support.statutFerme;
    if (key === 'ouvert') return t.support.statutOuvert;
    return s || t.support.none;
  };

  const prioriteLabel = (p?: string) => {
    const key = String(p || '').toLowerCase();
    if (key === 'basse') return t.support.prioBasse;
    if (key === 'haute') return t.support.prioHaute;
    if (key === 'urgente') return t.support.prioUrgente;
    if (key === 'normale') return t.support.prioNormale;
    return p || t.support.none;
  };

  const moduleLabel = (value?: string) => {
    if (!value) return t.support.noModule;
    const found = MODULES.find(m => m.value === value);
    return found ? (t.support as any)[found.labelKey] : value;
  };

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
  }, []);

  // Escape ferme la modale : le clavier est le seul moyen de sortir sur
  // mobile quand le contenu depasse l'ecran.
  useEffect(() => {
    if (!isModalOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeModal();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isModalOpen, closeModal]);

  const createMutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) => {
      const res = await supportAPI.createTicket(payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success(t.support.created);
      closeModal();
      setNewTicket({ sujet: '', module_concerne: 'admin-tenant', priorite: 'normale', description: '' });
      queryClient.invalidateQueries({ queryKey: ['support-tickets'] });
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || t.support.createFailed);
    },
  });

  const statutMutation = useMutation({
    mutationFn: async ({ id, statut }: { id: number; statut: string }) => {
      const res = await supportAPI.updateTicket(id, { statut });
      return res.data;
    },
    onSuccess: () => {
      toast.success(t.support.statutUpdated);
      queryClient.invalidateQueries({ queryKey: ['support-tickets'] });
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || t.support.statutUpdateFailed);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const sujet = newTicket.sujet.trim();
    if (!sujet) return;
    // demandeur : l'identite reellement connectee, sinon le champ reste vide.
    const demandeur = session?.user?.email || session?.user?.name || undefined;
    createMutation.mutate({
      sujet,
      description: newTicket.description.trim() || undefined,
      module_concerne: newTicket.module_concerne,
      priorite: newTicket.priorite,
      demandeur,
    });
  };

  const filtered = tickets.filter((tk: any) => {
    if (statusFilter && String(tk.statut || '').toLowerCase() !== statusFilter) return false;
    const q = searchQuery.trim().toLowerCase();
    if (!q) return true;
    return [tk.sujet, tk.description, tk.reference, tk.module_concerne]
      .some((field: any) => String(field || '').toLowerCase().includes(q));
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-5 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900 p-5">
        <div className="flex items-start gap-3">
          <div className="shrink-0 p-2.5 rounded-xl bg-slate-500/10 text-slate-400 border border-slate-500/20">
            <LifeBuoy className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              {t.support.title}
            </h1>
            <p className="text-sm text-slate-400 mt-1">{t.support.subtitle}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            aria-label={t.support.refresh}
            title={t.support.refresh}
            className="inline-flex items-center justify-center min-h-[44px] min-w-[44px] px-3 border border-slate-700 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center justify-center gap-1.5 min-h-[44px] px-4 text-sm font-semibold rounded-xl bg-slate-600 hover:bg-slate-500 text-white transition-colors"
          >
            <Plus className="w-4 h-4" /> {t.support.newTicket}
          </button>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder={t.support.searchPlaceholder}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full min-h-[44px] pl-9 pr-3 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="sm:w-56 min-h-[44px] px-3 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-slate-500"
        >
          <option value="">{t.support.filterAll}</option>
          {STATUTS.map(s => (
            <option key={s} value={s}>{statutLabel(s)}</option>
          ))}
        </select>
      </div>

      {/* Tickets */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">{t.support.colSujet}</th>
                <th className="px-4 py-3">{t.support.colReference}</th>
                <th className="px-4 py-3">{t.support.colModule}</th>
                <th className="px-4 py-3">{t.support.colPriorite}</th>
                <th className="px-4 py-3">{t.support.colCreated}</th>
                <th className="px-4 py-3">{t.support.colAssignee}</th>
                <th className="px-4 py-3 text-right">{t.support.colStatut}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="p-10 text-center text-slate-400">
                    {t.support.loading}
                  </td>
                </tr>
              ) : isError ? (
                <tr>
                  <td colSpan={7} className="p-10 text-center">
                    <AlertTriangle className="w-10 h-10 text-amber-500/50 mx-auto mb-3" />
                    <h3 className="font-semibold text-slate-100">{t.support.errorTitle}</h3>
                    <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto break-words">
                      {(error as any)?.response?.data?.detail || String(error)}
                    </p>
                    <button
                      onClick={() => refetch()}
                      className="mt-4 inline-flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl border border-slate-700 text-slate-200 hover:bg-slate-800 transition-colors"
                    >
                      <RefreshCw className="w-3.5 h-3.5" /> {t.shell.retry}
                    </button>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-10 text-center">
                    <CheckCircle2 className="w-10 h-10 text-slate-600 mx-auto mb-3" />
                    <h3 className="font-semibold text-slate-100">{t.support.emptyTitle}</h3>
                    <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">{t.support.emptyHint}</p>
                  </td>
                </tr>
              ) : (
                filtered.map((tk: any, idx: number) => (
                  <tr key={tk.id ?? idx} className="hover:bg-slate-800/40 transition-colors align-top">
                    <td className="px-4 py-3.5">
                      <div className="font-semibold text-slate-100">{tk.sujet || `#${tk.id}`}</div>
                      {tk.description && (
                        <div className="text-xs text-slate-400 line-clamp-1 max-w-xs">{tk.description}</div>
                      )}
                    </td>
                    <td className="px-4 py-3.5 font-mono text-xs text-slate-400 whitespace-nowrap">
                      {tk.reference || '—'}
                    </td>
                    <td className="px-4 py-3.5 text-xs">{moduleLabel(tk.module_concerne)}</td>
                    <td className="px-4 py-3.5">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-semibold border ${prioriteBadge(tk.priorite)}`}>
                        {prioriteLabel(tk.priorite)}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-400 whitespace-nowrap">
                      {tk.created_at ? String(tk.created_at).slice(0, 10) : t.support.unknownDate}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-400">
                      {tk.assigne_a || t.support.unassigned}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <select
                        value={String(tk.statut || 'ouvert').toLowerCase()}
                        disabled={statutMutation.isPending}
                        onChange={(e) =>
                          statutMutation.mutate({ id: Number(tk.id), statut: e.target.value })
                        }
                        aria-label={`${t.support.colStatut} — ${tk.reference || tk.sujet || tk.id}`}
                        className={`min-h-[36px] px-2 py-1 rounded-lg text-xs font-semibold border bg-transparent focus:outline-none focus:border-slate-500 ${statutBadge(tk.statut)}`}
                      >
                        {STATUTS.map(s => (
                          <option key={s} value={s} className="bg-slate-900 text-slate-100">
                            {statutLabel(s)}
                          </option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Creation modal */}
      {isModalOpen && (
        <div
          className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4"
          onClick={closeModal}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-label={t.support.modalTitle}
            onClick={(e) => e.stopPropagation()}
            className="bg-slate-900 border border-slate-800 w-full sm:max-w-lg max-h-[92vh] overflow-y-auto rounded-t-2xl sm:rounded-2xl p-5 sm:p-6 text-white shadow-2xl"
          >
            <div className="flex items-start justify-between gap-3 pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-base sm:text-lg font-bold flex items-center gap-2">
                  <LifeBuoy className="w-5 h-5 text-slate-400" /> {t.support.modalTitle}
                </h2>
                <p className="text-xs text-slate-400 mt-1">{t.support.modalHelp}</p>
              </div>
              <button
                onClick={closeModal}
                aria-label={t.support.closeAria}
                className="shrink-0 inline-flex items-center justify-center min-h-[44px] min-w-[44px] rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1.5">
                  {t.support.sujetLabel} *
                </label>
                <input
                  type="text"
                  required
                  maxLength={200}
                  placeholder={t.support.sujetPlaceholder}
                  value={newTicket.sujet}
                  onChange={e => setNewTicket({ ...newTicket, sujet: e.target.value })}
                  className="w-full px-3 py-2.5 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1.5">
                    {t.support.moduleLabel}
                  </label>
                  <select
                    value={newTicket.module_concerne}
                    onChange={e => setNewTicket({ ...newTicket, module_concerne: e.target.value })}
                    className="w-full min-h-[44px] px-3 py-2.5 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-slate-500"
                  >
                    {MODULES.map(m => (
                      <option key={m.value} value={m.value}>
                        {(t.support as any)[m.labelKey]}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1.5">
                    {t.support.prioriteLabel}
                  </label>
                  <select
                    value={newTicket.priorite}
                    onChange={e => setNewTicket({ ...newTicket, priorite: e.target.value })}
                    className="w-full min-h-[44px] px-3 py-2.5 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-slate-500"
                  >
                    {PRIORITES.map(p => (
                      <option key={p} value={p}>{prioriteLabel(p)}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1.5">
                  {t.support.descLabel}
                </label>
                <textarea
                  rows={4}
                  placeholder={t.support.descPlaceholder}
                  value={newTicket.description}
                  onChange={e => setNewTicket({ ...newTicket, description: e.target.value })}
                  className="w-full px-3 py-2.5 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-500"
                />
              </div>

              <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={closeModal}
                  className="min-h-[44px] px-4 text-sm font-semibold border border-slate-700 rounded-xl text-slate-300 hover:bg-slate-800"
                >
                  {t.common.cancel}
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="min-h-[44px] px-4 text-sm font-semibold bg-slate-600 hover:bg-slate-500 disabled:opacity-60 text-white rounded-xl"
                >
                  {createMutation.isPending ? t.support.submitting : t.support.submit}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

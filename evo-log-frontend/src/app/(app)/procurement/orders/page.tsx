'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { procurementAPI, tiersAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { toast } from 'sonner';
import { ArrowLeft, ClipboardCheck, PackageCheck, RefreshCw, Inbox, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

// File d'approbation réelle du registre acquisition : les bons de commande au
// statut « brouillon » attendent une validation (PUT /{id}/valider), ceux au
// statut « valide » attendent une réception (PUT /{id} avec date_reelle_livraison
// et statut « livre »). Aucun compteur inventé : les deux colonnes ci-dessous
// sont le décompte des lignes réellement renvoyées par GET /bons-commande.
type BonCommande = {
  id: number;
  numero_bc: string;
  fournisseur_id: number | null;
  date_creation: string | null;
  date_prevue_livraison: string | null;
  date_reelle_livraison: string | null;
  destinataire: string | null;
  lieu_livraison: string | null;
  devise: string | null;
  montant_total: number | null;
  statut: string | null;
  conditions_paiement: string | null;
  notes: string | null;
  valide_par: string | null;
  date_validation: string | null;
};

type Fournisseur = { id: number; code?: string; name?: string };

export default function ProcurementOrdersSubPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const queryClient = useQueryClient();

  const bcQuery = useQuery({
    queryKey: ['procurement-orders'],
    queryFn: async () => {
      const res = await procurementAPI.getOrders();
      const raw = res?.data ?? res;
      return (Array.isArray(raw) ? raw : []) as BonCommande[];
    },
  });

  const fournisseursQuery = useQuery({
    queryKey: ['procurement-fournisseurs'],
    queryFn: async () => {
      const res = await tiersAPI.getTiers({ type_tiers: 'fournisseur', limit: 500 });
      const raw = res?.data ?? res;
      return (Array.isArray(raw) ? raw : []) as Fournisseur[];
    },
  });

  const validerMutation = useMutation({
    mutationFn: async (id: number) => (await procurementAPI.validateOrder(id))?.data,
    onSuccess: (bc: BonCommande) => {
      toast.success(
        t(
          `Bon ${bc?.numero_bc ?? ''} validé${bc?.valide_par ? ` par ${bc.valide_par}` : ''}.`,
          `Order ${bc?.numero_bc ?? ''} approved${bc?.valide_par ? ` by ${bc.valide_par}` : ''}.`
        )
      );
      queryClient.invalidateQueries({ queryKey: ['procurement-orders'] });
    },
    onError: () => toast.error(t('La validation a échoué.', 'Approval failed.')),
  });

  const receptionMutation = useMutation({
    mutationFn: async ({ id, date }: { id: number; date: string }) =>
      (await procurementAPI.updateOrder(id, { statut: 'livre', date_reelle_livraison: date }))?.data,
    onSuccess: (bc: BonCommande) => {
      toast.success(
        t(
          `Bon ${bc?.numero_bc ?? ''} marqué comme livré.`,
          `Order ${bc?.numero_bc ?? ''} marked as received.`
        )
      );
      queryClient.invalidateQueries({ queryKey: ['procurement-orders'] });
    },
    onError: () =>
      toast.error(
        t("L'enregistrement de la réception a échoué.", 'Could not record the receipt.')
      ),
  });

  const [datesReception, setDatesReception] = useState<Record<number, string>>({});

  const items = bcQuery.data ?? [];
  const fournisseursById = new Map((fournisseursQuery.data ?? []).map((f) => [f.id, f]));
  const aApprouver = items.filter((b) => b.statut === 'brouillon');
  const aReceptionner = items.filter((b) => b.statut === 'valide');

  const charge = bcQuery.isLoading || fournisseursQuery.isLoading;
  const loadError = bcQuery.isError;
  const refreshing = bcQuery.isFetching || fournisseursQuery.isFetching;
  const reload = () => {
    bcQuery.refetch();
    fournisseursQuery.refetch();
  };

  const formatDate = (d: string | null) =>
    d ? new Date(d).toLocaleDateString(loc, { day: '2-digit', month: 'short', year: 'numeric' }) : '—';

  return (
    <div className="max-w-5xl mx-auto py-6 sm:py-8 px-4 text-white animate-in fade-in duration-500 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <Link
          href="/procurement"
          className="inline-flex min-h-[44px] w-fit items-center gap-2 text-sm text-slate-400 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" /> {t('Retour aux achats', 'Back to procurement')}
        </Link>
        <button
          type="button"
          onClick={reload}
          disabled={refreshing}
          className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 disabled:opacity-60"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          {t('Actualiser', 'Refresh')}
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 sm:p-8 shadow-2xl">
        <div className="flex items-start gap-3 pb-6 border-b border-slate-800 mb-6">
          <div className="w-12 h-12 shrink-0 bg-emerald-500/10 text-emerald-400 rounded-2xl flex items-center justify-center border border-emerald-500/20">
            <ClipboardCheck className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-black break-words">
              {t("Circuit d'approbation des commandes", 'Purchase order approval queue')}
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              {t(
                'Validation puis confirmation de réception, sur le registre réel des bons de commande.',
                'Approval then receipt confirmation, on the live purchase order register.'
              )}
            </p>
          </div>
        </div>

        {charge ? (
          <div className="p-8 text-center text-slate-400">
            {t('Chargement de la file d\'approbation…', 'Loading the approval queue…')}
          </div>
        ) : loadError ? (
          <div className="p-8 text-center text-red-400">
            {t(
              'La file na pas pu être chargée. Réessayez depuis le registre des achats.',
              'The queue could not be loaded. Retry from the purchase order register.'
            )}
          </div>
        ) : (
          <div className="space-y-8">
            {/* 1. Brouillons à valider */}
            <section>
              <h2 className="flex items-center gap-2 text-sm font-bold text-slate-200 uppercase tracking-wider mb-3">
                <Inbox className="w-4 h-4 text-amber-400" />
                {t(`À valider (${aApprouver.length})`, `To approve (${aApprouver.length})`)}
              </h2>
              {aApprouver.length === 0 ? (
                <p className="p-4 rounded-2xl border border-slate-800 bg-slate-950 text-sm text-slate-400">
                  {t(
                    'Aucun bon de commande en brouillon : rien n\'attend de validation.',
                    'No draft purchase order: nothing is waiting for approval.'
                  )}
                </p>
              ) : (
                <div className="space-y-3">
                  {aApprouver.map((b) => (
                    <div key={b.id} className="flex flex-col sm:flex-row sm:items-center gap-3 p-4 rounded-2xl border border-slate-800 bg-slate-950">
                      <div className="min-w-0 flex-1">
                        <p className="font-mono font-bold text-slate-100 truncate" title={b.numero_bc}>
                          {b.numero_bc || `#${b.id}`}
                        </p>
                        <p className="text-sm text-slate-400 truncate" title={(b.fournisseur_id ? fournisseursById.get(b.fournisseur_id)?.name : undefined) ?? undefined}>
                          {(b.fournisseur_id ? fournisseursById.get(b.fournisseur_id)?.name : undefined) ??
                            t('Fournisseur supprimé', 'Supplier removed')}
                          {b.destinataire ? ` · ${b.destinataire}` : ''}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          {t('à livrer le', 'due')} {formatDate(b.date_prevue_livraison)}
                          {b.montant_total != null
                            ? ` · ${Number(b.montant_total).toLocaleString(loc)} ${b.devise || 'XAF'}`
                            : ''}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => validerMutation.mutate(b.id)}
                        disabled={validerMutation.isPending}
                        className="min-h-[44px] shrink-0 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold disabled:opacity-60"
                      >
                        {t('Valider', 'Approve')}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* 2. Validés à réceptionner */}
            <section>
              <h2 className="flex items-center gap-2 text-sm font-bold text-slate-200 uppercase tracking-wider mb-3">
                <PackageCheck className="w-4 h-4 text-sky-400" />
                {t(`À réceptionner (${aReceptionner.length})`, `To receive (${aReceptionner.length})`)}
              </h2>
              {aReceptionner.length === 0 ? (
                <p className="p-4 rounded-2xl border border-slate-800 bg-slate-950 text-sm text-slate-400">
                  {t(
                    'Aucun bon validé en attente de réception.',
                    'No approved order waiting for receipt.'
                  )}
                </p>
              ) : (
                <div className="space-y-3">
                  {aReceptionner.map((b) => {
                    const four = b.fournisseur_id ? fournisseursById.get(b.fournisseur_id) : undefined;
                    const dateSaisie = datesReception[b.id] ?? new Date().toISOString().slice(0, 10);
                    return (
                      <div key={b.id} className="flex flex-col sm:flex-row sm:items-center gap-3 p-4 rounded-2xl border border-slate-800 bg-slate-950">
                        <div className="min-w-0 flex-1">
                          <p className="font-mono font-bold text-slate-100 truncate" title={b.numero_bc}>
                            {b.numero_bc || `#${b.id}`}
                          </p>
                          <p className="text-sm text-slate-400 truncate" title={four?.name ?? undefined}>
                            {four?.name ?? t('Fournisseur supprimé', 'Supplier removed')}
                            {b.lieu_livraison ? ` · ${b.lieu_livraison}` : ''}
                          </p>
                          <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                            {t('validé par', 'approved by')} {b.valide_par || '—'}
                            {b.date_validation ? ` · ${formatDate(b.date_validation)}` : ''}
                          </p>
                        </div>
                        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 shrink-0">
                          <input
                            type="date"
                            value={dateSaisie}
                            aria-label={t('Date de réception', 'Receipt date')}
                            onChange={(e) => setDatesReception((d) => ({ ...d, [b.id]: e.target.value }))}
                            className="min-h-[44px] bg-slate-900 border border-slate-700 rounded-xl px-3 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                          />
                          <button
                            type="button"
                            onClick={() => receptionMutation.mutate({ id: b.id, date: dateSaisie })}
                            disabled={receptionMutation.isPending || !dateSaisie}
                            className="min-h-[44px] px-4 rounded-xl border border-emerald-500/40 bg-emerald-500/10 text-sm font-semibold text-emerald-400 hover:bg-emerald-500/20 disabled:opacity-60"
                          >
                            {t('Confirmer réception', 'Confirm receipt')}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

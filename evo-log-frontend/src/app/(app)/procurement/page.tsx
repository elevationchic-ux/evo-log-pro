'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { procurementAPI, tiersAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { toast } from 'sonner';
import { ShoppingCart, Plus, Search, RefreshCw, ClipboardList, X } from 'lucide-react';
import Link from 'next/link';

// Registre réel : table bons_commande, exposée par le router acquisition
// (GET/POST /api/v1/acquisition/bons-commande, PUT /{id}, PUT /{id}/valider).
// L'ancien /api/v1/k-modules/procurement/orders répondait 501 sans modèle.
// Aucune colonne inventée : chaque cellule correspond à un champ renvoyé
// par BonCommandeResponse côté serveur.
type BonCommande = {
  id: number;
  numero_bc: string;
  fournisseur_id: number | null;
  contrat_cadre_id: number | null;
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

// fournisseur_id est une FK vers tiers.id : le nom du fournisseur n'est jamais
// stocké sur le bon de commande, on le résout depuis la liste des tiers de
// type « fournisseur ». /api/v1/suppliers serait le mauvaise source : il sert
// la table prestataires, pas tiers.
type Fournisseur = { id: number; code?: string; name?: string; is_active?: boolean };

// Statuts réels de la colonne bons_commande.statut (String(20)).
const STATUTS_BC = ['brouillon', 'valide', 'livre', 'annule'] as const;

function statutBadge(s: string | null) {
  if (s === 'valide') return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
  if (s === 'livre') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  if (s === 'annule') return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
  return 'bg-slate-500/10 text-slate-300 border-slate-500/30';
}

function libelleStatut(s: string | null, t: (fr: string, en: string) => string) {
  if (s === 'brouillon') return t('Brouillon', 'Draft');
  if (s === 'valide') return t('Validé', 'Approved');
  if (s === 'livre') return t('Livré', 'Received');
  if (s === 'annule') return t('Annulé', 'Cancelled');
  return s || '';
}

type FormState = {
  numero_bc: string;
  fournisseur_id: string;
  date_prevue_livraison: string;
  destinataire: string;
  lieu_livraison: string;
  conditions_paiement: string;
  montant_total: string;
  notes: string;
};

const FORM_VIDE: FormState = {
  numero_bc: '',
  fournisseur_id: '',
  date_prevue_livraison: '',
  destinataire: '',
  lieu_livraison: '',
  conditions_paiement: '',
  montant_total: '',
  notes: '',
};

export default function ProcurementPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statutFilter, setStatutFilter] = useState<string>('all');
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<FormState>(FORM_VIDE);

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

  const bonsCommande = bcQuery.data ?? [];
  const fournisseurs = fournisseursQuery.data ?? [];
  const fournisseursById = new Map(fournisseurs.map((f) => [f.id, f]));

  const createMutation = useMutation({
    mutationFn: async (payload: FormState) => {
      // BonCommandeCreate n'expose pas le montant : la colonne montant_total
      // n'est renseignable que par PUT /bons-commande/{id} (BonCommandeUpdate).
      // On crée donc le BC, puis on le complète si un montant a été saisi.
      const res = await procurementAPI.createOrder({
        numero_bc: payload.numero_bc.trim(),
        fournisseur_id: Number(payload.fournisseur_id),
        date_prevue_livraison: payload.date_prevue_livraison,
        destinataire: payload.destinataire.trim(),
        lieu_livraison: payload.lieu_livraison.trim(),
        conditions_paiement: payload.conditions_paiement.trim(),
        notes: payload.notes.trim(),
      });
      const cree = res?.data as BonCommande | undefined;
      const montant = payload.montant_total.trim();
      if (cree?.id && montant !== '') {
        try {
          await procurementAPI.updateOrder(cree.id, { montant_total: Number(montant) });
        } catch {
          // Le bon de commande est bien créé : seul le montant manque.
          toast.warning(
            t(
              `Bon ${cree.numero_bc} créé, mais le montant n'a pas pu être enregistré.`,
              `Order ${cree.numero_bc} created, but the amount could not be saved.`
            )
          );
        }
      }
      return cree;
    },
    onSuccess: (bc) => {
      toast.success(
        t(
          `Bon de commande ${bc?.numero_bc ?? ''} enregistré (brouillon).`,
          `Purchase order ${bc?.numero_bc ?? ''} saved (draft).`
        )
      );
      queryClient.invalidateQueries({ queryKey: ['procurement-orders'] });
      setModalOpen(false);
      setForm(FORM_VIDE);
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(
        detail ||
        t(
          "Le bon de commande n'a pas pu être enregistré.",
          'The purchase order could not be saved.'
        )
      );
    },
  });

  const validerMutation = useMutation({
    mutationFn: async (id: number) => (await procurementAPI.validateOrder(id))?.data,
    onSuccess: (bc) => {
      toast.success(
        t(
          `Bon ${bc?.numero_bc ?? ''} validé par ${bc?.valide_par ?? ''}.`,
          `Order ${bc?.numero_bc ?? ''} approved by ${bc?.valide_par ?? ''}.`
        )
      );
      queryClient.invalidateQueries({ queryKey: ['procurement-orders'] });
    },
    onError: () => {
      toast.error(
        t("La validation n'a pas abouti.", 'Approval failed.')
      );
    },
  });

  const numeroDejaPris = bonsCommande.some(
    (b) => b.numero_bc.toLowerCase() === form.numero_bc.trim().toLowerCase()
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.numero_bc.trim() || !form.fournisseur_id || !form.date_prevue_livraison) return;
    if (numeroDejaPris) {
      toast.error(
        t(
          'Ce numéro de bon de commande existe déjà.',
          'This purchase order number already exists.'
        )
      );
      return;
    }
    createMutation.mutate(form);
  };

  const filtered = bonsCommande.filter((b) => {
    if (statutFilter !== 'all' && (b.statut ?? '') !== statutFilter) return false;
    if (!searchQuery.trim()) return true;
    const four = b.fournisseur_id ? fournisseursById.get(b.fournisseur_id) : undefined;
    const hay = `${b.numero_bc} ${four?.name ?? ''} ${b.destinataire ?? ''} ${b.lieu_livraison ?? ''} ${b.notes ?? ''}`;
    return hay.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const enBrouillon = bonsCommande.filter((b) => b.statut === 'brouillon').length;
  const charge = bcQuery.isLoading || fournisseursQuery.isLoading;
  const loadError = bcQuery.isError;
  const refreshing = bcQuery.isFetching || fournisseursQuery.isFetching;
  const reload = () => {
    bcQuery.refetch();
    fournisseursQuery.refetch();
  };

  const formatDate = (d: string | null) =>
    d ? new Date(d).toLocaleDateString(loc, { day: '2-digit', month: 'short', year: 'numeric' }) : '';

  const champ = (k: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-xl">
        <div className="min-w-0">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <ShoppingCart className="w-3.5 h-3.5 shrink-0" />
            {t('Achats • Bons de commande fournisseurs', 'Procurement • Supplier purchase orders')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight break-words">
            {t('Registre des bons de commande', 'Purchase order register')}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            {enBrouillon > 0
              ? t(
                `${enBrouillon} bon(s) en attente d'approbation sur ${bonsCommande.length} enregistré(s).`,
                `${enBrouillon} of ${bonsCommande.length} order(s) awaiting approval.`
              )
              : t(
                `${bonsCommande.length} bon(s) de commande enregistré(s).`,
                `${bonsCommande.length} purchase order(s) on record.`
              )}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={reload}
            disabled={refreshing}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 disabled:opacity-60"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <Link
            href="/procurement/orders"
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700"
          >
            <ClipboardList className="w-4 h-4" />
            {t('Circuit d\'approbation', 'Approval queue')}
          </Link>
          <button
            type="button"
            onClick={() => setModalOpen(true)}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-colors"
          >
            <Plus className="w-4 h-4" />
            {t('Nouveau bon', 'New order')}
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            {t('Bons de commande', 'Purchase orders')}
            <span className="ml-2 text-xs font-mono text-slate-400">({filtered.length})</span>
          </h3>

          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-3.5 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t('N° BC, fournisseur, destinataire…', 'PO no., supplier, recipient…')}
                aria-label={t('Rechercher un bon de commande', 'Search a purchase order')}
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
              {STATUTS_BC.map((s) => (
                <option key={s} value={s}>{libelleStatut(s, t)}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">{t('N° BC', 'PO no.')}</th>
                <th className="px-6 py-4">{t('Fournisseur', 'Supplier')}</th>
                <th className="px-6 py-4">{t('Destinataire / Lieu', 'Recipient / Delivery point')}</th>
                <th className="px-6 py-4 whitespace-nowrap">{t('Livraison prévue', 'Due date')}</th>
                <th className="px-6 py-4 text-right whitespace-nowrap">{t('Montant', 'Amount')}</th>
                <th className="px-6 py-4">{t('Statut', 'Status')}</th>
                <th className="px-6 py-4 text-right">{t('Action', 'Action')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {charge ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-slate-400">
                    {t('Chargement des bons de commande…', 'Loading purchase orders…')}
                  </td>
                </tr>
              ) : loadError ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-red-400">
                    {t(
                      'Le registre des achats n\'a pas pu être chargé. Vérifiez votre connexion puis réessayez.',
                      'The procurement register could not be loaded. Check your connection and try again.'
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
                    {bonsCommande.length === 0
                      ? t(
                        'Aucun bon de commande enregistré. Créez le premier avec « Nouveau bon ».',
                        'No purchase order yet. Create the first one with “New order”.'
                      )
                      : t(
                        'Aucun bon de commande ne correspond à la recherche.',
                        'No purchase order matches your search.'
                      )}
                  </td>
                </tr>
              ) : (
                filtered.map((b) => {
                  const four = b.fournisseur_id ? fournisseursById.get(b.fournisseur_id) : undefined;
                  return (
                    <tr key={b.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-100 font-mono whitespace-nowrap">
                        {b.numero_bc || `#${b.id}`}
                        <div className="text-xs font-normal text-slate-400">{formatDate(b.date_creation)}</div>
                      </td>
                      <td className="px-6 py-4 max-w-[220px]">
                        <span className="block truncate" title={four?.name ?? undefined}>
                          {four?.name ?? t('Fournisseur supprimé', 'Supplier removed')}
                        </span>
                        {four?.code ? (
                          <span className="block text-xs font-normal text-slate-400 font-mono">{four.code}</span>
                        ) : null}
                      </td>
                      <td className="px-6 py-4 max-w-[260px]">
                        <span className="block truncate" title={b.destinataire ?? undefined}>
                          {b.destinataire || ''}
                        </span>
                        <span className="block text-xs text-slate-400 truncate" title={b.lieu_livraison ?? undefined}>
                          {b.lieu_livraison || ''}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {formatDate(b.date_prevue_livraison)}
                        {b.date_reelle_livraison ? (
                          <div className="text-xs text-emerald-400">
                            {t('Reçu', 'Received')} {formatDate(b.date_reelle_livraison)}
                          </div>
                        ) : null}
                      </td>
                      <td className="px-6 py-4 text-right font-mono font-bold whitespace-nowrap">
                        {b.montant_total != null
                          ? `${Number(b.montant_total).toLocaleString(loc)} ${b.devise || 'XAF'}`
                          : t(' (non saisi)', ' (not set)')}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${statutBadge(b.statut)}`}>
                          {libelleStatut(b.statut, t)}
                        </span>
                        {b.valide_par ? (
                          <div className="text-xs text-slate-400 mt-1 truncate" title={`${b.valide_par} · ${formatDate(b.date_validation)}`}>
                            {b.valide_par}
                          </div>
                        ) : null}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {b.statut === 'brouillon' ? (
                          <button
                            type="button"
                            onClick={() => validerMutation.mutate(b.id)}
                            disabled={validerMutation.isPending}
                            className="min-h-[44px] px-4 rounded-xl border border-emerald-500/40 bg-emerald-500/10 text-xs font-bold text-emerald-400 hover:bg-emerald-500/20 disabled:opacity-60"
                          >
                            {t('Approuver', 'Approve')}
                          </button>
                        ) : (
                          <span className="text-xs text-slate-600"></span>
                        )}
                      </td>
                    </tr>
                  );
                })
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
              <h3 className="text-lg font-bold">{t('Nouveau bon de commande', 'New purchase order')}</h3>
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
              {fournisseurs.length === 0 && !fournisseursQuery.isLoading ? (
                <div className="text-sm rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-400 p-3">
                  <p>{t('Aucun fournisseur nest enregistré : la liste est vide.', 'No supplier on record: the list is empty.')}</p>
                  <Link
                    href="/fournisseurs"
                    className="inline-flex min-h-[44px] items-center gap-1 text-xs font-bold underline mt-1"
                  >
                    {t('Ajouter un fournisseur', 'Add a supplier')}
                  </Link>
                </div>
              ) : null}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('N° bon de commande *', 'PO number *')}
                  </label>
                  <input
                    type="text"
                    required
                    value={form.numero_bc}
                    onChange={champ('numero_bc')}
                    placeholder="BC-2026-001"
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                  {numeroDejaPris ? (
                    <p className="text-xs text-rose-400 mt-1">
                      {t('Numéro déjà utilisé.', 'Number already used.')}
                    </p>
                  ) : null}
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Fournisseur *', 'Supplier *')}
                  </label>
                  <select
                    required
                    value={form.fournisseur_id}
                    onChange={champ('fournisseur_id')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-3 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="">{t(' choisir ', ' select ')}</option>
                    {fournisseurs.map((f) => (
                      <option key={f.id} value={String(f.id)}>
                        {f.name}{f.code ? ` (${f.code})` : ''}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Livraison prévue *', 'Due date *')}
                  </label>
                  <input
                    type="date"
                    required
                    value={form.date_prevue_livraison}
                    onChange={champ('date_prevue_livraison')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Conditions de paiement', 'Payment terms')}
                  </label>
                  <input
                    type="text"
                    required
                    value={form.conditions_paiement}
                    onChange={champ('conditions_paiement')}
                    placeholder={t('30 jours fin de mois', '30 days end of month')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Destinataire *', 'Recipient *')}
                  </label>
                  <input
                    type="text"
                    required
                    value={form.destinataire}
                    onChange={champ('destinataire')}
                    placeholder={t('Magasin de Douala', 'Douala warehouse')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Lieu de livraison *', 'Delivery location *')}
                  </label>
                  <input
                    type="text"
                    required
                    value={form.lieu_livraison}
                    onChange={champ('lieu_livraison')}
                    placeholder={t('Zone portuaire, Douala', 'Port area, Douala')}
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Montant total (facultatif)', 'Total amount (optional)')}
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={form.montant_total}
                    onChange={champ('montant_total')}
                    placeholder="0"
                    className="min-h-[44px] w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    {t(
                      'Un bon de commande part en brouillon : l\'approbation se fait depuis la liste.',
                      'A purchase order starts as a draft: approval happens from the list.'
                    )}
                  </p>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                    {t('Notes', 'Notes')}
                  </label>
                  <textarea
                    value={form.notes}
                    onChange={champ('notes')}
                    rows={2}
                    placeholder={t('Objet de la commande, quantités…', 'What is being ordered, quantities…')}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

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
                    createMutation.isPending ||
                    !form.numero_bc.trim() ||
                    !form.fournisseur_id ||
                    !form.date_prevue_livraison ||
                    numeroDejaPris
                  }
                  className="min-h-[44px] px-5 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30 disabled:opacity-60"
                >
                  {createMutation.isPending ? t('Enregistrement…', 'Saving…') : t('Enregistrer le brouillon', 'Save draft')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

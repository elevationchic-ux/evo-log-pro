'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  TrendingUp, Calculator, FileText, Users, RefreshCw, Plus,
  Tags, Wallet, Check, X, Search,
} from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { cotationsAPI, financeAPI, tiersAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { useAuth } from '@/components/layout/AuthProvider';

// ─────────────────────────────────────────────────────────────────────────────
// Ecran « Espace Commercial » : uniquement des registres reels.
//
// Ce qui a ete retire et pourquoi :
//  - les « baremes reels corridors CEMAC » (3 850 000 / 450 000 / 250 000 XAF,
//    TEC 18 %) etaient des nombres inventes dans le composant : le chiffrage
//    s'appuie desormais sur la grille tarifaire persistance (table tarifs,
//    GET/POST /api/v1/finance/tarifs) saisie par l'entreprise ;
//  - l'onglet « Commissions & Objectifs » affichait un CA de 48 500 000 XAF,
//    une commission de 1 455 000 XAF et « 12 dossiers » : aucune table de
//    commission n'existe dans l'ERP, l'onglet a donc supprime ;
//  - « Transmettre le devis » appelait /partner-api/cotation-request avec un
//    payload invalide (titre et description obligatoires) : la creation passe
//    par le vrai registre des devis, cotations_devis.
//
// Teinte : ambre = identite du module « portail-commercial » (modulePalette).
// Les badges d'etat utilisent d'autres couleurs pour ne pas confondre etat et
// module.
// ─────────────────────────────────────────────────────────────────────────────

type Onglet = 'chiffrage' | 'tarifs' | 'devis' | 'clients';

type Tarif = {
  id: number;
  code: string;
  designation: string;
  categorie: string | null;
  unite: string | null;
  prix: number;
  devise: string;
  tva: number;
};

type Client = {
  id: number;
  code: string | null;
  name: string;
  city: string | null;
  phone: string | null;
  email: string | null;
  is_active: boolean | null;
};

type Devis = {
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
};

type Encours = {
  total_facture: number;
  total_paye: number;
  encours: number;
  devise: string;
  nb_factures: number;
};

const STATUTS_DEVIS = ['SOUMIS', 'ACCEPTE', 'REJETE'] as const;

function libelleStatut(s: string | null, t: (fr: string, en: string) => string) {
  if (s === 'ACCEPTE') return t('Accepté', 'Accepted');
  if (s === 'REJETE') return t('Rejeté', 'Rejected');
  if (s === 'SOUMIS') return t('Soumis', 'Submitted');
  return s || '';
}

function badgeStatut(s: string | null) {
  if (s === 'ACCEPTE') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  if (s === 'REJETE') return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
  return 'bg-slate-500/10 text-slate-300 border-slate-500/30';
}

function brute(res: unknown): unknown[] {
  const body = (res ?? {}) as { data?: { items?: unknown[]; data?: unknown[] } | unknown[]; items?: unknown[] };
  const d = body?.data;
  if (Array.isArray(d)) return d;
  if (Array.isArray((d as { items?: unknown[] })?.items)) return (d as { items: unknown[] }).items;
  if (Array.isArray((d as { data?: unknown[] })?.data)) return (d as { data: unknown[] }).data;
  if (Array.isArray(body?.items)) return body.items;
  return [];
}

const FORM_TARIF = { code: '', designation: '', categorie: '', unite: '', prix: '', tva: '' };

export default function PortailCommercialPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const { user } = useAuth();
  const companyId = user?.companyId ?? null;

  const queryClient = useQueryClient();
  const [onglet, setOnglet] = useState<Onglet>('chiffrage');

  // Deep-link depuis la navigation : /portail-commercial?tab=... ouvre l'onglet.
  useEffect(() => {
    const demande = new URLSearchParams(window.location.search).get('tab');
    const allowed: string[] = ['chiffrage', 'tarifs', 'devis', 'clients'];
    if (demande && allowed.includes(demande)) setOnglet(demande as Onglet);
  }, []);

  const fmt = (v: number | null | undefined, decimals = 0) =>
    v === null || v === undefined || Number.isNaN(v)
      ? ''
      : new Intl.NumberFormat(loc, { maximumFractionDigits: decimals }).format(v);

  // ── Données réelles ────────────────────────────────────────────────────────
  const tarifsQuery = useQuery({
    queryKey: ['commercial-tarifs'],
    queryFn: async () => brute(await financeAPI.getTarifs({ limit: 500 })) as Tarif[],
  });

  const clientsQuery = useQuery({
    queryKey: ['commercial-clients'],
    queryFn: async () => brute(await tiersAPI.getClients({ limit: 500 })) as Client[],
  });

  const devisQuery = useQuery({
    queryKey: ['commercial-devis', companyId],
    queryFn: async () => {
      if (companyId === null) throw new Error('no-company');
      return brute(await cotationsAPI.getQuotes(companyId)) as Devis[];
    },
    enabled: companyId !== null,
  });

  const tarifs: Tarif[] = tarifsQuery.data ?? [];
  const clients: Client[] = clientsQuery.data ?? [];
  const devis: Devis[] = devisQuery.data ?? [];

  const refreshAll = () => {
    queryClient.invalidateQueries({ queryKey: ['commercial-tarifs'] });
    queryClient.invalidateQueries({ queryKey: ['commercial-clients'] });
    queryClient.invalidateQueries({ queryKey: ['commercial-devis'] });
  };

  const busy = tarifsQuery.isFetching || clientsQuery.isFetching || devisQuery.isFetching;

  // ── Onglet chiffrage ───────────────────────────────────────────────────────
  const [lignes, setLignes] = useState<Record<number, number>>({});
  const [entete, setEntete] = useState({ reference: '', client_nom: '', origine: '', destination: '', nature_fret: '' });
  const [margePct, setMargePct] = useState('15');

  const choixClient = (id: number) => {
    const c = clients.find((x) => x.id === id);
    if (c) setEntete((e) => ({ ...e, client_nom: c.name }));
  };

  const totalHt = useMemo(
    () =>
      tarifs.reduce((acc, tr) => acc + (lignes[tr.id] ? tr.prix * lignes[tr.id] : 0), 0),
    [tarifs, lignes]
  );
  const totalTva = useMemo(
    () =>
      tarifs.reduce(
        (acc, tr) => acc + (lignes[tr.id] ? (tr.prix * lignes[tr.id] * (tr.tva || 0)) / 100 : 0),
        0
      ),
    [tarifs, lignes]
  );
  const revient = totalHt + totalTva;
  const marge = Number(margePct) || 0;
  const prixVente = revient * (1 + marge / 100);
  const nbLignes = Object.values(lignes).filter((q) => q > 0).length;

  const referenceDejaPrise = devis.some(
    (d) => (d.reference ?? '').toLowerCase() === entete.reference.trim().toLowerCase()
  );

  const creationDevis = useMutation({
    mutationFn: async () => {
      if (companyId === null) throw new Error('no-company');
      const res = await cotationsAPI.createQuote(companyId, {
        reference: entete.reference.trim(),
        client_nom: entete.client_nom.trim(),
        origine: entete.origine.trim(),
        destination: entete.destination.trim(),
        nature_fret: entete.nature_fret.trim(),
        montant_estime_xaf: Math.round(prixVente),
      });
      const created = res?.data as Devis;
      // La marge saisie n'existe qu'en base si on l'écrit : PUT dedicate.
      if (created?.id && marge > 0) {
        await cotationsAPI.updateQuote(companyId, created.id, { marge_nette_pct: marge });
      }
      return created;
    },
    onSuccess: (d) => {
      toast.success(t(`Devis ${d?.reference ?? ''} enregistré.`, `Quote ${d?.reference ?? ''} saved.`));
      queryClient.invalidateQueries({ queryKey: ['commercial-devis'] });
      setLignes({});
      setEntete({ reference: '', client_nom: '', origine: '', destination: '', nature_fret: '' });
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(detail || t("Le devis n'a pas été enregistré.", 'The quote was not saved.'));
    },
  });

  const soumettreChiffrage = (e: React.FormEvent) => {
    e.preventDefault();
    if (nbLignes === 0) {
      toast.error(t('Sélectionnez au moins une ligne tarifaire.', 'Select at least one tariff line.'));
      return;
    }
    if (!entete.reference.trim()) {
      toast.error(t('La référence du devis est obligatoire.', 'The quote reference is required.'));
      return;
    }
    if (referenceDejaPrise) {
      toast.error(t('Cette référence existe déjà.', 'This reference already exists.'));
      return;
    }
    if (!entete.client_nom.trim()) {
      toast.error(t('Indiquez le client.', 'Specify the client.'));
      return;
    }
    creationDevis.mutate();
  };

  // ── Onglet tarifs ──────────────────────────────────────────────────────────
  const [formTarif, setFormTarif] = useState({ ...FORM_TARIF });
  const [afficherFormulaire, setAfficherFormulaire] = useState(false);

  const creationTarif = useMutation({
    mutationFn: async () => {
      const res = await financeAPI.createTarif({
        code: formTarif.code.trim() || undefined,
        designation: formTarif.designation.trim(),
        categorie: formTarif.categorie.trim() || null,
        unite: formTarif.unite.trim() || null,
        prix: Number(formTarif.prix) || 0,
        devise: 'XAF',
        tva: Number(formTarif.tva) || 0,
      });
      return res?.data;
    },
    onSuccess: () => {
      toast.success(t('Tarif ajouté à la grille.', 'Tariff added to the grid.'));
      queryClient.invalidateQueries({ queryKey: ['commercial-tarifs'] });
      setFormTarif({ ...FORM_TARIF });
      setAfficherFormulaire(false);
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(detail || t('Le tarif na pas été enregistré.', 'The tariff was not saved.'));
    },
  });

  const champTarif =
    (k: keyof typeof FORM_TARIF, type = 'text') =>
      (e: React.ChangeEvent<HTMLInputElement>) =>
        setFormTarif((f) => ({ ...f, [k]: e.target.value }));

  // ── Onglet devis : décision ────────────────────────────────────────────────
  const decision = useMutation({
    mutationFn: async ({ id, statut }: { id: number; statut: 'ACCEPTE' | 'REJETE' }) => {
      if (companyId === null) throw new Error('no-company');
      const res = await cotationsAPI.updateQuote(companyId, id, { statut });
      return res?.data as Devis;
    },
    onSuccess: (d) => {
      toast.success(
        d?.statut === 'ACCEPTE'
          ? t(`Devis ${d.reference ?? ''} accepté.`, `Quote ${d.reference ?? ''} accepted.`)
          : t(`Devis ${d?.reference ?? ''} rejeté.`, `Quote ${d?.reference ?? ''} rejected.`)
      );
      queryClient.invalidateQueries({ queryKey: ['commercial-devis'] });
    },
    onError: () => toast.error(t("La décision n'a pas été enregistrée.", 'The decision was not saved.')),
  });

  const [filtreDevis, setFiltreDevis] = useState('all');
  const devisFiltres = devis.filter((d) => filtreDevis === 'all' || (d.statut ?? '') === filtreDevis);

  // ── Onglet clients : encours à la demande ──────────────────────────────────
  const [encours, setEncours] = useState<Record<number, Encours | 'chargement' | 'erreur'>>({});

  const chargerEncours = useCallback(async (clientId: number) => {
    setEncours((prev) => ({ ...prev, [clientId]: 'chargement' }));
    try {
      const res = await financeAPI.getEncours(clientId);
      setEncours((prev) => ({ ...prev, [clientId]: (res?.data ?? res) as Encours }));
    } catch {
      setEncours((prev) => ({ ...prev, [clientId]: 'erreur' }));
    }
  }, []);

  const [rechercheClient, setRechercheClient] = useState('');
  const clientsFiltres = clients.filter((c) =>
    !rechercheClient.trim()
      ? true
      : `${c.name} ${c.code ?? ''} ${c.city ?? ''}`.toLowerCase().includes(rechercheClient.toLowerCase())
  );

  const onglets: { key: Onglet; label: string; icon: typeof Calculator; count?: number }[] = [
    { key: 'chiffrage', label: t('Chiffrage', 'Quoting'), icon: Calculator },
    { key: 'tarifs', label: t('Grille tarifaire', 'Tariff grid'), icon: Tags, count: tarifs.length },
    { key: 'devis', label: t('Devis émis', 'Quotes issued'), icon: FileText, count: devis.length },
    { key: 'clients', label: t('Portefeuille clients', 'Client portfolio'), icon: Users, count: clients.length },
  ];

  const attenteDecision = devis.filter((d) => d.statut === 'SOUMIS').length;

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto animate-in fade-in duration-500">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="min-w-0 space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-bold uppercase tracking-wider">
            <TrendingUp className="w-3.5 h-3.5 shrink-0" />
            {t('Espace commercial', 'Sales space')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight break-words">
            {t('Chiffrage, grille tarifaire et devis', 'Quoting, tariff grid and quotes')}
          </h1>
          <p className="text-sm text-slate-400">
            {t(
              `${tarifs.length} tarif(s) dans la grille, ${devis.length} devis enregistré(s)${attenteDecision > 0 ? `, ${attenteDecision} en attente de décision` : ''}.`,
              `${tarifs.length} tariff line(s), ${devis.length} quote(s) on record${attenteDecision > 0 ? `, ${attenteDecision} awaiting a decision` : ''}.`
            )}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3 shrink-0">
          <Link
            href="/cotations"
            className="inline-flex min-h-[44px] items-center gap-2 px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 text-xs font-bold text-slate-200 hover:bg-slate-700"
          >
            <FileText className="w-4 h-4 text-amber-400" />
            {t('Registre complet', 'Full register')}
          </Link>
          <button
            type="button"
            onClick={refreshAll}
            disabled={busy}
            className="inline-flex min-h-[44px] items-center gap-2 px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 transition-colors disabled:opacity-60"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${busy ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex overflow-x-auto gap-2 p-1.5 bg-slate-900 rounded-2xl border border-slate-800">
        {onglets.map((o) => {
          const Icon = o.icon;
          const actif = onglet === o.key;
          return (
            <button
              key={o.key}
              type="button"
              onClick={() => setOnglet(o.key)}
              className={`flex min-h-[44px] items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-colors ${actif
                  ? 'bg-amber-500/15 text-amber-300 border border-amber-500/40'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-white/5 border border-transparent'
                }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{o.label}</span>
              {o.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-mono ${actif ? 'bg-amber-500/20 text-amber-200' : 'bg-slate-800 text-slate-400'}`}>
                  {o.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* ── Chiffrage ─────────────────────────────────────────────────────── */}
      {onglet === 'chiffrage' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-5">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 pb-3 border-b border-slate-800">
              <Tags className="w-5 h-5 text-amber-400 shrink-0" />
              {t('Lignes tarifaires de la grille', 'Tariff lines from the grid')}
            </h2>

            {tarifsQuery.isLoading ? (
              <p className="text-sm text-slate-400">{t('Chargement de la grille…', 'Loading the grid…')}</p>
            ) : tarifsQuery.isError ? (
              <p className="text-sm text-rose-400">{t('Grille tarifaire illisible.', 'The tariff grid could not be read.')}</p>
            ) : tarifs.length === 0 ? (
              <div className="space-y-3">
                <p className="text-sm text-slate-400">
                  {t(
                    "Aucun tarif n'est enregistré : l'ERP n'invente aucun barème. Saisissez votre grille pour chiffrer une opération.",
                    'No tariff on record: the ERP invents no rate card. Enter your grid to price an operation.'
                  )}
                </p>
                <button
                  type="button"
                  onClick={() => { setOnglet('tarifs'); setAfficherFormulaire(true); }}
                  className="inline-flex min-h-[44px] items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-semibold"
                >
                  <Plus className="w-4 h-4" />
                  {t('Créer un tarif', 'Create a tariff')}
                </button>
              </div>
            ) : (
              <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
                {tarifs.map((tr) => {
                  const qte = lignes[tr.id] ?? 0;
                  return (
                    <div key={tr.id} className="flex items-center gap-3 p-3 rounded-xl bg-slate-950 border border-slate-800">
                      <input
                        type="checkbox"
                        checked={qte > 0}
                        onChange={(e) =>
                          setLignes((l) => {
                            const next = { ...l };
                            if (e.target.checked) next[tr.id] = 1;
                            else delete next[tr.id];
                            return next;
                          })
                        }
                        aria-label={tr.designation}
                        className="w-4 h-4 shrink-0 accent-amber-500"
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold text-slate-100 truncate" title={tr.designation}>
                          {tr.designation}
                        </p>
                        <p className="text-[11px] text-slate-500 font-mono truncate">
                          {tr.code} · {fmt(tr.prix)} {tr.devise}
                          {tr.unite ? ` / ${tr.unite}` : ''}
                          {tr.tva ? ` · TVA ${fmt(tr.tva, 2)} %` : ''}
                        </p>
                      </div>
                      {qte > 0 && (
                        <input
                          type="number"
                          min={0}
                          value={qte}
                          onChange={(e) => setLignes((l) => ({ ...l, [tr.id]: Math.max(0, Number(e.target.value) || 0) }))}
                          aria-label={t('Quantité', 'Quantity')}
                          className="w-20 min-h-[40px] px-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-slate-100 font-mono focus:outline-none focus:border-amber-500"
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            <div className="pt-3 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block text-slate-400 font-bold uppercase mb-1">{t('Marge commerciale', 'Sales margin')}</label>
                <div className="relative">
                  <input
                    type="number"
                    value={margePct}
                    onChange={(e) => setMargePct(e.target.value)}
                    aria-label={t('Marge en pourcentage', 'Margin percentage')}
                    className="w-full min-h-[44px] px-3 pr-8 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono focus:outline-none focus:border-amber-500"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 font-mono">%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Totaux + en-tete du devis */}
          <form onSubmit={soumettreChiffrage} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-4 flex flex-col">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 pb-3 border-b border-slate-800">
              <Calculator className="w-5 h-5 text-amber-400 shrink-0" />
              {t('Décomposition et envoi', 'Breakdown and issue')}
            </h2>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between text-slate-400">
                <span>{t('Sous-total hors taxes', 'Subtotal excl. tax')}</span>
                <span className="font-mono text-slate-100">{fmt(totalHt)} XAF</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>{t('TVA de la grille', 'Grid VAT')}</span>
                <span className="font-mono text-slate-100">{fmt(totalTva)} XAF</span>
              </div>
              <div className="flex justify-between text-slate-400 border-t border-slate-800 pt-2">
                <span>{t('Coût de revient', 'Cost price')}</span>
                <span className="font-mono text-slate-100">{fmt(revient)} XAF</span>
              </div>
              <div className="flex justify-between text-emerald-400">
                <span>{t(`Marge (${fmt(marge, 1)} %)`, `Margin (${fmt(marge, 1)} %)`)</span>
                <span className="font-mono">+{fmt(revient * marge / 100)} XAF</span>
              </div>
              <div className="flex items-baseline justify-between pt-2 border-t border-amber-500/30">
                <span className="text-xs font-bold text-slate-300 uppercase">
                  {t('Prix proposé client', 'Price quoted to client')}
                </span>
                <span className="text-xl sm:text-2xl font-mono font-black text-amber-400 break-words">
                  {fmt(prixVente)} XAF
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">{t('Client', 'Client')}</label>
                <select
                  value=""
                  onChange={(e) => e.target.value && choixClient(Number(e.target.value))}
                  aria-label={t('Sélectionner un client', 'Select a client')}
                  className="w-full min-h-[44px] px-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                >
                  <option value="">{t(' Choisir dans le portefeuille ', ' Pick from the portfolio ')}</option>
                  {clients.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}{c.code ? ` (${c.code})` : ''}</option>
                  ))}
                </select>
              </div>
              {([
                ['reference', t('Référence devis', 'Quote reference')],
                ['client_nom', t('Nom du client', 'Client name')],
                ['origine', t('Origine', 'Origin')],
                ['destination', t('Destination', 'Destination')],
                ['nature_fret', t('Nature du fret', 'Cargo nature')],
              ] as [keyof typeof entete, string][]).map(([k, label]) => (
                <div key={k} className={k === 'reference' || k === 'nature_fret' ? 'sm:col-span-2' : ''}>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">{label}</label>
                  <input
                    type="text"
                    value={entete[k]}
                    onChange={(e) => setEntete((f) => ({ ...f, [k]: e.target.value }))}
                    className={`w-full min-h-[44px] px-3 rounded-xl bg-slate-950 border text-sm text-slate-100 focus:outline-none focus:border-amber-500 ${k === 'reference' && referenceDejaPrise ? 'border-rose-500' : 'border-slate-800'
                      }`}
                  />
                  {k === 'reference' && referenceDejaPrise && (
                    <p className="text-[11px] text-rose-400 mt-1">{t('Référence déjà utilisée.', 'Reference already used.')}</p>
                  )}
                </div>
              ))}
            </div>

            <button
              type="submit"
              disabled={creationDevis.isPending || companyId === null}
              className="mt-auto w-full min-h-[44px] rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 text-xs font-black uppercase tracking-wider transition-colors disabled:opacity-60"
            >
              {creationDevis.isPending
                ? t('Enregistrement…', 'Saving…')
                : t('Enregistrer le devis', 'Save the quote')}
            </button>
            {companyId === null && (
              <p className="text-[11px] text-amber-400">
                {t("Aucune société sur le compte : devis non enregistrable.", 'No company on this account: quotes cannot be saved.')}
              </p>
            )}
          </form>
        </div>
      )}

      {/* ── Grille tarifaire ──────────────────────────────────────────────── */}
      {onglet === 'tarifs' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h2 className="text-base font-bold text-slate-100">
              {t('Grille tarifaire de la société', 'Company tariff grid')}
              <span className="ml-2 text-xs font-mono text-slate-400">({tarifs.length})</span>
            </h2>
            <button
              type="button"
              onClick={() => setAfficherFormulaire((v) => !v)}
              className="inline-flex min-h-[44px] items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-semibold"
            >
              {afficherFormulaire ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
              {afficherFormulaire ? t('Fermer', 'Close') : t('Nouveau tarif', 'New tariff')}
            </button>
          </div>

          {afficherFormulaire && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (!formTarif.designation.trim()) {
                  toast.error(t('La désignation est obligatoire.', 'The description is required.'));
                  return;
                }
                creationTarif.mutate();
              }}
              className="p-4 sm:p-6 border-b border-slate-800 bg-slate-950 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"
            >
              {([
                ['designation', t('Désignation *', 'Description *')],
                ['code', t('Code (auto si vide)', 'Code (auto if blank)')],
                ['categorie', t('Catégorie', 'Category')],
                ['unite', t('Unité (trajet, kg, TEU…)', 'Unit (trip, kg, TEU…)')],
                ['prix', t('Prix unitaire (XAF)', 'Unit price (XAF)')],
                ['tva', t('TVA (%)', 'VAT (%)')],
              ] as [keyof typeof FORM_TARIF, string][]).map(([k, label]) => (
                <div key={k}>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">{label}</label>
                  <input
                    type={k === 'prix' || k === 'tva' ? 'number' : 'text'}
                    step={k === 'tva' ? '0.01' : undefined}
                    value={formTarif[k]}
                    onChange={champTarif(k)}
                    className="w-full min-h-[44px] px-3 rounded-xl bg-slate-900 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
              ))}
              <div className="sm:col-span-2 lg:col-span-3">
                <button
                  type="submit"
                  disabled={creationTarif.isPending}
                  className="w-full sm:w-auto min-h-[44px] px-6 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 text-xs font-black uppercase tracking-wider disabled:opacity-60"
                >
                  {creationTarif.isPending ? t('Enregistrement…', 'Saving…') : t('Ajouter à la grille', 'Add to the grid')}
                </button>
              </div>
            </form>
          )}

          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">{t('Code', 'Code')}</th>
                  <th className="px-6 py-4">{t('Désignation', 'Description')}</th>
                  <th className="px-6 py-4">{t('Catégorie', 'Category')}</th>
                  <th className="px-6 py-4">{t('Unité', 'Unit')}</th>
                  <th className="px-6 py-4 text-right whitespace-nowrap">{t('Prix', 'Price')}</th>
                  <th className="px-6 py-4 text-right whitespace-nowrap">{t('TVA', 'VAT')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {tarifsQuery.isLoading ? (
                  <tr><td colSpan={6} className="p-12 text-center text-slate-400">{t('Chargement…', 'Loading…')}</td></tr>
                ) : tarifs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-12 text-center text-slate-500 text-sm">
                      {t('Grille vide : aucun tarif saisi pour la société.', 'Empty grid: no tariff entered for this company.')}
                    </td>
                  </tr>
                ) : (
                  tarifs.map((tr) => (
                    <tr key={tr.id} className="hover:bg-slate-800/40">
                      <td className="px-6 py-4 font-mono text-xs text-amber-400 whitespace-nowrap">{tr.code}</td>
                      <td className="px-6 py-4 max-w-[280px]">
                        <span className="block truncate" title={tr.designation}>{tr.designation}</span>
                      </td>
                      <td className="px-6 py-4 text-slate-400">{tr.categorie || ''}</td>
                      <td className="px-6 py-4 text-slate-400">{tr.unite || ''}</td>
                      <td className="px-6 py-4 text-right font-mono whitespace-nowrap">{fmt(tr.prix)} {tr.devise}</td>
                      <td className="px-6 py-4 text-right font-mono whitespace-nowrap">{tr.tva ? `${fmt(tr.tva, 2)} %` : ''}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Devis émis ────────────────────────────────────────────────────── */}
      {onglet === 'devis' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h2 className="text-base font-bold text-slate-100">
              {t('Devis de la société', 'Company quotes')}
              <span className="ml-2 text-xs font-mono text-slate-400">({devisFiltres.length})</span>
            </h2>
            <select
              value={filtreDevis}
              onChange={(e) => setFiltreDevis(e.target.value)}
              aria-label={t('Filtrer par statut', 'Filter by status')}
              className="w-full sm:w-auto min-h-[44px] px-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="all">{t('Tous les statuts', 'All statuses')}</option>
              {STATUTS_DEVIS.map((s) => (
                <option key={s} value={s}>{libelleStatut(s, t)}</option>
              ))}
            </select>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[880px] text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">{t('Référence / Client', 'Reference / Client')}</th>
                  <th className="px-6 py-4">{t('Tracé', 'Route')}</th>
                  <th className="px-6 py-4">{t('Fret', 'Cargo')}</th>
                  <th className="px-6 py-4 text-right whitespace-nowrap">{t('Montant', 'Amount')}</th>
                  <th className="px-6 py-4">{t('Statut', 'Status')}</th>
                  <th className="px-6 py-4 text-right">{t('Décision', 'Decision')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {devisQuery.isLoading ? (
                  <tr><td colSpan={6} className="p-12 text-center text-slate-400">{t('Chargement…', 'Loading…')}</td></tr>
                ) : devisFiltres.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-12 text-center text-slate-500 text-sm">
                      {t('Aucun devis pour ce filtre.', 'No quote matches this filter.')}
                    </td>
                  </tr>
                ) : (
                  devisFiltres.map((d) => (
                    <tr key={d.id} className="hover:bg-slate-800/40">
                      <td className="px-6 py-4">
                        <p className="font-mono text-xs text-amber-400">{d.reference || `#${d.id}`}</p>
                        <p className="text-slate-200 max-w-[220px] truncate" title={d.client_nom}>{d.client_nom}</p>
                      </td>
                      <td className="px-6 py-4 text-slate-400 max-w-[220px]">
                        <span className="block truncate" title={`${d.origine} → ${d.destination}`}>
                          {d.origine} → {d.destination}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-400 max-w-[160px]">
                        <span className="block truncate" title={d.nature_fret}>{d.nature_fret}</span>
                      </td>
                      <td className="px-6 py-4 text-right font-mono whitespace-nowrap">
                        {fmt(d.montant_estime_xaf)} XAF
                        {d.marge_nette_pct ? (
                          <span className="block text-[11px] text-slate-500">
                            {t(`marge ${fmt(d.marge_nette_pct, 1)} %`, `margin ${fmt(d.marge_nette_pct, 1)} %`)}
                          </span>
                        ) : null}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-block px-2.5 py-1 rounded-full border text-[11px] font-bold ${badgeStatut(d.statut)}`}>
                          {libelleStatut(d.statut, t)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {d.statut === 'SOUMIS' ? (
                          <div className="flex justify-end gap-2">
                            <button
                              type="button"
                              onClick={() => decision.mutate({ id: d.id, statut: 'ACCEPTE' })}
                              disabled={decision.isPending}
                              aria-label={t('Accepter', 'Accept')}
                              className="min-h-[40px] px-3 inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold disabled:opacity-50"
                            >
                              <Check className="w-3.5 h-3.5" />
                              {t('Accepter', 'Accept')}
                            </button>
                            <button
                              type="button"
                              onClick={() => decision.mutate({ id: d.id, statut: 'REJETE' })}
                              disabled={decision.isPending}
                              aria-label={t('Rejeter', 'Reject')}
                              className="min-h-[40px] px-3 inline-flex items-center gap-1.5 rounded-lg border border-rose-500/40 text-rose-400 hover:bg-rose-500/10 text-xs font-bold disabled:opacity-50"
                            >
                              <X className="w-3.5 h-3.5" />
                              {t('Rejeter', 'Reject')}
                            </button>
                          </div>
                        ) : (
                          <p className="text-right text-[11px] text-slate-500">
                            {t('Décidée', 'Decided')}
                          </p>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Portefeuille clients ──────────────────────────────────────────── */}
      {onglet === 'clients' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h2 className="text-base font-bold text-slate-100">
              {t('Comptes clients', 'Client accounts')}
              <span className="ml-2 text-xs font-mono text-slate-400">({clientsFiltres.length})</span>
            </h2>
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-3.5 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={rechercheClient}
                onChange={(e) => setRechercheClient(e.target.value)}
                placeholder={t('Nom, code, ville…', 'Name, code, city…')}
                aria-label={t('Rechercher un client', 'Search a client')}
                className="w-full min-h-[44px] pl-9 pr-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>

          {clientsQuery.isLoading ? (
            <p className="p-12 text-center text-slate-400 text-sm">{t('Chargement…', 'Loading…')}</p>
          ) : clientsFiltres.length === 0 ? (
            <p className="p-12 text-center text-slate-500 text-sm">
              {t('Aucun client dans le registre des tiers.', 'No client in the third-party register.')}
            </p>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {clientsFiltres.map((c) => {
                const info = encours[c.id];
                return (
                  <div key={c.id} className="p-4 sm:p-5">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-bold text-slate-100 break-words">{c.name}</p>
                        <p className="text-[11px] text-slate-500 font-mono">
                          {c.code || `#${c.id}`} · {c.city || ''} · {c.phone || ''} · {c.email || ''}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className={`px-2.5 py-1 rounded-full border text-[11px] font-bold ${c.is_active
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : 'bg-slate-500/10 text-slate-400 border-slate-500/30'
                          }`}>
                          {c.is_active ? t('Actif', 'Active') : t('Inactif', 'Inactive')}
                        </span>
                        <button
                          type="button"
                          onClick={() => chargerEncours(c.id)}
                          disabled={info === 'chargement'}
                          className="inline-flex min-h-[40px] items-center gap-1.5 px-3 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 disabled:opacity-60"
                        >
                          <Wallet className="w-3.5 h-3.5 text-amber-400" />
                          {t('Encours', 'Balance')}
                        </button>
                      </div>
                    </div>
                    {info && info !== 'chargement' && info !== 'erreur' && (
                      <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                        {([
                          { label: t('Facturé', 'Invoiced'), value: info.total_facture, devise: true },
                          { label: t('Encaissé', 'Collected'), value: info.total_paye, devise: true },
                          { label: t('Encours', 'Outstanding'), value: info.encours, devise: true },
                          { label: t('Factures', 'Invoices'), value: info.nb_factures, devise: false },
                        ]).map(({ label, value, devise }) => (
                          <div key={label} className="rounded-xl bg-slate-950 border border-slate-800 px-3 py-2">
                            <p className="text-slate-500 uppercase font-bold text-[10px]">{label}</p>
                            <p className="font-mono text-slate-100 whitespace-nowrap">
                              {fmt(value)}{devise ? ` ${info.devise}` : ''}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                    {info === 'erreur' && (
                      <p className="mt-3 text-xs text-rose-400">
                        {t('Encours indisponible pour ce compte.', 'Balance unavailable for this account.')}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

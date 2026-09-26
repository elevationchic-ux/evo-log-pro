'use client';

/**
 * K-Finance — Gestion des factures.
 *
 * Toutes les lignes viennent de GET /api/finance/factures (les deux tables de
 * factures de la base, `factures` d'exploitation et `factures_ohada`, fusionnées
 * côté serveur et taggées `source`). Les montants « restant dus » sont déduits
 * des colonnes réellement portées par la base, jamais d'un pourcentage estimé :
 * - facture OHADA : `solde_restant` / `reglement_partiel` ;
 * - facture d'exploitation : cumuls des `paiements` confirmés (GET /encaissements).
 * Aucune comparaison « vs mois précédent » n'est affichée : la base ne conserve
 * pas d'historique de clôture, ce serait une valeur inventée.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Receipt, RefreshCw, Download, Search, Plus, FileText, Banknote,
  AlertTriangle, CheckCircle2, XCircle, ChevronLeft, ChevronRight, Loader2,
} from 'lucide-react';
import { toast } from 'sonner';
import { financeAPI, tiersAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { DataEmptyState, DataErrorState, DataLoadingState } from '@/components/shared/StatePanels';
import { classifyApiError, type ApiErrorInfo } from '@/hooks/useApi';

interface FactureRow {
  id: number;
  source: 'exploitation' | 'ohada';
  numero_facture: string;
  client_id: number | null;
  client_nom: string | null;
  type_facture: string | null;
  date_emission: string | null;
  date_echeance: string | null;
  montant_ht: number;
  montant_tva: number;
  montant_ttc: number;
  solde_restant: number | null;
  reglement_partiel: number | null;
  statut: string;
}

interface EncaissementRow {
  id: number;
  facture_id: number | null;
  montant: number;
  date_paiement: string | null;
  mode_paiement: string | null;
  reference: string | null;
  statut: string;
}

interface ClientOption {
  id: number;
  name: string;
  code?: string;
}

type Famille = 'brouillon' | 'ouverte' | 'payee' | 'annulee';

const STATUTS_PAR_FAMILLE: Record<Famille, string[]> = {
  // Les deux tables n'orthographient pas le règlement partiel de la même façon.
  brouillon: ['brouillon', 'draft'],
  payee: ['payee', 'reglee', 'paid'],
  annulee: ['annulee', 'annule', 'cancellee'],
  ouverte: ['emise', 'envoyee', 'retard', 'en_attente', 'payee_partiel', 'payee_partiellement'],
};

function familleOf(statut: string | null | undefined): Famille {
  const s = String(statut || '').toLowerCase();
  for (const [fam, valeurs] of Object.entries(STATUTS_PAR_FAMILLE)) {
    if (valeurs.includes(s)) return fam as Famille;
  }
  return 'ouverte';
}

const TVA_DEFAUT = 19.25; // Cameroun
const PAR_PAGE = 20;

const PERIODES = [
  { key: 'all', jours: null },
  { key: '30', jours: 30 },
  { key: '90', jours: 90 },
  { key: '365', jours: 365 },
] as const;

type PeriodeKey = (typeof PERIODES)[number]['key'];

function isoAYMD(d: Date) {
  return d.toISOString().slice(0, 10);
}

export default function KFinanceBillingPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = useCallback((fr: string, en: string) => (lang === 'en' ? en : fr), [lang]);
  const locale = lang === 'en' ? 'en-GB' : 'fr-FR';

  const [factures, setFactures] = useState<FactureRow[]>([]);
  const [encaissements, setEncaissements] = useState<EncaissementRow[]>([]);
  const [clients, setClients] = useState<ClientOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiErrorInfo | null>(null);

  const [search, setSearch] = useState('');
  const [famille, setFamille] = useState<'all' | Famille>('all');
  const [periode, setPeriode] = useState<PeriodeKey>('all');
  const [page, setPage] = useState(1);

  const [showCreate, setShowCreate] = useState(false);
  const [showPay, setShowPay] = useState<FactureRow | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [f, e] = await Promise.all([
        financeAPI.getFactures(),
        financeAPI.getEncaissements(),
      ]);
      setFactures(Array.isArray(f.data) ? (f.data as FactureRow[]) : []);
      setEncaissements(Array.isArray(e.data) ? (e.data as EncaissementRow[]) : []);
    } catch (err) {
      setError(classifyApiError(err));
      setFactures([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    // La liste des clients n'est chargee qu'une fois : elle ne sert qu'aux
    // libelles et au formulaire de creation.
    tiersAPI
      .getClients({ limit: 500 })
      .then((res) => {
        const rows = Array.isArray(res.data) ? res.data : [];
        setClients(
          rows.map((r: { id: number; name?: string; code?: string }) => ({
            id: r.id,
            name: r.name || `#${r.id}`,
            code: r.code,
          })),
        );
      })
      .catch(() => setClients([]));
  }, [load]);

  // Echap ferme le panneau ouvert le plus proche, comme le reste du chrome.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return;
      if (showPay) setShowPay(null);
      else if (showCreate) setShowCreate(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [showPay, showCreate]);

  const money = useMemo(() => new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }), [locale]);
  const dateFmt = useMemo(() => new Intl.DateTimeFormat(locale, { day: '2-digit', month: 'short', year: 'numeric' }), [locale]);

  const fmtDate = useCallback(
    (iso: string | null) => (iso ? dateFmt.format(new Date(iso)) : '—'),
    [dateFmt],
  );

  /** Total déjà encaissé par facture d'exploitation (paiements confirmés). */
  const payeParFacture = useMemo(() => {
    const map = new Map<number, number>();
    for (const e of encaissements) {
      if (!e.facture_id) continue;
      if (String(e.statut || '').toLowerCase() !== 'confirme') continue;
      map.set(e.facture_id, (map.get(e.facture_id) || 0) + (e.montant || 0));
    }
    return map;
  }, [encaissements]);

  /** Solde dû calculé depuis les seules données persistées. */
  const resteDu = useCallback(
    (f: FactureRow): number | null => {
      if (f.solde_restant !== null && f.solde_restant !== undefined) return Math.max(0, f.solde_restant);
      if (f.reglement_partiel !== null && f.reglement_partiel !== undefined) {
        return Math.max(0, (f.montant_ttc || 0) - f.reglement_partiel);
      }
      if (f.source === 'exploitation') {
        const paye = payeParFacture.get(f.id);
        if (paye !== undefined) return Math.max(0, (f.montant_ttc || 0) - paye);
      }
      // Ni solde connu ni paiement enregistré : on ne peut pas affirmer qu'il
      // reste quelque chose, on laisse la cellule vide plutôt que deviner.
      return null;
    },
    [payeParFacture],
  );

  const today = useMemo(() => isoAYMD(new Date()), []);

  const isEchue = useCallback(
    (f: FactureRow) => {
      const fam = familleOf(f.statut);
      if (fam === 'payee' || fam === 'annulee' || fam === 'brouillon') return false;
      return !!f.date_echeance && f.date_echeance < today;
    },
    [today],
  );

  const kpis = useMemo(() => {
    let enAttente = 0;
    let nbARecouvrer = 0;
    let echueMontant = 0;
    let echueCount = 0;
    let brouillons = 0;
    let emises = 0;
    for (const f of factures) {
      const fam = familleOf(f.statut);
      if (fam === 'brouillon') brouillons += 1;
      else emises += 1;
      if (fam === 'annulee') continue;
      const reste = fam === 'payee' ? 0 : resteDu(f) ?? f.montant_ttc ?? 0;
      if (fam === 'ouverte' || fam === 'brouillon') {
        if (fam === 'ouverte') {
          enAttente += reste;
          nbARecouvrer += 1;
          if (isEchue(f)) {
            echueMontant += reste;
            echueCount += 1;
          }
        }
      }
    }
    const moisCourant = today.slice(0, 7);
    let encaisseMois = 0;
    let nbEncaissements = 0;
    for (const e of encaissements) {
      if (!e.date_paiement || e.date_paiement.slice(0, 7) !== moisCourant) continue;
      if (String(e.statut || '').toLowerCase() === 'annule') continue;
      encaisseMois += e.montant || 0;
      nbEncaissements += 1;
    }
    return { enAttente, nbARecouvrer, echueMontant, echueCount, brouillons, emises, encaisseMois, nbEncaissements };
  }, [factures, encaissements, resteDu, isEchue, today]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const bornes = PERIODES.find((p) => p.key === periode)?.jours;
    const plancher = bornes ? isoAYMD(new Date(Date.now() - bornes * 86400000)) : null;
    return factures.filter((f) => {
      if (famille !== 'all') {
        const fam = familleOf(f.statut);
        if (fam !== famille) return false;
      }
      if (plancher && (!f.date_emission || f.date_emission < plancher)) return false;
      if (!q) return true;
      return (
        (f.numero_facture || '').toLowerCase().includes(q) ||
        (f.client_nom || '').toLowerCase().includes(q) ||
        String(f.client_id || '').includes(q)
      );
    });
  }, [factures, search, famille, periode]);

  useEffect(() => {
    setPage(1);
  }, [search, famille, periode]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAR_PAGE));
  const pageSafe = Math.min(page, totalPages);
  const visible = useMemo(
    () => filtered.slice((pageSafe - 1) * PAR_PAGE, pageSafe * PAR_PAGE),
    [filtered, pageSafe],
  );

  const nomClient = useCallback(
    (f: FactureRow) => f.client_nom || clients.find((c) => c.id === f.client_id)?.name || null,
    [clients],
  );

  const exportCsv = useCallback(() => {
    if (!filtered.length) return;
    const entetes = [
      t('Numéro', 'Number'), t('Client', 'Client'), t('Émission', 'Issue date'),
      t('Échéance', 'Due date'), t('HT', 'Net'), t('TVA', 'VAT'), t('TTC', 'Gross'),
      t('Reste dû', 'Balance due'), t('Statut', 'Status'), t('Origine', 'Source'),
    ];
    const lignes = filtered.map((f) => {
      const reste = resteDu(f);
      return [
        f.numero_facture, nomClient(f) || '', f.date_emission || '', f.date_echeance || '',
        f.montant_ht, f.montant_tva, f.montant_ttc, reste === null ? '' : reste,
        f.statut, f.source,
      ];
    });
    const csv = [entetes, ...lignes]
      .map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(';'))
      .join('\n');
    const url = URL.createObjectURL(new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `factures-${today}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(t(
      `${filtered.length} facture(s) exportée(s) depuis la liste affichée.`,
      `${filtered.length} invoice(s) exported from the displayed list.`,
    ));
  }, [filtered, resteDu, nomClient, t, lang, today]);

  const telechargerPdf = useCallback(async (f: FactureRow) => {
    setBusyId(f.id);
    try {
      const res = await financeAPI.getFacturePdf(f.id);
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `facture-${f.numero_facture}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      const info = classifyApiError(err);
      toast.error(info.message || t('Génération du PDF impossible.', 'Unable to generate the PDF.'));
    } finally {
      setBusyId(null);
    }
  }, [t, lang]);

  const changerStatut = useCallback(async (f: FactureRow, statut: string) => {
    setBusyId(f.id);
    try {
      await financeAPI.updateFacture(f.id, { statut }, f.source);
      toast.success(t(`Facture ${f.numero_facture} : statut « ${statut} » enregistré.`, `Invoice ${f.numero_facture}: status "${statut}" saved.`));
      setFactures((prev) => prev.map((x) => (x.id === f.id && x.source === f.source ? { ...x, statut } : x)));
    } catch (err) {
      const info = classifyApiError(err);
      toast.error(info.message || t('Enregistrement refusé par le serveur.', 'The server rejected the update.'));
    } finally {
      setBusyId(null);
    }
  }, [t, lang]);

  const statutsDisponibles = useMemo(() => {
    const vus = new Set(factures.map((f) => String(f.statut || '').toLowerCase()));
    return Array.from(vus).filter(Boolean).sort();
  }, [factures]);

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* En-tête */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3 min-w-0">
          <div className="p-2.5 bg-emerald-500/10 rounded-xl text-emerald-400 shrink-0">
            <Receipt className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              {t('Gestion des factures', 'Invoice management')}
            </h1>
            <p className="text-sm text-on-surface-variant">
              {t('Suivi des émissions et des encaissements enregistrés.', 'Tracking of issued invoices and recorded payments.')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={load}
            disabled={loading}
            aria-label={t('Recharger', 'Reload')}
            className="p-2.5 min-h-11 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            type="button"
            onClick={exportCsv}
            disabled={!filtered.length}
            className="flex items-center gap-1.5 px-4 py-2 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface hover:bg-surface-container disabled:opacity-50"
          >
            <Download className="w-4 h-4" /> {t('Exporter', 'Export')}
          </button>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-1.5 px-4 py-2 min-h-11 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white"
          >
            <Plus className="w-4 h-4" /> {t('Créer une facture', 'Create invoice')}
          </button>
        </div>
      </div>

      {/* KPI agrégés depuis les lignes réelles */}
      {!loading && !error && factures.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
          <KpiCard
            icon={Banknote}
            label={t('Reste à recouvrer', 'Outstanding balance')}
            value={`${money.format(Math.round(kpis.enAttente))} XAF`}
            hint={t(`${kpis.nbARecouvrer} facture(s) ouverte(s)`, `${kpis.nbARecouvrer} open invoice(s)`)}
          />
          <KpiCard
            icon={AlertTriangle}
            label={t('Échues', 'Overdue')}
            value={`${money.format(Math.round(kpis.echueMontant))} XAF`}
            hint={t(`${kpis.echueCount} facture(s) passée(s) d'échéance`, `${kpis.echueCount} invoice(s) past due date`)}
            tone={kpis.echueCount ? 'danger' : 'default'}
          />
          <KpiCard
            icon={CheckCircle2}
            label={t('Encaissé ce mois', 'Collected this month')}
            value={`${money.format(Math.round(kpis.encaisseMois))} XAF`}
            hint={t(`${kpis.nbEncaissements} règlement(s) confirmé(s)`, `${kpis.nbEncaissements} confirmed payment(s)`)}
          />
          <KpiCard
            icon={FileText}
            label={t('Factures émises', 'Invoices issued')}
            value={String(kpis.emises)}
            hint={t(`${kpis.brouillons} brouillon(s) non émis`, `${kpis.brouillons} unissued draft(s)`)}
          />
        </div>
      )}

      {/* Filtres */}
      {!loading && !error && factures.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="relative sm:col-span-2">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t('Rechercher un numéro ou un client…', 'Search a number or a client…')}
              aria-label={t('Rechercher une facture', 'Search an invoice')}
              className="w-full pl-9 pr-4 py-2.5 min-h-11 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-emerald-500"
            />
          </div>
          <label className="flex flex-col gap-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Statut', 'Status')}
            </span>
            <select
              value={famille}
              onChange={(e) => setFamille(e.target.value as 'all' | Famille)}
              className="px-3 py-2 min-h-11 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-emerald-500"
            >
              <option value="all">{t('Tous', 'All')}</option>
              <option value="ouverte">{t('Ouvertes', 'Open')}</option>
              <option value="brouillon">{t('Brouillons', 'Drafts')}</option>
              <option value="payee">{t('Payées', 'Paid')}</option>
              <option value="annulee">{t('Annulées', 'Cancelled')}</option>
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Période d''émission', 'Issue period')}
            </span>
            <select
              value={periode}
              onChange={(e) => setPeriode(e.target.value as PeriodeKey)}
              className="px-3 py-2 min-h-11 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-emerald-500"
            >
              <option value="all">{t('Tout l''historique', 'Full history')}</option>
              <option value="30">{t('30 derniers jours', 'Last 30 days')}</option>
              <option value="90">{t('90 derniers jours', 'Last 90 days')}</option>
              <option value="365">{t('12 derniers mois', 'Last 12 months')}</option>
            </select>
          </label>
        </div>
      )}

      {/* Liste */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-6">
            <DataLoadingState rows={6} />
          </div>
        ) : error ? (
          <div className="p-6">
            <DataErrorState error={error} onRetry={load} />
          </div>
        ) : factures.length === 0 ? (
          <DataEmptyState
            title={t('Aucune facture en base', 'No invoice in the database')}
            description={t(
              'Cet écran lit les factures réellement enregistrées (exploitation et OHADA). Aucune n existe encore.',
              'This screen reads invoices actually stored (operational and OHADA tables). None exists yet.',
            )}
            actionLabel={t('Créer une facture', 'Create invoice')}
            onAction={() => setShowCreate(true)}
          />
        ) : filtered.length === 0 ? (
          <DataEmptyState
            title={t('Aucun résultat', 'No result')}
            description={t(
              'Les filtres excluent les ' + factures.length + ' facture(s) disponibles.',
              'Current filters exclude all ' + factures.length + ' stored invoice(s).',
            )}
            actionLabel={t('Réinitialiser les filtres', 'Reset filters')}
            onAction={() => {
              setSearch('');
              setFamille('all');
              setPeriode('all');
            }}
          />
        ) : (
          <>
            {/* Tableau : écrans moyens et larges */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[900px]">
                <thead className="bg-surface-container-low">
                  <tr>
                    {([
                      t('Facture', 'Invoice'),
                      t('Client', 'Client'),
                      t('Émission', 'Issued'),
                      t('Échéance', 'Due'),
                      t('Montant TTC', 'Gross amount'),
                      t('Reste dû', 'Balance'),
                      t('Statut', 'Status'),
                      t('Actions', 'Actions'),
                    ] as string[]).map((h, i) => (
                      <th
                        key={h}
                        className={`px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant ${i >= 4 && i <= 5 ? 'text-right' : ''} ${i === 7 ? 'text-right' : ''}`}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline/40">
                  {visible.map((f) => (
                    <tr key={`${f.source}-${f.id}`} className="hover:bg-surface-container/40">
                      <td className="px-4 py-3">
                        <div className="font-semibold text-on-surface">{f.numero_facture}</div>
                        <div className="text-[11px] text-on-surface-variant">
                          {(f.type_facture || 'vente')} · {f.source}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-on-surface">{nomClient(f) || t('Client non rattaché', 'Unlinked client')}</td>
                      <td className="px-4 py-3 text-on-surface-variant tabular-nums">{fmtDate(f.date_emission)}</td>
                      <td className={`px-4 py-3 tabular-nums ${isEchue(f) ? 'text-red-400 font-semibold' : 'text-on-surface-variant'}`}>
                        {fmtDate(f.date_echeance)}
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums text-on-surface">
                        {money.format(Math.round(f.montant_ttc || 0))}
                        <div className="text-[11px] text-on-surface-variant">
                          {t('TVA', 'VAT')} {money.format(Math.round(f.montant_tva || 0))}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums text-on-surface">
                        {(() => {
                          const r = resteDu(f);
                          return r === null ? '—' : money.format(Math.round(r));
                        })()}
                      </td>
                      <td className="px-4 py-3"><StatutBadge statut={f.statut} t={t} /></td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-1">
                          {f.source === 'ohada' && (
                            <IconButton
                              label={t('Télécharger le PDF', 'Download PDF')}
                              onClick={() => telechargerPdf(f)}
                              disabled={busyId === f.id}
                              icon={busyId === f.id ? Loader2 : FileText}
                              spin={busyId === f.id}
                            />
                          )}
                          {familleOf(f.statut) === 'brouillon' && (
                            <IconButton
                              label={t('Marquer émise', 'Mark as issued')}
                              onClick={() => changerStatut(f, 'emise')}
                              disabled={busyId === f.id}
                              icon={CheckCircle2}
                            />
                          )}
                          {(familleOf(f.statut) === 'ouverte' || familleOf(f.statut) === 'brouillon') && (
                            <>
                              <IconButton
                                label={t('Enregistrer un encaissement', 'Record a payment')}
                                onClick={() => setShowPay(f)}
                                disabled={busyId === f.id}
                                icon={Banknote}
                              />
                              <IconButton
                                label={t('Annuler la facture', 'Cancel invoice')}
                                onClick={() => changerStatut(f, 'annulee')}
                                disabled={busyId === f.id}
                                icon={XCircle}
                                tone="danger"
                              />
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Cartes : mobile */}
            <ul className="md:hidden divide-y divide-outline/40">
              {visible.map((f) => {
                const r = resteDu(f);
                return (
                  <li key={`${f.source}-${f.id}`} className="p-4 space-y-2">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="font-semibold text-on-surface truncate">{f.numero_facture}</div>
                        <div className="text-[11px] text-on-surface-variant truncate">
                          {nomClient(f) || t('Client non rattaché', 'Unlinked client')}
                        </div>
                      </div>
                      <StatutBadge statut={f.statut} t={t} />
                    </div>
                    <dl className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px]">
                      <dt className="text-on-surface-variant">{t('Émission', 'Issued')}</dt>
                      <dd className="text-on-surface tabular-nums">{fmtDate(f.date_emission)}</dd>
                      <dt className="text-on-surface-variant">{t('Échéance', 'Due')}</dt>
                      <dd className={`tabular-nums ${isEchue(f) ? 'text-red-400 font-semibold' : 'text-on-surface'}`}>
                        {fmtDate(f.date_echeance)}
                      </dd>
                      <dt className="text-on-surface-variant">{t('Montant TTC', 'Gross')}</dt>
                      <dd className="text-on-surface tabular-nums">{money.format(Math.round(f.montant_ttc || 0))} XAF</dd>
                      <dt className="text-on-surface-variant">{t('Reste dû', 'Balance')}</dt>
                      <dd className="text-on-surface tabular-nums">{r === null ? '—' : `${money.format(Math.round(r))} XAF`}</dd>
                    </dl>
                    <div className="flex flex-wrap items-center gap-2 pt-1">
                      {f.source === 'ohada' && (
                        <MobileAction
                          onClick={() => telechargerPdf(f)}
                          disabled={busyId === f.id}
                          label={t('PDF', 'PDF')}
                        />
                      )}
                      {(familleOf(f.statut) === 'ouverte' || familleOf(f.statut) === 'brouillon') && (
                        <MobileAction onClick={() => setShowPay(f)} label={t('Encaisser', 'Record payment')} primary />
                      )}
                      {familleOf(f.statut) === 'brouillon' && (
                        <MobileAction onClick={() => changerStatut(f, 'emise')} label={t('Émettre', 'Issue')} />
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>

            {/* Pagination */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 border-t border-outline text-sm text-on-surface-variant">
              <div>
                {t(
                  `${((pageSafe - 1) * PAR_PAGE) + 1}–${Math.min(pageSafe * PAR_PAGE, filtered.length)} sur ${filtered.length} facture(s)`,
                  `${((pageSafe - 1) * PAR_PAGE) + 1}–${Math.min(pageSafe * PAR_PAGE, filtered.length)} of ${filtered.length} invoice(s)`,
                )}
              </div>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={pageSafe <= 1}
                  aria-label={t('Page précédente', 'Previous page')}
                  className="grid place-items-center w-11 h-11 rounded-xl border border-outline hover:bg-surface-container disabled:opacity-40"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="px-3 tabular-nums text-on-surface">
                  {pageSafe} / {totalPages}
                </span>
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={pageSafe >= totalPages}
                  aria-label={t('Page suivante', 'Next page')}
                  className="grid place-items-center w-11 h-11 rounded-xl border border-outline hover:bg-surface-container disabled:opacity-40"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      <p className="text-[11px] text-on-surface-variant">
        {t(
          `Statuts rencontrés dans la base : ${statutsDisponibles.join(', ') || 'aucun'}. Le TVA par défaut (${TVA_DEFAUT} %) vient du paramétrage fiscal camerounais.`,
          `Statuses found in the database: ${statutsDisponibles.join(', ') || 'none'}. The default VAT rate (${TVA_DEFAUT}%) comes from the Cameroonian tax settings.`,
        )}
      </p>

      {showCreate && (
        <CreateInvoiceModal
          clients={clients}
          onClose={() => setShowCreate(false)}
          onCreated={(numero) => {
            setShowCreate(false);
            load();
            toast.success(t(`Facture ${numero} créée.`, `Invoice ${numero} created.`));
          }}
        />
      )}

      {showPay && (
        <PaymentModal
          facture={showPay}
          reste={resteDu(showPay)}
          onClose={() => setShowPay(null)}
          onSaved={() => {
            setShowPay(null);
            load();
          }}
        />
      )}
    </div>
  );
}

/* ------------------------------ sous-vues ------------------------------ */

function KpiCard({
  icon: Icon, label, value, hint, tone = 'default',
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  hint: string;
  tone?: 'default' | 'danger';
}) {
  return (
    <div className={`p-4 border rounded-2xl ${tone === 'danger' ? 'bg-red-500/10 border-red-500/30' : 'bg-surface border-outline'}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">{label}</span>
        <Icon className={`w-4 h-4 shrink-0 ${tone === 'danger' ? 'text-red-400' : 'text-emerald-400'}`} />
      </div>
      <div className={`mt-1 text-xl font-bold tabular-nums ${tone === 'danger' ? 'text-red-300' : 'text-on-surface'}`}>{value}</div>
      <div className="mt-0.5 text-[11px] text-on-surface-variant">{hint}</div>
    </div>
  );
}

function StatutBadge({
  statut, t,
}: {
  statut: string;
  t: (fr: string, en: string) => string;
}) {
  const fam = familleOf(statut);
  const classes =
    fam === 'payee' ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
    : fam === 'annulee' ? 'bg-red-500/10 text-red-300 border-red-500/30'
    : fam === 'brouillon' ? 'bg-slate-500/10 text-slate-300 border-slate-500/30'
    : 'bg-amber-500/10 text-amber-300 border-amber-500/30';
  const libelle =
    fam === 'payee' ? t('Payée', 'Paid')
    : fam === 'annulee' ? t('Annulée', 'Cancelled')
    : fam === 'brouillon' ? t('Brouillon', 'Draft')
    : statut === 'retard' ? t('En retard', 'Late')
    : statut === 'payee_partiel' || statut === 'payee_partiellement' ? t('Partiellement payée', 'Partially paid')
    : t('Émise', 'Issued');
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-lg border text-[11px] font-semibold whitespace-nowrap ${classes}`}>
      {libelle}
      <span className="ml-1.5 opacity-60 font-mono">{String(statut || '').slice(0, 12)}</span>
    </span>
  );
}

function IconButton({
  label, onClick, icon: Icon, disabled, tone = 'default', spin,
}: {
  label: string;
  onClick: () => void;
  icon: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
  tone?: 'default' | 'danger';
  spin?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={label}
      aria-label={label}
      className={`grid place-items-center w-11 h-11 rounded-xl border border-outline transition-colors disabled:opacity-40 ${
        tone === 'danger' ? 'text-red-300 hover:bg-red-500/10' : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
      }`}
    >
      <Icon className={`w-4 h-4 ${spin ? 'animate-spin' : ''}`} />
    </button>
  );
}

function MobileAction({
  label, onClick, disabled, primary,
}: {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`px-3 py-2 min-h-11 text-xs font-semibold rounded-xl border transition-colors disabled:opacity-40 ${
        primary ? 'bg-emerald-600 border-emerald-500 text-white' : 'border-outline text-on-surface hover:bg-surface-container'
      }`}
    >
      {label}
    </button>
  );
}

function ModalShell({
  title, onClose, children, footer,
}: {
  title: string;
  onClose: () => void;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <div
      className="fixed inset-0 z-[80] bg-slate-950/85 flex items-end sm:items-center justify-center p-0 sm:p-4"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="w-full sm:max-w-lg max-h-[92vh] overflow-y-auto bg-surface border border-outline rounded-t-2xl sm:rounded-2xl shadow-2xl"
      >
        <div className="flex items-center justify-between gap-3 px-5 py-4 border-b border-outline sticky top-0 bg-surface">
          <h2 className="text-base font-semibold text-on-surface">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fermer"
            className="grid place-items-center w-11 h-11 rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>
        <div className="px-5 py-4 space-y-4">{children}</div>
        {footer && <div className="px-5 py-4 border-t border-outline sticky bottom-0 bg-surface">{footer}</div>}
      </div>
    </div>
  );
}

function Field({
  label, children, hint,
}: {
  label: string;
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">{label}</span>
      {children}
      {hint && <span className="text-[11px] text-on-surface-variant">{hint}</span>}
    </label>
  );
}

const inputCls =
  'w-full px-3 py-2.5 min-h-11 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none focus:border-emerald-500';

function CreateInvoiceModal({
  clients, onClose, onCreated,
}: {
  clients: ClientOption[];
  onClose: () => void;
  onCreated: (numero: string) => void;
}) {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    client_id: clients[0] ? String(clients[0].id) : '',
    type_facture: 'vente',
    date_emission: isoAYMD(new Date()),
    date_echeance: '',
    montant_ht: '',
    taux_tva: String(TVA_DEFAUT),
  });
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const ht = Number(form.montant_ht) || 0;
  const tva = Number(form.taux_tva) || 0;
  const ttc = Math.round((ht + ht * (tva / 100)) * 100) / 100;

  const submit = async () => {
    if (!form.client_id) {
      toast.error(t('Sélectionnez un client.', 'Select a client.'));
      return;
    }
    if (ht <= 0) {
      toast.error(t('Le montant HT doit être positif.', 'The net amount must be positive.'));
      return;
    }
    setSaving(true);
    try {
      const res = await financeAPI.createFacture({
        client_id: Number(form.client_id),
        type_facture: form.type_facture,
        date_emission: form.date_emission,
        date_echeance: form.date_echeance || undefined,
        montant_ht: ht,
        taux_tva: tva,
      });
      onCreated(res.data?.numero_facture || t('(numéro attribué par le serveur)', '(number assigned by the server)'));
    } catch (err) {
      const info = classifyApiError(err);
      toast.error(info.message || t('Création refusée par le serveur.', 'The server rejected the creation.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalShell
      title={t('Nouvelle facture', 'New invoice')}
      onClose={onClose}
      footer={
        <div className="flex items-center justify-between gap-3">
          <span className="text-[11px] text-on-surface-variant">
            {t('Total TTC calculé : ', 'Computed gross total: ')}
            <span className="font-semibold text-on-surface tabular-nums">{ttc.toLocaleString(lang === 'en' ? 'en-GB' : 'fr-FR')} XAF</span>
          </span>
          <div className="flex gap-2">
            <button type="button" onClick={onClose} className="px-4 py-2 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface hover:bg-surface-container">
              {t('Annuler', 'Cancel')}
            </button>
            <button
              type="button"
              onClick={submit}
              disabled={saving}
              className="flex items-center gap-1.5 px-4 py-2 min-h-11 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              {t('Enregistrer', 'Save')}
            </button>
          </div>
        </div>
      }
    >
      {clients.length === 0 ? (
        <DataEmptyState
          title={t('Aucun client enregistré', 'No client registered')}
          description={t(
            'Une facture doit être rattachée à un client. Créez-en un dans la master data.',
            'An invoice must be linked to a client. Create one in the master data.',
          )}
          actionLabel={t('Ouvrir les tiers', 'Open clients')}
          actionHref="/master-data/tiers"
        />
      ) : (
        <>
          <Field label={t('Client', 'Client')}>
            <select className={inputCls} value={form.client_id} onChange={(e) => set('client_id', e.target.value)}>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code ? `${c.code} — ${c.name}` : c.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label={t('Type de facture', 'Invoice type')}>
            <select className={inputCls} value={form.type_facture} onChange={(e) => set('type_facture', e.target.value)}>
              <option value="vente">{t('Vente', 'Sales')}</option>
              <option value="prestation">{t('Prestation', 'Service')}</option>
              <option value="achat">{t('Achat', 'Purchase')}</option>
              <option value="avoir">{t('Avoir', 'Credit note')}</option>
            </select>
          </Field>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Field label={t('Date d''émission', 'Issue date')}>
              <input type="date" className={inputCls} value={form.date_emission} onChange={(e) => set('date_emission', e.target.value)} />
            </Field>
            <Field label={t('Échéance', 'Due date')} hint={t('Vide = sans échéance enregistrée.', 'Empty = no stored due date.')}>
              <input type="date" className={inputCls} value={form.date_echeance} onChange={(e) => set('date_echeance', e.target.value)} />
            </Field>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label={t('Montant HT (XAF)', 'Net amount (XAF)')}>
              <input
                type="number" min="0" step="0.01" inputMode="decimal" className={inputCls}
                value={form.montant_ht} onChange={(e) => set('montant_ht', e.target.value)}
              />
            </Field>
            <Field label={t('Taux TVA (%)', 'VAT rate (%)')} hint={t('19,25 % au Cameroun.', '19.25% in Cameroon.')}>
              <input
                type="number" min="0" step="0.01" inputMode="decimal" className={inputCls}
                value={form.taux_tva} onChange={(e) => set('taux_tva', e.target.value)}
              />
            </Field>
          </div>
          <p className="text-[11px] text-on-surface-variant">
            {t(
              'Le numéro est attribué par le serveur selon la séquence légale continue (FAC-ANNÉE-000X) : il n est pas saisi ici.',
              'The number is assigned by the server from the continuous legal sequence (FAC-YEAR-000X): it is not entered here.',
            )}
          </p>
        </>
      )}
    </ModalShell>
  );
}

function PaymentModal({
  facture, reste, onClose, onSaved,
}: {
  facture: FactureRow;
  reste: number | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const locale = lang === 'en' ? 'en-GB' : 'fr-FR';
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    montant: reste === null ? '' : String(Math.round(reste)),
    mode_paiement: 'virement',
    reference: '',
    date_paiement: isoAYMD(new Date()),
    notes: '',
  });
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async () => {
    const montant = Number(form.montant);
    if (!(montant > 0)) {
      toast.error(t('Indiquez un montant strictement positif.', 'Enter a strictly positive amount.'));
      return;
    }
    setSaving(true);
    try {
      const res = await financeAPI.enregistrerEncaissement({
        facture_id: facture.id,
        source: facture.source,
        montant_encaisse: montant,
        mode_paiement: form.mode_paiement,
        reference_paiement: form.reference || undefined,
        date_paiement: form.date_paiement,
        notes: form.notes || undefined,
      });
      const apres = res.data?.statut_facture;
      toast.success(t(
        `Encaissement enregistré${apres ? ` — facture « ${apres} »` : ''}.`,
        `Payment recorded${apres ? ` — invoice "${apres}"` : ''}.`,
      ));
      onSaved();
    } catch (err) {
      const info = classifyApiError(err);
      toast.error(info.message || t('Encaissement refusé par le serveur.', 'The server rejected the payment.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalShell
      title={t(`Encaissement — ${facture.numero_facture}`, `Payment — ${facture.numero_facture}`)}
      onClose={onClose}
      footer={
        <div className="flex items-center justify-end gap-2">
          <button type="button" onClick={onClose} className="px-4 py-2 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface hover:bg-surface-container">
            {t('Annuler', 'Cancel')}
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={saving}
            className="flex items-center gap-1.5 px-4 py-2 min-h-11 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50"
          >
            {saving && <Loader2 className="w-4 h-4 animate-spin" />}
            {t('Enregistrer', 'Save')}
          </button>
        </div>
      }
    >
      <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px]">
        <span className="text-on-surface-variant">{t('Client', 'Client')}</span>
        <span className="text-on-surface">{facture.client_nom || '—'}</span>
        <span className="text-on-surface-variant">{t('Montant TTC', 'Gross total')}</span>
        <span className="text-on-surface tabular-nums">{(facture.montant_ttc || 0).toLocaleString(locale)} XAF</span>
        <span className="text-on-surface-variant">{t('Reste dû connu', 'Known balance')}</span>
        <span className="text-on-surface tabular-nums">
          {reste === null ? t('non calculable', 'not computable') : `${Math.round(reste).toLocaleString(locale)} XAF`}
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Field label={t('Montant encaissé (XAF)', 'Amount received (XAF)')}>
          <input type="number" min="0" step="0.01" inputMode="decimal" className={inputCls}
            value={form.montant} onChange={(e) => set('montant', e.target.value)} />
        </Field>
        <Field label={t('Date du règlement', 'Payment date')}>
          <input type="date" className={inputCls} value={form.date_paiement} onChange={(e) => set('date_paiement', e.target.value)} />
        </Field>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Field label={t('Mode de paiement', 'Payment method')}>
          <select className={inputCls} value={form.mode_paiement} onChange={(e) => set('mode_paiement', e.target.value)}>
            <option value="virement">{t('Virement', 'Bank transfer')}</option>
            <option value="especes">{t('Espèces', 'Cash')}</option>
            <option value="cheque">{t('Chèque', 'Cheque')}</option>
            <option value="mobile_money">{t('Mobile Money', 'Mobile Money')}</option>
            <option value="carte">{t('Carte bancaire', 'Card')}</option>
          </select>
        </Field>
        <Field label={t('Référence', 'Reference')} hint={t('Facultatif.', 'Optional.')}>
          <input type="text" className={inputCls} value={form.reference} onChange={(e) => set('reference', e.target.value)} />
        </Field>
      </div>
      <Field label={t('Note interne', 'Internal note')} hint={t('Facultatif.', 'Optional.')}>
        <input type="text" className={inputCls} value={form.notes} onChange={(e) => set('notes', e.target.value)} />
      </Field>
    </ModalShell>
  );
}

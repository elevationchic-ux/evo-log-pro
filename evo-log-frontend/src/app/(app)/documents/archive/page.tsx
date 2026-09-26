'use client';

/**
 * K-Documents — Archivage légal.
 *
 * Source unique : GET /api/v1/documents/archivages-legal, qui lit la table
 * `archivages_legal` et joint le document archivé (titre / numéro / type).
 * L'écran ne prétend à rien qu'il ne peut prouver :
 * - aucun bouton de téléchargement : la GED n'expose aucune route de délivrance
 *   de fichier, un lien « Exporter le PDF » serait mort ;
 * - aucun compteur par catégorie inventé : les cartes sont le décomptage réel
 *   des lignes archivées ;
 * - la « conformité » affichée est celle qui a été consignée dans la base
 *   (`verification_conformite`), pas un taux estimé.
 * Les actions proposées (archiver, restaurer, consigner la vérification)
 * écrivent exactement les colonnes portées par le modèle.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { toast } from 'sonner';
import {
  Archive, RefreshCw, Download, Search, Plus, RotateCcw, Loader2,
  ChevronLeft, ChevronRight, X, ShieldCheck, ShieldAlert, BadgeCheck, Eye,
} from 'lucide-react';
import { documentsAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { DataEmptyState, DataErrorState, DataLoadingState } from '@/components/shared/StatePanels';
import { classifyApiError, type ApiErrorInfo } from '@/hooks/useApi';

interface ArchivageRow {
  id: number;
  document_id: number;
  type_archivage: string | null;
  duree_conservation: number | null;
  autorite_archivage: string | null;
  date_archivage: string | null;
  date_expiration: string | null;
  numero_archivage: string;
  reference_archivage: string | null;
  classification: string | null;
  conformite: boolean;
  verification_conformite: string | null;
  certificat_conformite: string | null;
  statut: string;
  date_restauration: string | null;
  motif_restauration: string | null;
  document_titre: string | null;
  document_numero: string | null;
  document_type: string | null;
}

interface DocumentOption {
  id: number;
  numero_document: string;
  titre: string;
  type_document: string | null;
}

/** Libellés des énumérations du modèle — la base stocke des mots-clés, pas des phrases. */
const LIBELLES: Record<string, { fr: string; en: string }> = {
  fiscal: { fr: 'Fiscal', en: 'Tax' },
  juridique: { fr: 'Juridique', en: 'Legal' },
  comptable: { fr: 'Comptable', en: 'Accounting' },
  social: { fr: 'Social', en: 'Payroll' },
  archive: { fr: 'Archivé', en: 'Archived' },
  restaure: { fr: 'Restauré', en: 'Restored' },
  detruit: { fr: 'Détruit', en: 'Destroyed' },
  confidentiel: { fr: 'Confidentiel', en: 'Confidential' },
  prive: { fr: 'Privé', en: 'Private' },
  public: { fr: 'Public', en: 'Public' },
  autre: { fr: 'Autre', en: 'Other' },
};

const TYPES_ARCHIVAGE = ['fiscal', 'juridique', 'comptable', 'social', 'autre'];
const CLASSIFICATIONS = ['confidentiel', 'prive', 'public'];
const PAR_PAGE = 20;

/** Durée de conservation en mois — propositions usuelles, saisie libre. */
const DUREES = [60, 72, 120, 180, 240, 360];

function isoToday() {
  return new Date().toISOString().slice(0, 10);
}

export default function DocumentsArchivePage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = useCallback(
    (fr: string, en: string) => (lang === 'en' ? en : fr),
    [lang],
  );
  const locale = lang === 'en' ? 'en-GB' : 'fr-FR';
  const lbl = useCallback(
    (v: string | null | undefined) => {
      if (!v) return '—';
      const cle = String(v).toLowerCase();
      return LIBELLES[cle] ? (lang === 'en' ? LIBELLES[cle].en : LIBELLES[cle].fr) : v;
    },
    [lang],
  );

  const [rows, setRows] = useState<ArchivageRow[]>([]);
  const [docs, setDocs] = useState<DocumentOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiErrorInfo | null>(null);

  const [search, setSearch] = useState('');
  const [fStatut, setFStatut] = useState('all');
  const [fType, setFType] = useState('all');
  const [sortDesc, setSortDesc] = useState(true);
  const [page, setPage] = useState(1);

  const [detail, setDetail] = useState<ArchivageRow | null>(null);
  const [restoreTarget, setRestoreTarget] = useState<ArchivageRow | null>(null);
  const [conformTarget, setConformTarget] = useState<ArchivageRow | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [a, d] = await Promise.all([
        documentsAPI.getArchivagesLegal({ limit: 500 }),
        documentsAPI.getDocuments({ limit: 500 }).catch(() => ({ data: [] })),
      ]);
      setRows(Array.isArray(a.data) ? (a.data as ArchivageRow[]) : []);
      const raw = Array.isArray(d.data) ? d.data : (d.data?.items ?? []);
      setDocs(
        (Array.isArray(raw) ? raw : []).map((r: DocumentOption) => ({
          id: r.id,
          numero_document: r.numero_document,
          titre: r.titre,
          type_document: r.type_document ?? null,
        })),
      );
    } catch (err) {
      setError(classifyApiError(err));
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Echap ferme le panneau ouvert le plus proche, comme le reste du chrome.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return;
      if (restoreTarget) setRestoreTarget(null);
      else if (conformTarget) setConformTarget(null);
      else if (showCreate) setShowCreate(false);
      else if (detail) setDetail(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [restoreTarget, conformTarget, showCreate, detail]);

  const dateFmt = useMemo(
    () => new Intl.DateTimeFormat(locale, { day: '2-digit', month: 'short', year: 'numeric' }),
    [locale],
  );
  const fmtDate = useCallback(
    (iso: string | null | undefined) => (iso ? dateFmt.format(new Date(iso)) : '—'),
    [dateFmt],
  );

  const today = useMemo(() => isoToday(), []);

  const isExpiryDepassee = useCallback(
    (r: ArchivageRow) => r.statut === 'archive' && !!r.date_expiration && r.date_expiration < today,
    [today],
  );

  /** Types réellement présents dans les archivages — aucune catégorie inventée. */
  const typesPresent = useMemo(() => {
    const m = new Map<string, number>();
    for (const r of rows) {
      const cle = (r.type_archivage || 'autre').toLowerCase();
      m.set(cle, (m.get(cle) || 0) + 1);
    }
    return Array.from(m.entries()).sort((a, b) => b[1] - a[1]);
  }, [rows]);

  const statutsPresents = useMemo(() => {
    const m = new Map<string, number>();
    for (const r of rows) {
      const cle = (r.statut || 'archive').toLowerCase();
      m.set(cle, (m.get(cle) || 0) + 1);
    }
    return Array.from(m.entries()).sort((a, b) => b[1] - a[1]);
  }, [rows]);

  /** Documents déjà sous archivage actif : à re-proposer quand même (le serveur
   *  répond 409), mais signalé pour éviter une manipulation perdue. */
  const docsDejaArchives = useMemo(() => {
    const s = new Set<number>();
    for (const r of rows) if (r.statut === 'archive') s.add(r.document_id);
    return s;
  }, [rows]);

  const kpis = useMemo(() => {
    let archives = 0;
    let restaures = 0;
    let expires = 0;
    let verifiees = 0;
    for (const r of rows) {
      const st = String(r.statut || '').toLowerCase();
      if (st === 'archive') archives += 1;
      else if (st === 'restaure') restaures += 1;
      if (isExpiryDepassee(r)) expires += 1;
      if ((r.verification_conformite || '').trim()) verifiees += 1;
    }
    return { total: rows.length, archives, restaures, expires, verifiees };
  }, [rows, isExpiryDepassee]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const liste = rows.filter((r) => {
      if (fStatut !== 'all' && String(r.statut || '').toLowerCase() !== fStatut) return false;
      if (fType !== 'all' && String(r.type_archivage || 'autre').toLowerCase() !== fType) return false;
      if (!q) return true;
      return [
        r.numero_archivage,
        r.reference_archivage,
        r.document_titre,
        r.document_numero,
        r.autorite_archivage,
        r.certificat_conformite,
      ]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q));
    });
    return liste.sort((a, b) => {
      const av = a.date_archivage || a.numero_archivage || '';
      const bv = b.date_archivage || b.numero_archivage || '';
      return sortDesc ? String(bv).localeCompare(String(av)) : String(av).localeCompare(String(bv));
    });
  }, [rows, search, fStatut, fType, sortDesc]);

  useEffect(() => {
    setPage(1);
  }, [search, fStatut, fType]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAR_PAGE));
  const pageSafe = Math.min(page, totalPages);
  const visible = useMemo(
    () => filtered.slice((pageSafe - 1) * PAR_PAGE, pageSafe * PAR_PAGE),
    [filtered, pageSafe],
  );

  const serverMessage = useCallback(
    (err: unknown, fallback: string) => {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      if (typeof detail === 'string' && detail) {
        // Le backend écrit en français ; on ne le traduit pas, on le transmet.
        return detail;
      }
      return fallback;
    },
    [],
  );

  const exportCsv = useCallback(() => {
    if (!filtered.length) return;
    const entetes = [
      t("N° d'archivage", 'Archive no.'),
      t('Document', 'Document'),
      t('Titre', 'Title'),
      t('Type', 'Type'),
      t('Statut', 'Status'),
      t('Autorité', 'Authority'),
      t('Archivé le', 'Archived on'),
      t('Expire le', 'Expires on'),
      t('Vérification', 'Verification'),
    ];
    const lignes = filtered.map((r) => [
      r.numero_archivage,
      r.document_numero || `#${r.document_id}`,
      r.document_titre || '',
      lbl(r.type_archivage),
      lbl(r.statut),
      r.autorite_archivage || '',
      r.date_archivage ? new Date(r.date_archivage).toISOString().slice(0, 10) : '',
      r.date_expiration || '',
      r.verification_conformite || '',
    ]);
    const csv = [entetes, ...lignes]
      .map((ligne) => ligne.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(';'))
      .join('\n');
    const url = URL.createObjectURL(new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `archivage-legal-${today}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(t('Export généré depuis les lignes affichées.', 'Export built from the displayed rows.'));
  }, [filtered, t, lbl, today]);

  const onRestaurer = useCallback(
    async (cible: ArchivageRow, motif: string) => {
      setBusy(true);
      try {
        await documentsAPI.mettreAJourArchivageLegal(cible.id, {
          statut: 'restaure',
          date_restauration: today,
          motif_restauration: motif,
        });
        toast.success(t(`Archivage ${cible.numero_archivage} restauré.`, `Archive ${cible.numero_archivage} restored.`));
        setRestoreTarget(null);
        load();
      } catch (err) {
        toast.error(serverMessage(err, t("Échec de la restauration.", 'Restore failed.')));
      } finally {
        setBusy(false);
      }
    },
    [t, today, load, serverMessage],
  );

  const onConformite = useCallback(
    async (cible: ArchivageRow, valeur: { conformite: boolean; verification: string; certificat: string }) => {
      setBusy(true);
      try {
        await documentsAPI.mettreAJourArchivageLegal(cible.id, {
          conformite: valeur.conformite,
          verification_conformite: valeur.verification,
          certificat_conformite: valeur.certificat || null,
        });
        toast.success(t('Vérification consignée.', 'Verification recorded.'));
        setConformTarget(null);
        load();
      } catch (err) {
        toast.error(serverMessage(err, t("Échec de l'enregistrement.", 'Save failed.')));
      } finally {
        setBusy(false);
      }
    },
    [t, load, serverMessage],
  );

  const onCreer = useCallback(
    async (payload: {
      document_id: number;
      type_archivage: string;
      duree_conservation: number;
      autorite_archivage: string;
      classification: string;
    }) => {
      setBusy(true);
      try {
        const res = await documentsAPI.creerArchivageLegal(payload);
        toast.success(
          t(
            `Document archivé sous le numéro ${res.data?.numero_archivage || ''}.`,
            `Document archived as ${res.data?.numero_archivage || ''}.`,
          ),
        );
        setShowCreate(false);
        load();
      } catch (err) {
        toast.error(serverMessage(err, t("Échec de l'archivage.", 'Archiving failed.')));
      } finally {
        setBusy(false);
      }
    },
    [t, load, serverMessage],
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* En-tête */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3 min-w-0">
          <div className="p-2.5 bg-slate-500/10 rounded-xl text-slate-300 shrink-0">
            <Archive className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              {t('Archivage légal', 'Legal archiving')}
            </h1>
            <p className="text-sm text-on-surface-variant">
              {t(
                'Coffre d’archivage : durées, autorités et vérifications consignées en base.',
                'Archive vault: retention periods, authorities and checks recorded in the database.',
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0 flex-wrap">
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
            className="flex items-center justify-center gap-1.5 px-4 py-2.5 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface hover:bg-surface-container disabled:opacity-50"
          >
            <Download className="w-4 h-4" /> {t('Exporter CSV', 'Export CSV')}
          </button>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="flex items-center justify-center gap-1.5 px-4 py-2.5 min-h-11 text-xs font-bold rounded-xl bg-slate-200 text-slate-950 hover:bg-white"
          >
            <Plus className="w-4 h-4" /> {t('Archiver un document', 'Archive a document')}
          </button>
        </div>
      </div>

      {/* KPI décomptés depuis les lignes réelles */}
      {!loading && !error && rows.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="p-4 bg-surface border border-outline rounded-2xl">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Archivages enregistrés', 'Archives recorded')}
            </div>
            <div className="mt-1 text-2xl font-bold text-on-surface tabular-nums">{kpis.total}</div>
            <p className="mt-1 text-[11px] text-on-surface-variant">
              {t(`${kpis.archives} sous archive active`, `${kpis.archives} currently archived`)}
              {kpis.restaures > 0
                ? t(` · ${kpis.restaures} restauré(s)`, ` · ${kpis.restaures} restored`)
                : ''}
            </p>
          </div>
          <div className={`p-4 border rounded-2xl ${kpis.expires ? 'bg-red-500/10 border-red-500/30' : 'bg-surface border-outline'}`}>
            <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Échéances dépassées', 'Expired retention')}
            </div>
            <div className="mt-1 text-2xl font-bold text-on-surface tabular-nums">{kpis.expires}</div>
            <p className="mt-1 text-[11px] text-on-surface-variant">
              {t(
                'Date d’expiration antérieure à aujourd’hui.',
                'Expiration date earlier than today.',
              )}
            </p>
          </div>
          <div className="p-4 bg-surface border border-outline rounded-2xl">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Vérifications consignées', 'Checks recorded')}
            </div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-on-surface tabular-nums">{kpis.verifiees}</span>
              <span className="text-xs text-on-surface-variant tabular-nums">/ {kpis.total}</span>
            </div>
            <p className="mt-1 text-[11px] text-on-surface-variant">
              {t(
                'Le solde na aucun compte rendu écrit en base.',
                'The remainder has no written report in the database.',
              )}
            </p>
          </div>
          <div className="p-4 bg-surface border border-outline rounded-2xl">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Documents en GED', 'Documents in the DMS')}
            </div>
            <div className="mt-1 text-2xl font-bold text-on-surface tabular-nums">{docs.length}</div>
            <p className="mt-1 text-[11px] text-on-surface-variant">
              {t(
                `${docsDejaArchives.size} déjà archivé(s) légalement.`,
                `${docsDejaArchives.size} already legally archived.`,
              )}
            </p>
          </div>
        </div>
      )}

      {/* Répartition réelle par type (remplace les cartes de catégorie inventées) */}
      {!loading && !error && typesPresent.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {typesPresent.map(([cle, nb]) => {
            const actif = fType === cle;
            return (
              <button
                key={cle}
                type="button"
                onClick={() => setFType(actif ? 'all' : cle)}
                aria-pressed={actif}
                className={`px-3 py-2 min-h-11 text-xs font-semibold rounded-xl border transition-colors ${
                  actif
                    ? 'bg-slate-300 text-slate-950 border-slate-300'
                    : 'bg-surface border-outline text-on-surface-variant hover:bg-surface-container'
                }`}
              >
                {lbl(cle)}
                <span className="ml-1.5 tabular-nums opacity-70">{nb}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Filtres */}
      {!loading && !error && rows.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 bg-surface border border-outline rounded-2xl p-3 sm:p-4">
          <label className="block sm:col-span-2">
            <span className="block text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant mb-1.5">
              {t('Recherche', 'Search')}
            </span>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
              <input
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('N° d’archivage, document, autorité…', 'Archive no., document, authority…')}
                aria-label={t('Rechercher un archivage', 'Search an archive')}
                className="w-full pl-9 pr-4 py-2.5 min-h-11 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-slate-400"
              />
            </div>
          </label>
          <label className="block">
            <span className="block text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant mb-1.5">
              {t('Statut', 'Status')}
            </span>
            <select
              value={fStatut}
              onChange={(e) => setFStatut(e.target.value)}
              className="w-full px-3 py-2.5 min-h-11 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-slate-400"
            >
              <option value="all">{t('Tous les statuts', 'All statuses')}</option>
              {statutsPresents.map(([cle, nb]) => (
                <option key={cle} value={cle}>
                  {lbl(cle)} ({nb})
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="block text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant mb-1.5">
              {t('Tri par date d’archivage', 'Sort by archive date')}
            </span>
            <button
              type="button"
              onClick={() => setSortDesc((v) => !v)}
              className="w-full px-3 py-2.5 min-h-11 text-sm font-semibold text-left bg-surface-container-low border border-outline rounded-xl text-on-surface hover:border-slate-400"
            >
              {sortDesc
                ? t('Plus récents d’abord', 'Most recent first')
                : t('Plus anciens d’abord', 'Oldest first')}
            </button>
          </label>
        </div>
      )}

      {/* Liste */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden">
        <div className="px-4 sm:px-5 py-3 border-b border-outline flex items-center justify-between gap-3">
          <h2 className="font-semibold text-on-surface text-sm sm:text-base truncate">
            {t('Registre des archivages', 'Archive register')}
          </h2>
          {!loading && !error && rows.length > 0 && (
            <span className="text-[11px] text-on-surface-variant tabular-nums shrink-0">
              {t(`${filtered.length} ligne(s)`, `${filtered.length} row(s)`)}
            </span>
          )}
        </div>

        {loading ? (
          <div className="p-6">
            <DataLoadingState rows={5} />
          </div>
        ) : error ? (
          <div className="p-6">
            <DataErrorState error={error} onRetry={load} />
          </div>
        ) : rows.length === 0 ? (
          <DataEmptyState
            title={t('Aucun archivage légal', 'No legal archive')}
            description={t(
              'Aucune ligne dans la table des archivages. Archivez un document déjà indexé dans la GED pour alimenter ce registre.',
              'No row in the archiving table. Archive a document already indexed in the DMS to feed this register.',
            )}
            actionLabel={t('Archiver un document', 'Archive a document')}
            onAction={() => setShowCreate(true)}
          />
        ) : filtered.length === 0 ? (
          <DataEmptyState
            title={t('Aucun archivage ne correspond', 'No matching archive')}
            description={t(
              'Aucune ligne pour ces filtres. Élargissez la recherche pour retrouver le registre complet.',
              'No row for these filters. Widen the search to get the full register back.',
            )}
            actionLabel={t('Réinitialiser les filtres', 'Reset filters')}
            onAction={() => {
              setSearch('');
              setFStatut('all');
              setFType('all');
            }}
          />
        ) : (
          <>
            {/* Mobile / tablette : cartes */}
            <ul className="md:hidden divide-y divide-outline/60">
              {visible.map((r) => (
                <li key={r.id} className="p-4 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="font-mono text-sm font-semibold text-on-surface break-all">
                        {r.numero_archivage}
                      </div>
                      <div className="text-xs text-on-surface-variant truncate mt-0.5">
                        {r.document_titre || t('Document supprimé de la GED', 'Document removed from the DMS')}
                      </div>
                      <div className="text-[11px] text-on-surface-variant tabular-nums mt-0.5">
                        {r.document_numero ? `${t('N°', 'No.')} ${r.document_numero} · ` : ''}
                        {lbl(r.document_type)}
                      </div>
                    </div>
                    <StatutPill label={lbl(r.statut)} expiry={isExpiryDepassee(r)} />
                  </div>
                  <dl className="grid grid-cols-2 gap-x-3 gap-y-2 text-[11px]">
                    <Cell label={t('Type', 'Type')} value={lbl(r.type_archivage)} />
                    <Cell label={t('Autorité', 'Authority')} value={r.autorite_archivage || '—'} />
                    <Cell label={t('Archivé le', 'Archived on')} value={fmtDate(r.date_archivage)} />
                    <Cell label={t('Expire le', 'Expires on')} value={fmtDate(r.date_expiration)} />
                  </dl>
                  <div className="flex flex-wrap gap-2">
                    <RowAction icon={Eye} label={t('Détail', 'Details')} onClick={() => setDetail(r)} />
                    {r.statut === 'archive' && (
                      <RowAction
                        icon={RotateCcw}
                        label={t('Restaurer', 'Restore')}
                        onClick={() => setRestoreTarget(r)}
                      />
                    )}
                    <RowAction
                      icon={BadgeCheck}
                      label={t('Vérification', 'Verification')}
                      onClick={() => setConformTarget(r)}
                    />
                  </div>
                </li>
              ))}
            </ul>

            {/* Desktop : tableau */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="bg-surface-container-low border-b border-outline text-[11px] uppercase tracking-wider text-on-surface-variant">
                    <th className="px-4 py-3 font-semibold">{t('N° archivage', 'Archive no.')}</th>
                    <th className="px-4 py-3 font-semibold">{t('Document', 'Document')}</th>
                    <th className="px-4 py-3 font-semibold">{t('Type', 'Type')}</th>
                    <th className="px-4 py-3 font-semibold">{t('Autorité', 'Authority')}</th>
                    <th className="px-4 py-3 font-semibold">{t('Archivé le', 'Archived on')}</th>
                    <th className="px-4 py-3 font-semibold">{t('Expire le', 'Expires on')}</th>
                    <th className="px-4 py-3 font-semibold">{t('Statut', 'Status')}</th>
                    <th className="px-4 py-3 font-semibold text-right">{t('Actions', 'Actions')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline/60">
                  {visible.map((r) => (
                    <tr key={r.id} className="hover:bg-surface-container/50 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs font-semibold text-on-surface whitespace-nowrap">
                        {r.numero_archivage}
                      </td>
                      <td className="px-4 py-3 max-w-[16rem]">
                        <div className="truncate text-on-surface" title={r.document_titre || ''}>
                          {r.document_titre || t('Document supprimé de la GED', 'Document removed from the DMS')}
                        </div>
                        <div className="text-[11px] text-on-surface-variant tabular-nums truncate">
                          {r.document_numero || `#${r.document_id}`} · {lbl(r.document_type)}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-on-surface-variant whitespace-nowrap">{lbl(r.type_archivage)}</td>
                      <td className="px-4 py-3 text-on-surface-variant max-w-[12rem] truncate" title={r.autorite_archivage || ''}>
                        {r.autorite_archivage || '—'}
                      </td>
                      <td className="px-4 py-3 tabular-nums whitespace-nowrap">{fmtDate(r.date_archivage)}</td>
                      <td className="px-4 py-3 tabular-nums whitespace-nowrap">
                        <span className={isExpiryDepassee(r) ? 'text-red-400 font-semibold' : ''}>
                          {fmtDate(r.date_expiration)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <StatutPill label={lbl(r.statut)} expiry={isExpiryDepassee(r)} />
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-1 opacity-100 md:opacity-100">
                          <IconButton title={t('Voir le détail', 'View details')} onClick={() => setDetail(r)}>
                            <Eye className="w-4 h-4" />
                          </IconButton>
                          {r.statut === 'archive' && (
                            <IconButton
                              title={t('Restaurer de l’archive', 'Restore from archive')}
                              onClick={() => setRestoreTarget(r)}
                            >
                              <RotateCcw className="w-4 h-4" />
                            </IconButton>
                          )}
                          <IconButton
                            title={t('Consigner la vérification', 'Record the verification')}
                            onClick={() => setConformTarget(r)}
                          >
                            <BadgeCheck className="w-4 h-4" />
                          </IconButton>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 border-t border-outline flex flex-col sm:flex-row items-center justify-between gap-2">
              <span className="text-xs text-on-surface-variant tabular-nums">
                {t(
                  `${((pageSafe - 1) * PAR_PAGE) + 1} à ${Math.min(pageSafe * PAR_PAGE, filtered.length)} sur ${filtered.length}`,
                  `${((pageSafe - 1) * PAR_PAGE) + 1} to ${Math.min(pageSafe * PAR_PAGE, filtered.length)} of ${filtered.length}`,
                )}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={pageSafe <= 1}
                  aria-label={t('Page précédente', 'Previous page')}
                  className="p-2.5 min-h-11 rounded-xl border border-outline text-on-surface-variant hover:bg-surface-container disabled:opacity-40"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-xs text-on-surface tabular-nums">
                  {t(`Page ${pageSafe} / ${totalPages}`, `Page ${pageSafe} / ${totalPages}`)}
                </span>
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={pageSafe >= totalPages}
                  aria-label={t('Page suivante', 'Next page')}
                  className="p-2.5 min-h-11 rounded-xl border border-outline text-on-surface-variant hover:bg-surface-container disabled:opacity-40"
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
          'Les durées proposées à l’archivage sont des repères de conservation ; la date d’expiration est calculée par le serveur (aujourd’hui + durée en mois × 30 jours).',
          'The retention periods offered when archiving are guidance only; the expiry date is computed by the server (today + months × 30 days).',
        )}
        {' '}
        <Link href="/documents" className="font-semibold text-slate-300 hover:underline">
          {t('Ouvrir la GED', 'Open the DMS')}
        </Link>
      </p>

      {showCreate && (
        <CreateModal
          t={t}
          docs={docs}
          alreadyArchived={docsDejaArchives}
          busy={busy}
          onClose={() => setShowCreate(false)}
          onSubmit={onCreer}
        />
      )}

      {detail && (
        <DetailModal
          t={t}
          lbl={lbl}
          row={detail}
          fmtDate={fmtDate}
          expiry={isExpiryDepassee(detail)}
          onClose={() => setDetail(null)}
        />
      )}

      {restoreTarget && (
        <RestoreModal
          t={t}
          row={restoreTarget}
          busy={busy}
          onClose={() => setRestoreTarget(null)}
          onSubmit={(motif) => onRestaurer(restoreTarget, motif)}
        />
      )}

      {conformTarget && (
        <ConformiteModal
          t={t}
          row={conformTarget}
          busy={busy}
          onClose={() => setConformTarget(null)}
          onSubmit={(v) => onConformite(conformTarget, v)}
        />
      )}
    </div>
  );
}

/* ------------------------------ Sous-composants ---------------------------- */

type T = (fr: string, en: string) => string;
type Lbl = (v: string | null | undefined) => string;

function StatutPill({ label, expiry }: { label: string; expiry: boolean }) {
  if (expiry) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-[11px] font-bold whitespace-nowrap">
        <ShieldAlert className="w-3.5 h-3.5" />
        {label}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-500/10 border border-slate-500/30 text-slate-300 text-[11px] font-bold whitespace-nowrap">
      <ShieldCheck className="w-3.5 h-3.5" />
      {label}
    </span>
  );
}

function Cell({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant">{label}</dt>
      <dd className="text-xs text-on-surface truncate">{value}</dd>
    </div>
  );
}

function IconButton({
  title,
  onClick,
  children,
}: {
  title: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      title={title}
      aria-label={title}
      onClick={onClick}
      className="w-11 h-11 inline-flex items-center justify-center rounded-xl border border-outline text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
    >
      {children}
    </button>
  );
}

function RowAction({
  icon: Icon,
  label,
  onClick,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1.5 px-3 py-2.5 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface-variant hover:bg-surface-container"
    >
      <Icon className="w-4 h-4" /> {label}
    </button>
  );
}

function ModalShell({
  title,
  onClose,
  children,
  closeLabel,
}: {
  title: string;
  onClose: () => void;
  children: React.ReactNode;
  closeLabel: string;
}) {
  return (
    <div
      className="fixed inset-0 z-[70] flex items-end sm:items-center justify-center bg-slate-950/85 p-0 sm:p-4"
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
        <div className="sticky top-0 bg-surface border-b border-outline px-5 py-4 flex items-center justify-between gap-3">
          <h3 className="font-bold text-on-surface text-base min-w-0 truncate">{title}</h3>
          <button
            type="button"
            onClick={onClose}
            aria-label={closeLabel}
            title={closeLabel}
            className="w-11 h-11 shrink-0 -mr-2 inline-flex items-center justify-center rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="block text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant mb-1.5">
        {label}
      </span>
      {children}
      {hint && <span className="mt-1 block text-[11px] text-on-surface-variant">{hint}</span>}
    </label>
  );
}

const INPUT =
  'w-full px-3 py-2.5 min-h-11 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-slate-400';

function CreateModal({
  t,
  docs,
  alreadyArchived,
  busy,
  onClose,
  onSubmit,
}: {
  t: T;
  docs: DocumentOption[];
  alreadyArchived: Set<number>;
  busy: boolean;
  onClose: () => void;
  onSubmit: (p: {
    document_id: number;
    type_archivage: string;
    duree_conservation: number;
    autorite_archivage: string;
    classification: string;
  }) => Promise<void>;
}) {
  const [documentId, setDocumentId] = useState<number | ''>('');
  const [typeArchivage, setTypeArchivage] = useState('fiscal');
  const [duree, setDuree] = useState(120);
  const [autorite, setAutorite] = useState('');
  const [classification, setClassification] = useState('confidentiel');

  const soumettre = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!documentId) {
      toast.error(t('Sélectionnez le document à archiver.', 'Select the document to archive.'));
      return;
    }
    if (!autorite.trim()) {
      toast.error(
        t("Indiquez l'autorité d'archivage.", 'Provide the archiving authority.'),
      );
      return;
    }
    if (!Number.isFinite(duree) || duree < 1) {
      toast.error(
        t('La durée de conservation doit être d’au moins 1 mois.', 'The retention period must be at least 1 month.'),
      );
      return;
    }
    await onSubmit({
      document_id: Number(documentId),
      type_archivage: typeArchivage,
      duree_conservation: Number(duree),
      autorite_archivage: autorite.trim(),
      classification,
    });
  };

  return (
    <ModalShell title={t('Archiver un document', 'Archive a document')} onClose={onClose} closeLabel={t('Fermer', 'Close')}>
      <form onSubmit={soumettre} className="space-y-4">
        {docs.length === 0 ? (
          <p className="text-sm text-on-surface-variant">
            {t(
              'Aucun document indexé dans la GED : l’archivage légal ne peut porter que sur un document déjà enregistré.',
              'No document indexed in the DMS: legal archiving can only cover an already registered document.',
            )}
          </p>
        ) : (
          <Field
            label={t('Document', 'Document')}
            hint={t(
              'Un document déjà sous archive active sera refusé par le serveur (conflit).',
              'A document already under active archive will be refused by the server (conflict).',
            )}
          >
            <select
              value={documentId}
              onChange={(e) => setDocumentId(e.target.value ? Number(e.target.value) : '')}
              className={INPUT}
            >
              <option value="">{t('— Choisir —', '— Choose —')}</option>
              {docs.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.numero_document || `#${d.id}`} — {d.titre}
                  {alreadyArchived.has(d.id) ? t('  [déjà archivé]', '  [already archived]') : ''}
                </option>
              ))}
            </select>
          </Field>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label={t('Type d’archivage', 'Archive type')}>
            <select
              value={typeArchivage}
              onChange={(e) => setTypeArchivage(e.target.value)}
              className={INPUT}
            >
              {TYPES_ARCHIVAGE.map((v) => (
                <option key={v} value={v}>
                  {v === 'fiscal' ? t('Fiscal', 'Tax')
                    : v === 'juridique' ? t('Juridique', 'Legal')
                    : v === 'comptable' ? t('Comptable', 'Accounting')
                    : v === 'social' ? t('Social', 'Payroll')
                    : t('Autre', 'Other')}
                </option>
              ))}
            </select>
          </Field>
          <Field label={t('Classification', 'Classification')}>
            <select
              value={classification}
              onChange={(e) => setClassification(e.target.value)}
              className={INPUT}
            >
              {CLASSIFICATIONS.map((v) => (
                <option key={v} value={v}>
                  {v === 'confidentiel' ? t('Confidentiel', 'Confidential')
                    : v === 'prive' ? t('Privé', 'Private')
                    : t('Public', 'Public')}
                </option>
              ))}
            </select>
          </Field>
        </div>

        <Field
          label={t('Durée de conservation (mois)', 'Retention period (months)')}
          hint={t(
            'Date d’expiration calculée côté serveur : aujourd’hui + durée × 30 jours.',
            'Expiry date computed server-side: today + period × 30 days.',
          )}
        >
          <div className="flex flex-wrap gap-2 mb-2">
            {DUREES.map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setDuree(m)}
                aria-pressed={duree === m}
                className={`px-3 py-2 min-h-11 text-xs font-semibold rounded-xl border ${
                  duree === m
                    ? 'bg-slate-300 text-slate-950 border-slate-300'
                    : 'bg-surface-container-low border-outline text-on-surface-variant hover:bg-surface-container'
                }`}
              >
                {t(`${m} mois`, `${m} months`)}
              </button>
            ))}
          </div>
          <input
            type="number"
            min={1}
            max={1200}
            value={duree}
            onChange={(e) => setDuree(Number(e.target.value))}
            className={INPUT}
          />
        </Field>

        <Field label={t('Autorité d’archivage', 'Archiving authority')}>
          <input
            type="text"
            value={autorite}
            maxLength={100}
            onChange={(e) => setAutorite(e.target.value)}
            placeholder={t('Ex. Direction générale, CNPS, DGI…', 'E.g. Head office, CNPS, DGI…')}
            className={INPUT}
          />
        </Field>

        <div className="flex flex-col sm:flex-row gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="sm:order-2 px-4 py-2.5 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface-variant hover:bg-surface-container"
          >
            {t('Annuler', 'Cancel')}
          </button>
          <button
            type="submit"
            disabled={busy || docs.length === 0}
            className="sm:order-1 flex-1 flex items-center justify-center gap-2 px-4 py-2.5 min-h-11 text-xs font-bold rounded-xl bg-slate-200 text-slate-950 hover:bg-white disabled:opacity-50"
          >
            {busy && <Loader2 className="w-4 h-4 animate-spin" />}
            {t('Archiver', 'Archive')}
          </button>
        </div>
      </form>
    </ModalShell>
  );
}

function DetailModal({
  t,
  lbl,
  row,
  fmtDate,
  expiry,
  onClose,
}: {
  t: T;
  lbl: Lbl;
  row: ArchivageRow;
  fmtDate: (iso: string | null | undefined) => string;
  expiry: boolean;
  onClose: () => void;
}) {
  const lignes: Array<{ label: string; value: string }> = [
    { label: t('Document', 'Document'), value: row.document_numero || `#${row.document_id}` },
    { label: t('Titre', 'Title'), value: row.document_titre || '—' },
    { label: t('Type de document', 'Document type'), value: lbl(row.document_type) },
    { label: t('Type d’archivage', 'Archive type'), value: lbl(row.type_archivage) },
    { label: t('Classification', 'Classification'), value: lbl(row.classification) },
    { label: t('Autorité', 'Authority'), value: row.autorite_archivage || '—' },
    {
      label: t('Conservation', 'Retention'),
      value: row.duree_conservation
        ? t(`${row.duree_conservation} mois`, `${row.duree_conservation} months`)
        : '—',
    },
    { label: t('Archivé le', 'Archived on'), value: fmtDate(row.date_archivage) },
    { label: t('Expire le', 'Expires on'), value: fmtDate(row.date_expiration) },
    { label: t('Référence d’archivage', 'Archive reference'), value: row.reference_archivage || '—' },
    {
      label: t('Certificat de conformité', 'Compliance certificate'),
      value: row.certificat_conformite || '—',
    },
  ];
  if (row.statut === 'restaure') {
    lignes.push({ label: t('Restauré le', 'Restored on'), value: fmtDate(row.date_restauration) });
    lignes.push({ label: t('Motif', 'Reason'), value: row.motif_restauration || '—' });
  }

  return (
    <ModalShell
      title={t(`Archivage ${row.numero_archivage}`, `Archive ${row.numero_archivage}`)}
      onClose={onClose}
      closeLabel={t('Fermer', 'Close')}
    >
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <StatutPill label={lbl(row.statut)} expiry={expiry} />
          {expiry && (
            <span className="text-[11px] text-red-400">
              {t('Durée de conservation dépassée.', 'Retention period over.')}
            </span>
          )}
        </div>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-3">
          {lignes.map((l) => (
            <div key={l.label} className="min-w-0">
              <dt className="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant">{l.label}</dt>
              <dd className="text-sm text-on-surface break-words">{l.value}</dd>
            </div>
          ))}
        </dl>
        <div className="p-3 rounded-xl bg-surface-container-low border border-outline">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant mb-1">
            {t('Procès-verbal de vérification', 'Verification report')}
          </div>
          <p className="text-sm text-on-surface whitespace-pre-wrap break-words">
            {(row.verification_conformite || '').trim()
              ? row.verification_conformite
              : t(
                  'Aucun procès-verbal n’a été consigné pour cet archivage.',
                  'No report has been recorded for this archive.',
                )}
          </p>
        </div>
        <p className="text-[11px] text-on-surface-variant">
          {t(
            'La GED ne délivre pas le fichier archivé via cette interface : seul le contenu déclaré ci-dessus est consultable.',
            'The DMS does not deliver the archived file through this screen: only the content declared above is available.',
          )}
        </p>
        <button
          type="button"
          onClick={onClose}
          className="w-full sm:w-auto px-4 py-2.5 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface hover:bg-surface-container"
        >
          {t('Fermer', 'Close')}
        </button>
      </div>
    </ModalShell>
  );
}

function RestoreModal({
  t,
  row,
  busy,
  onClose,
  onSubmit,
}: {
  t: T;
  row: ArchivageRow;
  busy: boolean;
  onClose: () => void;
  onSubmit: (motif: string) => Promise<void>;
}) {
  const [motif, setMotif] = useState('');

  const soumettre = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!motif.trim()) {
      toast.error(t('Le motif de restauration est obligatoire.', 'The restore reason is required.'));
      return;
    }
    await onSubmit(motif.trim().slice(0, 200));
  };

  return (
    <ModalShell
      title={t(`Restaurer ${row.numero_archivage}`, `Restore ${row.numero_archivage}`)}
      onClose={onClose}
      closeLabel={t('Annuler', 'Cancel')}
    >
      <form onSubmit={soumettre} className="space-y-4">
        <p className="text-sm text-on-surface-variant">
          {t(
            'La restauration inscrit la date du jour et le motif dans la ligne d’archivage ; le statut passe à « restauré ».',
            'Restoring writes today’s date and the reason on the archive row; the status becomes “restored”.',
          )}
        </p>
        <Field label={t('Motif de la restauration', 'Restore reason')}>
          <textarea
            value={motif}
            rows={3}
            maxLength={200}
            onChange={(e) => setMotif(e.target.value)}
            placeholder={t(
              'Ex. contrôle fiscal sur l’exercice 2025, demande d’audit interne…',
              'E.g. tax audit on the 2025 year, internal audit request…',
            )}
            className={`${INPUT} resize-y`}
          />
        </Field>
        <div className="flex flex-col sm:flex-row gap-2">
          <button
            type="button"
            onClick={onClose}
            className="sm:order-2 px-4 py-2.5 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface-variant hover:bg-surface-container"
          >
            {t('Annuler', 'Cancel')}
          </button>
          <button
            type="submit"
            disabled={busy}
            className="sm:order-1 flex-1 flex items-center justify-center gap-2 px-4 py-2.5 min-h-11 text-xs font-bold rounded-xl bg-slate-200 text-slate-950 hover:bg-white disabled:opacity-50"
          >
            {busy && <Loader2 className="w-4 h-4 animate-spin" />}
            {t('Confirmer la restauration', 'Confirm restore')}
          </button>
        </div>
      </form>
    </ModalShell>
  );
}

function ConformiteModal({
  t,
  row,
  busy,
  onClose,
  onSubmit,
}: {
  t: T;
  row: ArchivageRow;
  busy: boolean;
  onClose: () => void;
  onSubmit: (v: { conformite: boolean; verification: string; certificat: string }) => Promise<void>;
}) {
  const [conformite, setConformite] = useState<boolean>(!!row.conformite);
  const [verification, setVerification] = useState(row.verification_conformite || '');
  const [certificat, setCertificat] = useState(row.certificat_conformite || '');

  const soumettre = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!verification.trim()) {
      toast.error(
        t(
          'Décrivez la vérification effectuée : la case seule ne prouve rien.',
          'Describe the check performed: the tick alone proves nothing.',
        ),
      );
      return;
    }
    await onSubmit({
      conformite,
      verification: verification.trim(),
      certificat: certificat.trim(),
    });
  };

  return (
    <ModalShell
      title={t(`Vérification ${row.numero_archivage}`, `Verification ${row.numero_archivage}`)}
      onClose={onClose}
      closeLabel={t('Annuler', 'Cancel')}
    >
      <form onSubmit={soumettre} className="space-y-4">
        <div className="grid grid-cols-2 gap-2">
          {[true, false].map((v) => (
            <button
              key={String(v)}
              type="button"
              onClick={() => setConformite(v)}
              aria-pressed={conformite === v}
              className={`px-3 py-2.5 min-h-11 text-xs font-semibold rounded-xl border ${
                conformite === v
                  ? v
                    ? 'bg-slate-300 text-slate-950 border-slate-300'
                    : 'bg-red-500/15 text-red-400 border-red-500/40'
                  : 'bg-surface-container-low border-outline text-on-surface-variant hover:bg-surface-container'
              }`}
            >
              {v ? t('Conforme', 'Compliant') : t('Non conforme', 'Non-compliant')}
            </button>
          ))}
        </div>
        <Field
          label={t('Procès-verbal de vérification', 'Verification report')}
          hint={t('Libre ; horodaté à la mise à jour de la ligne.', 'Free text; stamped when the row is updated.')}
        >
          <textarea
            value={verification}
            rows={4}
            maxLength={2000}
            onChange={(e) => setVerification(e.target.value)}
            placeholder={t(
              'Ex. intégrité du scellé contrôlée, checksum confronté à l’inventaire GED…',
              'E.g. seal integrity checked, checksum matched against the DMS inventory…',
            )}
            className={`${INPUT} resize-y`}
          />
        </Field>
        <Field label={t('Référence du certificat', 'Certificate reference')}>
          <input
            type="text"
            value={certificat}
            maxLength={255}
            onChange={(e) => setCertificat(e.target.value)}
            placeholder={t('Ex. CERT-2026-0148', 'E.g. CERT-2026-0148')}
            className={INPUT}
          />
        </Field>
        <div className="flex flex-col sm:flex-row gap-2">
          <button
            type="button"
            onClick={onClose}
            className="sm:order-2 px-4 py-2.5 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface-variant hover:bg-surface-container"
          >
            {t('Annuler', 'Cancel')}
          </button>
          <button
            type="submit"
            disabled={busy}
            className="sm:order-1 flex-1 flex items-center justify-center gap-2 px-4 py-2.5 min-h-11 text-xs font-bold rounded-xl bg-slate-200 text-slate-950 hover:bg-white disabled:opacity-50"
          >
            {busy && <Loader2 className="w-4 h-4 animate-spin" />}
            {t('Consigner', 'Record it')}
          </button>
        </div>
      </form>
    </ModalShell>
  );
}

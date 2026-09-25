'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { FileText, Search, Inbox, RefreshCw, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';
import { useSettings } from '@/components/layout/SettingsProvider';

interface DocumentGer {
  id: number;
  numero_document: string;
  type_document: string;
  titre: string;
  description: string | null;
  nom_fichier: string | null;
  type_mime: string | null;
  taille_octets: number | null;
  statut: string;
  date_creation: string | null;
}

function fmtDate(v: string | null): string {
  if (!v) return '';
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? v : d.toLocaleDateString('fr-FR');
}

function fmtSize(n: number | null): string {
  if (n == null) return '';
  if (n < 1024) return `${n} o`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} Ko`;
  return `${(n / (1024 * 1024)).toFixed(1)} Mo`;
}

export default function B2BDocumentsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [docs, setDocs] = useState<DocumentGer[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/documents/', { params: { limit: 200 } });
      const data = res.data;
      const rows: DocumentGer[] = Array.isArray(data) ? data : (data?.items ?? []);
      setDocs(rows);
      setLoaded(true);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Erreur de chargement', 'Failed to load'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = docs.filter((d) => {
    const q = query.toLowerCase();
    return !q || (d.titre || '').toLowerCase().includes(q) || (d.numero_document || '').toLowerCase().includes(q);
  });

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-4 pb-24 text-slate-100 sm:p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/b2b" className="flex items-center gap-1 hover:text-amber-400">
          <ArrowLeft className="h-3.5 w-3.5" /> {t('Portail Client B2B', 'B2B Client Portal')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Coffre-fort documentaire', 'Document vault')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-2.5 text-amber-400">
            <FileText className="h-6 w-6" />
          </div>
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-black text-white">
              {t('Coffre-fort documentaire', 'Document Vault')}
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              {t('Documents réellement archivés, affichés depuis la base persistante.', 'Genuinely archived documents, read from the persistent database.')}
            </p>
          </div>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          {t('Actualiser', 'Refresh')}
        </button>
      </div>

      {/* Search */}
      <div className="relative w-full sm:w-80">
        <Search className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
        <input
          type="text"
          placeholder={t('Rechercher un document...', 'Search a document...')}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-xl border border-slate-700 bg-slate-900 py-2 pl-9 pr-4 text-sm text-white placeholder:text-slate-500 focus:border-amber-500 focus:outline-none"
        />
      </div>

      {/* Documents */}
      {filtered.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-950/40 p-12 text-center">
          <Inbox className="mx-auto mb-3 h-12 w-12 text-slate-300" />
          <h3 className="text-base font-semibold text-white">
            {loaded
              ? t('Aucun document archivé', 'No archived document')
              : t('Chargement…', 'Loading…')}
          </h3>
          {loaded && (
            <p className="mx-auto mt-1 max-w-md text-sm text-slate-400">
              {t('Les documents téléversés via la GED apparaîtront ici.', 'Documents uploaded through the DMS will appear here.')}
            </p>
          )}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/60 text-xs uppercase text-slate-400">
              <tr>
                <th className="px-4 py-3">{t('Document', 'Document')}</th>
                <th className="px-4 py-3">{t('Type', 'Type')}</th>
                <th className="px-4 py-3">{t('Fichier', 'File')}</th>
                <th className="px-4 py-3">{t('Date', 'Date')}</th>
                <th className="px-4 py-3">{t('Statut', 'Status')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filtered.map((d) => (
                <tr key={d.id} className="transition hover:bg-slate-800/40">
                  <td className="px-4 py-3">
                    <div className="font-medium text-white">{d.titre}</div>
                    <div className="font-mono text-xs text-slate-500">{d.numero_document}</div>
                  </td>
                  <td className="px-4 py-3 text-xs text-amber-400">{d.type_document}</td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {d.nom_fichier ? `${d.nom_fichier} · ${fmtSize(d.taille_octets)}` : ''}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">{fmtDate(d.date_creation)}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full border border-slate-700 bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                      {d.statut}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { complianceAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { ClipboardCheck, Award, Search, RefreshCw, ArrowRight } from 'lucide-react';
import Link from 'next/link';

// Registre réel : tables audits_qualite / normes_certifications (router QHSE).
// Aucune colonne inventée : ce qu'on affiche correspond exactement aux champs
// renvoyés par /api/v1/qhse/audits et /api/v1/qhse/certifications.
type Audit = {
  id: number;
  numero_audit: string;
  certification_id: number | null;
  type_audit: string | null;
  auditeur: string;
  date_debut: string | null;
  date_fin: string | null;
  statut: string | null;
  scope: string | null;
  non_conformites: string | null;
  conclusion: string | null;
};

type Certification = {
  id: number;
  numero_certificat: string;
  norme: string;
  organisme: string;
  date_obtention: string | null;
  date_expiration: string | null;
  statut: string | null;
  resultat_audit: string | null;
};

function listeBrute(res: unknown): unknown[] {
  const body = (res as { data?: unknown })?.data ?? res;
  const inner = (body as { items?: unknown; data?: unknown })?.items
    ?? (body as { data?: unknown })?.data
    ?? body;
  return Array.isArray(inner) ? inner : [];
}

// Le rouge est l'identité du module QHSE & Sécurité, dont la conformité
// dépend : les badges d'état utilisent donc d'autres teintes.
const STATUTS_AUDIT = ['en_cours', 'complete', 'annule'] as const;

function statutAuditBadge(s: string | null) {
  if (s === 'complete') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  if (s === 'en_cours') return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  if (s === 'annule') return 'bg-slate-600/20 text-slate-400 border-slate-600/40';
  return 'bg-slate-500/10 text-slate-300 border-slate-500/30';
}

export default function CompliancePage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const [searchQuery, setSearchQuery] = useState('');
  const [statutFilter, setStatutFilter] = useState<string>('all');

  const auditsQuery = useQuery({
    queryKey: ['compliance-audits'],
    queryFn: async () => listeBrute(await complianceAPI.getAudits()) as Audit[],
  });

  const certsQuery = useQuery({
    queryKey: ['compliance-certifications'],
    queryFn: async () => listeBrute(await complianceAPI.getCertifications()) as Certification[],
  });

  const audits = auditsQuery.data ?? [];
  const certifications = certsQuery.data ?? [];
  const normesById = new Map(certifications.map((c) => [c.id, c]));

  const filtered = audits.filter((a) => {
    if (statutFilter !== 'all' && (a.statut ?? '') !== statutFilter) return false;
    const cert = a.certification_id ? normesById.get(a.certification_id) : undefined;
    const hay = `${a.numero_audit} ${a.auditeur ?? ''} ${a.scope ?? ''} ${cert?.norme ?? ''} ${cert?.numero_certificat ?? ''}`;
    return hay.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const isLoading = auditsQuery.isLoading || certsQuery.isLoading;
  const loadError = auditsQuery.isError || certsQuery.isError;

  const refreshing = auditsQuery.isFetching || certsQuery.isFetching;
  const reload = () => {
    auditsQuery.refetch();
    certsQuery.refetch();
  };

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-xl">
        <div className="min-w-0">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-semibold mb-2 border border-red-500/20">
            <ClipboardCheck className="w-3.5 h-3.5 shrink-0" />
            {t('QHSE • Audits qualité & certifications', 'QHSE • Quality audits & certifications')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight break-words">
            {t('Registre des audits de conformité', 'Compliance audit register')}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            {t('Audits internes, externes et de certification rattachés aux normes en vigueur.', 'Internal, external and certification audits tied to the active standards.')}
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
            href="/compliance/audits"
            className="inline-flex min-h-[44px] items-center justify-center gap-2 bg-red-600 hover:bg-red-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-red-600/30 transition-colors"
          >
            <Award className="w-4 h-4" />
            {t('Normes & certifications', 'Standards & certifications')}
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            {t('Audits enregistrés', 'Recorded audits')}
            <span className="ml-2 text-xs font-mono text-slate-400">({filtered.length})</span>
          </h3>

          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-3.5 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t('N° audit, auditeur, périmètre…', 'Audit no., auditor, scope…')}
                aria-label={t('Rechercher un audit', 'Search an audit')}
                className="min-h-[44px] w-full pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-red-500"
              />
            </div>
            <select
              value={statutFilter}
              onChange={(e) => setStatutFilter(e.target.value)}
              aria-label={t('Filtrer par statut', 'Filter by status')}
              className="min-h-[44px] w-full sm:w-auto px-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-red-500"
            >
              <option value="all">{t('Tous les statuts', 'All statuses')}</option>
              {STATUTS_AUDIT.map((s) => (
                <option key={s} value={s}>
                  {s === 'en_cours' ? t('En cours', 'In progress')
                    : s === 'complete' ? t('Terminé', 'Completed')
                      : t('Annulé', 'Cancelled')}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[840px] text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">{t('N° audit', 'Audit no.')}</th>
                <th className="px-6 py-4">{t('Norme / certification', 'Standard / certificate')}</th>
                <th className="px-6 py-4">{t('Type', 'Type')}</th>
                <th className="px-6 py-4">{t('Période', 'Period')}</th>
                <th className="px-6 py-4">{t('Auditeur', 'Auditor')}</th>
                <th className="px-6 py-4">{t('Non-conformités', 'Non-conformities')}</th>
                <th className="px-6 py-4 text-right">{t('Statut', 'Status')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-slate-400">
                    {t('Chargement des audits…', 'Loading audits…')}
                  </td>
                </tr>
              ) : loadError ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-red-400">
                    {t(
                      "Le registre d'audits n'a pas pu être chargé. Vérifiez votre connexion puis réessayez.",
                      'The audit register could not be loaded. Check your connection and try again.'
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
                    {audits.length === 0
                      ? t(
                        'Aucun audit enregistré. Créez-le depuis le module QHSE & Sécurité.',
                        'No audit on record. Create one from the QHSE & Security module.'
                      )
                      : t('Aucun audit ne correspond à la recherche.', 'No audit matches your search.')}
                  </td>
                </tr>
              ) : (
                filtered.map((a) => {
                  const cert = a.certification_id ? normesById.get(a.certification_id) : undefined;
                  return (
                    <tr key={a.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-100 font-mono whitespace-nowrap">
                        {a.numero_audit || `#${a.id}`}
                      </td>
                      <td className="px-6 py-4 font-semibold text-slate-200">
                        {cert
                          ? `${cert.norme}  ${cert.numero_certificat}`
                          : t('Sans certification rattachée', 'No linked certificate')}
                      </td>
                      <td className="px-6 py-4">
                        {a.type_audit
                          ? a.type_audit === 'interne' ? t('Interne', 'Internal')
                            : a.type_audit === 'externe' ? t('Externe', 'External')
                              : a.type_audit === 'certification' ? t('Certification', 'Certification')
                                : a.type_audit
                          : ''}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {a.date_debut || a.date_fin
                          ? `${a.date_debut ? new Date(a.date_debut).toLocaleDateString(loc) : ''} → ${a.date_fin ? new Date(a.date_fin).toLocaleDateString(loc) : ''}`
                          : ''}
                      </td>
                      <td className="px-6 py-4">{a.auditeur || ''}</td>
                      <td className="px-6 py-4 max-w-[240px] truncate" title={a.non_conformites ?? undefined}>
                        {a.non_conformites || ''}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${statutAuditBadge(a.statut)}`}>
                          {(a.statut ?? '').toString().toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

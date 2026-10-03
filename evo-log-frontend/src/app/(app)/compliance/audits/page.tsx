'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, Award, RefreshCw, BadgeCheck, AlertTriangle } from 'lucide-react';
import { complianceAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

// Registre réel : table normes_certifications (router QHSE). Les seules
// valeurs affichées viennent des colonnes numero_certificat, norme, organisme,
// date_obtention, date_expiration, statut et resultat_audit.
type Certification = {
  id: number;
  numero_certificat: string;
  norme: string;
  organisme: string;
  date_obtention: string | null;
  date_expiration: string | null;
  statut: string | null;
  scope: string | null;
  resultat_audit: string | null;
};

function listeBrute(res: unknown): Certification[] {
  const body = (res as { data?: unknown })?.data ?? res;
  const inner = (body as { items?: unknown; data?: unknown })?.items
    ?? (body as { data?: unknown })?.data
    ?? body;
  return Array.isArray(inner) ? (inner as Certification[]) : [];
}

export default function ComplianceAuditsSubPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const certsQuery = useQuery({
    queryKey: ['compliance-certifications'],
    queryFn: async () => listeBrute(await complianceAPI.getCertifications()),
  });

  const certs = certsQuery.data ?? [];
  const today = new Date();
  const fmt = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString(loc) : '');

  // Taux de couverture calculé sur les certificats réellement en base :
  // certificat actif et non expiré. Rien n'est supposé ni arrondi.
  const valides = certs.filter((c) => {
    const exp = c.date_expiration ? new Date(c.date_expiration) : null;
    return c.statut === 'actif' && (!exp || exp.getTime() > today.getTime());
  });
  const couverture = certs.length > 0 ? Math.round((valides.length / certs.length) * 100) : null;

  return (
    <div className="max-w-5xl mx-auto py-6 sm:py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/compliance" className="inline-flex min-h-[44px] items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4" /> {t('Retour au registre des audits', 'Back to the audit register')}
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 sm:p-8 shadow-2xl">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800 mb-6">
          <div className="w-12 h-12 bg-red-500/10 text-red-400 rounded-2xl flex items-center justify-center border border-red-500/20 shrink-0">
            <Award className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-black break-words">
              {t('Normes & certifications', 'Standards & certifications')}
            </h1>
            <p className="text-sm text-slate-400">
              {t('Certificats ISO suivis par le système de management QHSE.', 'ISO certificates tracked by the QHSE management system.')}
            </p>
          </div>
          <button
            type="button"
            onClick={() => certsQuery.refetch()}
            disabled={certsQuery.isFetching}
            className="ml-auto inline-flex min-h-[44px] shrink-0 items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-bold text-slate-200 hover:bg-slate-700 disabled:opacity-60"
          >
            <RefreshCw className={`w-4 h-4 ${certsQuery.isFetching ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
        </div>

        {certsQuery.isLoading ? (
          <div className="p-8 text-center text-slate-400 text-sm">{t('Chargement des certifications…', 'Loading certifications…')}</div>
        ) : certsQuery.isError ? (
          <div className="p-8 rounded-2xl bg-slate-950 border border-red-500/30 text-center text-red-400 text-sm">
            {t('Le registre des certifications n’a pas pu être chargé.', 'The certification register could not be loaded.')}
            <button
              type="button"
              onClick={() => certsQuery.refetch()}
              className="block mx-auto mt-3 min-h-[44px] px-4 py-2 rounded-xl border border-slate-700 text-xs font-bold text-slate-200 hover:bg-slate-800"
            >
              {t('Réessayer', 'Retry')}
            </button>
          </div>
        ) : certs.length === 0 ? (
          <div className="p-8 rounded-2xl bg-slate-950 border border-slate-800 text-center text-slate-400 text-sm">
            {t('Aucune certification enregistrée.', 'No certificate on record.')}
          </div>
        ) : (
          <>
            <div className="mb-6 p-5 bg-slate-950 border border-slate-800 rounded-2xl flex items-start sm:items-center gap-4">
              {couverture !== null && couverture === 100 ? (
                <BadgeCheck className="w-9 h-9 text-emerald-400 shrink-0" />
              ) : (
                <AlertTriangle className="w-9 h-9 text-amber-400 shrink-0" />
              )}
              <div className="min-w-0">
                <h4 className="font-bold text-slate-200">
                  {couverture === null
                    ? t('Certificats en base : 0', 'Certificates on record: 0')
                    : t(
                      `${valides.length} certificat(s) actif(s) sur ${certs.length}  couverture ${couverture}%`,
                      `${valides.length} active certificate(s) out of ${certs.length}  ${couverture}% coverage`
                    )}
                </h4>
                <p className="text-xs text-slate-400">
                  {t('Un certificat est compté comme valide si son statut est « actif » et sa date d’expiration postérieure à aujourd’hui.', 'A certificate counts as valid when its status is “actif” and its expiry date is in the future.')}
                </p>
              </div>
            </div>

            <ul className="space-y-3">
              {certs.map((c) => {
                const exp = c.date_expiration ? new Date(c.date_expiration) : null;
                const expireBientot = exp && exp.getTime() - today.getTime() < 90 * 86400000;
                return (
                  <li key={c.id} className="p-4 sm:p-5 bg-slate-950 border border-slate-800 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-black text-slate-100">{c.norme}</span>
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 text-red-400 border border-slate-800">
                          {c.numero_certificat}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1 break-words">
                        {c.organisme} • {t('Obtenu le', 'Obtained')} {fmt(c.date_obtention)} • {t('Expire le', 'Expires')} {fmt(c.date_expiration)}
                      </p>
                      {c.resultat_audit ? (
                        <p className="text-xs text-slate-400 mt-1 break-words">
                          {t('Dernier résultat d’audit', 'Last audit result')} : {c.resultat_audit}
                        </p>
                      ) : null}
                    </div>
                    <span
                      className={`shrink-0 inline-flex items-center self-start sm:self-auto px-3 py-1 rounded-full text-xs font-semibold border ${c.statut !== 'actif'
                          ? 'bg-slate-600/20 text-slate-400 border-slate-600/40'
                          : expireBientot
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        }`}
                    >
                      {(c.statut ?? '').toString().toUpperCase()}
                      {expireBientot && c.statut === 'actif' ? ' • ' + t('expiration < 90 j', 'expiring < 90 d') : ''}
                    </span>
                  </li>
                );
              })}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}

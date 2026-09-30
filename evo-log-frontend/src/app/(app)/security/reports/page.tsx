'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen, Download, FileText, RefreshCw, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';
import { complianceAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

// Rapport = ligne réelle de la table audits_qualite. Seules les colonnes
// renvoyées par /api/v1/qhse/audits sont affichées et imprimées : le champ
// « score de conformité » n'existe nulle part en base et a donc été retiré.
interface SecurityReport {
  id: string;
  reference: string;
  scope: string;
  period: string;
  author: string;
  typeAudit: string;
  nonConformites: string;
  conclusion: string;
  status: string;
}

// Échappement HTML : les champs proviennent du backend et sont injectés dans le
// document d'impression via document.write.
function esc(v: unknown): string {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export default function SecurityReportsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const [mounted, setMounted] = useState(false);
  const [reportsList, setReportsList] = useState<SecurityReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const formatDate = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString(loc) : '');

  const chargerRapports = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await complianceAPI.getAudits();
      const raw = res?.data?.items ?? res?.data?.data ?? res?.data ?? [];
      const list = Array.isArray(raw) ? raw : [];
      setReportsList(list.map((a: any): SecurityReport => ({
        id: String(a.id ?? ''),
        reference: a.numero_audit ?? '',
        scope: a.scope ?? '',
        period: a.date_debut || a.date_fin
          ? `${formatDate(a.date_debut) || '—'} → ${formatDate(a.date_fin) || '—'}`
          : '',
        author: a.auditeur ?? '',
        typeAudit: a.type_audit ?? '',
        nonConformites: a.non_conformites ?? '',
        conclusion: a.conclusion ?? '',
        status: a.statut ?? '',
      })));
    } catch {
      setLoadError(t("Les rapports n'ont pas pu être chargés. Vérifiez votre connexion et réessayez.", 'Reports could not be loaded. Check your connection and try again.'));
      setReportsList([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setMounted(true);
    chargerRapports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">{t('Chargement des Rapports de Sécurité...', 'Loading Security Reports...')}</div>;

  // Export réel : génération d'un rapport imprimable à partir des données d'audit affichées.
  const handleExportPDF = (rep: SecurityReport) => {
    const win = window.open('', '_blank', 'width=800,height=600');
    if (!win) {
      toast.error(t("Impression impossible : la fenêtre d'impression a été bloquée par le navigateur.", 'Print blocked by the browser.'));
      return;
    }
    const ligne = (label: string, value: string) =>
      value ? `<p><strong>${esc(label)} :</strong> ${esc(value)}</p>` : '';
    win.document.write(`<!DOCTYPE html><html lang="${lang}"><head><title>${esc(t('Rapport de Sécurité', 'Security Report'))} ${esc(rep.reference || rep.id)}</title></head>
      <body style="font-family:Arial,sans-serif;padding:32px;color:#0f172a">
        <h1>${esc(t('Rapport d\'audit QHSE', 'QHSE audit report'))}</h1>
        ${ligne(t('Référence', 'Reference'), rep.reference || rep.id)}
        ${ligne(t('Périmètre', 'Scope'), rep.scope)}
        ${ligne(t('Type d\'audit', 'Audit type'), rep.typeAudit)}
        ${ligne(t('Période', 'Period'), rep.period)}
        ${ligne(t('Auditeur', 'Auditor'), rep.author)}
        ${ligne(t('Non-conformités', 'Non-conformities'), rep.nonConformites)}
        ${ligne(t('Conclusion', 'Conclusion'), rep.conclusion)}
        ${ligne(t('Statut', 'Status'), rep.status)}
        <p style="margin-top:48px">${esc(t('Édité le', 'Issued on'))} ${esc(new Date().toLocaleString(loc))} &nbsp;&nbsp; Signature : ______________________</p>
        <script>window.print()</script>
      </body></html>`);
    win.document.close();
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-xl">
        <div className="min-w-0">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-semibold mb-2 border border-red-500/20">
            <BookOpen className="w-3.5 h-3.5 shrink-0" />
            {t("QHSE • Rapports & registres d'audit", 'QHSE • Reports & audit registers')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight break-words">{t("Rapports d'audit", 'Audit reports')}</h1>
          <p className="text-slate-400 text-sm mt-1">{t("Registre des audits qualité et certifications, imprimable et signé.", 'Register of quality audits and certifications, printable and signable.')}</p>
        </div>

        <button
          onClick={() => chargerRapports()}
          disabled={loading}
          className="inline-flex min-h-[44px] shrink-0 items-center justify-center gap-2 bg-red-600 hover:bg-red-500 disabled:opacity-60 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-red-600/30 transition-colors cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {t("Recharger les rapports d'audit", 'Reload audit reports')}
        </button>
      </div>

      {/* Reports List */}
      <div className="grid grid-cols-1 gap-4">
        {loading ? (
          <div className="bg-slate-900 border border-slate-800 p-12 rounded-2xl text-center text-slate-400 text-sm">{t('Chargement des rapports…', 'Loading reports…')}</div>
        ) : loadError ? (
          <div className="bg-slate-900 border border-red-500/30 p-12 rounded-2xl text-center text-red-400 text-sm flex flex-col items-center gap-3">
            <ShieldCheck className="w-6 h-6" />
            {loadError}
            <button onClick={chargerRapports} className="min-h-[44px] px-4 py-2 rounded-xl border border-slate-700 text-xs font-bold text-slate-200 hover:bg-slate-800">{t('Réessayer', 'Retry')}</button>
          </div>
        ) : reportsList.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 p-12 rounded-2xl text-center text-slate-400 text-sm">
            <FileText className="w-8 h-8 mx-auto mb-2 text-slate-400" />
            {t('Aucun rapport d\'audit enregistré pour le moment.', 'No audit report on record yet.')}
          </div>
        ) : (
          reportsList.map(rep => (
            <div key={rep.id} className="bg-slate-900 border border-slate-800 p-5 sm:p-6 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-4 min-w-0">
                <div className="w-12 h-12 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 flex items-center justify-center shrink-0">
                  <FileText className="w-6 h-6" />
                </div>
                <div className="space-y-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-3">
                    <h3 className="font-bold text-slate-100 text-base break-words">
                      {rep.scope || rep.reference || t('Audit sans périmètre renseigné', 'Audit with no stated scope')}
                    </h3>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-950 text-red-400 border border-slate-800">
                      {rep.reference || `#${rep.id}`}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 break-words">
                    {rep.period ? `${t('Période', 'Period')} : ${rep.period} • ` : ''}
                    {rep.author ? `${t('Auditeur', 'Auditor')} : ${rep.author}` : ''}
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-4 shrink-0">
                <div className="text-right">
                  <div className="text-xs text-slate-400">{t('Statut', 'Status')}</div>
                  <div className="text-sm font-bold text-slate-200 font-mono uppercase">{rep.status || '—'}</div>
                </div>

                <button
                  onClick={() => handleExportPDF(rep)}
                  className="inline-flex min-h-[44px] items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                >
                  <Download className="w-4 h-4 text-red-400" />
                  {t('Télécharger PDF', 'Download PDF')}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

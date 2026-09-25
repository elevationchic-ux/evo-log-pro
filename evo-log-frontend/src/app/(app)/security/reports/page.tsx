'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen, Download, FileText, Plus, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';
import { complianceAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

interface SecurityReport {
  id: string;
  title: string;
  period: string;
  author: string;
  score: string;
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

  const [mounted, setMounted] = useState(false);
  const [reportsList, setReportsList] = useState<SecurityReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const chargerRapports = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await complianceAPI.getAudits();
      const raw = res?.data?.data ?? res?.data ?? [];
      const list = Array.isArray(raw) ? raw : [];
      setReportsList(list.map((a: any): SecurityReport => ({
        id: String(a.id ?? a.reference ?? ''),
        title: a.title ?? a.objet ?? a.nom ?? t('Audit de conformité', 'Compliance audit'),
        period: a.period ?? a.periode ?? a.date ?? '',
        author: a.author ?? a.redacteur ?? a.responsable ?? '',
        score: a.score ? `${a.score}%` : '',
        status: a.status ?? a.statut ?? '',
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
    win.document.write(`<!DOCTYPE html><html lang="${lang}"><head><title>${esc(t('Rapport de Sécurité', 'Security Report'))} ${esc(rep.id)}</title></head>
      <body style="font-family:Arial,sans-serif;padding:32px;color:#0f172a">
        <h1>${esc(t('Rapport de Sécurité & Conformité', 'Security & Compliance Report'))}</h1>
        <p><strong>${esc(t('Référence', 'Reference'))} :</strong> ${esc(rep.id)}</p>
        <p><strong>${esc(t('Titre', 'Title'))} :</strong> ${esc(rep.title)}</p>
        <p><strong>${esc(t('Période', 'Period'))} :</strong> ${esc(rep.period || '')}</p>
        <p><strong>${esc(t('Rédigé par', 'Authored by'))} :</strong> ${esc(rep.author || '')}</p>
        <p><strong>${esc(t('Score de conformité', 'Compliance score'))} :</strong> ${esc(rep.score || '')}</p>
        <p><strong>${esc(t('Statut', 'Status'))} :</strong> ${esc(rep.status || '')}</p>
        <p style="margin-top:48px">${esc(t('Édité le', 'Issued on'))} ${esc(new Date().toLocaleString(lang === 'en' ? 'en-US' : 'fr-FR'))} &nbsp;&nbsp; Signature : ______________________</p>
        <script>window.print()</script>
      </body></html>`);
    win.document.close();
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <BookOpen className="w-3.5 h-3.5" />
            {t("Sécurité SI • Rapports & Registres d'Audit", 'IT Security • Reports & Audit Registers')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">{t('Rapports de Sécurité & Conformité', 'Security & Compliance Reports')}</h1>
          <p className="text-slate-400 text-sm mt-1">{t("Génération des rapports d'audit, historiques de conformité et bilans de sécurité portuaire.", 'Audit report generation, compliance history and port security reviews.')}</p>
        </div>

        <button
          onClick={() => chargerRapports()}
          className="inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-all hover:scale-[1.02] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          {t("Recharger les Rapports d'Audit", 'Reload Audit Reports')}
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
            <button onClick={chargerRapports} className="px-4 py-2 rounded-xl border border-slate-700 text-xs font-bold text-slate-200 hover:bg-slate-800">{t('Réessayer', 'Retry')}</button>
          </div>
        ) : reportsList.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 p-12 rounded-2xl text-center text-slate-400 text-sm">
            <FileText className="w-8 h-8 mx-auto mb-2 text-slate-400" />
            {t('Aucun rapport de conformité pour le moment.', 'No compliance report yet.')}
          </div>
        ) : (
          reportsList.map(rep => (
            <div key={rep.id} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
                  <FileText className="w-6 h-6" />
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-bold text-slate-100 text-base">{rep.title}</h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-emerald-400 border border-slate-800">
                      {rep.id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{t('Période', 'Period')} : {rep.period || ''} • {t('Rédigé par', 'Authored by')} : {rep.author || ''}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-xs text-slate-400">{t('Score Conformité', 'Compliance Score')}</div>
                  <div className="text-lg font-black text-emerald-400 font-mono">{rep.score || ''}</div>
                </div>

                <button
                  onClick={() => handleExportPDF(rep)}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-all cursor-pointer"
                >
                  <Download className="w-4 h-4 text-emerald-400" />
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

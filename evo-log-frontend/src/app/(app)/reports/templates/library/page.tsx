'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Library,
  Search,
  Plus,
  Play,
  Copy,
  Trash2,
  RefreshCw,
  FileSpreadsheet,
  FileText,
} from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';
import { useSettings } from '@/components/layout/SettingsProvider';

interface RapportModele {
  id: number;
  numero_rapport: string;
  titre: string;
  description: string | null;
  type_rapport: string | null;
  frequence: string | null;
  statut: string;
  date_creation: string | null;
  date_generation: string | null;
  nombre_lignes: number | null;
  parametres: Record<string, unknown> | null;
}

function formatTypeIcon(typeRapport: string | null): 'EXCEL' | 'PDF' {
  const t = (typeRapport || '').toLowerCase();
  return t.includes('excel') || t.includes('csv') || t.includes('xlsx') ? 'EXCEL' : 'PDF';
}

function fmtDate(v: string | null): string {
  if (!v) return '';
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? v : d.toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' });
}

export default function ReportLibraryPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('ALL');
  const [models, setModels] = useState<RapportModele[]>([]);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/reporting/rapports', { params: { limit: 200 } });
      const data = res.data;
      const rows: RapportModele[] = Array.isArray(data) ? data : (data?.items ?? []);
      setModels(rows);
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

  const handleRunReport = async (model: RapportModele) => {
    try {
      await api.put(`/api/v1/reporting/rapports/${model.id}/generer`);
      toast.success(t(`Rapport « ${model.titre} » généré.`, `Report "${model.titre}" generated.`));
      await load();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t("Échec de la génération du rapport.", 'Report generation failed.'));
    }
  };

  const handleDuplicate = async (model: RapportModele) => {
    try {
      await api.post('/api/v1/reporting/rapports', {
        numero_rapport: `RP-${Date.now()}`,
        titre: `${model.titre} (${t('Copie', 'Copy')})`,
        type_rapport: model.type_rapport || 'divers',
        frequence: model.frequence || 'Ponctuelle',
        requetes: model.parametres && typeof model.parametres === 'object' ? model.parametres : {},
        colonnes: {},
        description: model.description || undefined,
      });
      toast.success(t('Modèle dupliqué avec succès.', 'Model duplicated successfully.'));
      await load();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Échec de la duplication.', 'Duplicate failed.'));
    }
  };

  const handleDelete = async (model: RapportModele) => {
    try {
      await api.delete(`/api/v1/reporting/rapports/${model.id}`);
      setModels((prev) => prev.filter((m) => m.id !== model.id));
      toast.success(t('Modèle retiré de la bibliothèque.', 'Model removed from the library.'));
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Échec de la suppression.', 'Delete failed.'));
    }
  };

  const filtered = models.filter((m) => {
    const matchFmt = selectedFormat === 'ALL' || formatTypeIcon(m.type_rapport) === selectedFormat;
    const q = searchQuery.toLowerCase();
    const matchQuery =
      !q ||
      (m.titre || '').toLowerCase().includes(q) ||
      (m.description || '').toLowerCase().includes(q) ||
      (m.numero_rapport || '').toLowerCase().includes(q);
    return matchFmt && matchQuery;
  });

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-4 pb-24 sm:p-6 lg:p-8 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Library className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">
              {t('Bibliothèque des Modèles Enregistrés', 'Saved Template Library')}
            </h1>
            <p className="text-sm text-slate-400">
              {t("Gestion de vos requêtes personnalisées, automatisations d'extractions et exports planifiés", 'Manage your custom queries, extraction automations and scheduled exports')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <Link
            href="/reports/custom/builder"
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-500 transition"
          >
            <Plus className="w-4 h-4" /> {t('Créer un Nouveau Modèle', 'Create New Template')}
          </Link>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder={t('Rechercher un modèle enregistré...', 'Search a saved template...')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex gap-2 flex-wrap">
          {['ALL', 'EXCEL', 'PDF'].map((fmt) => (
            <button
              key={fmt}
              onClick={() => setSelectedFormat(fmt)}
              className={`px-3.5 py-1.5 rounded-xl border text-xs font-semibold transition-colors ${selectedFormat === fmt
                  ? 'bg-indigo-600 text-white border-indigo-500'
                  : 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
                }`}
            >
              {fmt === 'ALL' ? t('Tous les formats', 'All formats') : fmt}
            </button>
          ))}
        </div>
      </div>

      {/* Models List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.length === 0 ? (
          <div className="col-span-full p-12 text-center bg-slate-900/60 border border-dashed border-slate-800 rounded-2xl">
            <Library className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="font-semibold text-white text-base">
              {loaded
                ? t('Aucun modèle de rapport enregistré', 'No saved report template')
                : t('Chargement…', 'Loading…')}
            </h3>
            {loaded && (
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                {t(
                  'Utilisez le générateur personnalisé pour configurer vos jeux de données et enregistrer vos canevas réutilisables.',
                  'Use the custom builder to configure your datasets and save reusable report templates.',
                )}
              </p>
            )}
          </div>
        ) : (
          filtered.map((model) => {
            const fmt = formatTypeIcon(model.type_rapport);
            return (
              <div
                key={model.id}
                className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3 hover:border-indigo-500/50 transition-all flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex items-center gap-2">
                      {fmt === 'EXCEL' ? (
                        <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
                          <FileSpreadsheet className="w-4 h-4" />
                        </span>
                      ) : (
                        <span className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
                          <FileText className="w-4 h-4" />
                        </span>
                      )}
                      <span className="text-xs font-bold text-slate-400 font-mono">{model.numero_rapport}</span>
                    </div>
                    <span className="text-[11px] font-mono text-slate-500 text-right">
                      {t('Dernière exécution', 'Last run')}: {fmtDate(model.date_generation)}
                    </span>
                  </div>

                  <h3 className="font-bold text-base text-white">{model.titre}</h3>
                  <p className="text-xs text-slate-400">{model.description || t('Sans description', 'No description')}</p>

                  <div className="flex flex-wrap gap-1.5 text-[11px]">
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {model.frequence || fmt}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {model.statut}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                      {model.nombre_lignes ?? 0} {t('lignes', 'rows')}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleDuplicate(model)}
                      className="p-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-400 transition"
                      title={t('Dupliquer Modèle', 'Duplicate Template')}
                    >
                      <Copy className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(model)}
                      className="p-1.5 rounded-lg border border-slate-700 hover:bg-rose-500/10 text-rose-400 transition"
                      title={t('Supprimer Modèle', 'Delete Template')}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <button
                    onClick={() => handleRunReport(model)}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition"
                  >
                    <Play className="w-3.5 h-3.5" /> {t('Exécuter & Télécharger', 'Run & Download')}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

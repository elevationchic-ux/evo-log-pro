'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  FileCheck, Plus, Search, ArrowLeft, CheckCircle2,
  AlertTriangle, Loader2
} from 'lucide-react';
import apiClient from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

const REGISTRY = 'veille-conformite';

interface ConformiteItem {
  id: number;
  article_reference: string;
  theme: string;
  exigence_legale: string;
  niveau_conformite: string;
  derniere_revue: string;
  actions_mises_en_oeuvre: string;
}

export default function QhseOhadaCompliancePage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [items, setItems] = useState<ConformiteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    article_reference: '',
    theme: '',
    exigence_legale: '',
    niveau_conformite: 'CONFORME',
    derniere_revue: '',
    actions_mises_en_oeuvre: '',
  });

  const fetchItems = useCallback(async () => {
    try {
      const res = await apiClient.get(`/api/v1/registres/${REGISTRY}`);
      const list = Array.isArray(res?.data) ? res.data : (res?.data?.items || []);
      setItems(
        list.map((r: any) => ({
          id: r.id,
          article_reference: r.article_reference || r.reference || '',
          theme: r.theme || '',
          exigence_legale: r.exigence_legale || '',
          niveau_conformite: r.statut || r.niveau_conformite || 'CONFORME',
          derniere_revue: r.derniere_revue || '',
          actions_mises_en_oeuvre: r.actions_mises_en_oeuvre || '',
        }))
      );
    } catch {
      toast.error(t('Impossible de charger le registre de conformité', 'Unable to load the compliance register'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post(`/api/v1/registres/${REGISTRY}`, {
        reference: formData.article_reference,
        statut: formData.niveau_conformite,
        ...formData,
      });
      toast.success(t('Exigence enregistrée dans le registre', 'Requirement recorded in the register'));
      setIsModalOpen(false);
      setFormData({
        article_reference: '', theme: '', exigence_legale: '',
        niveau_conformite: 'CONFORME', derniere_revue: '', actions_mises_en_oeuvre: '',
      });
      fetchItems();
    } catch {
      toast.error(t('Erreur réseau  enregistrement impossible', 'Network error  could not save'));
    } finally {
      setSaving(false);
    }
  };

  const filtered = items.filter(item =>
    item.article_reference.toLowerCase().includes(search.toLowerCase()) ||
    item.theme.toLowerCase().includes(search.toLowerCase()) ||
    item.exigence_legale.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Centre Sécurité QHSE', 'QHSE Safety Center')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Conformité Légale & Hygiène du Travail', 'Legal Compliance & Occupational Hygiene')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex flex-wrap items-center gap-2">
              {t('Veille Réglementaire & Conformité Hygiène / Sécurité', 'Regulatory Watch & Hygiene / Safety Compliance')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30 font-mono">
                KQHS_OHD
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Registre de conformité légale Code du Travail Camerounais, arrêtés MTPS et normes de prévention CEMAC', 'Compliance register for Cameroonian Labour Code legal requirements, MTPS decrees and CEMAC prevention standards')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-sm shadow-lg shadow-purple-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Ajouter une Exigence Légale', 'Add a Legal Requirement')}
          </button>
        </div>
      </div>

      {/* Main card */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder={t('Rechercher article, texte de loi, exigence...', 'Search article, law text, requirement...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 flex items-center justify-center gap-2 text-slate-400">
            <Loader2 className="w-5 h-5 animate-spin" />
            {t('Chargement du registre...', 'Loading register...')}
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <FileCheck className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">
              {t('Aucune exigence enregistrée', 'No requirement recorded')}
            </h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Le registre de veille réglementaire est vide. Enregistrez les textes légaux applicables à votre structure.', 'The regulatory watch register is empty. Record the legal texts applicable to your organization.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Ajouter une première exigence', 'Add a first requirement')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(item => (
                <div key={item.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-mono text-xs font-medium text-purple-400 break-all">{item.article_reference}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border flex items-center gap-1 shrink-0 ${item.niveau_conformite === 'ACTION_REQUISE'
                        ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      }`}>
                      {item.niveau_conformite === 'ACTION_REQUISE'
                        ? <AlertTriangle className="w-3 h-3" />
                        : <CheckCircle2 className="w-3 h-3" />}
                      {item.niveau_conformite === 'ACTION_REQUISE' ? t('Action requise', 'Action required') : t('Conforme', 'Compliant')}
                    </span>
                  </div>
                  <div className="font-semibold text-white text-sm">{item.theme}</div>
                  <div className="text-xs text-slate-300">{item.exigence_legale}</div>
                  {item.derniere_revue && (
                    <div className="text-xs font-mono text-slate-400">
                      {t('Dernier contrôle', 'Last check')}: {item.derniere_revue}
                    </div>
                  )}
                  {item.actions_mises_en_oeuvre && (
                    <div className="text-xs text-emerald-400">{item.actions_mises_en_oeuvre}</div>
                  )}
                </div>
              ))}
            </div>
            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                  <tr>
                    <th className="py-3 px-4 rounded-l-xl">{t('Référence Légale', 'Legal Reference')}</th>
                    <th className="py-3 px-4">{t('Thématique', 'Topic')}</th>
                    <th className="py-3 px-4">{t('Exigence Réglementaire', 'Regulatory Requirement')}</th>
                    <th className="py-3 px-4">{t('Dernier Contrôle', 'Last Check')}</th>
                    <th className="py-3 px-4">{t('Dispositions Prises', 'Measures Taken')}</th>
                    <th className="py-3 px-4 rounded-r-xl">{t('Statut', 'Status')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(item => (
                    <tr key={item.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-purple-400">{item.article_reference}</td>
                      <td className="py-3.5 px-4 font-semibold text-white">{item.theme}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-300 max-w-xs">{item.exigence_legale}</td>
                      <td className="py-3.5 px-4 text-xs font-mono text-slate-400">{item.derniere_revue || ''}</td>
                      <td className="py-3.5 px-4 text-xs text-emerald-400 max-w-xs">{item.actions_mises_en_oeuvre || ''}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border flex items-center gap-1 w-fit ${item.niveau_conformite === 'ACTION_REQUISE'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          }`}>
                          {item.niveau_conformite === 'ACTION_REQUISE'
                            ? <AlertTriangle className="w-3 h-3" />
                            : <CheckCircle2 className="w-3 h-3" />}
                          {item.niveau_conformite === 'ACTION_REQUISE' ? t('Action requise', 'Action required') : t('Conforme', 'Compliant')}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Modal Ajout Exigence */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-purple-400" />
              {t('Ajouter une Exigence Légale de Sécurité', 'Add a Safety Legal Requirement')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t("Enregistrement dans le registre de veille réglementaire de l'entreprise", 'Recording in the company regulatory watch register')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Texte de Référence / Article *', 'Reference Text / Article *')}</label>
                <input
                  type="text"
                  required
                  value={formData.article_reference}
                  onChange={e => setFormData({ ...formData, article_reference: e.target.value })}
                  placeholder={t('Ex: Arrêté n° 018/MTPS/SG/CJ', 'e.g. Decree No. 018/MTPS/SG/CJ')}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Thématique Couverte', 'Topic Covered')}</label>
                <input
                  type="text"
                  value={formData.theme}
                  onChange={e => setFormData({ ...formData, theme: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Obligation Légale *', 'Legal Obligation *')}</label>
                <textarea
                  rows={2}
                  required
                  value={formData.exigence_legale}
                  onChange={e => setFormData({ ...formData, exigence_legale: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Niveau de Conformité', 'Compliance Level')}</label>
                  <select
                    value={formData.niveau_conformite}
                    onChange={e => setFormData({ ...formData, niveau_conformite: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="CONFORME">{t('Conforme', 'Compliant')}</option>
                    <option value="ACTION_REQUISE">{t('Action requise', 'Action required')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Dernier Contrôle', 'Last Check')}</label>
                  <input
                    type="date"
                    value={formData.derniere_revue}
                    onChange={e => setFormData({ ...formData, derniere_revue: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Mesures Mises en Œuvre', 'Measures Implemented')}</label>
                <textarea
                  rows={2}
                  value={formData.actions_mises_en_oeuvre}
                  onChange={e => setFormData({ ...formData, actions_mises_en_oeuvre: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-lg transition flex items-center gap-2"
                >
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('Enregistrer dans le Registre', 'Save to Register')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

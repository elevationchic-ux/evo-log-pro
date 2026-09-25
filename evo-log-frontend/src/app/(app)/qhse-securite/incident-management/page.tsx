'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  AlertTriangle, Plus, Search, ArrowLeft, RefreshCw, ShieldAlert
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

interface IncidentInvestigation {
  id: number;
  accident_id: number | null;
  code_incident: string;
  titre: string;
  responsable_enquete: string;
  cause_racine: string;
  action_corrective: string;
  echeance: string;
  statut: string;
}

export default function QhseIncidentManagementPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [investigations, setInvestigations] = useState<IncidentInvestigation[]>([]);
  const [accidents, setAccidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [closingId, setClosingId] = useState<number | null>(null);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    accident_id: '' as string | number,
    responsable_enquete: '',
    cause_racine: '',
    action_corrective: '',
    echeance: '',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [inv, acc] = await Promise.all([
        apiClient.get('/api/v1/qhse/investigations', { params: { limit: 200 } }),
        apiClient.get('/api/v1/qhse/accidents', { params: { limit: 200 } }).catch(() => null),
      ]);
      setAccidents(Array.isArray(acc?.data?.items) ? acc.data.items : []);
      const rows = Array.isArray(inv?.data?.items) ? inv.data.items : [];
      const accById: Record<number, any> = {};
      setInvestigations(rows.map((i: any) => {
        const a = (Array.isArray(acc?.data?.items) ? acc.data.items : []).find((x: any) => x.id === i.accident_id);
        if (a) accById[a.id] = a;
        return {
          id: i.id,
          accident_id: i.accident_id,
          code_incident: i.numero_investigation,
          titre: a ? `${a.type_accident}  ${a.lieu}` : `${t('Enquête', 'Investigation')} #${i.accident_id}`,
          responsable_enquete: i.investigateur,
          cause_racine: i.causes_racines || i.causes_directes || '',
          action_corrective: i.mesures_correctives || '',
          echeance: i.date_investigation || '',
          statut: (i.statut || 'en_cours').toUpperCase(),
        };
      }));
    } catch {
      toast.error(t('Les enquêtes n\'ont pas pu être chargées. Vérifiez votre connexion.', 'Investigations could not be loaded. Check your connection.'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.accident_id) {
      toast.error(t('Sélectionnez l\'incident à la base de l\'enquête.', 'Select the source incident for the investigation.'));
      return;
    }
    setSaving(true);
    try {
      await apiClient.post('/api/v1/qhse/investigations', {
        accident_id: Number(formData.accident_id),
        date_investigation: new Date().toISOString().slice(0, 10),
        investigateur: formData.responsable_enquete,
        causes_racines: formData.cause_racine,
        mesures_correctives: formData.action_corrective,
        delai_mise_oeuvre: formData.echeance
          ? Math.max(0, Math.round((new Date(formData.echeance).getTime() - Date.now()) / 86400000))
          : 0,
        responsable_suivi: formData.responsable_enquete,
        conclusions: formData.echeance ? `${t('Échéance', 'Due date')}: ${formData.echeance}` : '',
      });
      toast.success(t('Enquête CAPA ouverte et enregistrée.', 'CAPA investigation opened and saved.'));
      setIsModalOpen(false);
      setFormData(f => ({ ...f, accident_id: '', cause_racine: '', action_corrective: '' }));
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec de l\'ouverture de l\'enquête.', 'Failed to open the investigation.'));
    } finally {
      setSaving(false);
    }
  };

  const cloturerAction = async (item: IncidentInvestigation) => {
    setClosingId(item.id);
    try {
      await apiClient.put(`/api/v1/qhse/investigations/${item.id}`, { statut: 'complete' });
      toast.success(t('Plan d\'action clôturé.', 'Action plan closed.'));
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec de la clôture.', 'Closing failed.'));
    } finally {
      setClosingId(null);
    }
  };

  const filtered = investigations.filter(i =>
    i.titre.toLowerCase().includes(search.toLowerCase()) ||
    i.code_incident.toLowerCase().includes(search.toLowerCase()) ||
    i.action_corrective.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Centre Sécurité QHSE', 'QHSE Safety Center')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Gestion des Incidents & Arbre des Causes', 'Incident Management & Root-Cause Analysis')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-red-500/10 text-red-400 rounded-xl border border-red-500/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2 flex-wrap">
              {t('Plan d\'Actions Correctives & Préventives (CAPA)', 'Corrective & Preventive Action Plan (CAPA)')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/30 font-mono">
                KQHS_INC
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Analyse des causes profondes (5 Pourquoi / Ishikawa), assignation des responsabilités et suivi des clôtures', 'Deep root-cause analysis (5 Whys / Ishikawa), responsibility assignment and closure tracking')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={load} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-700 text-slate-300 text-sm hover:bg-slate-800">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-medium text-sm shadow-lg shadow-red-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Ouvrir une Enquête CAPA', 'Open a CAPA Investigation')}
          </button>
        </div>
      </div>

      {/* Main Table card */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder={t('Rechercher code CAPA, titre, action...', 'Search CAPA code, title, action...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-red-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400 text-sm">{t('Chargement des enquêtes…', 'Loading investigations…')}</div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <ShieldAlert className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucun plan d\'action CAPA actif', 'No active CAPA plan')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {accidents.length === 0
                ? t('Ouvrez d\'abord un signalement depuis le centre QHSE, puis déclenchez l\'enquête associée.', 'First open a report from the QHSE center, then trigger the linked investigation.')
                : t('Tous les incidents ont été traités ou aucune anomalie n\'a nécessité l\'ouverture d\'un plan d\'actions correctives.', 'All incidents have been handled, or no anomaly required opening a corrective action plan.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Ouvrir un premier dossier d\'enquête', 'Open the first investigation file')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(item => (
                <div key={item.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-sm font-bold text-red-400">{item.code_incident}</span>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${item.statut === 'CLOTURE' || item.statut === 'COMPLETE'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>{item.statut}</span>
                  </div>
                  <div className="text-sm font-semibold text-white">{item.titre}</div>
                  <div className="text-xs text-slate-400">{item.cause_racine}</div>
                  <div className="text-xs text-emerald-400">{item.action_corrective}</div>
                  {item.statut !== 'CLOTURE' && item.statut !== 'COMPLETE' && (
                    <button
                      onClick={() => cloturerAction(item)}
                      disabled={closingId === item.id}
                      className="w-full px-3 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 disabled:opacity-60 text-emerald-400 text-xs font-medium rounded-lg border border-emerald-500/30 transition"
                    >
                      {closingId === item.id ? t('Clôture…', 'Closing…') : t('Clôturer Action', 'Close Action')}
                    </button>
                  )}
                </div>
              ))}
            </div>
            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                  <tr>
                    <th className="py-3 px-4 rounded-l-xl">{t('Réf. CAPA', 'CAPA Ref.')}</th>
                    <th className="py-3 px-4">{t('Incident à la base', 'Source Incident')}</th>
                    <th className="py-3 px-4">{t('Cause Racine Identifiée', 'Identified Root Cause')}</th>
                    <th className="py-3 px-4">{t('Action Corrective Retenue', 'Selected Corrective Action')}</th>
                    <th className="py-3 px-4">{t('Responsable', 'Owner')}</th>
                    <th className="py-3 px-4">{t('Date Enquête', 'Investigation Date')}</th>
                    <th className="py-3 px-4">{t('Statut', 'Status')}</th>
                    <th className="py-3 px-4 rounded-r-xl text-right">{t('Action', 'Action')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(item => (
                    <tr key={item.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-red-400">{item.code_incident}</td>
                      <td className="py-3.5 px-4 font-semibold text-white">{item.titre}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-300 max-w-xs truncate">{item.cause_racine}</td>
                      <td className="py-3.5 px-4 text-xs text-emerald-400 max-w-xs truncate">{item.action_corrective}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-400">{item.responsable_enquete}</td>
                      <td className="py-3.5 px-4 text-xs font-mono">{item.echeance || ''}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${item.statut === 'CLOTURE' || item.statut === 'COMPLETE'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}>{item.statut}</span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        {item.statut !== 'CLOTURE' && item.statut !== 'COMPLETE' && (
                          <button
                            onClick={() => cloturerAction(item)}
                            disabled={closingId === item.id}
                            className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 disabled:opacity-60 text-emerald-400 text-xs rounded border border-emerald-500/30 transition"
                          >
                            {closingId === item.id ? t('Clôture…', 'Closing…') : t('Clôturer Action', 'Close Action')}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Modal Enquête CAPA */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              {t('Ouvrir un Plan d\'Action CAPA', 'Open a CAPA Action Plan')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Enquête de sécurité et attribution d\'actions correctives', 'Safety investigation and corrective action assignment')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Incident à la base de l\'enquête *', 'Source incident *')}</label>
                {accidents.length === 0 ? (
                  <p className="text-xs text-slate-400 bg-slate-800/60 border border-dashed border-slate-700 rounded-xl px-3 py-2.5">
                    {t('Aucun incident enregistré. ', 'No incident recorded. ')}
                    <Link href="/qhse-securite/dashboard" className="text-red-400 underline">{t('Déclarez d\'abord un signalement.', 'Declare a report first.')}</Link>
                  </p>
                ) : (
                  <select
                    required
                    value={formData.accident_id}
                    onChange={e => setFormData({ ...formData, accident_id: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  >
                    <option value="">{t(' Sélectionner un incident ', ' Select an incident ')}</option>
                    {accidents.map((a: any) => (
                      <option key={a.id} value={a.id}>
                        {a.numero_accident}  {a.type_accident} ({a.lieu})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Responsable Enquête', 'Investigation Owner')}</label>
                  <input
                    type="text"
                    required
                    value={formData.responsable_enquete}
                    onChange={e => setFormData({ ...formData, responsable_enquete: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Date d\'Échéance', 'Due Date')}</label>
                  <input
                    type="date"
                    value={formData.echeance}
                    onChange={e => setFormData({ ...formData, echeance: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Cause Racine Déterminée (Arbre des Causes) *', 'Root Cause (Cause Tree) *')}</label>
                <textarea
                  rows={2}
                  required
                  value={formData.cause_racine}
                  onChange={e => setFormData({ ...formData, cause_racine: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Action Corrective / Mesure d\'Amélioration *', 'Corrective Action / Improvement Measure *')}</label>
                <textarea
                  rows={2}
                  required
                  value={formData.action_corrective}
                  onChange={e => setFormData({ ...formData, action_corrective: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
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
                  className="px-5 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-60 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  {saving ? t('Enregistrement…', 'Saving…') : t('Valider le Plan d\'Action', 'Confirm Action Plan')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Anchor, Plus, RefreshCw, Search, ArrowLeft,
  Activity, CheckCircle2, Loader2
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { useSettings } from '@/components/layout/SettingsProvider';

const REGISTRY = 'operations-quai';

interface OperationQuai {
  id: number;
  navire_nom: string;
  quai: string;
  grue_assignee: string;
  equipe_dockers: string;
  statut: string;
  mouvements_prevus: number;
  mouvements_realises: number;
  cadence_horaire: number;
  heure_debut?: string;
}

export default function PortOperationsQuaiPage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [operations, setOperations] = useState<OperationQuai[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [progressOp, setProgressOp] = useState<OperationQuai | null>(null);
  const [progressValue, setProgressValue] = useState(0);

  const [formData, setFormData] = useState({
    navire_nom: '',
    quai: '',
    grue_assignee: '',
    equipe_dockers: '',
    mouvements_prevus: 0,
    cadence_horaire: 0,
    heure_debut: '',
  });

  const fetchOperations = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/registres/${REGISTRY}`);
      const list = Array.isArray(res?.data) ? res.data : (res?.data?.items || []);
      setOperations(
        list.map((r: any) => ({
          id: r.id,
          navire_nom: r.navire_nom || r.reference || '',
          quai: r.quai || '',
          grue_assignee: r.grue_assignee || '',
          equipe_dockers: r.equipe_dockers || '',
          statut: r.statut || 'EN_COURS',
          mouvements_prevus: Number(r.mouvements_prevus) || 0,
          mouvements_realises: Number(r.mouvements_realises) || 0,
          cadence_horaire: Number(r.cadence_horaire) || 0,
          heure_debut: r.heure_debut || '',
        }))
      );
    } catch {
      setOperations([]);
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    fetchOperations();
  }, [fetchOperations]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post(`/api/v1/registres/${REGISTRY}`, {
        reference: formData.navire_nom,
        statut: 'EN_COURS',
        mouvements_realises: 0,
        ...formData,
      });
      toast.success(t('Opération de quai ouverte', 'Wharf operation opened'));
      setIsModalOpen(false);
      setFormData({
        navire_nom: '', quai: '', grue_assignee: '', equipe_dockers: '',
        mouvements_prevus: 0, cadence_horaire: 0, heure_debut: '',
      });
      fetchOperations();
    } catch {
      toast.error(t('Erreur réseau  enregistrement impossible', 'Network error  could not save'));
    } finally {
      setSaving(false);
    }
  };

  const saveProgress = async () => {
    if (!progressOp) return;
    try {
      const terminé = progressValue >= progressOp.mouvements_prevus && progressOp.mouvements_prevus > 0;
      await apiClient.put(`/api/v1/registres/${REGISTRY}/${progressOp.id}`, {
        mouvements_realises: progressValue,
        statut: terminé ? 'A_TERME' : 'EN_COURS',
      });
      toast.success(t('Progression enregistrée', 'Progress saved'));
      setProgressOp(null);
      fetchOperations();
    } catch {
      toast.error(t('Erreur réseau  mise à jour impossible', 'Network error  could not update'));
    }
  };

  const filtered = operations.filter(op =>
    op.navire_nom.toLowerCase().includes(search.toLowerCase()) ||
    op.quai.toLowerCase().includes(search.toLowerCase()) ||
    op.grue_assignee.toLowerCase().includes(search.toLowerCase())
  );

  const progressPct = (op: OperationQuai) =>
    op.mouvements_prevus > 0 ? Math.min(100, Math.round((op.mouvements_realises / op.mouvements_prevus) * 100)) : 0;

  const statutBadge = (statut: string) => (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border flex items-center gap-1 w-fit ${statut === 'A_TERME'
        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
        : 'bg-sky-500/10 text-sky-400 border-sky-500/20'
      }`}>
      {statut === 'A_TERME' ? <CheckCircle2 className="w-3 h-3" /> : <Activity className="w-3 h-3" />}
      {statut === 'A_TERME' ? t('Terminé', 'Completed') : t('En cours', 'In progress')}
    </span>
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Opérations de Quai & Manutention', 'Wharf Operations & Stevedoring')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-sky-500/10 text-sky-400 rounded-xl border border-sky-500/20">
            <Anchor className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex flex-wrap items-center gap-2">
              {t('Opérations de Quai & Manutention Portuaire', 'Wharf & Port Stevedoring Operations')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30 font-mono">
                KACC_OPS
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Pilotage des grues, affectation des shifts dockers et cadences de déchargement/chargement', 'Crane supervision, docker shift assignment and discharge/loading rates')}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={fetchOperations}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm shadow-lg shadow-sky-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Ouvrir une Opération', 'Open an Operation')}
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
              placeholder={t('Rechercher navire, quai, grue...', 'Search vessel, berth, crane...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 flex items-center justify-center gap-2 text-slate-400">
            <Loader2 className="w-5 h-5 animate-spin" />
            {t('Chargement des opérations...', 'Loading operations...')}
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Anchor className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucune opération de quai en cours', 'No wharf operation in progress')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Ouvrez une opération pour affecter une grue, une équipe docker et suivre la cadence de manutention.', 'Open an operation to assign a crane, a docker crew and track the handling rate.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Ouvrir une première opération', 'Open a first operation')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(op => (
                <div key={op.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="font-semibold text-white text-sm">{op.navire_nom}</div>
                      <div className="text-xs text-slate-400">{op.quai || ''} • {op.grue_assignee || ''}</div>
                    </div>
                    {statutBadge(op.statut)}
                  </div>
                  <div className="text-xs text-slate-400">{op.equipe_dockers || ''}</div>
                  <div>
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>{op.mouvements_realises} / {op.mouvements_prevus || ''} {t('mouvements', 'moves')}</span>
                      <span>{progressPct(op)}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-sky-500 rounded-full transition-all" style={{ width: `${progressPct(op)}%` }} />
                    </div>
                  </div>
                  {op.statut !== 'A_TERME' && (
                    <button
                      onClick={() => { setProgressOp(op); setProgressValue(op.mouvements_realises); }}
                      className="w-full px-3 py-1.5 rounded-lg bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 border border-sky-500/30 text-xs font-medium transition"
                    >
                      {t('Mettre à jour la progression', 'Update progress')}
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
                    <th className="py-3 px-4 rounded-l-xl">{t('Navire', 'Vessel')}</th>
                    <th className="py-3 px-4">{t('Quai', 'Berth')}</th>
                    <th className="py-3 px-4">{t('Grue Affectée', 'Assigned Crane')}</th>
                    <th className="py-3 px-4">{t('Équipe Dockers', 'Docker Crew')}</th>
                    <th className="py-3 px-4">{t('Progression', 'Progress')}</th>
                    <th className="py-3 px-4">{t('Cadence /h', 'Rate /h')}</th>
                    <th className="py-3 px-4">{t('Statut', 'Status')}</th>
                    <th className="py-3 px-4 rounded-r-xl text-right">{t('Actions', 'Actions')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(op => (
                    <tr key={op.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-semibold text-white">{op.navire_nom}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-300">{op.quai || ''}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-200">{op.grue_assignee || ''}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-400">{op.equipe_dockers || ''}</td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-sky-500 rounded-full transition-all" style={{ width: `${progressPct(op)}%` }} />
                          </div>
                          <span className="text-xs font-mono text-slate-400 whitespace-nowrap">
                            {op.mouvements_realises}/{op.mouvements_prevus || ''}
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-xs text-white">
                        {op.cadence_horaire ? `${op.cadence_horaire} EVP/h` : ''}
                      </td>
                      <td className="py-3.5 px-4">{statutBadge(op.statut)}</td>
                      <td className="py-3.5 px-4 text-right">
                        {op.statut !== 'A_TERME' && (
                          <button
                            onClick={() => { setProgressOp(op); setProgressValue(op.mouvements_realises); }}
                            className="px-2.5 py-1 rounded-lg bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 border border-sky-500/30 text-xs font-medium transition"
                          >
                            {t('Progression', 'Progress')}
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

      {/* Modal Nouvelle Opération */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Anchor className="w-5 h-5 text-sky-400" />
              {t('Ouvrir une Opération de Quai', 'Open a Wharf Operation')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Affectation grue + équipe et objectif de mouvements', 'Crane and crew assignment with a moves target')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Nom du Navire *', 'Vessel Name *')}</label>
                <input
                  type="text"
                  required
                  value={formData.navire_nom}
                  onChange={e => setFormData({ ...formData, navire_nom: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Poste à Quai', 'Berth')}</label>
                  <input
                    type="text"
                    value={formData.quai}
                    onChange={e => setFormData({ ...formData, quai: e.target.value })}
                    placeholder={t('Ex: Poste 14', 'e.g. Berth 14')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Grue Affectée', 'Assigned Crane')}</label>
                  <input
                    type="text"
                    value={formData.grue_assignee}
                    onChange={e => setFormData({ ...formData, grue_assignee: e.target.value })}
                    placeholder={t('Ex: Portique Post-Panamax 01', 'e.g. Post-Panamax Gantry 01')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Équipe Dockers', 'Docker Crew')}</label>
                  <input
                    type="text"
                    value={formData.equipe_dockers}
                    onChange={e => setFormData({ ...formData, equipe_dockers: e.target.value })}
                    placeholder={t('Ex: Équipe Alpha (Shift A)', 'e.g. Alpha Crew (Shift A)')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Heure de Début', 'Start Time')}</label>
                  <input
                    type="datetime-local"
                    value={formData.heure_debut}
                    onChange={e => setFormData({ ...formData, heure_debut: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Mouvements Prévus (EVP)', 'Planned Moves (TEU)')}</label>
                  <input
                    type="number"
                    min={0}
                    value={formData.mouvements_prevus || ''}
                    onChange={e => setFormData({ ...formData, mouvements_prevus: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Cadence Objectif (/h)', 'Target Rate (/h)')}</label>
                  <input
                    type="number"
                    min={0}
                    value={formData.cadence_horaire || ''}
                    onChange={e => setFormData({ ...formData, cadence_horaire: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
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
                  className="px-5 py-2 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-lg transition flex items-center gap-2"
                >
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('Ouvrir l\'Opération', 'Open the Operation')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Progression */}
      {progressOp && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-sm w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Activity className="w-5 h-5 text-sky-400" />
              {t('Progression  ', 'Progress  ')}{progressOp.navire_nom}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {progressOp.mouvements_prevus > 0
                ? `${progressOp.mouvements_realises} / ${progressOp.mouvements_prevus} ${t('mouvements réalisés', 'moves completed')}`
                : t('Saisissez les mouvements réalisés à ce jour.', 'Enter the moves completed so far.')}
            </p>
            <input
              type="number"
              min={0}
              value={progressValue || ''}
              onChange={e => setProgressValue(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500 font-mono"
            />
            <div className="flex items-center justify-end gap-3 pt-4 mt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setProgressOp(null)}
                className="px-4 py-2 text-sm text-slate-400 hover:text-white"
              >
                {t('Annuler', 'Cancel')}
              </button>
              <button
                type="button"
                onClick={saveProgress}
                className="px-5 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
              >
                {t('Enregistrer', 'Save')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

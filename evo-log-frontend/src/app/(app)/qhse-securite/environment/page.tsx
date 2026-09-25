'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import { Leaf, Plus, Search, ArrowLeft, RefreshCw } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

const REGISTRY = 'bsdd-bordereaux';

interface DechetEnvironnement {
  id: number;
  bordereau_numero: string | null;
  type_dechet: string;
  quantite: number | string;
  unite: string;
  centre_traitement: string;
  date_evacuation: string;
  statut: string;
}

export default function QhseEnvironmentPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [dechets, setDechets] = useState<DechetEnvironnement[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [validatingId, setValidatingId] = useState<number | null>(null);

  const [formData, setFormData] = useState({
    type_dechet: '',
    quantite: 100,
    unite: 'Litres',
    centre_traitement: '',
    date_evacuation: new Date().toISOString().slice(0, 10),
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/registres/${REGISTRY}`);
      const rows = Array.isArray(res?.data?.items) ? res.data.items : [];
      setDechets(rows.map((r: any) => ({
        id: r.id,
        bordereau_numero: r.reference,
        type_dechet: r.type_dechet || '',
        quantite: r.quantite ?? '',
        unite: r.unite || '',
        centre_traitement: r.centre_traitement || '',
        date_evacuation: r.date_evacuation || '',
        statut: r.statut || 'EN_COURS',
      })));
    } catch {
      toast.error(t('Les bordereaux n\'ont pas pu être chargés. Vérifiez votre connexion.', 'Waste manifests could not be loaded. Check your connection.'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post(`/api/v1/registres/${REGISTRY}`, {
        type_dechet: formData.type_dechet,
        quantite: Number(formData.quantite),
        unite: formData.unite,
        centre_traitement: formData.centre_traitement,
        date_evacuation: formData.date_evacuation,
        statut: 'EN_COURS',
      });
      toast.success(t('Bordereau BSDD émis et enregistré.', 'BSDD manifest issued and recorded.'));
      setIsModalOpen(false);
      setFormData(f => ({ ...f, type_dechet: '', centre_traitement: '' }));
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec de l\'émission du bordereau.', 'Failed to issue the manifest.'));
    } finally {
      setSaving(false);
    }
  };

  const validerBordereau = async (d: DechetEnvironnement) => {
    setValidatingId(d.id);
    try {
      await apiClient.put(`/api/v1/registres/${REGISTRY}/${d.id}`, { statut: 'VALIDE' });
      toast.success(t('Bordereau validé (traçabilité MARPOL / ANAC).', 'Manifest validated (MARPOL / ANAC traceability).'));
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec de la validation.', 'Validation failed.'));
    } finally {
      setValidatingId(null);
    }
  };

  const filtered = dechets.filter(d =>
    d.type_dechet.toLowerCase().includes(search.toLowerCase()) ||
    (d.bordereau_numero || '').toLowerCase().includes(search.toLowerCase()) ||
    d.centre_traitement.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Centre Sécurité QHSE', 'QHSE Safety Center')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Environnement, MARPOL & Gestion des Déchets', 'Environment, MARPOL & Waste Management')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-green-500/10 text-green-400 rounded-xl border border-green-500/20">
            <Leaf className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2 flex-wrap">
              {t('Management Environnemental & Norme MARPOL', 'Environmental Management & MARPOL Standard')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/30 font-mono">
                KQHS_ENV
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Traçabilité des déchets portuaires, hydrocarbures, valorisation et respect de la convention MARPOL 73/78', 'Traceability of port waste, hydrocarbons, recovery and compliance with MARPOL 73/78')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={load} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-700 text-slate-300 text-sm hover:bg-slate-800">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-green-600 hover:bg-green-500 text-white font-medium text-sm shadow-lg shadow-green-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Émettre un Bordereau BSDD', 'Issue a BSDD Manifest')}
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
              placeholder={t('Rechercher par type de déchet, N° bordereau...', 'Search by waste type, manifest No....')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-green-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400 text-sm">{t('Chargement des bordereaux…', 'Loading manifests…')}</div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Leaf className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucun bordereau de déchet enregistré', 'No waste manifest recorded')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Votre structure n\'a pas encore enregistré d\'évacuation de déchets industriels ou portuaires. Émettez votre premier bordereau BSDD.', 'Your organization has not yet recorded any industrial or port waste evacuation. Issue your first BSDD manifest.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Créer un premier bordereau', 'Create a first manifest')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(d => (
                <div key={d.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-sm font-bold text-green-400">{d.bordereau_numero || `#${d.id}`}</span>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${d.statut === 'VALIDE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>{d.statut === 'VALIDE' ? t('Validé', 'Validated') : t('En cours', 'In progress')}</span>
                  </div>
                  <div className="text-sm text-white">{d.type_dechet}</div>
                  <div className="text-xs text-slate-400">{d.quantite} {d.unite} → {d.centre_traitement}</div>
                  <div className="text-xs font-mono text-slate-500">{d.date_evacuation}</div>
                  {d.statut !== 'VALIDE' && (
                    <button
                      onClick={() => validerBordereau(d)}
                      disabled={validatingId === d.id}
                      className="w-full px-3 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 disabled:opacity-60 text-emerald-400 text-xs font-medium rounded-lg border border-emerald-500/30 transition"
                    >
                      {validatingId === d.id ? t('Validation…', 'Validating…') : t('Valider la Réception', 'Validate Reception')}
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
                    <th className="py-3 px-4 rounded-l-xl">{t('N° Bordereau', 'Manifest No.')}</th>
                    <th className="py-3 px-4">{t('Type de Déchet', 'Waste Type')}</th>
                    <th className="py-3 px-4">{t('Quantité', 'Quantity')}</th>
                    <th className="py-3 px-4">{t('Centre de Traitement Agréé', 'Approved Treatment Center')}</th>
                    <th className="py-3 px-4">{t('Date Évacuation', 'Evacuation Date')}</th>
                    <th className="py-3 px-4">{t('Statut', 'Status')}</th>
                    <th className="py-3 px-4 rounded-r-xl text-right">{t('Action', 'Action')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(d => (
                    <tr key={d.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-mono text-xs text-green-400">{d.bordereau_numero || `#${d.id}`}</td>
                      <td className="py-3.5 px-4 font-semibold text-white">{d.type_dechet}</td>
                      <td className="py-3.5 px-4 font-mono">{d.quantite} {d.unite}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-300">{d.centre_traitement}</td>
                      <td className="py-3.5 px-4 text-xs font-mono text-slate-400">{d.date_evacuation || ''}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${d.statut === 'VALIDE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          }`}>{d.statut === 'VALIDE' ? t('Validé', 'Validated') : t('En cours', 'In progress')}</span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        {d.statut !== 'VALIDE' && (
                          <button
                            onClick={() => validerBordereau(d)}
                            disabled={validatingId === d.id}
                            className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 disabled:opacity-60 text-emerald-400 text-xs rounded border border-emerald-500/30 transition"
                          >
                            {validatingId === d.id ? t('Validation…', 'Validating…') : t('Valider', 'Validate')}
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

      {/* Modal Bordereau */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Leaf className="w-5 h-5 text-green-400" />
              {t('Émettre un Bordereau BSDD', 'Issue a BSDD Manifest')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Déchets spéciaux / hydrocarbures vers filière agréée (MARPOL Annexes I & IV)', 'Special / hydrocarbon waste to approved channel (MARPOL Annexes I & IV)')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Type de Déchet *', 'Waste Type *')}</label>
                <input
                  type="text"
                  required
                  value={formData.type_dechet}
                  onChange={e => setFormData({ ...formData, type_dechet: e.target.value })}
                  placeholder={t('Ex: Huiles de Vidange Usagées', 'E.g. Used Engine Oils')}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Quantité *', 'Quantity *')}</label>
                  <input
                    type="number"
                    min={0}
                    required
                    value={formData.quantite}
                    onChange={e => setFormData({ ...formData, quantite: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Unité', 'Unit')}</label>
                  <select
                    value={formData.unite}
                    onChange={e => setFormData({ ...formData, unite: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500"
                  >
                    <option>Litres</option>
                    <option>{t('Kg', 'Kg')}</option>
                    <option>{t('Tonnes', 'Tonnes')}</option>
                    <option>{t('Unités', 'Units')}</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Centre de Traitement Agréé *', 'Approved Treatment Center *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.centre_traitement}
                    onChange={e => setFormData({ ...formData, centre_traitement: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Date d\'Évacuation', 'Evacuation Date')}</label>
                  <input
                    type="date"
                    value={formData.date_evacuation}
                    onChange={e => setFormData({ ...formData, date_evacuation: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500"
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
                  className="px-5 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-60 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  {saving ? t('Émission…', 'Issuing…') : t('Émettre le Bordereau', 'Issue the Manifest')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

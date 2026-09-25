'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  FileText, Plus, RefreshCw, Search, Ship,
  CheckCircle2, AlertCircle, ArrowLeft, Loader2
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';
import { toast } from 'sonner';
import { useSettings } from '@/components/layout/SettingsProvider';

interface Manifeste {
  id: number;
  numero_manifeste: string;
  type_manifeste?: string;
  navire?: string;
  voyage?: string;
  port_provenance?: string;
  port_destination?: string;
  nombre_conteneurs?: number;
  tonnage_total?: number;
  conforme?: boolean;
  observations?: string;
  date_enregistrement?: string;
}

export default function PortOperationsManifestsPage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [manifestes, setManifestes] = useState<Manifeste[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    numero_manifeste: '',
    navire: '',
    type_manifeste: 'import',
    voyage: '',
    port_provenance: '',
    port_destination: '',
    nombre_conteneurs: 0,
    tonnage_total: 0,
    valeur_marchandise: 0,
  });

  const fetchManifestes = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/acconage-avance/manifestes');
      setManifestes(Array.isArray(res.data) ? res.data : []);
    } catch {
      setManifestes([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchManifestes();
  }, []);

  const handleCreateManifeste = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiClient.post('/api/v1/acconage-avance/manifestes', {
        numero_manifeste: formData.numero_manifeste,
        navire: formData.navire,
        type_manifeste: formData.type_manifeste,
        voyage: formData.voyage || undefined,
        port_provenance: formData.port_provenance,
        port_destination: formData.port_destination || undefined,
        nombre_conteneurs: formData.nombre_conteneurs || 0,
        tonnage_total: formData.tonnage_total || undefined,
        valeur_marchandise: formData.valeur_marchandise || undefined,
      });
      toast.success(t('Manifeste enregistré', 'Manifest recorded'));
      setIsModalOpen(false);
      setFormData({
        numero_manifeste: '', navire: '', type_manifeste: 'import', voyage: '',
        port_provenance: '', port_destination: '', nombre_conteneurs: 0,
        tonnage_total: 0, valeur_marchandise: 0,
      });
      fetchManifestes();
    } catch {
      toast.error(t('Erreur réseau : le manifeste n\'a pas pu être enregistré.', 'Network error: the manifest could not be saved.'));
    } finally {
      setSubmitting(false);
    }
  };

  const filtered = manifestes.filter(m =>
    (m.numero_manifeste || '').toLowerCase().includes(search.toLowerCase()) ||
    (m.navire || '').toLowerCase().includes(search.toLowerCase()) ||
    (m.port_provenance || '').toLowerCase().includes(search.toLowerCase()) ||
    (m.port_destination || '').toLowerCase().includes(search.toLowerCase())
  );

  const handleExport = () => {
    exportToCSV(
      filtered.map(m => ({
        'N° Manifeste': m.numero_manifeste,
        'Navire': m.navire || '',
        'Type': m.type_manifeste || '',
        'Voyage': m.voyage || '',
        'Provenance': m.port_provenance || '',
        'Destination': m.port_destination || '',
        'Conteneurs (EVP)': m.nombre_conteneurs ?? '',
        'Tonnage total': m.tonnage_total ?? '',
        'Conforme': m.conforme ? 'OUI' : 'NON',
      })),
      'manifestes'
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Manifestes & Cargaisons Navires', 'Ship Manifests & Cargo')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex flex-wrap items-center gap-2">
              {t('Manifestes & Cargaisons Navires', 'Ship Manifests & Cargo')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                KACC_MNF
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Déclaration des cargaisons par escale, contrôle de conformité douanière et suivi des connaissements', 'Cargo declaration per port call, customs compliance check and bill-of-lading tracking')}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={fetchManifestes}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          {manifestes.length > 0 && (
            <button
              onClick={handleExport}
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm border border-slate-700 transition"
            >
              {t('Export CSV', 'CSV Export')}
            </button>
          )}
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Enregistrer un Manifeste', 'Record a Manifest')}
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
              placeholder={t('Rechercher n° manifeste, navire, port...', 'Search manifest no., vessel, port...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 flex items-center justify-center gap-2 text-slate-400">
            <Loader2 className="w-5 h-5 animate-spin" />
            {t('Chargement des manifestes...', 'Loading manifests...')}
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Ship className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucun manifeste enregistré', 'No manifest recorded')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Déclarez la cargaison de vos navires ici : le manifeste est le document opposable à la douane.', 'Declare your vessels cargo here: the manifest is the document enforceable against customs.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Enregistrer un premier manifeste', 'Record a first manifest')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(m => (
                <div key={m.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-mono text-xs font-medium text-blue-400 break-all">{m.numero_manifeste}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border shrink-0 flex items-center gap-1 ${m.conforme
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                      {m.conforme ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                      {m.conforme ? t('Conforme', 'Compliant') : t('À contrôler', 'To check')}
                    </span>
                  </div>
                  <div className="text-white font-medium text-sm">{m.navire || ''}</div>
                  <div className="text-xs text-slate-400">
                    {m.port_provenance || ''} → {m.port_destination || ''}
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs font-mono text-slate-400">
                    <span>{(m.type_manifeste || 'import').toUpperCase()}</span>
                    {m.nombre_conteneurs ? <span>{m.nombre_conteneurs} EVP</span> : null}
                    {m.tonnage_total ? <span>{Number(m.tonnage_total).toLocaleString()} t</span> : null}
                  </div>
                </div>
              ))}
            </div>
            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                  <tr>
                    <th className="py-3 px-4 rounded-l-xl">{t('N° Manifeste', 'Manifest No.')}</th>
                    <th className="py-3 px-4">{t('Navire', 'Vessel')}</th>
                    <th className="py-3 px-4">{t('Type', 'Type')}</th>
                    <th className="py-3 px-4">{t('Provenance → Destination', 'Origin → Destination')}</th>
                    <th className="py-3 px-4">{t('EVP', 'TEU')}</th>
                    <th className="py-3 px-4">{t('Tonnage', 'Tonnage')}</th>
                    <th className="py-3 px-4 rounded-r-xl">{t('Conformité', 'Compliance')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(m => (
                    <tr key={m.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-blue-400">{m.numero_manifeste}</td>
                      <td className="py-3.5 px-4 text-white font-medium">{m.navire || ''}</td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-700/50 text-slate-300 uppercase border border-slate-600/50">
                          {m.type_manifeste || 'import'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-300">
                        {m.port_provenance || ''} → {m.port_destination || ''}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-white">{m.nombre_conteneurs ?? ''}</td>
                      <td className="py-3.5 px-4 font-mono text-slate-300 text-xs">
                        {m.tonnage_total ? `${Number(m.tonnage_total).toLocaleString()} t` : ''}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border flex items-center gap-1 w-fit ${m.conforme
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          }`}>
                          {m.conforme ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                          {m.conforme ? t('Conforme', 'Compliant') : t('À contrôler', 'To check')}
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

      {/* Modal Nouveau Manifeste */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-400" />
              {t('Enregistrer un Manifeste', 'Record a Manifest')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Déclaration officielle de la cargaison d\'un navire', 'Official declaration of a vessel cargo')}
            </p>

            <form onSubmit={handleCreateManifeste} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('N° Manifeste *', 'Manifest No. *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.numero_manifeste}
                    onChange={e => setFormData({ ...formData, numero_manifeste: e.target.value })}
                    placeholder={t('Ex: MAN-2026-0148', 'e.g. MAN-2026-0148')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Type de manifeste', 'Manifest Type')}</label>
                  <select
                    value={formData.type_manifeste}
                    onChange={e => setFormData({ ...formData, type_manifeste: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="import">{t('Import (déchargement)', 'Import (discharge)')}</option>
                    <option value="export">{t('Export (chargement)', 'Export (loading)')}</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Nom du Navire *', 'Vessel Name *')}</label>
                <input
                  type="text"
                  required
                  value={formData.navire}
                  onChange={e => setFormData({ ...formData, navire: e.target.value })}
                  placeholder={t('Ex: CMA CGM Kribi', 'e.g. CMA CGM Kribi')}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Port de Provenance *', 'Port of Origin *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.port_provenance}
                    onChange={e => setFormData({ ...formData, port_provenance: e.target.value })}
                    placeholder={t('Ex: Anvers', 'e.g. Antwerp')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Port de Destination', 'Port of Destination')}</label>
                  <input
                    type="text"
                    value={formData.port_destination}
                    onChange={e => setFormData({ ...formData, port_destination: e.target.value })}
                    placeholder={t('Ex: Douala', 'e.g. Douala')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Voyage / N°', 'Voyage / No.')}</label>
                  <input
                    type="text"
                    value={formData.voyage}
                    onChange={e => setFormData({ ...formData, voyage: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Conteneurs (EVP)', 'Containers (TEU)')}</label>
                  <input
                    type="number"
                    min={0}
                    value={formData.nombre_conteneurs || ''}
                    onChange={e => setFormData({ ...formData, nombre_conteneurs: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Tonnage total (kg)', 'Total tonnage (kg)')}</label>
                  <input
                    type="number"
                    min={0}
                    value={formData.tonnage_total || ''}
                    onChange={e => setFormData({ ...formData, tonnage_total: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Valeur déclarée des marchandises (XAF)', 'Declared cargo value (XAF)')}</label>
                <input
                  type="number"
                  min={0}
                  value={formData.valeur_marchandise || ''}
                  onChange={e => setFormData({ ...formData, valeur_marchandise: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
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
                  disabled={submitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-lg transition flex items-center gap-2"
                >
                  {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                  {submitting ? t('Enregistrement...', 'Saving...') : t('Enregistrer le Manifeste', 'Save Manifest')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

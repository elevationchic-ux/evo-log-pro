'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import { ShieldCheck, Plus, Search, ArrowLeft, RefreshCw } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

const REGISTRY = 'isps-inspections';

interface InspectionISPS {
  id: number;
  reference: string | null;
  zone_portuaire: string;
  type_inspection: string;
  auditeur: string;
  date_inspection: string;
  score_conformite_pct: number | string;
  statut: string;
  remarques: string;
}

export default function QhsePortInspectionsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [inspections, setInspections] = useState<InspectionISPS[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    zone_portuaire: '',
    type_inspection: t('Contrôle Sûreté Code ISPS (Clôtures & Badges)', 'ISPS Security Check (Fences & Badges)'),
    auditeur: '',
    date_inspection: new Date().toISOString().slice(0, 10),
    score_conformite_pct: 95,
    statut: 'CONFORME' as 'CONFORME' | 'NON_CONFORME_MINEURE' | 'RESERVE_MAJEURE',
    remarques: '',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/registres/${REGISTRY}`);
      const rows = Array.isArray(res?.data?.items) ? res.data.items : [];
      setInspections(rows.map((r: any) => ({
        id: r.id,
        reference: r.reference,
        zone_portuaire: r.zone_portuaire || '',
        type_inspection: r.type_inspection || '',
        auditeur: r.auditeur || '',
        date_inspection: r.date_inspection || '',
        score_conformite_pct: r.score_conformite_pct ?? '',
        statut: r.statut || 'CONFORME',
        remarques: r.remarques || '',
      })));
    } catch {
      toast.error(t('Les inspections n\'ont pas pu être chargées. Vérifiez votre connexion.', 'Inspections could not be loaded. Check your connection.'));
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
        zone_portuaire: formData.zone_portuaire,
        type_inspection: formData.type_inspection,
        auditeur: formData.auditeur,
        date_inspection: formData.date_inspection,
        score_conformite_pct: Number(formData.score_conformite_pct),
        remarques: formData.remarques,
        statut: formData.statut,
      });
      toast.success(t('Fiche d\'inspection enregistrée.', 'Inspection sheet saved.'));
      setIsModalOpen(false);
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec de l\'enregistrement de l\'inspection.', 'Failed to save the inspection.'));
    } finally {
      setSaving(false);
    }
  };

  const filtered = inspections.filter(i =>
    i.zone_portuaire.toLowerCase().includes(search.toLowerCase()) ||
    (i.reference || '').toLowerCase().includes(search.toLowerCase()) ||
    i.type_inspection.toLowerCase().includes(search.toLowerCase())
  );

  const statutBadge = (s: string) =>
    s === 'CONFORME' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      : s === 'NON_CONFORME_MINEURE' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
        : 'bg-red-500/10 text-red-400 border-red-500/20';

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Centre Sécurité QHSE', 'QHSE Safety Center')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Inspections Portuaires & Code ISPS', 'Port Inspections & ISPS Code')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2 flex-wrap">
              {t('Inspections Portuaires & Conformité Code ISPS', 'Port Inspections & ISPS Code Compliance')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                KQHS_ISP
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Vérification des zones de restriction portuaire, barriérage, éclairage de quai et dispositifs anti-intrusion', 'Verification of port restricted areas, fencing, quay lighting and anti-intrusion devices')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={load} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-700 text-slate-300 text-sm hover:bg-slate-800">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Nouvelle Fiche d\'Inspection', 'New Inspection Sheet')}
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
              placeholder={t('Rechercher zone portuaire, référence, type d\'inspection...', 'Search port zone, reference, inspection type...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400 text-sm">{t('Chargement des inspections…', 'Loading inspections…')}</div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <ShieldCheck className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucune inspection portuaire enregistrée', 'No port inspection recorded')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Votre structure n\'a pas encore consigné de rapport d\'inspection Code ISPS pour ses installations.', 'Your organization has not yet recorded an ISPS Code inspection report for its facilities.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Consigner une première inspection', 'Record a first inspection')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(i => (
                <div key={i.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-sm font-bold text-white">{i.reference || `#${i.id}`}</span>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${statutBadge(i.statut)}`}>{i.statut}</span>
                  </div>
                  <div className="text-sm text-white">{i.zone_portuaire}</div>
                  <div className="text-xs text-slate-400">{i.type_inspection} · {i.auditeur}</div>
                  <div className="text-xs font-mono text-slate-400">{i.date_inspection}  {i.score_conformite_pct}% {t('conformité', 'compliance')}</div>
                </div>
              ))}
            </div>
            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                  <tr>
                    <th className="py-3 px-4 rounded-l-xl">{t('Réf.', 'Ref.')}</th>
                    <th className="py-3 px-4">{t('Zone Portuaire', 'Port Zone')}</th>
                    <th className="py-3 px-4">{t('Type d\'Inspection', 'Inspection Type')}</th>
                    <th className="py-3 px-4">{t('Auditeur / Inspecteur', 'Auditor / Inspector')}</th>
                    <th className="py-3 px-4">{t('Date', 'Date')}</th>
                    <th className="py-3 px-4">{t('Score Conformité', 'Compliance Score')}</th>
                    <th className="py-3 px-4 rounded-r-xl">{t('Statut', 'Status')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(i => (
                    <tr key={i.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-mono text-xs text-blue-400">{i.reference || `#${i.id}`}</td>
                      <td className="py-3.5 px-4 font-semibold text-white">{i.zone_portuaire}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-300">{i.type_inspection}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-400">{i.auditeur}</td>
                      <td className="py-3.5 px-4 text-xs font-mono text-slate-400">{i.date_inspection || ''}</td>
                      <td className="py-3.5 px-4 font-mono text-emerald-400">{i.score_conformite_pct}%</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${statutBadge(i.statut)}`}>{i.statut}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Modal Inspection */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-blue-400" />
              {t('Fiche d\'Inspection Code ISPS', 'ISPS Code Inspection Sheet')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Contrôle de zone de restriction et consignature sûreté', 'Restricted area check and security endorsement')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Zone Portuaire *', 'Port Zone *')}</label>
                <input
                  type="text"
                  required
                  value={formData.zone_portuaire}
                  onChange={e => setFormData({ ...formData, zone_portuaire: e.target.value })}
                  placeholder={t('Ex: Zone Sous-Douane Quai 14 (Douala)', 'E.g. Customs Sub-zone Quay 14 (Douala)')}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Type d\'Inspection', 'Inspection Type')}</label>
                <input
                  type="text"
                  value={formData.type_inspection}
                  onChange={e => setFormData({ ...formData, type_inspection: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Auditeur / Inspecteur *', 'Auditor / Inspector *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.auditeur}
                    onChange={e => setFormData({ ...formData, auditeur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Date d\'Inspection', 'Inspection Date')}</label>
                  <input
                    type="date"
                    value={formData.date_inspection}
                    onChange={e => setFormData({ ...formData, date_inspection: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Score de Conformité (%)', 'Compliance Score (%)')}</label>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={formData.score_conformite_pct}
                    onChange={e => setFormData({ ...formData, score_conformite_pct: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Verdict', 'Verdict')}</label>
                  <select
                    value={formData.statut}
                    onChange={e => setFormData({ ...formData, statut: e.target.value as any })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="CONFORME">{t('Conforme', 'Compliant')}</option>
                    <option value="NON_CONFORME_MINEURE">{t('Non-conformité mineure', 'Minor non-conformity')}</option>
                    <option value="RESERVE_MAJEURE">{t('Réserve majeure', 'Major reservation')}</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Remarques & Observations', 'Remarks & Observations')}</label>
                <textarea
                  rows={2}
                  value={formData.remarques}
                  onChange={e => setFormData({ ...formData, remarques: e.target.value })}
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
                  disabled={saving}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  {saving ? t('Enregistrement…', 'Saving…') : t('Enregistrer l\'Inspection', 'Save Inspection')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  ShieldAlert, Plus, CheckCircle2,
  AlertTriangle, ShieldCheck, Users, FileCheck,
  ArrowUpRight, Leaf, RefreshCw
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { toast } from 'sonner';

interface IncidentQHSE {
  id: number;
  reference: string;
  type_evenement: string;
  lieu: string;
  date_heure: string | null;
  gravite: string;
  arret_travail: boolean;
  statut: string;
  description: string;
}

const GRAVITE_MAP: Record<string, string> = {
  BENIN: 'leger', SIGNIFICATIF: 'moyen', GRAVE: 'grave',
};

export default function QhseSecuriteDashboardPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [incidents, setIncidents] = useState<IncidentQHSE[]>([]);
  const [certifs, setCertifs] = useState<any[]>([]);
  const [investigations, setInvestigations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    type_evenement: 'Presqu\'accident (Near-Miss)',
    lieu: '',
    gravite: 'BENIN' as 'BENIN' | 'SIGNIFICATIF' | 'GRAVE',
    arret_travail: false,
    description: '',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [acc, cert, inv] = await Promise.all([
        apiClient.get('/api/v1/qhse/accidents', { params: { limit: 200 } }),
        apiClient.get('/api/v1/qhse/certifications').catch(() => null),
        apiClient.get('/api/v1/qhse/investigations').catch(() => null),
      ]);
      const rows = Array.isArray(acc?.data?.items) ? acc.data.items : [];
      setIncidents(rows.map((a: any) => ({
        id: a.id,
        reference: a.numero_accident,
        type_evenement: a.type_accident,
        lieu: a.lieu,
        date_heure: a.date_accident,
        gravite: (a.gravite || '').toUpperCase(),
        arret_travail: (a.arret_travail || 0) > 0,
        statut: a.statut,
        description: a.description,
      })));
      setCertifs(Array.isArray(cert?.data?.items) ? cert.data.items : []);
      setInvestigations(Array.isArray(inv?.data?.items) ? inv.data.items : []);
    } catch {
      toast.error(t('Les registres QHSE n\'ont pas pu être chargés. Vérifiez votre connexion.', 'QHSE registers could not be loaded. Check your connection.'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { load(); }, [load]);

  const handleCreateIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post('/api/v1/qhse/accidents', {
        date_accident: new Date().toISOString(),
        lieu: formData.lieu,
        type_accident: formData.type_evenement,
        description: formData.description,
        gravite: GRAVITE_MAP[formData.gravite] || 'leger',
        arret_travail: formData.arret_travail ? 1 : 0,
      });
      toast.success(t('Signalement enregistré au registre QHSE.', 'Report recorded in the QHSE register.'));
      setIsModalOpen(false);
      setFormData(f => ({ ...f, lieu: '', description: '' }));
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec de l\'enregistrement du signalement.', 'Failed to save the report.'));
    } finally {
      setSaving(false);
    }
  };

  // Scoreboard calcule a partir des registres reels
  const now = new Date();
  const ltiDates = incidents.filter(i => i.arret_travail || i.gravite === 'GRAVE')
    .map(i => i.date_heure ? new Date(i.date_heure).getTime() : 0)
    .filter(Boolean)
    .sort((a, b) => b - a);
  const joursSansLti = ltiDates.length > 0
    ? Math.max(0, Math.floor((now.getTime() - ltiDates[0]) / 86400000))
    : null;
  const accidents12m = incidents.filter(i => i.date_heure && (now.getTime() - new Date(i.date_heure).getTime()) < 365 * 86400000).length;
  const certifsActives = certifs.filter(c => c.statut === 'actif' && (!c.date_expiration || new Date(c.date_expiration) >= now)).length;
  const enquetesOuvertes = investigations.filter(i => i.statut !== 'complete').length;

  const scoreboard = [
    {
      label: t('Jours Sans Accident LTI', 'Days Without LTI Accident'),
      value: joursSansLti != null ? String(joursSansLti) : '',
      note: joursSansLti != null
        ? t('Depuis le dernier accident avec arrêt', 'Since the last lost-time accident')
        : t('Aucun accident avec arrêt enregistré', 'No lost-time accident recorded'),
      tone: 'text-emerald-400',
    },
    {
      label: t('Accidents déclarés (12 mois)', 'Reported accidents (12 months)'),
      value: String(accidents12m),
      note: t('Registre accidents du travail', 'Work-accident register'),
      tone: 'text-white',
    },
    {
      label: t('Enquêtes CAPA ouvertes', 'Open CAPA investigations'),
      value: String(enquetesOuvertes),
      note: t('Plans d\'actions en cours', 'Active action plans'),
      tone: 'text-blue-400',
    },
    {
      label: t('Certifications ISO actives', 'Active ISO certifications'),
      value: String(certifsActives),
      note: t('Normes & référentiels déclarés', 'Declared standards'),
      tone: 'text-purple-400',
    },
  ];

  const submodules = [
    { title: t('Gestion des Incidents', 'Incident Management'), desc: t('Arbre des causes & actions correctives', 'Root-cause analysis & corrective actions'), path: '/qhse-securite/incident-management', icon: AlertTriangle, tcode: 'KQHS_INC', color: 'from-red-600 to-amber-600' },
    { title: t('Inspections Portuaires', 'Port Inspections'), desc: t('Contrôles de zone & sûreté Code ISPS', 'Zone checks & ISPS Code security'), path: '/qhse-securite/port-inspections', icon: ShieldCheck, tcode: 'KQHS_ISP', color: 'from-blue-600 to-indigo-600' },
    { title: t('Formations & Habilitations', 'Training & Certifications'), desc: t('Passeports sécurité, CACES, SST', 'Safety passports, CACES, first aid'), path: '/qhse-securite/safety-training', icon: Users, tcode: 'KQHS_TRN', color: 'from-emerald-600 to-teal-600' },
    { title: t('Environnement & MARPOL', 'Environment & MARPOL'), desc: t('Rejets soute, hydrocarbures, tri déchets', 'Bilge discharge, oils, waste sorting'), path: '/qhse-securite/environment', icon: Leaf, tcode: 'KQHS_ENV', color: 'from-green-600 to-emerald-600' },
    { title: t('Conformité Réglementaire', 'Regulatory Compliance'), desc: t('Code du Travail & veille légale CEMAC', 'Labour Code & CEMAC legal watch'), path: '/qhse-securite/ohada-compliance', icon: FileCheck, tcode: 'KQHS_OHD', color: 'from-purple-600 to-indigo-600' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2 flex-wrap">
              {t('Centre de Pilotage QHSE & Sûreté Portuaire', 'QHSE & Port Security Command Center')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                KQHS_DSH • ISPS
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Qualité, Hygiène, Sécurité au Travail, Protection de l\'Environnement et Sûreté Maritime', 'Quality, Health, Safety, Environment and Maritime Security')}
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
            {t('Déclarer un Incident / Presqu\'accident', 'Report an Incident / Near-Miss')}
          </button>
        </div>
      </div>

      {/* Safety Scoreboard */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {scoreboard.map((k, i) => (
          <div key={i} className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-400 uppercase font-semibold">{k.label}</span>
            <p className={`text-3xl font-extrabold ${k.tone} mt-1 font-mono`}>{k.value}</p>
            <span className="text-xs text-slate-400 flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> {k.note}
            </span>
          </div>
        ))}
      </div>

      {/* Submodules Grid */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">{t('Modules Spécialisés QHSE', 'Specialized QHSE Modules')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {submodules.map((sub, i) => {
            const Icon = sub.icon;
            return (
              <Link
                key={i}
                href={sub.path}
                className="group relative bg-slate-900/70 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-slate-700 transition duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className={`p-2.5 rounded-xl bg-gradient-to-br ${sub.color} text-white shadow-md`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                        {sub.tcode}
                      </span>
                      <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition" />
                    </div>
                  </div>
                  <h3 className="font-semibold text-white text-base group-hover:text-emerald-400 transition">
                    {sub.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">{sub.desc}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                  <span>{t('Accéder au registre', 'Open the register')}</span>
                  <span className="text-emerald-400 font-medium">{t('Ouvrir →', 'Open →')}</span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Incidents Table */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-4 sm:p-6">
        <h2 className="text-lg font-semibold text-white mb-1">{t('Registre des Signalements & Événements', 'Reports & Events Register')}</h2>
        <p className="text-xs text-slate-400 mb-6">{t('Suivi des événements indésirables, accidents et presqu\'accidents', 'Tracking of adverse events, accidents and near-misses')}</p>

        {loading ? (
          <div className="py-16 text-center text-slate-400 text-sm">{t('Chargement des registres…', 'Loading registers…')}</div>
        ) : incidents.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <ShieldCheck className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucun incident de sécurité enregistré', 'No security incident recorded')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Aucun événement indésirable n\'est ouvert pour votre structure. En cas de situation dangereuse, effectuez un signalement immédiat.', 'No adverse event is open for your organization. In case of a dangerous situation, report it immediately.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Signaler un risque / presqu\'accident', 'Report a risk / near-miss')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {incidents.map(inc => (
                <div key={inc.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-sm font-bold text-red-400">{inc.reference}</span>
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${inc.gravite === 'GRAVE' ? 'bg-red-500/20 text-red-400'
                        : inc.gravite === 'SIGNIFICATIF' ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>{inc.gravite || ''}</span>
                  </div>
                  <div className="text-sm text-white font-medium">{inc.type_evenement}</div>
                  <div className="text-xs text-slate-400">{inc.lieu} · {inc.date_heure ? new Date(inc.date_heure).toLocaleString(lang === 'en' ? 'en-GB' : 'fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : ''}</div>
                  <div className="text-xs"><span className={inc.arret_travail ? 'text-red-400' : 'text-emerald-400'}>{inc.arret_travail ? t('Oui (LTI)', 'Yes (LTI)') : t('Non', 'No')}</span></div>
                </div>
              ))}
            </div>
            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                  <tr>
                    <th className="py-3 px-4 rounded-l-xl">{t('Réf. Incident', 'Ref.')}</th>
                    <th className="py-3 px-4">{t('Nature de l\'Événement', 'Event Type')}</th>
                    <th className="py-3 px-4">{t('Lieu', 'Location')}</th>
                    <th className="py-3 px-4">{t('Gravité', 'Severity')}</th>
                    <th className="py-3 px-4">{t('Arrêt de Travail', 'Lost Time')}</th>
                    <th className="py-3 px-4">{t('Date / Heure', 'Date / Time')}</th>
                    <th className="py-3 px-4 rounded-r-xl">{t('Statut', 'Status')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {incidents.map(inc => (
                    <tr key={inc.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-red-400">{inc.reference}</td>
                      <td className="py-3.5 px-4 text-white font-medium">{inc.type_evenement}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-300">{inc.lieu}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${inc.gravite === 'GRAVE' ? 'bg-red-500/20 text-red-400'
                            : inc.gravite === 'SIGNIFICATIF' ? 'bg-amber-500/20 text-amber-400'
                              : 'bg-blue-500/20 text-blue-400'
                          }`}>{inc.gravite || ''}</span>
                      </td>
                      <td className="py-3.5 px-4 text-xs font-semibold">
                        {inc.arret_travail
                          ? <span className="text-red-400">{t('Oui (LTI)', 'Yes (LTI)')}</span>
                          : <span className="text-emerald-400">{t('Non', 'No')}</span>}
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-400 font-mono">
                        {inc.date_heure ? new Date(inc.date_heure).toLocaleString(lang === 'en' ? 'en-GB' : 'fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : ''}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">{inc.statut}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Modal Signalement */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              {t('Signaler un Événement Sécurité QHSE', 'Report a QHSE Safety Event')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Enregistrement immédiat pour déclenchement de l\'arbre des causes', 'Immediate recording to trigger the root-cause analysis')}
            </p>

            <form onSubmit={handleCreateIncident} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Type d\'Événement *', 'Event Type *')}</label>
                <select
                  value={formData.type_evenement}
                  onChange={e => setFormData({ ...formData, type_evenement: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                >
                  <option value="Presqu'accident (Near-Miss)">{t('Presqu\'accident (Near-Miss)', 'Near-Miss')}</option>
                  <option value="Accident du Travail (avec arrêt)">{t('Accident du Travail (avec arrêt)', 'Work Accident (with lost time)')}</option>
                  <option value="Accident du Travail (sans arrêt)">{t('Accident du Travail (sans arrêt)', 'Work Accident (no lost time)')}</option>
                  <option value="Déversement Hydrocarbure (Environnement)">{t('Déversement Hydrocarbure', 'Hydrocarbon Spill')}</option>
                  <option value="Non-conformité Sûreté Code ISPS">{t('Non-conformité Sûreté Code ISPS', 'ISPS Code Non-Conformity')}</option>
                  <option value="Incident Incendie / Électrique">{t('Incident Incendie / Électrique', 'Fire / Electrical Incident')}</option>
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Lieu Exact *', 'Exact Location *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.lieu}
                    onChange={e => setFormData({ ...formData, lieu: e.target.value })}
                    placeholder={t('Ex: Terre-plein Quai 14', 'E.g. Quay 14 yard')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Gravité Potentielle', 'Potential Severity')}</label>
                  <select
                    value={formData.gravite}
                    onChange={e => setFormData({ ...formData, gravite: e.target.value as any })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  >
                    <option value="BENIN">{t('Bénin (Sans dommage majeur)', 'Minor (no major damage)')}</option>
                    <option value="SIGNIFICATIF">{t('Significatif (Soins médicaux)', 'Significant (medical care)')}</option>
                    <option value="GRAVE">{t('Grave (Hospitalisation / Danger mortel)', 'Severe (hospitalization / fatal risk)')}</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.arret_travail}
                    onChange={e => setFormData({ ...formData, arret_travail: e.target.checked })}
                    className="rounded bg-slate-800 border-slate-700 text-red-600 focus:ring-0"
                  />
                  <span>{t('Arrêt de travail consécutif (Impact LTI)', 'Resulting lost time (LTI impact)')}</span>
                </label>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Description des Circonstances *', 'Circumstances *')}</label>
                <textarea
                  rows={3}
                  required
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  placeholder={t('Décrivez précisément ce qui s\'est passé, les engins impliqués et les premières mesures prises...', 'Describe precisely what happened, equipment involved and first actions taken...')}
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
                  {saving ? t('Enregistrement…', 'Saving…') : t('Enregistrer le Signalement', 'Save the Report')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Plus, Search, ArrowLeft, CheckCircle2,
  CalendarClock, Award, AlertTriangle, Loader2
} from 'lucide-react';
import apiClient from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

const REGISTRY = 'habilitations-securite';

interface HabilitationSecurite {
  id: number;
  employe_nom: string;
  matricule: string;
  type_formation: string;
  organisme_formateur: string;
  date_obtention: string;
  date_expiration: string;
  statut: 'VALIDE' | 'EXPIRATION_PROCHE' | 'EXPIRE';
}

const computeStatut = (dateExpiration: string): HabilitationSecurite['statut'] => {
  if (!dateExpiration) return 'VALIDE';
  const today = new Date();
  const exp = new Date(dateExpiration);
  if (isNaN(exp.getTime())) return 'VALIDE';
  if (exp < today) return 'EXPIRE';
  const soon = new Date(today.getTime() + 60 * 24 * 3600 * 1000);
  if (exp < soon) return 'EXPIRATION_PROCHE';
  return 'VALIDE';
};

export default function QhseSafetyTrainingPage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [formations, setFormations] = useState<HabilitationSecurite[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    employe_nom: '',
    matricule: '',
    type_formation: 'CACES R489 - Chariots Automoteurs de Manutention',
    organisme_formateur: '',
    date_obtention: '',
    date_expiration: '',
  });

  const fetchFormations = useCallback(async () => {
    try {
      const res = await apiClient.get(`/api/v1/registres/${REGISTRY}`);
      const list = Array.isArray(res?.data) ? res.data : (res?.data?.items || []);
      setFormations(
        list.map((r: any) => ({
          id: r.id,
          employe_nom: r.employe_nom || r.reference || '',
          matricule: r.matricule || '',
          type_formation: r.type_formation || '',
          organisme_formateur: r.organisme_formateur || '',
          date_obtention: r.date_obtention || '',
          date_expiration: r.date_expiration || '',
          statut: computeStatut(r.date_expiration),
        }))
      );
    } catch {
      toast.error(t('Impossible de charger les habilitations', 'Unable to load certifications'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    fetchFormations();
  }, [fetchFormations]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post(`/api/v1/registres/${REGISTRY}`, {
        reference: formData.matricule,
        statut: computeStatut(formData.date_expiration),
        ...formData,
      });
      toast.success(t('Habilitation enregistrée', 'Certification recorded'));
      setIsModalOpen(false);
      setFormData({
        employe_nom: '', matricule: '',
        type_formation: 'CACES R489 - Chariots Automoteurs de Manutention',
        organisme_formateur: '', date_obtention: '', date_expiration: '',
      });
      fetchFormations();
    } catch {
      toast.error(t('Erreur réseau  enregistrement impossible', 'Network error  could not save'));
    } finally {
      setSaving(false);
    }
  };

  const filtered = formations.filter(f =>
    f.employe_nom.toLowerCase().includes(search.toLowerCase()) ||
    f.matricule.toLowerCase().includes(search.toLowerCase()) ||
    f.type_formation.toLowerCase().includes(search.toLowerCase())
  );

  const statutBadge = (statut: HabilitationSecurite['statut']) => {
    if (statut === 'EXPIRE') {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20 flex items-center gap-1 w-fit">
          <AlertTriangle className="w-3 h-3" /> {t('Expiré', 'Expired')}
        </span>
      );
    }
    if (statut === 'EXPIRATION_PROCHE') {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1 w-fit">
          <CalendarClock className="w-3 h-3" /> {t('Expiration proche', 'Expiring soon')}
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
        <CheckCircle2 className="w-3 h-3" /> {t('Valide', 'Valid')}
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Centre Sécurité QHSE', 'QHSE Safety Center')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Formations & Habilitations de Sécurité', 'Safety Training & Certifications')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex flex-wrap items-center gap-2">
              {t('Passeports Sécurité & Habilitations Professionnelles', 'Safety Passports & Professional Certifications')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                KQHS_TRN
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Registre des certifications de sécurité portuaire, CACES, SST et habilitations aux matières dangereuses (IMDG)', 'Register of port safety certifications, CACES, first aid and dangerous goods (IMDG) certifications')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm shadow-lg shadow-emerald-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Attribuer une Habilitation', 'Assign a Certification')}
          </button>
        </div>
      </div>

      {/* Main Table card */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder={t('Rechercher collaborateur, matricule, formation...', 'Search employee, ID number, training...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500"
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
            <Award className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">{t('Aucune habilitation enregistrée', 'No certification recorded')}</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {t('Le passeport sécurité de votre structure est actuellement vide. Enregistrez les habilitations de vos premiers conducteurs ou dockers.', 'Your organization safety passport is currently empty. Record the certifications of your first drivers or dock workers.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              {t('Attribuer une première certification', 'Assign a first certification')}
            </button>
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="space-y-3 lg:hidden">
              {filtered.map(item => (
                <div key={item.id} className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="font-semibold text-white text-sm">{item.employe_nom}</div>
                      <div className="font-mono text-xs text-emerald-400">{item.matricule}</div>
                    </div>
                    {statutBadge(item.statut)}
                  </div>
                  <div className="text-xs text-slate-200">{item.type_formation}</div>
                  <div className="text-xs text-slate-400">{item.organisme_formateur}</div>
                  <div className="text-xs font-mono text-slate-400 flex flex-wrap gap-x-4">
                    {item.date_obtention && <span>{t('Obtention', 'Issued')}: {item.date_obtention}</span>}
                    {item.date_expiration && <span>{t('Échéance', 'Expiry')}: {item.date_expiration}</span>}
                  </div>
                </div>
              ))}
            </div>
            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                  <tr>
                    <th className="py-3 px-4 rounded-l-xl">{t('Collaborateur', 'Employee')}</th>
                    <th className="py-3 px-4">{t('Matricule', 'ID Number')}</th>
                    <th className="py-3 px-4">{t('Habilitation / Formation', 'Certification / Training')}</th>
                    <th className="py-3 px-4">{t('Organisme Certificateur', 'Certifying Body')}</th>
                    <th className="py-3 px-4">{t('Obtention', 'Issued')}</th>
                    <th className="py-3 px-4">{t('Échéance Recyclage', 'Refresher Deadline')}</th>
                    <th className="py-3 px-4 rounded-r-xl">{t('Statut', 'Status')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filtered.map(item => (
                    <tr key={item.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-semibold text-white">{item.employe_nom}</td>
                      <td className="py-3.5 px-4 font-mono text-xs text-emerald-400">{item.matricule}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-200">{item.type_formation}</td>
                      <td className="py-3.5 px-4 text-xs text-slate-400">{item.organisme_formateur}</td>
                      <td className="py-3.5 px-4 text-xs font-mono text-slate-400">{item.date_obtention || ''}</td>
                      <td className="py-3.5 px-4 text-xs font-mono text-slate-200">{item.date_expiration || ''}</td>
                      <td className="py-3.5 px-4">{statutBadge(item.statut)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Modal Habilitation */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Award className="w-5 h-5 text-emerald-400" />
              {t('Attribuer une Habilitation Sécurité', 'Assign a Safety Certification')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Enregistrement dans le passeport de formation individuel', 'Recording in the individual training passport')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Nom du Salarié *', 'Employee Name *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.employe_nom}
                    onChange={e => setFormData({ ...formData, employe_nom: e.target.value })}
                    placeholder={t('Ex: Jean Dupont', 'e.g. Jean Dupont')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Matricule Salarié *', 'Employee ID *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.matricule}
                    onChange={e => setFormData({ ...formData, matricule: e.target.value })}
                    placeholder={t('Ex: MAT-0142', 'e.g. MAT-0142')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t("Type d'Habilitation / Formation", 'Certification / Training Type')}</label>
                <select
                  value={formData.type_formation}
                  onChange={e => setFormData({ ...formData, type_formation: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="CACES R489 - Chariots Automoteurs">CACES R489 - Chariots Automoteurs</option>
                  <option value="CACES R484 - Ponts Roulants & Portiques">CACES R484 - Ponts Roulants &amp; Portiques</option>
                  <option value="SST - Sauveteur Secouriste du Travail">SST - Sauveteur Secouriste du Travail</option>
                  <option value="Code IMDG - Matières Dangereuses">Code IMDG - Matières Dangereuses</option>
                  <option value="Sécurité Incendie & Évacuation Quai">Sécurité Incendie &amp; Évacuation Quai</option>
                  <option value="Sensibilisation Code ISPS Niveau 1">Sensibilisation Code ISPS Niveau 1</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Organisme Formateur', 'Training Organization')}</label>
                <input
                  type="text"
                  value={formData.organisme_formateur}
                  onChange={e => setFormData({ ...formData, organisme_formateur: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t("Date d'Obtention", 'Issue Date')}</label>
                  <input
                    type="date"
                    value={formData.date_obtention}
                    onChange={e => setFormData({ ...formData, date_obtention: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t("Date d'Échéance (Recyclage)", 'Expiry Date (Refresher)')}</label>
                  <input
                    type="date"
                    value={formData.date_expiration}
                    onChange={e => setFormData({ ...formData, date_expiration: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
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
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-lg transition flex items-center gap-2"
                >
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t("Enregistrer l'Habilitation", 'Save Certification')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

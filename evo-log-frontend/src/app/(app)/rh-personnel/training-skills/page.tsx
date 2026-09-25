'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Award, Plus, Search, Download, Loader2, ShieldCheck, X
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';
import { useSettings } from '@/components/layout/SettingsProvider';

const REGISTRY = 'habilitations-competences';

interface CertificationSkill {
  id: number;
  employeeName: string;
  matricule: string;
  certificationName: string;
  category: string;
  issueDate: string;
  expiryDate: string;
  issuingBody: string;
  status: 'VALIDE' | 'EXPIRATION_PROCHE' | 'EXPIRE';
}

const CATEGORIES: Array<[string, string, string]> = [
  ['CACES_CARISTE', 'CACES R489 Cariste', 'Forklift certificate CACES R489'],
  ['CACES_R484', 'CACES R484 Engins de levage', 'CACES R484 Lifting equipment'],
  ['ISPS_PORTUAIRE', 'Sûreté portuaire PAD / ISPS', 'Port facility security ISPS'],
  ['MATIERES_DANGEREUSES', 'Matières dangereuses IMDG', 'Dangerous goods IMDG'],
  ['SECOURISME', 'Secourisme SST', 'First aid SST'],
  ['ECO_CONDUITE', 'Éco-conduite', 'Eco-driving'],
];

// Statut déduit de la date d'expiration réelle (fenêtre d'alerte : 60 jours)
const computeStatus = (expiry: string | null): CertificationSkill['status'] => {
  if (!expiry) return 'VALIDE';
  const d = new Date(expiry);
  if (Number.isNaN(d.getTime())) return 'VALIDE';
  const now = new Date();
  if (d < now) return 'EXPIRE';
  const soon = new Date(now.getTime() + 60 * 24 * 3600 * 1000);
  return d <= soon ? 'EXPIRATION_PROCHE' : 'VALIDE';
};

export default function RhPersonnelTrainingSkills() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [skills, setSkills] = useState<CertificationSkill[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    employeeName: '', matricule: '', certificationName: '', category: 'CACES_CARISTE',
    issueDate: '', expiryDate: '', issuingBody: '',
  });

  const loadSkills = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/registres/${REGISTRY}`);
      const list = Array.isArray(res?.data) ? res.data : (res?.data?.items || []);
      setSkills(list.map((e: any) => {
        const p = e.payload || {};
        return {
          id: e.id,
          employeeName: p.employeeName || e.reference || '',
          matricule: p.matricule || '',
          certificationName: p.certificationName || e.reference || '',
          category: p.category || '',
          issueDate: p.issueDate || '',
          expiryDate: p.expiryDate || null,
          issuingBody: p.issuingBody || '',
          status: computeStatus(p.expiryDate || null),
        };
      }));
    } catch {
      setSkills([]);
      toast.error(t('Erreur réseau  chargement des habilitations impossible', 'Network error  could not load accreditations'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { loadSkills(); }, [loadSkills]);

  const filtered = skills.filter(s =>
    !searchQuery ||
    s.employeeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.certificationName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.issuingBody.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.employeeName.trim() || !form.certificationName.trim()) {
      toast.error(t('Collaborateur et certification sont obligatoires.', 'Employee and certification are required.'));
      return;
    }
    setSaving(true);
    try {
      await apiClient.post(`/api/v1/registres/${REGISTRY}`, {
        reference: form.certificationName.trim(),
        statut: computeStatus(form.expiryDate || null),
        employeeName: form.employeeName.trim(),
        matricule: form.matricule.trim(),
        certificationName: form.certificationName.trim(),
        category: form.category,
        issueDate: form.issueDate,
        expiryDate: form.expiryDate,
        issuingBody: form.issuingBody.trim(),
      });
      toast.success(t('Habilitation enregistrée', 'Accreditation recorded'));
      setShowModal(false);
      setForm({ employeeName: '', matricule: '', certificationName: '', category: 'CACES_CARISTE', issueDate: '', expiryDate: '', issuingBody: '' });
      loadSkills();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('Erreur réseau  enregistrement impossible', 'Network error  could not save'));
    } finally {
      setSaving(false);
    }
  };

  const handleExport = () => {
    if (filtered.length === 0) {
      toast.error(t('Aucune habilitation à exporter', 'No accreditation to export'));
      return;
    }
    exportToCSV(
      filtered.map(s => ({
        [t('Collaborateur', 'Employee')]: s.employeeName,
        [t('Matricule', 'Staff ID')]: s.matricule,
        [t('Certification', 'Certification')]: s.certificationName,
        [t('Catégorie', 'Category')]: s.category,
        [t('Organisme', 'Issuing body')]: s.issuingBody,
        [t('Délivrance', 'Issue date')]: s.issueDate,
        [t('Expiration', 'Expiry date')]: s.expiryDate,
        [t('Statut', 'Status')]: s.status,
      })),
      'habilitations_competences'
    );
    toast.success(t('Export CSV généré', 'CSV export generated'));
  };

  const statutBadge = (s: CertificationSkill) => {
    if (s.status === 'EXPIRE') {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">✗ {t('Expiré', 'Expired')}</span>;
    }
    if (s.status === 'EXPIRATION_PROCHE') {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">⚠ {t('Expire bientôt', 'Expiring soon')}</span>;
    }
    return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">✓ {t('Valide', 'Valid')}</span>;
  };

  const inputCls = "w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500";
  const labelCls = "block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1";

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              {t('Habilitations & Compétences Portuaires', 'Port Accreditation & Skills')}
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_TRN
            </span>
          </div>
          <h1 className="text-xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Award className="w-7 h-7 sm:w-8 sm:h-8 text-pink-400 shrink-0" />
            {t('Certifications, CACES & Formations ISPS', 'Certificates, CACES & ISPS Training')}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {t('Suivi des validités des permis caristes CACES, habilitations sûreté portuaire PAD et formations réglementaires.', 'Tracking of CACES forklift permits validity, PAD port security accreditations and regulatory training.')}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleExport}
            className="px-4 py-2.5 bg-slate-800 border border-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2 hover:border-pink-500/50 transition-colors"
          >
            <Download className="w-4 h-4" /> {t('Exporter', 'Export')}
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> {t('Ajouter Habilitation', 'Add Accreditation')}
          </button>
        </div>
      </div>

      {/* Table Habilitations */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('Rechercher collaborateur, certification, organisme...', 'Search employee, certification, body...')}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500 font-mono"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 flex items-center justify-center gap-2 text-slate-400 text-sm">
            <Loader2 className="w-5 h-5 animate-spin text-pink-400" />
            {t('Chargement des habilitations...', 'Loading accreditations...')}
          </div>
        ) : (
          <>
            {/* Mobile cards */}
            <div className="lg:hidden p-4 space-y-3">
              {filtered.length === 0 && (
                <div className="py-10 text-center">
                  <ShieldCheck className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-slate-400 text-sm font-sans">
                    {skills.length === 0
                      ? t('Aucune habilitation enregistrée. Ajoutez la première pour suivre les validités CACES, ISPS et SST de vos équipes.', 'No accreditation on record. Add the first one to track your teams\u2019 CACES, ISPS and first-aid validities.')
                      : t('Aucun résultat pour la recherche appliquée.', 'No result for the applied search.')}
                  </p>
                </div>
              )}
              {filtered.map(s => (
                <div key={s.id} className="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-sans font-bold text-slate-100">{s.employeeName}</span>
                    {statutBadge(s)}
                  </div>
                  <p className="font-sans text-sm text-pink-300 font-bold">{s.certificationName}</p>
                  <p className="text-[11px] text-slate-400 font-mono">{s.category || ''} {s.matricule ? `· ${s.matricule}` : ''}</p>
                  <p className="text-[11px] text-slate-400 font-sans">{s.issuingBody || ''}</p>
                  <p className="text-[11px] text-slate-500 font-mono">
                    {s.issueDate || ''} → <span className="font-bold text-slate-300">{s.expiryDate || ''}</span>
                  </p>
                </div>
              ))}
            </div>

            {/* Desktop table */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                    <th className="py-3.5 px-4">{t('Collaborateur', 'Employee')}</th>
                    <th className="py-3.5 px-4">{t('Certification & Habilitation', 'Certification & Accreditation')}</th>
                    <th className="py-3.5 px-4">{t('Organisme Émetteur', 'Issuing Body')}</th>
                    <th className="py-3.5 px-4">{t('Date Délivrance', 'Issue Date')}</th>
                    <th className="py-3.5 px-4">{t('Date Expiration', 'Expiry Date')}</th>
                    <th className="py-3.5 px-4 text-center">{t('Statut', 'Status')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {filtered.map(s => (
                    <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-pink-400">{s.matricule}</div>
                        <div className="font-sans text-slate-100 font-bold">{s.employeeName}</div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-sans font-bold text-slate-100">{s.certificationName}</div>
                        <div className="text-[11px] text-slate-400 font-mono">{s.category}</div>
                      </td>
                      <td className="py-3.5 px-4 text-slate-300 font-sans">{s.issuingBody || ''}</td>
                      <td className="py-3.5 px-4 text-slate-400">{s.issueDate || ''}</td>
                      <td className="py-3.5 px-4 font-bold text-slate-200">{s.expiryDate || ''}</td>
                      <td className="py-3.5 px-4 text-center">{statutBadge(s)}</td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-12 px-4 text-center">
                        <ShieldCheck className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                        <p className="text-slate-400 text-sm font-sans">
                          {skills.length === 0
                            ? t('Aucune habilitation enregistrée. Ajoutez la première pour suivre les validités CACES, ISPS et SST de vos équipes.', 'No accreditation on record. Add the first one to track your teams\u2019 CACES, ISPS and first-aid validities.')
                            : t('Aucun résultat pour la recherche appliquée.', 'No result for the applied search.')}
                        </p>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Add Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-pink-500/30 rounded-3xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100 text-base">{t('Nouvelle habilitation', 'New accreditation')}</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white"><X size={18} /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className={labelCls}>{t('Collaborateur *', 'Employee *')}</label>
                  <input className={inputCls} value={form.employeeName} onChange={e => setForm({ ...form, employeeName: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t('Matricule', 'Staff ID')}</label>
                  <input className={inputCls} value={form.matricule} onChange={e => setForm({ ...form, matricule: e.target.value })} />
                </div>
                <div className="sm:col-span-2">
                  <label className={labelCls}>{t('Intitulé de la certification *', 'Certification name *')}</label>
                  <input className={inputCls} placeholder={t('Ex. CACES R489 catégorie 3', 'E.g. CACES R489 category 3')} value={form.certificationName} onChange={e => setForm({ ...form, certificationName: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t('Catégorie', 'Category')}</label>
                  <select className={inputCls} value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>
                    {CATEGORIES.map(([code, fr, en]) => (
                      <option key={code} value={code}>{lang === 'en' ? en : fr}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className={labelCls}>{t('Organisme émetteur', 'Issuing body')}</label>
                  <input className={inputCls} placeholder={t('Ex. APAVIF, Bureau Veritas...', 'E.g. APAVIF, Bureau Veritas...')} value={form.issuingBody} onChange={e => setForm({ ...form, issuingBody: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t('Date délivrance', 'Issue date')}</label>
                  <input type="date" className={inputCls} value={form.issueDate} onChange={e => setForm({ ...form, issueDate: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t('Date expiration', 'Expiry date')}</label>
                  <input type="date" className={inputCls} value={form.expiryDate} onChange={e => setForm({ ...form, expiryDate: e.target.value })} />
                </div>
              </div>
              <button type="submit" disabled={saving} className="w-full py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl disabled:opacity-50 flex items-center justify-center gap-2">
                {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                {t('Enregistrer l\u2019habilitation', 'Save accreditation')}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

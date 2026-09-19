'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  Building2, Plus, Search, Edit, Shield, CheckCircle2,
  AlertTriangle, Globe, ShieldAlert, ArrowRight, RefreshCw,
  Upload, X, Sliders, Package, Users, Database, Zap,
  ChevronDown, Eye, EyeOff, Pause, Play, Trash2
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/components/shared/AuthProvider';
import { apiClient } from '@/lib/api-client';

interface Tenant {
  id: number;
  code: string;
  nom: string;
  sigle?: string;
  legal_form?: string;
  capital_social?: string;
  tax_id?: string;
  rccm?: string;
  agrement_douane?: string;
  agrement_pad?: string;
  agrement_pak?: string;
  rib?: string;
  ville?: string;
  pays?: string;
  telephone?: string;
  email?: string;
  website?: string;
  logo_url?: string;
  is_active: boolean;
  is_verified: boolean;
  suspension_reason?: string;
  subscription_plan_id?: number;
  subscription_start?: string;
  subscription_end?: string;
  max_users: number;
  max_storage_mb: number;
  max_camions?: number;
  current_users: number;
  current_storage_mb: number;
  primary_color?: string;
  secondary_color?: string;
  modules_actives?: string;
  created_at: string;
  updated_at?: string;
}

const ALL_MODULES = [
  { id: 'transport', label: 'K-Transport', icon: '🚛' },
  { id: 'magasin', label: 'K-Magasin MAG3', icon: '🏭' },
  { id: 'finance', label: 'K-Finance OHADA', icon: '💰' },
  { id: 'acconage', label: 'K-Acconage', icon: '⚓' },
  { id: 'qhse', label: 'K-QHSE', icon: '🦺' },
  { id: 'transit', label: 'K-Transit Douane', icon: '🛃' },
  { id: 'maintenance', label: 'K-GMAO', icon: '🔧' },
  { id: 'rh', label: 'K-RH & Paie', icon: '👥' },
  { id: 'chef-personnel', label: 'Chef du Personnel', icon: '🎯' },
  { id: 'cotations', label: 'K-Cotations', icon: '📋' },
  { id: 'tracking', label: 'K-Tracking e-POD', icon: '📍' },
  { id: 'fuel-guard', label: 'K-FuelGuard', icon: '⛽' },
  { id: 'bi', label: 'K-Analytics BI', icon: '📊' },
  { id: 'annuaire', label: 'Annuaire Prestataires', icon: '📇' },
  { id: 'b2b-portal', label: 'Portail Client B2B', icon: '🌐' },
  { id: 'ged', label: 'K-GED Documents', icon: '📂' },
];

const PLAN_STYLES: Record<string, string> = {
  starter: 'bg-slate-700/50 text-slate-300 border-slate-600',
  pro: 'bg-blue-500/10 text-blue-300 border-blue-500/20',
  enterprise: 'bg-amber-500/10 text-amber-300 border-amber-500/20',
  custom: 'bg-purple-500/10 text-purple-300 border-purple-500/20',
};

const emptyForm = () => ({
  code: '', nom: '', sigle: '', legal_form: 'SA',
  capital_social: '', tax_id: '', rccm: '',
  agrement_douane: '', agrement_pad: '', agrement_pak: '', rib: '',
  ville: 'Douala', pays: 'Cameroun', telephone: '', email: '', website: '',
  subscription_plan_id: 1,
  max_users: 20, max_storage_mb: 2048, max_camions: 20,
  modules_actives: ['transport', 'magasin', 'finance', 'qhse'],
});

export default function AdminTenantMultiTenant() {
  const { user } = useAuth();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [expandedModules, setExpandedModules] = useState(false);
  const logoInputRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState(emptyForm());

  const isSuperAdmin = Boolean(
    (user as any)?.is_superuser ||
    user?.roles?.some((r: string) => r.toUpperCase() === 'SUPER_ADMIN' || r.toUpperCase() === 'SUPERADMIN')
  );

  if (!isSuperAdmin) {
    return (
      <div className="max-w-2xl mx-auto my-12 bg-slate-900/90 border border-red-500/40 rounded-3xl p-8 text-center space-y-4 shadow-2xl backdrop-blur-xl">
        <div className="w-16 h-16 rounded-2xl bg-red-500/15 border border-red-500/30 text-red-400 flex items-center justify-center mx-auto">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <span className="text-xs font-black uppercase tracking-widest text-red-400 bg-red-500/10 px-3 py-1 rounded-full border border-red-500/20">
          Accès Restreint • Super Administrateur SaaS
        </span>
        <h2 className="text-2xl font-black text-slate-100">Supervision Multi-Entreprises Interdite</h2>
        <p className="text-xs text-slate-400 leading-relaxed max-w-lg mx-auto">
          Cette vue est réservée exclusivement au Super Administrateur de la plateforme CADC EVO-LOG SaaS.
        </p>
        <Link
          href="/admin-tenant/dashboard"
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-black rounded-xl shadow-lg transition-all"
        >
          <span>Retourner au Dashboard</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const fetchTenants = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/tenant/companies');
      const raw = res.data || [];
      setTenants(Array.isArray(raw) ? raw : []);
    } catch {
      setTenants([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTenants(); }, []);

  const filtered = tenants.filter(t =>
    t.nom.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (t.ville || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleLogoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLogoFile(file);
    const reader = new FileReader();
    reader.onload = () => setLogoPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const toggleModule = (modId: string) => {
    setForm(prev => {
      const current = Array.isArray(prev.modules_actives) ? prev.modules_actives : [];
      const updated = current.includes(modId) ? current.filter(m => m !== modId) : [...current, modId];
      return { ...prev, modules_actives: updated };
    });
  };

  const openCreateModal = () => {
    setEditingTenant(null);
    setForm(emptyForm());
    setLogoFile(null);
    setLogoPreview(null);
    setShowModal(true);
  };

  const openEditModal = (t: Tenant) => {
    setEditingTenant(t);
    let mods: string[] = [];
    try { mods = JSON.parse(t.modules_actives || '[]'); } catch { mods = []; }
    setForm({
      code: t.code, nom: t.nom, sigle: t.sigle || '',
      legal_form: t.legal_form || 'SA', capital_social: t.capital_social || '',
      tax_id: t.tax_id || '', rccm: t.rccm || '',
      agrement_douane: t.agrement_douane || '', agrement_pad: t.agrement_pad || '',
      agrement_pak: t.agrement_pak || '', rib: t.rib || '',
      ville: t.ville || 'Douala', pays: t.pays || 'Cameroun',
      telephone: t.telephone || '', email: t.email || '', website: t.website || '',
      subscription_plan_id: t.subscription_plan_id || 1,
      max_users: t.max_users, max_storage_mb: t.max_storage_mb, max_camions: t.max_camions || 20,
      modules_actives: mods,
    });
    setLogoPreview(t.logo_url || null);
    setLogoFile(null);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.code || !form.nom || !form.email || !form.tax_id) {
      toast.error('Code, Raison Sociale, Email et NIF sont obligatoires.');
      return;
    }
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        modules_actives: JSON.stringify(form.modules_actives),
      };

      let tenantId: number | null = editingTenant?.id ?? null;

      if (editingTenant) {
        await apiClient.put(`/api/v1/tenant/companies/${editingTenant.id}`, payload);
        toast.success('Entreprise mise à jour.');
      } else {
        const res = await apiClient.post('/api/v1/tenant/companies', payload);
        tenantId = res.data?.id;
        toast.success(`Tenant "${form.nom}" créé avec succès.`);
      }

      // Upload logo if selected
      if (logoFile && tenantId) {
        const fd = new FormData();
        fd.append('file', logoFile);
        await apiClient.post(`/api/v1/tenant/company-profile/upload-logo?company_id=${tenantId}`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }

      setShowModal(false);
      fetchTenants();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur lors de l\'enregistrement.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSuspend = async (t: Tenant) => {
    const raison = prompt(`Raison de suspension de "${t.nom}" :`);
    if (!raison) return;
    try {
      await apiClient.put(`/api/v1/tenant/companies/${t.id}/suspendre?raison=${encodeURIComponent(raison)}`);
      toast.success('Tenant suspendu.');
      fetchTenants();
    } catch { toast.error('Erreur lors de la suspension.'); }
  };

  const handleActivate = async (t: Tenant) => {
    try {
      await apiClient.put(`/api/v1/tenant/companies/${t.id}/activer`);
      toast.success('Tenant réactivé.');
      fetchTenants();
    } catch { toast.error('Erreur lors de la réactivation.'); }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-rose-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-rose-500/20 text-rose-300 border border-rose-500/30">
              Infrastructure Multi-Tenant CADC
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              SaaS SuperAdmin
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Building2 className="w-8 h-8 text-rose-400" />
            Gestion Multi-Tenant — Sociétés Clientes
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Provisionnement, onboarding, quotas, logo, informations légales OHADA et modules activés.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchTenants}
            className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={openCreateModal}
            className="px-4 py-2.5 bg-gradient-to-r from-rose-600 to-pink-500 text-white font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-rose-500/25 transition-all hover:opacity-90"
          >
            <Plus className="w-4 h-4" /> Nouvel Onboarding
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total Tenants', value: tenants.length, color: 'text-slate-100' },
          { label: 'Actifs', value: tenants.filter(t => t.is_active).length, color: 'text-emerald-400' },
          { label: 'Suspendus', value: tenants.filter(t => !t.is_active).length, color: 'text-amber-400' },
          { label: 'Total Utilisateurs', value: tenants.reduce((s, t) => s + t.current_users, 0), color: 'text-blue-400' },
        ].map(kpi => (
          <div key={kpi.label} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
            <p className="text-[10px] text-slate-400 uppercase tracking-wider">{kpi.label}</p>
            <p className={`text-2xl font-black mt-1 ${kpi.color}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Search + Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Rechercher par nom, code ou ville..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Entreprise</th>
                <th className="py-3.5 px-4">Infos Légales</th>
                <th className="py-3.5 px-4 text-center">Utilisateurs</th>
                <th className="py-3.5 px-4">Stockage</th>
                <th className="py-3.5 px-4 text-center">Modules</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-rose-400" />
                    Chargement des tenants...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center text-slate-400">
                    <Building2 className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                    <p className="font-sans font-semibold text-slate-300 text-sm">Aucune entreprise provisionnée</p>
                    <p className="text-xs mt-1 font-sans">Cliquez sur "Nouvel Onboarding" pour créer le premier tenant.</p>
                    <button
                      onClick={openCreateModal}
                      className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-xl transition-colors"
                    >
                      <Plus className="w-3.5 h-3.5" /> Premier Tenant
                    </button>
                  </td>
                </tr>
              ) : (
                filtered.map(t => {
                  let mods: string[] = [];
                  try { mods = JSON.parse(t.modules_actives || '[]'); } catch {}
                  const storageUsedGb = (t.current_storage_mb / 1024).toFixed(1);
                  const storageLimitGb = (t.max_storage_mb / 1024).toFixed(0);
                  const storagePct = Math.min((t.current_storage_mb / t.max_storage_mb) * 100, 100);

                  return (
                    <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          {t.logo_url ? (
                            <img src={t.logo_url} alt={t.nom} className="w-8 h-8 rounded-lg object-contain bg-white p-0.5 border border-slate-700" />
                          ) : (
                            <div className="w-8 h-8 rounded-lg bg-slate-700 text-slate-200 flex items-center justify-center font-black text-[10px]">
                              {(t.sigle || t.code || '?').slice(0, 3).toUpperCase()}
                            </div>
                          )}
                          <div>
                            <div className="font-bold text-rose-400 font-mono text-[11px]">{t.code}</div>
                            <div className="font-sans font-semibold text-slate-100 text-sm leading-tight">{t.nom}</div>
                            <div className="text-slate-400 text-[10px]">{t.ville}, {t.pays}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="space-y-0.5 text-[10px]">
                          {t.tax_id && <p><span className="text-slate-500">NIF :</span> {t.tax_id}</p>}
                          {t.rccm && <p><span className="text-slate-500">RCCM :</span> {t.rccm}</p>}
                          {t.email && <p className="text-slate-400">{t.email}</p>}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="font-bold text-blue-400">{t.current_users}</span>
                        <span className="text-slate-500">/{t.max_users}</span>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden min-w-[60px]">
                            <div
                              className="h-full bg-rose-500 rounded-full transition-all"
                              style={{ width: `${storagePct}%` }}
                            />
                          </div>
                          <span className="text-slate-300 whitespace-nowrap text-[10px]">
                            {storageUsedGb}/{storageLimitGb}Go
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="text-slate-300 font-sans">
                          {mods.length}/{ALL_MODULES.length}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          t.is_active
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}>
                          {t.is_active ? 'ACTIF' : 'SUSPENDU'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <button
                            onClick={() => openEditModal(t)}
                            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
                            title="Configurer"
                          >
                            <Edit className="w-3.5 h-3.5" />
                          </button>
                          {t.is_active ? (
                            <button
                              onClick={() => handleSuspend(t)}
                              className="p-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-lg border border-amber-500/20"
                              title="Suspendre"
                            >
                              <Pause className="w-3.5 h-3.5" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handleActivate(t)}
                              className="p-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-lg border border-emerald-500/20"
                              title="Réactiver"
                            >
                              <Play className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Onboarding Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-start justify-center p-4 bg-black/70 backdrop-blur-sm overflow-y-auto">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-2xl w-full p-6 sm:p-8 space-y-6 my-8 shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-black uppercase tracking-widest text-rose-400">
                  {editingTenant ? 'Modifier Tenant' : 'Onboarding Nouveau Tenant'}
                </span>
                <h3 className="text-lg font-black text-slate-100">
                  {editingTenant ? editingTenant.nom : 'Nouvelle Entreprise Cliente'}
                </h3>
              </div>
              <button onClick={() => setShowModal(false)}
                className="p-2 rounded-xl border border-slate-700 hover:bg-slate-800 text-slate-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Logo Upload */}
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">
                  Logo Officiel de l'Entreprise
                </label>
                <div className="flex items-center gap-4">
                  <div
                    className="w-20 h-20 rounded-2xl bg-slate-800 border-2 border-dashed border-slate-600 flex items-center justify-center cursor-pointer hover:border-rose-500 transition-colors overflow-hidden"
                    onClick={() => logoInputRef.current?.click()}
                  >
                    {logoPreview ? (
                      <img src={logoPreview} alt="Logo" className="w-full h-full object-contain p-1" />
                    ) : (
                      <div className="text-center">
                        <Upload className="w-6 h-6 text-slate-500 mx-auto mb-1" />
                        <span className="text-[9px] text-slate-500">PNG/SVG</span>
                      </div>
                    )}
                  </div>
                  <input ref={logoInputRef} type="file" accept="image/*" className="hidden" onChange={handleLogoSelect} />
                  <div className="text-xs text-slate-400">
                    <p>Glissez ou cliquez pour uploader le logo officiel.</p>
                    <p className="text-slate-500 mt-0.5">Formats : PNG, JPG, SVG, WEBP • Max 2 Mo</p>
                    {logoFile && <p className="text-emerald-400 mt-1">✓ {logoFile.name}</p>}
                  </div>
                </div>
              </div>

              {/* Identity */}
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-rose-400 mb-3">Identité & Raison Sociale</p>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Code Tenant *', key: 'code', ph: 'EX: LPC-DLA' },
                    { label: 'Sigle', key: 'sigle', ph: 'Ex: LPC' },
                  ].map(f => (
                    <div key={f.key}>
                      <label className="block text-[11px] font-semibold text-slate-400 mb-1">{f.label}</label>
                      <input
                        value={(form as any)[f.key]}
                        onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                        placeholder={f.ph}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-rose-500 font-mono"
                        required={f.key === 'code'}
                      />
                    </div>
                  ))}
                </div>
                <div className="mt-3">
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Raison Sociale Complète *</label>
                  <input
                    value={form.nom}
                    onChange={e => setForm(p => ({ ...p, nom: e.target.value }))}
                    placeholder="Logistique Portuaire Cameroun SA"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-rose-500"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-3 mt-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 mb-1">Forme Juridique</label>
                    <select
                      value={form.legal_form}
                      onChange={e => setForm(p => ({ ...p, legal_form: e.target.value }))}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-rose-500"
                    >
                      {['SA', 'SARL', 'SAS', 'SNC', 'GIE', 'EP'].map(f => <option key={f}>{f}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 mb-1">Capital Social</label>
                    <input
                      value={form.capital_social}
                      onChange={e => setForm(p => ({ ...p, capital_social: e.target.value }))}
                      placeholder="100 000 000 FCFA"
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-rose-500"
                    />
                  </div>
                </div>
              </div>

              {/* Legal IDs */}
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-rose-400 mb-3">Identifiants Légaux OHADA</p>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'NIF *', key: 'tax_id', ph: 'M010200034567P' },
                    { label: 'RCCM', key: 'rccm', ph: 'RC/DLA/2019/B/890' },
                    { label: 'Agrémt Douane DGD', key: 'agrement_douane', ph: 'DEC-DGD-2021/045' },
                    { label: 'Agrémt PAD', key: 'agrement_pad', ph: 'PAD-ACC-2022/88' },
                    { label: 'Agrémt PAK', key: 'agrement_pak', ph: 'PAK-TRANSIT-2023/12' },
                    { label: 'RIB Bancaire', key: 'rib', ph: '10019 02345 01234567890 45' },
                  ].map(f => (
                    <div key={f.key}>
                      <label className="block text-[11px] font-semibold text-slate-400 mb-1">{f.label}</label>
                      <input
                        value={(form as any)[f.key]}
                        onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                        placeholder={f.ph}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-[11px] text-slate-100 placeholder-slate-600 focus:outline-none focus:border-rose-500 font-mono"
                        required={f.key === 'tax_id'}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Coordinates */}
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-rose-400 mb-3">Coordonnées</p>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Email Admin *', key: 'email', ph: 'admin@entreprise.cm' },
                    { label: 'Téléphone', key: 'telephone', ph: '+237 233 XX XX XX' },
                    { label: 'Ville', key: 'ville', ph: 'Douala' },
                    { label: 'Site Web', key: 'website', ph: 'https://entreprise.cm' },
                  ].map(f => (
                    <div key={f.key}>
                      <label className="block text-[11px] font-semibold text-slate-400 mb-1">{f.label}</label>
                      <input
                        value={(form as any)[f.key]}
                        onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                        placeholder={f.ph}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-rose-500"
                        required={f.key === 'email'}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Quotas */}
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-rose-400 mb-3">Quotas & Limites</p>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: 'Max Utilisateurs', key: 'max_users' },
                    { label: 'Stockage (Mo)', key: 'max_storage_mb' },
                    { label: 'Max Camions', key: 'max_camions' },
                  ].map(f => (
                    <div key={f.key}>
                      <label className="block text-[11px] font-semibold text-slate-400 mb-1">{f.label}</label>
                      <input
                        type="number"
                        value={(form as any)[f.key]}
                        onChange={e => setForm(p => ({ ...p, [f.key]: Number(e.target.value) }))}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-rose-500 font-mono"
                        min={0}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Module Flags */}
              <div>
                <button
                  type="button"
                  onClick={() => setExpandedModules(p => !p)}
                  className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-rose-400 mb-3 hover:text-rose-300"
                >
                  <Zap className="w-3.5 h-3.5" />
                  Modules Activés ({(form.modules_actives as string[]).length}/{ALL_MODULES.length})
                  <ChevronDown className={`w-3.5 h-3.5 transition-transform ${expandedModules ? 'rotate-180' : ''}`} />
                </button>
                {expandedModules && (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {ALL_MODULES.map(mod => {
                      const active = (form.modules_actives as string[]).includes(mod.id);
                      return (
                        <label
                          key={mod.id}
                          className={`flex items-center gap-2 p-2 rounded-xl border cursor-pointer text-xs transition-colors ${
                            active
                              ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                              : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={active}
                            onChange={() => toggleModule(mod.id)}
                            className="w-3.5 h-3.5 accent-rose-500"
                          />
                          <span>{mod.icon}</span>
                          <span className="font-medium truncate">{mod.label}</span>
                        </label>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="flex gap-3 justify-end pt-2 border-t border-slate-800">
                <button type="button"
                  onClick={() => setShowModal(false)}
                  className="px-5 py-2.5 text-xs font-bold border border-slate-700 rounded-xl text-slate-300 hover:bg-slate-800">
                  Annuler
                </button>
                <button type="submit" disabled={submitting}
                  className="px-6 py-2.5 text-xs font-black rounded-xl bg-gradient-to-r from-rose-600 to-pink-500 text-white hover:opacity-90 disabled:opacity-50 shadow-lg shadow-rose-500/20">
                  {submitting ? 'Enregistrement...' : editingTenant ? 'Mettre à Jour' : 'Créer le Tenant'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

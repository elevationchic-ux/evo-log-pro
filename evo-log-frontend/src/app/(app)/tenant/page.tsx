'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2, Users, Shield, CreditCard, RefreshCw, PlusCircle,
  CheckCircle2, AlertTriangle, Settings, Activity, Globe, X, Save
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function TenantPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [plans, setPlans] = useState<any[]>([]);
  const [companyProfile, setCompanyProfile] = useState<any>(null);
  const [rapportCompanies, setRapportCompanies] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCompany, setNewCompany] = useState({
    nom: '',
    email: '',
    pays: 'Cameroun',
    plan_id: '',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resCo, resPlans, resProfile, resRapport] = await Promise.allSettled([
        apiClient.get('/api/v1/tenant/companies'),
        apiClient.get('/api/v1/tenant/plans'),
        apiClient.get('/api/v1/tenant/company-profile'),
        apiClient.get('/api/v1/tenant/reports/companies')
      ]);
      if (resCo.status === 'fulfilled' && resCo.value.data)
        setCompanies(resCo.value.data || []);
      if (resPlans.status === 'fulfilled' && resPlans.value.data)
        setPlans(resPlans.value.data || []);
      if (resProfile.status === 'fulfilled' && resProfile.value.data)
        setCompanyProfile(resProfile.value.data);
      if (resRapport.status === 'fulfilled' && resRapport.value.data)
        setRapportCompanies(resRapport.value.data);
    } catch (err) {
      console.error('Tenant fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreateCompany = async () => {
    try {
      await apiClient.post('/api/v1/tenant/companies', {
        ...newCompany,
        plan_id: parseInt(newCompany.plan_id) || 1,
      });
      setShowCreateForm(false);
      fetchData();
    } catch (err) { console.error('Erreur création société:', err); }
  };

  const handleActiver = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/tenant/companies/${id}/activer`);
      fetchData();
    } catch (err) { console.error('Erreur activation:', err); }
  };

  const handleSuspendre = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/tenant/companies/${id}/suspendre`);
      fetchData();
    } catch (err) { console.error('Erreur suspension:', err); }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Building2 className="w-3.5 h-3.5" /> Multi-Tenant  Gestion des Sociétés Clientes & Abonnements SaaS
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Gestion Multi-Tenant & Sociétés</h1>
          <p className="text-xs text-slate-400 mt-1">Administration des tenants SaaS, plans d'abonnement, activation/suspension de sociétés et personnalisation des portails B2B.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => setShowCreateForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-900/20 transition-all">
            <PlusCircle className="w-4 h-4" /> Nouvelle Société
          </button>
        </div>
      </div>

      {/* Rapport Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Sociétés Actives', value: rapportCompanies?.actives ?? companies.filter(c => c.statut === 'actif').length, icon: Building2, color: 'text-emerald-400' },
          { label: 'Total Sociétés', value: companies.length, icon: Globe, color: 'text-cyan-400' },
          { label: 'Plans Disponibles', value: plans.length, icon: CreditCard, color: 'text-purple-400' },
          { label: 'Suspendues', value: rapportCompanies?.suspendues ?? companies.filter(c => c.statut === 'suspendu').length, icon: AlertTriangle, color: 'text-amber-400' },
        ].map((s) => (
          <div key={s.label} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">{s.label}</span>
              <s.icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <p className={`text-2xl font-black mt-2 ${s.color}`}>{loading ? '' : s.value}</p>
          </div>
        ))}
      </div>

      {/* Company Profile Card */}
      {companyProfile && (
        <div className="bg-slate-900/80 border border-emerald-500/20 p-6 rounded-3xl">
          <div className="flex items-center gap-3 mb-4">
            <Settings className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-black text-white">Profil de la Société Courante</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {[
              { label: 'Raison Sociale', value: companyProfile.nom },
              { label: 'Pays', value: companyProfile.pays },
              { label: 'Email', value: companyProfile.email },
              { label: 'Statut', value: companyProfile.statut || 'Actif' },
            ].map(f => (
              <div key={f.label}>
                <span className="text-[11px] font-semibold text-slate-500 block">{f.label}</span>
                <span className="text-slate-100 font-bold">{f.value || ''}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {showCreateForm && (
        <div className="bg-slate-900/90 border border-emerald-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Créer une Nouvelle Société (Tenant)</h2>
            <button onClick={() => setShowCreateForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'nom', label: 'Raison Sociale', type: 'text' },
              { key: 'email', label: 'Email Principal', type: 'email' },
              { key: 'pays', label: 'Pays', type: 'text' },
              { key: 'plan_id', label: 'ID Plan Abonnement', type: 'number' },
            ].map(f => (
              <div key={f.key}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input type={f.type} value={(newCompany as any)[f.key]} onChange={(e) => setNewCompany({ ...newCompany, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-emerald-500 transition-colors" />
              </div>
            ))}
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowCreateForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreateCompany} className="px-5 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-2">
              <Save className="w-4 h-4" /> Créer le Tenant
            </button>
          </div>
        </div>
      )}

      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <Building2 className="w-5 h-5 text-emerald-400" />
          <h2 className="text-base font-black text-white">Sociétés Clientes (Tenants)</h2>
          <span className="ml-auto text-xs text-slate-400">{companies.length} sociétés</span>
        </div>
        {loading ? (
          <div className="p-12 text-center"><RefreshCw className="w-6 h-6 animate-spin text-emerald-400 mx-auto mb-2" /></div>
        ) : companies.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Building2 className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="font-bold text-white">Aucune société cliente enregistrée</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800/80">
                  {['Raison Sociale', 'Pays', 'Email', 'Plan', 'Statut', 'Actions'].map(h => (
                    <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {companies.map((c: any) => (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-4 font-bold text-white">{c.nom}</td>
                    <td className="px-5 py-4 text-slate-300">{c.pays || '-'}</td>
                    <td className="px-5 py-4 text-slate-300 text-xs">{c.email || '-'}</td>
                    <td className="px-5 py-4 text-slate-300">{c.plan_id || '-'}</td>
                    <td className="px-5 py-4">
                      <span className={`px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase border ${c.statut === 'actif' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : c.statut === 'suspendu' ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' : 'bg-slate-500/20 text-slate-400 border-slate-500/30'}`}>
                        {c.statut || 'Actif'}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        {c.statut !== 'actif' ? (
                          <button onClick={() => handleActiver(c.id)} className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold transition-all">Activer</button>
                        ) : (
                          <button onClick={() => handleSuspendre(c.id)} className="px-3 py-1.5 rounded-xl bg-amber-600/20 hover:bg-amber-600/30 text-amber-400 border border-amber-500/30 text-xs font-bold transition-all">Suspendre</button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

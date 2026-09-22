'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { 
  Crown, Building2, ShieldAlert, Zap, Tag, Activity, 
  Server, Database, CheckCircle2, AlertTriangle, ArrowRight,
  RefreshCw, Plus, Users, Globe, HardDrive, ShieldCheck, FileSpreadsheet, Loader2
} from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';
import { adminAPI, auditAPI, apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

interface GlobalKpis {
  tenants_total: number;
  tenants_actifs: number;
  users_total: number;
  users_actifs: number;
  storage_used_gb: number;
  system_uptime: string;
  active_sessions: number;
  api_calls_today: number;
}

interface TenantItem {
  id: number;
  code: string;
  nom: string;
  sigle?: string;
  ville?: string;
  pays?: string;
  max_users?: number;
  current_users?: number;
  is_active: boolean;
  is_verified?: boolean;
  legal_form?: string;
}

interface PlanItem {
  id: number;
  code: string;
  nom: string;
  prix_mensuel: number;
  devise: string;
  max_users: number;
  max_storage_mb: number;
  description?: string;
}

interface SystemServiceItem {
  service: string;
  status: 'OK' | 'DEGRADED' | 'DOWN';
  uptime: string;
  responseMs: number;
  lastCheck: string;
  category?: string;
}

export default function SuperAdminSaasHub() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'tenants' | 'plans' | 'infra' | 'audit'>('tenants');
  const [loading, setLoading] = useState(true);

  // Dynamic state
  const [kpis, setKpis] = useState<GlobalKpis>({
    tenants_total: 4,
    tenants_actifs: 4,
    users_total: 87,
    users_actifs: 82,
    storage_used_gb: 17.8,
    system_uptime: '99.98%',
    active_sessions: 28,
    api_calls_today: 14250,
  });
  const [tenants, setTenants] = useState<TenantItem[]>([]);
  const [plans, setPlans] = useState<PlanItem[]>([]);
  const [services, setServices] = useState<SystemServiceItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);

  const isSuperAdmin = Boolean(
    (user as any)?.is_superuser ||
    user?.roles?.some(r => r.toUpperCase() === 'SUPER_ADMIN' || r.toUpperCase() === 'SUPERADMIN')
  );

  const loadAllData = useCallback(async () => {
    setLoading(true);
    try {
      const [kpiRes, tenantRes, planRes, healthRes, auditRes] = await Promise.allSettled([
        adminAPI.getDashboardKpis(),
        apiClient.get('/api/v1/tenant/companies'),
        apiClient.get('/api/v1/tenant/plans'),
        adminAPI.getSystemHealth(),
        auditAPI.getLogs({ limit: 10 })
      ]);

      if (kpiRes.status === 'fulfilled' && kpiRes.value?.data) {
        setKpis(kpiRes.value.data);
      }

      if (tenantRes.status === 'fulfilled' && tenantRes.value?.data) {
        const raw = tenantRes.value.data;
        setTenants(Array.isArray(raw) ? raw : []);
      }

      if (planRes.status === 'fulfilled' && planRes.value?.data) {
        const raw = planRes.value.data;
        setPlans(Array.isArray(raw) ? raw : []);
      }

      if (healthRes.status === 'fulfilled' && healthRes.value?.data?.services) {
        setServices(healthRes.value.data.services);
      }

      if (auditRes.status === 'fulfilled' && auditRes.value?.data) {
        const raw = auditRes.value.data?.items || auditRes.value.data || [];
        setAuditLogs(Array.isArray(raw) ? raw : []);
      }
    } catch (err) {
      console.error('Failed to load SuperAdmin dashboard data', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  if (!isSuperAdmin) {
    return (
      <div className="max-w-2xl mx-auto my-12 bg-slate-900/90 border border-red-500/40 rounded-3xl p-8 text-center space-y-4 shadow-2xl backdrop-blur-xl">
        <div className="w-16 h-16 rounded-2xl bg-red-500/15 border border-red-500/30 text-red-400 flex items-center justify-center mx-auto">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <span className="text-xs font-black uppercase tracking-widest text-red-400 bg-red-500/10 px-3 py-1 rounded-full border border-red-500/20">
          Accès Restreint • Super Administrateur SaaS
        </span>
        <h2 className="text-2xl font-black text-slate-100">Gouvernance Plateforme CADC Réservée</h2>
        <p className="text-xs text-slate-400 leading-relaxed max-w-lg mx-auto">
          Cette console de gouvernance globale est réservée exclusivement au Super Administrateur de la plateforme SaaS (<b>supadmin</b>). 
          Les administrateurs d&apos;entreprises clientes (LPC SA, TCL) doivent utiliser leur console dédiée.
        </p>
        <div className="pt-2">
          <Link
            href="/admin-tenant/dashboard"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-black rounded-xl shadow-lg transition-all"
          >
            <span>Accéder à l&apos;Administration de votre Entreprise</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Super Admin Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-amber-950/40 border border-amber-500/30 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden backdrop-blur-xl">
        <div className="absolute right-0 top-0 translate-x-10 -translate-y-10 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-amber-500 to-yellow-400 flex items-center justify-center text-slate-950 font-black text-2xl shadow-xl shadow-amber-500/20">
              <Crown className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-black uppercase tracking-widest text-amber-400 bg-amber-500/15 px-3 py-1 rounded-full border border-amber-500/30">
                  Gouvernance Plateforme Multi-Entreprises
                </span>
                <span className="text-xs text-slate-400 font-mono">Code Axis Digital Cameroun (CADC)</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-white mt-1">
                Console Super Administrateur SaaS
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Pilotage centralisé des entreprises clientes, plans d&apos;abonnement, quotas d&apos;infrastructure et passerelle portuaire.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                loadAllData();
                toast.success('Métriques multi-tenants rafraîchies');
              }}
              disabled={loading}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-xl text-xs font-bold flex items-center gap-2 transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-amber-400' : ''}`} />
              <span>Rafraîchir Métriques</span>
            </button>
            <Link
              href="/admin-tenant/multi-tenant"
              className="px-4 py-2.5 bg-gradient-to-r from-amber-600 to-yellow-500 hover:from-amber-500 hover:to-yellow-400 text-slate-950 font-black rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>Nouveau Tenant Client</span>
            </Link>
          </div>
        </div>

        {/* Global SaaS Platform KPIs */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-slate-800/80">
          <div className="bg-slate-950/60 rounded-xl p-3 border border-slate-800">
            <div className="text-[11px] text-slate-400 font-medium">Entreprises Actives</div>
            <div className="text-lg font-black text-amber-400 mt-0.5">{kpis.tenants_actifs} / {kpis.tenants_total} Tenants</div>
          </div>
          <div className="bg-slate-950/60 rounded-xl p-3 border border-slate-800">
            <div className="text-[11px] text-slate-400 font-medium">Utilisateurs Globaux</div>
            <div className="text-lg font-black text-slate-100 mt-0.5">{kpis.users_total} Comptes ({kpis.users_actifs} actifs)</div>
          </div>
          <div className="bg-slate-950/60 rounded-xl p-3 border border-slate-800">
            <div className="text-[11px] text-slate-400 font-medium">Volume de Données Total</div>
            <div className="text-lg font-black text-blue-400 mt-0.5">{kpis.storage_used_gb} Go</div>
          </div>
          <div className="bg-slate-950/60 rounded-xl p-3 border border-slate-800">
            <div className="text-[11px] text-slate-400 font-medium">Statut Infrastructure</div>
            <div className="text-lg font-black text-emerald-400 mt-0.5">{kpis.system_uptime} Uptime</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('tenants')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'tenants'
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Building2 className="w-4 h-4" />
          <span>Entreprises Clientes ({tenants.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('plans')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'plans'
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Tag className="w-4 h-4" />
          <span>Plans d&apos;Abonnement SaaS</span>
        </button>
        <button
          onClick={() => setActiveTab('infra')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'infra'
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Zap className="w-4 h-4" />
          <span>Infrastructure & Services Live</span>
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black transition-all ${
            activeTab === 'audit'
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Piste d&apos;Audit Immuable</span>
        </button>
      </div>

      {/* Tab: Tenants List */}
      {activeTab === 'tenants' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-200">Entreprises Clientes Déployées sur le SaaS EVO-LOG</span>
            <div className="flex items-center gap-3">
              <span className="text-[11px] text-amber-400 font-mono">Multi-Tenant Isolé</span>
              <Link
                href="/admin-tenant/multi-tenant"
                className="text-xs text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1"
              >
                <span>Gérer les Quotas</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          <div className="divide-y divide-slate-800/80">
            {tenants.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                {loading ? 'Chargement des entreprises clientes...' : 'Aucune entreprise trouvée.'}
              </div>
            ) : (
              tenants.map(t => (
                <div key={t.id} className="p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:bg-slate-800/40 transition-all">
                  <div className="flex items-center gap-3.5">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center justify-center font-black text-xs uppercase">
                      {t.sigle || t.code.slice(0, 3)}
                    </div>
                    <div>
                      <div className="text-sm font-bold text-slate-100 flex items-center gap-2">
                        <span>{t.nom}</span>
                        <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                          {t.legal_form || 'SA'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400">
                        {t.ville || 'Douala'} • Code : <span className="font-mono text-slate-300">{t.code}</span> • Max : {t.max_users || 20} utilisateurs
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-mono px-2.5 py-1 rounded-lg border ${
                      t.is_active 
                        ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' 
                        : 'text-red-400 bg-red-500/10 border-red-500/20'
                    }`}>
                      {t.is_active ? 'Actif & Vérifié' : 'Suspendu'}
                    </span>
                    <Link
                      href="/admin-tenant/multi-tenant"
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-lg transition-all"
                    >
                      Superviser
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab: Plans */}
      {activeTab === 'plans' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {plans.length > 0 ? (
            plans.map(p => (
              <div key={p.id} className="bg-slate-900/80 border border-slate-800 hover:border-amber-500/40 rounded-3xl p-6 space-y-4 shadow-xl transition-all">
                <span className="text-xs font-black uppercase px-3 py-1 rounded-full bg-slate-800 text-amber-300 border border-slate-700">
                  {p.nom}
                </span>
                <div className="text-2xl font-black text-slate-100">
                  {Number(p.prix_mensuel).toLocaleString('fr-FR')} {p.devise}{' '}
                  <span className="text-xs text-slate-400 font-normal">/ mois</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {p.description || `Jusqu'à ${p.max_users} utilisateurs et ${Math.round(p.max_storage_mb / 1024)} Go d'espace.`}
                </p>
                <div className="text-xs font-mono text-slate-300 pt-2 border-t border-slate-800">
                  Quota max : {p.max_users} comptes • {p.max_storage_mb} Mo
                </div>
              </div>
            ))
          ) : (
            <>
              <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
                <span className="text-xs font-black uppercase px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  STARTER
                </span>
                <div className="text-2xl font-black text-slate-100">350 000 FCFA <span className="text-xs text-slate-400 font-normal">/ mois</span></div>
                <p className="text-xs text-slate-400">Jusqu&apos;à 10 utilisateurs, Magasin, Transport de base, 5 Go de stockage.</p>
              </div>

              <div className="bg-slate-900/80 border border-blue-500/40 rounded-3xl p-6 space-y-4 shadow-xl">
                <span className="text-xs font-black uppercase px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40">
                  PRO
                </span>
                <div className="text-2xl font-black text-slate-100">750 000 FCFA <span className="text-xs text-slate-400 font-normal">/ mois</span></div>
                <p className="text-xs text-slate-400">Jusqu&apos;à 25 utilisateurs, SYDONIA+, Télémétrie FuelGuard, 20 Go de stockage.</p>
              </div>

              <div className="bg-gradient-to-b from-slate-900 to-amber-950/30 border border-amber-500/50 rounded-3xl p-6 space-y-4 shadow-xl shadow-amber-500/10">
                <span className="text-xs font-black uppercase px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                  ENTERPRISE (Actif LPC)
                </span>
                <div className="text-2xl font-black text-amber-400">1 500 000 FCFA <span className="text-xs text-slate-400 font-normal">/ mois</span></div>
                <p className="text-xs text-slate-400">Jusqu&apos;à 100 utilisateurs, Opérations Navires Quai 14, B2B Portal, 50 Go, SLA 99.9%.</p>
              </div>
            </>
          )}
        </div>
      )}

      {/* Tab: Infra */}
      {activeTab === 'infra' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.length > 0 ? (
            services.map((s, idx) => (
              <div key={idx} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Server className="w-5 h-5 text-amber-400" />
                    <h3 className="text-xs font-bold text-slate-100">{s.service}</h3>
                  </div>
                  <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full border ${
                    s.status === 'OK' 
                      ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' 
                      : 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                  }`}>
                    {s.status}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400 font-mono pt-2 border-t border-slate-800/80">
                  <span>Latence : {s.responseMs}ms</span>
                  <span>Uptime : {s.uptime}</span>
                </div>
                <div className="text-[11px] text-slate-500">Dernière vérif : {s.lastCheck}</div>
              </div>
            ))
          ) : (
            <div className="col-span-full p-6 text-center text-xs text-slate-400">
              Vérification des sondes de santé système en cours...
            </div>
          )}
        </div>
      )}

      {/* Tab: Audit */}
      {activeTab === 'audit' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-200">Journal d&apos;Audit Immuable de l&apos;Hébergeur SaaS</span>
            <Link
              href="/admin/audit"
              className="text-xs text-amber-400 hover:text-amber-300 font-bold flex items-center gap-1"
            >
              <span>Voir tout l&apos;audit trail</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="divide-y divide-slate-800/80">
            {auditLogs.slice(0, 5).map((log, idx) => (
              <div key={idx} className="p-4 flex items-center justify-between gap-4 text-xs">
                <div>
                  <div className="font-bold text-slate-200">{log.action || 'API_CALL'}</div>
                  <div className="text-slate-400">{log.user_email || 'Système'} • {log.target || log.resource || log.ip}</div>
                </div>
                <div className="text-right">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {log.status || 'SUCCESS'}
                  </span>
                  <div className="text-[11px] text-slate-500 mt-1 font-mono">{log.timestamp ? new Date(log.timestamp).toLocaleString('fr-FR') : 'Récent'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

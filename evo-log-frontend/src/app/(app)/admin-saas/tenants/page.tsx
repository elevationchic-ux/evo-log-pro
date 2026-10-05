'use client';

/**
 * Administration SaaS — Gestion des tenants.
 *
 * Honnêteté des données (règle Zéro-Mock) :
 *  - aucun tenant n'est jamais inventé : si /tenant/companies échoue, on
 *    affiche un état d'erreur, JAMAIS une liste de démonstration ;
 *  - aucun KPI n'est simulé : « Infrastructure Uptime 99.98% » a été retiré
 *    car aucune source de mesure n'existe. Les quatre compteurs viennent de la
 *    liste réelle des entreprises (retournée en totalité, non paginée) ;
 *  - une bascule actif/suspendu qui échoue côté serveur ne prétend pas avoir
 *    réussi : on show une erreur et on relit le serveur, pas de mise à jour
 *    optimiste mensongère ;
 *  - les colonnes vides restent vides (un tiret), elles ne reçoivent pas de
 *    valeur par défaut (« Cameroun », « 20 », « 10 ») qui ferait croire à une
 *    donnée saisie.
 */
import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Building2, Users, Package, CheckCircle2, Globe, Plus, Search, RefreshCw, WifiOff } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';
import { DataEmptyState, DataLoadingState } from '@/components/shared/StatePanels';

interface Tenant {
  id: number;
  code: string;
  nom: string;
  sigle?: string | null;
  pays?: string | null;
  ville?: string | null;
  max_users?: number | null;
  current_users?: number | null;
  is_active: boolean;
  is_verified?: boolean;
  legal_form?: string | null;
  modules_actives?: string | null;
}

/** Distingue un refus d'autorisation d'une panne réseau, pour un message honnête. */
function messageErreur(e: unknown, defaut: string): string {
  const status = (e as { response?: { status?: number } })?.response?.status;
  if (status === 401) return 'Session expirée. Reconnectez-vous pour consulter les tenants.';
  if (status === 403) return 'Accès réservé au Super-Admin : votre rôle ne peut pas lister les tenants.';
  return defaut;
}

export default function AdminSaasTenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const fetchTenants = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get('/api/v1/tenant/companies');
      const raw = res.data || [];
      setTenants(Array.isArray(raw) ? (raw as Tenant[]) : []);
    } catch (err) {
      console.error('Failed to fetch tenants', err);
      // Aucun repli sur des données fictives : la liste reste vide et l'état
      // d'erreur est montré à l'écran.
      setTenants([]);
      setError(messageErreur(err, 'Impossible de charger les tenants. Réessayez.'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTenants();
  }, [fetchTenants]);

  const handleToggleActive = async (tenant: Tenant) => {
    const nextActive = !tenant.is_active;
    try {
      if (tenant.is_active) {
        await apiClient.put(`/api/v1/tenant/companies/${tenant.id}/suspendre?raison=Suspension%20administrative`);
        toast.success(`Tenant ${tenant.nom} suspendu`);
      } else {
        await apiClient.put(`/api/v1/tenant/companies/${tenant.id}/activer`);
        toast.success(`Tenant ${tenant.nom} réactivé avec succès`);
      }
      // Relit la vérité serveur plutôt que de supposer le résultat.
      fetchTenants();
    } catch (err) {
      // Échec réel : on ne flippe PAS l'état local et on n'affiche pas un faux
      // succès. L'écran reflète ce que la base contient réellement.
      toast.error(messageErreur(err, `Échec de la ${nextActive ? 'réactivation' : 'suspension'} du tenant ${tenant.nom}.`));
    }
  };

  const filtered = tenants.filter(t =>
    t.nom.toLowerCase().includes(search.toLowerCase()) || t.code.toLowerCase().includes(search.toLowerCase())
  );

  // Compteurs réels, dérivés de la liste complète (le lister backend n'est pas
  // paginé : `tenants.length` est bien le total, pas une tranche tronquée).
  const activeCount = tenants.filter(t => t.is_active).length;
  const suspendedCount = tenants.length - activeCount;
  const verifiedCount = tenants.filter(t => t.is_verified).length;
  const totalUsers = tenants.reduce((acc, t) => acc + (Number(t.current_users) || 0), 0);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-slate-900/90 border border-purple-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-purple-500/20 text-purple-300 border border-purple-500/30">
            Administration SaaS • Gestion Multi-Tenant
          </span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
            T-Code : KADM_TNT
          </span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <Globe className="w-8 h-8 text-purple-400" />
              Gestion des Tenants EVO-LOG SaaS
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Supervision de tous les clients SaaS EVO-LOG : statut, quota d&apos;utilisateurs et vérification.
            </p>
          </div>
          <button
            onClick={fetchTenants}
            className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 self-start sm:self-center transition-all"
            title="Rafraîchir"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-purple-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPIs — tous issus des entreprises réellement retournées par le serveur */}
      {!loading && !error && tenants.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Tenants Actifs', value: `${activeCount} / ${tenants.length}`, icon: Building2, color: 'text-purple-400' },
            { label: 'Total Utilisateurs', value: totalUsers.toString(), icon: Users, color: 'text-blue-400' },
            { label: 'Comptes Suspendus', value: suspendedCount.toString(), icon: Package, color: 'text-amber-400' },
            { label: 'Tenants Vérifiés', value: `${verifiedCount} / ${tenants.length}`, icon: CheckCircle2, color: 'text-emerald-400' },
          ].map((kpi, i) => (
            <div key={i} className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl shadow-lg">
              <kpi.icon className={`w-5 h-5 ${kpi.color} mb-2`} />
              <div className={`text-xl font-black font-mono ${kpi.color}`}>{kpi.value}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">{kpi.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* États honnêtes : chargement, erreur, vide */}
      {loading ? (
        <DataLoadingState rows={5} label="Chargement des tenants…" />
      ) : error ? (
        <div className="text-center py-12 px-4 bg-slate-900/90 border border-red-500/30 rounded-3xl">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/30">
            <WifiOff className="w-6 h-6 text-red-400" />
          </div>
          <p className="mt-3 text-sm font-semibold text-slate-200">Chargement impossible</p>
          <p className="mt-1 text-xs text-slate-400 max-w-md mx-auto leading-relaxed">{error}</p>
          <button
            type="button"
            onClick={fetchTenants}
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 min-h-11 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Réessayer
          </button>
        </div>
      ) : tenants.length === 0 ? (
        <DataEmptyState
          title="Aucun tenant enregistré"
          description="Aucune entreprise n'existe encore dans la base SaaS. Créez le premier tenant pour démarrer la supervision."
        />
      ) : (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between gap-4">
            <div className="relative max-w-sm flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Rechercher un tenant par nom, code, pays..."
                className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500"
              />
            </div>
            <Link
              href="/admin-tenant/multi-tenant"
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors shadow-lg shadow-purple-600/20"
            >
              <Plus className="w-4 h-4" /> Nouveau Tenant
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider bg-slate-950">
                  <th className="py-3.5 px-4">Organisation</th>
                  <th className="py-3.5 px-4">Localisation</th>
                  <th className="py-3.5 px-4 text-center">Forme</th>
                  <th className="py-3.5 px-4 text-center">Utilisateurs</th>
                  <th className="py-3.5 px-4 text-center">Statut</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold font-sans text-slate-100">{t.nom}</div>
                      <div className="text-[11px] text-purple-400 font-mono">{t.code}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      {/* Une valeur non saisie reste un tiret, jamais un pays/ville par défaut. */}
                      <div className="font-sans">{t.pays || '—'}</div>
                      <div className="text-[11px] text-slate-500">{t.ville || '—'}</div>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="px-2 py-0.5 rounded text-[11px] font-black border border-slate-700 bg-slate-800 text-slate-300">
                        {t.legal_form || '—'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-blue-400">
                      {t.current_users ?? 0} / {t.max_users ?? 0}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${
                        t.is_active
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-red-500/10 text-red-400 border-red-500/20'
                      }`}>
                        {t.is_active ? 'ACTIF' : 'SUSPENDU'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleToggleActive(t)}
                          className={`px-2.5 py-1 text-[11px] rounded-lg font-bold transition-all ${
                            t.is_active
                              ? 'bg-amber-500/15 text-amber-300 hover:bg-amber-500/25 border border-amber-500/30'
                              : 'bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/25 border border-emerald-500/30'
                          }`}
                        >
                          {t.is_active ? 'Suspendre' : 'Activer'}
                        </button>
                        <Link
                          href="/admin-tenant/multi-tenant"
                          className="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-bold border border-slate-700 transition-all"
                        >
                          Éditer
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

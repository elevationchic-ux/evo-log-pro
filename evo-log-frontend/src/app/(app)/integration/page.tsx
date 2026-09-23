'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Link, Plug, RefreshCw, CheckCircle2, AlertTriangle,
  Activity, Server, Globe, Database, Zap, ArrowRight, XCircle
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function IntegrationPage() {
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [sydonia, setSydonia] = useState<any[]>([]);
  const [guichetUnique, setGuichetUnique] = useState<any[]>([]);
  const [pcs, setPcs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resInt, resSyd, resGU, resPCS] = await Promise.allSettled([
        apiClient.get('/api/v1/integration/integrations', { params: { limit: 20 } }),
        apiClient.get('/api/v1/integration/sydonia', { params: { limit: 10 } }),
        apiClient.get('/api/v1/integration/guichet-unique', { params: { limit: 10 } }),
        apiClient.get('/api/v1/integration/pcs', { params: { limit: 10 } })
      ]);
      if (resInt.status === 'fulfilled' && resInt.value.data)
        setIntegrations(resInt.value.data?.data || resInt.value.data || []);
      if (resSyd.status === 'fulfilled' && resSyd.value.data)
        setSydonia(resSyd.value.data?.data || resSyd.value.data || []);
      if (resGU.status === 'fulfilled' && resGU.value.data)
        setGuichetUnique(resGU.value.data?.data || resGU.value.data || []);
      if (resPCS.status === 'fulfilled' && resPCS.value.data)
        setPcs(resPCS.value.data?.data || resPCS.value.data || []);
    } catch (err) {
      console.error('Integration fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleActiverIntegration = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/integration/integrations/${id}/activer`);
      fetchData();
    } catch (err) { console.error('Erreur activation:', err); }
  };

  const systemCards = [
    {
      name: 'SYDONIA World',
      description: 'Interface EDI avec le système douanier Sydonia World DGD',
      dossiers: sydonia.length,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10 border-emerald-500/30',
      icon: Database,
    },
    {
      name: 'e-GUCE Cameroun',
      description: 'Guichet Unique de Commerce Extérieur  Formalités pré-dédouanement',
      dossiers: guichetUnique.length,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10 border-blue-500/30',
      icon: Globe,
    },
    {
      name: 'PCS Port Community',
      description: 'Port Community System  Échange données entre acteurs portuaires PAD/PAK',
      dossiers: pcs.length,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10 border-purple-500/30',
      icon: Server,
    },
    {
      name: 'Connecteurs Banques',
      description: 'Interfaces SWIFT / SEPA avec banques commerciales et BEAC',
      dossiers: integrations.filter(i => i.type === 'banque').length,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10 border-amber-500/30',
      icon: Zap,
    },
  ];

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Plug className="w-3.5 h-3.5" /> Intégrations Systèmes Cameroun  CAMCIS, GUCE, Sydonia, PCS, BEAC
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Passerelles & Intégrations Système</h1>
          <p className="text-xs text-slate-400 mt-1">Connecteurs temps-réel vers Sydonia World DGD, e-GUCE, PCS PAD/PAK, BEAC/XEAC et banques commerciales.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
        </div>
      </div>

      {/* System Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {systemCards.map((s) => (
          <div key={s.name} className={`bg-slate-900/80 border p-5 rounded-3xl ${s.bgColor}`}>
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-xl bg-slate-800/80 border border-slate-700/60`}>
                <s.icon className={`w-5 h-5 ${s.color}`} />
              </div>
              <span className="font-black text-white text-sm">{s.name}</span>
            </div>
            <p className="text-xs text-slate-400 mb-3">{s.description}</p>
            <div className="flex items-center justify-between">
              <span className={`text-2xl font-black ${s.color}`}>{loading ? '' : s.dossiers}</span>
              <span className="text-[10px] text-slate-500">dossiers liés</span>
            </div>
          </div>
        ))}
      </div>

      {/* Integrations Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <Link className="w-5 h-5 text-rose-400" />
          <h2 className="text-base font-black text-white">Intégrations Configurées</h2>
          <span className="ml-auto text-xs text-slate-400">{integrations.length} intégrations</span>
        </div>
        {loading ? (
          <div className="p-12 text-center text-slate-400"><RefreshCw className="w-6 h-6 animate-spin text-rose-400 mx-auto mb-2" /></div>
        ) : integrations.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Plug className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="font-bold text-white">Aucune intégration configurée</p>
            <p className="text-xs text-slate-500 mt-1">Configurez les connecteurs depuis le panneau administrateur.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800/80">
                  {['Système', 'Type', 'URL / Endpoint', 'Statut', 'Dernière Synchro', 'Actions'].map(h => (
                    <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {integrations.map((i: any) => (
                  <tr key={i.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-4 font-bold text-white">{i.nom}</td>
                    <td className="px-5 py-4 text-slate-300 capitalize">{i.type}</td>
                    <td className="px-5 py-4 font-mono text-xs text-slate-400 max-w-xs truncate">{i.base_url || i.url || '-'}</td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-1.5">
                        {i.actif ? (
                          <><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /><span className="text-xs text-emerald-400 font-bold">Actif</span></>
                        ) : (
                          <><XCircle className="w-3.5 h-3.5 text-slate-400" /><span className="text-xs text-slate-400 font-bold">Inactif</span></>
                        )}
                      </div>
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-400">
                      {i.derniere_synchro ? new Date(i.derniere_synchro).toLocaleString('fr-FR') : '-'}
                    </td>
                    <td className="px-5 py-4">
                      {!i.actif && (
                        <button onClick={() => handleActiverIntegration(i.id)} className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5 transition-all">
                          <Zap className="w-3.5 h-3.5" /> Activer
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Sydonia Dossiers */}
      {sydonia.length > 0 && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <Database className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-black text-white">Dossiers Sydonia World DGD</h2>
          </div>
          <div className="divide-y divide-slate-800/60">
            {sydonia.slice(0, 6).map((s: any) => (
              <div key={s.id} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                <div>
                  <span className="text-sm font-bold text-white">DUM #{s.numero_dum || s.id}</span>
                  <p className="text-xs text-slate-400 mt-0.5">Valeur CIF: {s.valeur_cif_xaf?.toLocaleString('fr-FR') || '-'} XAF • Circuit: {s.circuit_controle || '-'}</p>
                </div>
                <span className={`px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase border ${s.statut === 'accepté' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'}`}>
                  {s.statut || 'En cours'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

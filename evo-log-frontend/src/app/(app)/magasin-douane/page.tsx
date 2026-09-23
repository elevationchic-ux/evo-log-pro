'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Warehouse, FileText, RefreshCw, PlusCircle, CheckCircle2,
  AlertTriangle, Package, BarChart2, X, Save, Shield
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function MagasinDouanePage() {
  const [entrepots, setEntrepots] = useState<any[]>([]);
  const [declarations, setDeclarations] = useState<any[]>([]);
  const [inventaires, setInventaires] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEntrepotForm, setShowEntrepotForm] = useState(false);
  const [newEntrepot, setNewEntrepot] = useState({
    code_entrepot: `EA-${Date.now().toString().slice(-5)}`,
    nom: '',
    regime_douanier: 'entrepôt_public_type_A',
    capacite_m3: '',
    bureau_douane_id: '1',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resEntr, resDecl, resInv] = await Promise.allSettled([
        apiClient.get('/api/v1/magasin-douane/entrepots'),
        apiClient.get('/api/v1/magasin-douane/declarations', { params: { limit: 50 } }),
        apiClient.get('/api/v1/magasin-douane/inventaires', { params: { limit: 50 } })
      ]);
      if (resEntr.status === 'fulfilled' && resEntr.value.data)
        setEntrepots(resEntr.value.data?.data || resEntr.value.data || []);
      if (resDecl.status === 'fulfilled' && resDecl.value.data)
        setDeclarations(resDecl.value.data?.data || resDecl.value.data || []);
      if (resInv.status === 'fulfilled' && resInv.value.data)
        setInventaires(resInv.value.data?.data || resInv.value.data || []);
    } catch (err) {
      console.error('Magasin douane fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreateEntrepot = async () => {
    try {
      await apiClient.post('/api/v1/magasin-douane/entrepots', {
        ...newEntrepot,
        capacite_m3: parseFloat(newEntrepot.capacite_m3) || 1000,
        bureau_douane_id: parseInt(newEntrepot.bureau_douane_id) || 1,
      });
      setShowEntrepotForm(false);
      fetchData();
    } catch (err) { console.error('Erreur création entrepôt:', err); }
  };

  const handleAccepterDeclaration = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/magasin-douane/declarations/${id}/accepter`);
      fetchData();
    } catch (err) { console.error('Erreur acceptation:', err); }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Warehouse className="w-3.5 h-3.5" /> Entrepôt Sous Douane  Régimes Spéciaux Code des Douanes CEMAC
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Magasin Douane & Entrepôt Sous Douane</h1>
          <p className="text-xs text-slate-400 mt-1">Gestion des entrepôts agréés DGD, déclarations de mise en entrepôt, inventaires douaniers et surveillance douanière physique.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => setShowEntrepotForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold shadow-lg shadow-teal-900/20 transition-all">
            <PlusCircle className="w-4 h-4" /> Nouvel Entrepôt
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Entrepôts Agréés', value: entrepots.length, icon: Warehouse, color: 'text-teal-400' },
          { label: 'Déclarations', value: declarations.length, icon: FileText, color: 'text-cyan-400' },
          { label: 'En Attente', value: declarations.filter(d => d.statut === 'en_attente' || !d.statut).length, icon: AlertTriangle, color: 'text-amber-400' },
          { label: 'Inventaires', value: inventaires.length, icon: Package, color: 'text-purple-400' },
        ].map((s) => (
          <div key={s.label} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">{s.label}</span>
              <s.icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <p className={`text-2xl font-black mt-2 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {showEntrepotForm && (
        <div className="bg-slate-900/90 border border-teal-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Créer un Entrepôt Agréé DGD</h2>
            <button onClick={() => setShowEntrepotForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'code_entrepot', label: 'Code Entrepôt', type: 'text' },
              { key: 'nom', label: 'Nom / Dénomination', type: 'text' },
              { key: 'capacite_m3', label: 'Capacité (m³)', type: 'number' },
              { key: 'bureau_douane_id', label: 'Bureau de Douane', type: 'number' },
            ].map(f => (
              <div key={f.key}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input type={f.type} value={(newEntrepot as any)[f.key]} onChange={(e) => setNewEntrepot({ ...newEntrepot, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-teal-500 transition-colors" />
              </div>
            ))}
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Régime Douanier</label>
              <select value={newEntrepot.regime_douanier} onChange={(e) => setNewEntrepot({ ...newEntrepot, regime_douanier: e.target.value })}
                className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-teal-500">
                <option value="entrepôt_public_type_A">Entrepôt Public Type A</option>
                <option value="entrepôt_privé_type_D">Entrepôt Privé Type D</option>
                <option value="entrepôt_spécial">Entrepôt Spécial</option>
                <option value="zone_franche">Zone Franche</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowEntrepotForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreateEntrepot} className="px-5 py-2.5 rounded-2xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold flex items-center gap-2">
              <Save className="w-4 h-4" /> Créer l'Entrepôt
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Entrepôts */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <Warehouse className="w-5 h-5 text-teal-400" />
            <h2 className="text-base font-black text-white">Entrepôts Agréés DGD</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center"><RefreshCw className="w-5 h-5 animate-spin text-teal-400 mx-auto mb-2 mt-2" /></div>
          ) : entrepots.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucun entrepôt enregistré.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {entrepots.map((e: any) => (
                <div key={e.id} className="p-4 hover:bg-slate-800/40 transition-colors">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">{e.code_entrepot}  {e.nom}</span>
                    <span className={`px-2 py-1 rounded-lg text-[10px] font-bold border ${e.statut === 'actif' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-slate-500/20 text-slate-400 border-slate-500/30'}`}>
                      {e.statut || 'Actif'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">Régime: {e.regime_douanier} • Cap: {e.capacite_m3} m³</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Déclarations de Mise en Entrepôt */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <FileText className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-black text-white">Déclarations de Mise en Entrepôt</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center"><RefreshCw className="w-5 h-5 animate-spin text-teal-400 mx-auto mb-2 mt-2" /></div>
          ) : declarations.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucune déclaration en attente.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {declarations.slice(0, 8).map((d: any) => (
                <div key={d.id} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                  <div>
                    <span className="text-sm font-bold text-white">{d.numero_declaration || `DECL-${d.id}`}</span>
                    <p className="text-xs text-slate-400 mt-0.5">Entrepôt #{d.entrepot_id} • {d.date_entree ? new Date(d.date_entree).toLocaleDateString('fr-FR') : '-'}</p>
                  </div>
                  {d.statut === 'en_attente' || !d.statut ? (
                    <button onClick={() => handleAccepterDeclaration(d.id)} className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5 transition-all">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Accepter
                    </button>
                  ) : (
                    <span className="px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Accepté</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Globe, Truck, FileText, Shield, RefreshCw, PlusCircle,
  CheckCircle2, AlertTriangle, Map, X, Save, ArrowRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function TransitAvancePage() {
  const [dossiers, setDossiers] = useState<any[]>([]);
  const [bureauxDouane, setBureauxDouane] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newBureau, setNewBureau] = useState({
    code_bureau: '',
    nom: '',
    pays: 'Cameroun',
    type_bureau: 'principal',
    adresse: '',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resDoss, resBur] = await Promise.allSettled([
        apiClient.get('/api/v1/transit-avance/dossiers', { params: { limit: 50 } }),
        apiClient.get('/api/v1/transit-avance/bureaux-douane')
      ]);
      if (resDoss.status === 'fulfilled' && resDoss.value.data)
        setDossiers(resDoss.value.data?.data || resDoss.value.data || []);
      if (resBur.status === 'fulfilled' && resBur.value.data)
        setBureauxDouane(resBur.value.data?.data || resBur.value.data || []);
    } catch (err) {
      console.error('Transit avancé fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreateBureau = async () => {
    try {
      await apiClient.post('/api/v1/transit-avance/bureaux-douane', newBureau);
      setShowForm(false);
      fetchData();
    } catch (err) { console.error('Erreur création bureau:', err); }
  };

  const getStatutBadge = (s: string) => {
    switch (s) {
      case 'en_transit': return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      case 'delivré': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'bloqué': return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      default: return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Globe className="w-3.5 h-3.5" /> Transit Avancé — Corridors CEMAC, TIR, Bureaux Douane
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Transit Routier Avancé — Corridor CEMAC</h1>
          <p className="text-xs text-slate-400 mt-1">Suivi des dossiers de transit sur les corridors Douala-N'Djaména, Douala-Bangui, Douala-Moundou avec les bureaux de douane CEMAC.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-lg shadow-blue-900/20 transition-all">
            <PlusCircle className="w-4 h-4" /> Bureau Douane
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Dossiers Transit', value: dossiers.length, icon: FileText, color: 'text-cyan-400' },
          { label: 'En Transit', value: dossiers.filter(d => d.statut === 'en_transit').length, icon: Truck, color: 'text-blue-400' },
          { label: 'Livrés', value: dossiers.filter(d => d.statut === 'delivré').length, icon: CheckCircle2, color: 'text-emerald-400' },
          { label: 'Bureaux Douane', value: bureauxDouane.length, icon: Shield, color: 'text-purple-400' },
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

      {showForm && (
        <div className="bg-slate-900/90 border border-blue-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Enregistrer Bureau de Douane CEMAC</h2>
            <button onClick={() => setShowForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'code_bureau', label: 'Code Bureau', type: 'text' },
              { key: 'nom', label: 'Nom du Bureau', type: 'text' },
              { key: 'pays', label: 'Pays', type: 'text' },
              { key: 'adresse', label: 'Adresse / Localité', type: 'text' },
            ].map(f => (
              <div key={f.key}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input type={f.type} value={(newBureau as any)[f.key]} onChange={(e) => setNewBureau({ ...newBureau, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
            ))}
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Type Bureau</label>
              <select value={newBureau.type_bureau} onChange={(e) => setNewBureau({ ...newBureau, type_bureau: e.target.value })}
                className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-blue-500">
                <option value="principal">Principal</option>
                <option value="annexe">Annexe</option>
                <option value="frontalier">Frontalier</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreateBureau} className="px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center gap-2">
              <Save className="w-4 h-4" /> Enregistrer
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <FileText className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-black text-white">Dossiers de Transit CEMAC</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center"><RefreshCw className="w-5 h-5 animate-spin text-blue-400 mx-auto mb-2 mt-2" /></div>
          ) : dossiers.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucun dossier de transit.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {dossiers.slice(0, 10).map((d: any) => (
                <div key={d.id} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                  <div>
                    <span className="text-sm font-bold text-white">{d.numero_dossier || `TRANSIT-${d.id}`}</span>
                    <p className="text-xs text-slate-400 mt-0.5">{d.corridor || 'Corridor CEMAC'} • {d.date_depart ? new Date(d.date_depart).toLocaleDateString('fr-FR') : '-'}</p>
                  </div>
                  <span className={`px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase border ${getStatutBadge(d.statut)}`}>
                    {d.statut || 'En attente'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <Map className="w-5 h-5 text-blue-400" />
            <h2 className="text-base font-black text-white">Bureaux de Douane Enregistrés</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center"><RefreshCw className="w-5 h-5 animate-spin text-blue-400 mx-auto mb-2 mt-2" /></div>
          ) : bureauxDouane.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucun bureau de douane.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {bureauxDouane.map((b: any) => (
                <div key={b.id} className="p-4 hover:bg-slate-800/40 transition-colors">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">{b.code_bureau} — {b.nom}</span>
                    <span className="text-xs text-slate-400">{b.pays}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">Type: {b.type_bureau} • {b.adresse || '-'}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

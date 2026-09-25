'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Truck, Globe, FileText, Shield, RefreshCw, PlusCircle,
  CheckCircle2, AlertTriangle, MapPin, X, Save, ArrowRight, Anchor
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function TransportInternationalPage() {
  const [ordres, setOrdres] = useState<any[]>([]);
  const [carnets, setCarnets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newOrdre, setNewOrdre] = useState({
    numero_ordre: '',
    mode_transport: 'routier',
    pays_depart: 'Cameroun',
    pays_destination: 'Tchad',
    marchandise: '',
    poids_kg: '',
    incoterm: 'CIF',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resOrdres, resCarnets] = await Promise.allSettled([
        apiClient.get('/api/v1/transport-international/ordres-transport', { params: { limit: 50 } }),
        apiClient.get('/api/v1/transport-international/carnets-tir', { params: { limit: 50 } })
      ]);
      if (resOrdres.status === 'fulfilled' && resOrdres.value.data)
        setOrdres(resOrdres.value.data?.data || resOrdres.value.data || []);
      if (resCarnets.status === 'fulfilled' && resCarnets.value.data)
        setCarnets(resCarnets.value.data?.data || resCarnets.value.data || []);
    } catch (err) {
      console.error('Transport international fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreateOrdre = async () => {
    try {
      await apiClient.post('/api/v1/transport-international/ordres-transport', {
        ...newOrdre,
        poids_kg: parseFloat(newOrdre.poids_kg) || 0,
      });
      setShowForm(false);
      fetchData();
    } catch (err) { console.error('Erreur création OT:', err); }
  };

  const handleEnTransit = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/transport-international/ordres-transport/${id}/en-transit`);
      fetchData();
    } catch (err) { console.error('Erreur mise en transit:', err); }
  };

  const handleLivrer = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/transport-international/ordres-transport/${id}/livre`);
      fetchData();
    } catch (err) { console.error('Erreur livraison:', err); }
  };

  const getStatutBadge = (s: string) => {
    switch (s) {
      case 'en_transit': return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      case 'livré': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'annulé': return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      default: return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Globe className="w-3.5 h-3.5" /> Transport International  TIR, CMR, Corridors CEMAC & Afrique Centrale
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Transport International & TIR Routier</h1>
          <p className="text-xs text-slate-400 mt-1">Gestion des ordres de transport internationaux, carnets TIR IRU, lettres de voiture CMR, et corridors Douala-N'Djaména-Bangui.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-900/20 transition-all">
            <PlusCircle className="w-4 h-4" /> Ordre Transport
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Ordres Transport', value: ordres.length, icon: Truck, color: 'text-indigo-400' },
          { label: 'En Transit', value: ordres.filter(o => o.statut === 'en_transit').length, icon: ArrowRight, color: 'text-cyan-400' },
          { label: 'Livrés', value: ordres.filter(o => o.statut === 'livré').length, icon: CheckCircle2, color: 'text-emerald-400' },
          { label: 'Carnets TIR', value: carnets.length, icon: Shield, color: 'text-amber-400' },
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
        <div className="bg-slate-900/90 border border-indigo-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Créer un Ordre de Transport International</h2>
            <button onClick={() => setShowForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'numero_ordre', label: 'N° Ordre Transport', type: 'text' },
              { key: 'pays_depart', label: 'Pays de Départ', type: 'text' },
              { key: 'pays_destination', label: 'Pays de Destination', type: 'text' },
              { key: 'marchandise', label: 'Nature de la Marchandise', type: 'text' },
              { key: 'poids_kg', label: 'Poids (kg)', type: 'number' },
            ].map(f => (
              <div key={f.key}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input type={f.type} value={(newOrdre as any)[f.key]} onChange={(e) => setNewOrdre({ ...newOrdre, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-indigo-500 transition-colors" />
              </div>
            ))}
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Mode Transport</label>
              <select value={newOrdre.mode_transport} onChange={(e) => setNewOrdre({ ...newOrdre, mode_transport: e.target.value })}
                className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-indigo-500">
                <option value="routier">Routier</option>
                <option value="maritime">Maritime</option>
                <option value="aérien">Aérien</option>
                <option value="ferroviaire">Ferroviaire</option>
                <option value="multimodal">Multimodal</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Incoterm ICC</label>
              <select value={newOrdre.incoterm} onChange={(e) => setNewOrdre({ ...newOrdre, incoterm: e.target.value })}
                className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-indigo-500">
                {['EXW', 'FCA', 'CPT', 'CIP', 'DAP', 'DPU', 'DDP', 'FAS', 'FOB', 'CFR', 'CIF'].map(i => (
                  <option key={i} value={i}>{i}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreateOrdre} className="px-5 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-2">
              <Save className="w-4 h-4" /> Créer l'Ordre
            </button>
          </div>
        </div>
      )}

      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <Truck className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-black text-white">Ordres de Transport International</h2>
          <span className="ml-auto text-xs text-slate-400">{ordres.length} ordres</span>
        </div>
        {loading ? (
          <div className="p-12 text-center text-slate-400"><RefreshCw className="w-6 h-6 animate-spin text-indigo-400 mx-auto mb-2" /></div>
        ) : ordres.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Globe className="w-10 h-10 text-slate-400 mx-auto mb-2" />
            <p className="font-bold text-white">Aucun ordre de transport international</p>
            <p className="text-xs text-slate-500 mt-1">Créez le premier OTI pour commencer.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800/80">
                  {['N° OTI', 'Mode', 'Départ → Destination', 'Incoterm', 'Poids (kg)', 'Statut', 'Actions'].map(h => (
                    <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {ordres.map((o: any) => (
                  <tr key={o.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-4 font-mono text-xs text-indigo-400">{o.numero_ordre}</td>
                    <td className="px-5 py-4 text-slate-300 capitalize">{o.mode_transport}</td>
                    <td className="px-5 py-4 text-slate-300 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-500" />{o.pays_depart}
                      <ArrowRight className="w-3 h-3 text-slate-500 mx-1" />
                      <MapPin className="w-3 h-3 text-cyan-500" />{o.pays_destination}
                    </td>
                    <td className="px-5 py-4 text-slate-300 font-mono">{o.incoterm}</td>
                    <td className="px-5 py-4 text-slate-300">{o.poids_kg?.toLocaleString('fr-FR') || '-'}</td>
                    <td className="px-5 py-4">
                      <span className={`px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase border ${getStatutBadge(o.statut)}`}>
                        {o.statut || 'Créé'}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        {o.statut === 'créé' || !o.statut ? (
                          <button onClick={() => handleEnTransit(o.id)} className="px-3 py-1.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 border border-cyan-500/30 text-xs font-bold transition-all">
                            → Transit
                          </button>
                        ) : o.statut === 'en_transit' ? (
                          <button onClick={() => handleLivrer(o.id)} className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold transition-all">
                            Livrer
                          </button>
                        ) : null}
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

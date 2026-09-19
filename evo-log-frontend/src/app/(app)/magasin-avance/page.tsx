'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Package, AlertTriangle, RefreshCw, Calendar, ArrowRight,
  Layers, BarChart2, ShieldAlert, PlusCircle, X, Save, Clock
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function MagasinAvancePage() {
  const [peremptions, setPeremptions] = useState<any[]>([]);
  const [peremptionsCritiques, setPeremptionsCritiques] = useState<any[]>([]);
  const [reservations, setReservations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showReservationForm, setShowReservationForm] = useState(false);
  const [newReservation, setNewReservation] = useState({ article_id: '', quantite: '', motif: '', expiration_heures: '48' });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resCritiques, resPerem, resRes] = await Promise.allSettled([
        apiClient.get('/api/v1/magasin-avance/peremptions/critiques'),
        apiClient.get('/api/v1/magasin-avance/peremptions/expirees'),
        apiClient.get('/api/v1/magasin-avance/reservations', { params: { limit: 50 } })
      ]);
      if (resCritiques.status === 'fulfilled' && resCritiques.value.data)
        setPeremptionsCritiques(resCritiques.value.data?.data || resCritiques.value.data || []);
      if (resPerem.status === 'fulfilled' && resPerem.value.data)
        setPeremptions(resPerem.value.data?.data || resPerem.value.data || []);
      if (resRes.status === 'fulfilled' && resRes.value.data)
        setReservations(resRes.value.data?.data || resRes.value.data || []);
    } catch (err) {
      console.error('Magasin avancé fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreateReservation = async () => {
    try {
      await apiClient.post('/api/v1/magasin-avance/reservations', {
        article_id: parseInt(newReservation.article_id) || 1,
        quantite: parseFloat(newReservation.quantite) || 1,
        motif: newReservation.motif,
        expiration_heures: parseInt(newReservation.expiration_heures) || 48
      });
      setShowReservationForm(false);
      fetchData();
    } catch (err) { console.error('Erreur création réservation:', err); }
  };

  const handleLiberer = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/magasin-avance/reservations/${id}/liberer`);
      fetchData();
    } catch (err) { console.error('Erreur libération:', err); }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Package className="w-3.5 h-3.5" /> WMS Avancé — FEFO, Réservations, Kits, Inventaire Tournant
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Magasin Avancé & Gestion des Stocks</h1>
          <p className="text-xs text-slate-400 mt-1">Gestion FEFO (First Expired First Out), réservations de lots, assemblage de kits et transferts inter-emplacements.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => setShowReservationForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold shadow-lg shadow-purple-900/20 transition-all">
            <PlusCircle className="w-4 h-4" /> Réserver Lot
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Lots Critiques', value: peremptionsCritiques.length, icon: AlertTriangle, color: 'text-rose-400' },
          { label: 'Lots Expirés', value: peremptions.length, icon: Clock, color: 'text-amber-400' },
          { label: 'Réservations Actives', value: reservations.filter(r => r.statut === 'active' || !r.statut).length, icon: Layers, color: 'text-purple-400' },
          { label: 'Total Réservations', value: reservations.length, icon: BarChart2, color: 'text-cyan-400' },
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

      {/* Reservation Form */}
      {showReservationForm && (
        <div className="bg-slate-900/90 border border-purple-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Nouvelle Réservation de Stock</h2>
            <button onClick={() => setShowReservationForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'article_id', label: 'ID Article', type: 'number' },
              { key: 'quantite', label: 'Quantité à Réserver', type: 'number' },
              { key: 'motif', label: 'Motif de Réservation', type: 'text' },
              { key: 'expiration_heures', label: 'Expiration (heures)', type: 'number' },
            ].map((f) => (
              <div key={f.key}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input
                  type={f.type}
                  value={(newReservation as any)[f.key]}
                  onChange={(e) => setNewReservation({ ...newReservation, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-purple-500 transition-colors"
                />
              </div>
            ))}
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowReservationForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreateReservation} className="px-5 py-2.5 rounded-2xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold flex items-center gap-2">
              <Save className="w-4 h-4" /> Réserver
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lots Critiques FEFO */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <h2 className="text-base font-black text-white">Lots Critiques (FEFO — Péremption &lt; 30j)</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center text-slate-400"><RefreshCw className="w-5 h-5 animate-spin text-purple-400 mx-auto mb-2" /></div>
          ) : peremptionsCritiques.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucun lot critique détecté.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {peremptionsCritiques.slice(0, 8).map((p: any) => (
                <div key={p.id} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                  <div>
                    <span className="text-sm font-bold text-white">Lot #{p.id} — Article {p.article_id}</span>
                    <p className="text-xs text-slate-400 mt-0.5">Qté: {p.quantite} • Expiration: {p.date_expiration ? new Date(p.date_expiration).toLocaleDateString('fr-FR') : '-'}</p>
                  </div>
                  <span className="px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/30">Critique</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Réservations */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <Layers className="w-5 h-5 text-purple-400" />
            <h2 className="text-base font-black text-white">Réservations de Stock Actives</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center text-slate-400"><RefreshCw className="w-5 h-5 animate-spin text-purple-400 mx-auto mb-2" /></div>
          ) : reservations.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucune réservation active.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {reservations.slice(0, 8).map((r: any) => (
                <div key={r.id} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                  <div>
                    <span className="text-sm font-bold text-white">Art. #{r.article_id} — {r.quantite} unités</span>
                    <p className="text-xs text-slate-400 mt-0.5">{r.motif || 'Sans motif'} • Expire: {r.expiration ? new Date(r.expiration).toLocaleDateString('fr-FR') : '-'}</p>
                  </div>
                  <button onClick={() => handleLiberer(r.id)} className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-bold transition-all">
                    Libérer
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

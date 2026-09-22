'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Code, Search, Plus, CheckCircle2, Webhook, Key, Terminal,
  RefreshCw, X, Shield, Globe, Send, ArrowRight
} from 'lucide-react';
import { partnerB2BAPI } from '@/lib/api-client';

interface WebhookItem {
  id: number;
  nom: string;
  url_webhook: string;
  evenements: string;
  statut: string;
  nombre_reussites: number;
  nombre_echecs: number;
}

export default function PartnerApiPage() {
  const [webhooks, setWebhooks] = useState<WebhookItem[]>([]);
  const [overview, setOverview] = useState<any>({
    api_name: 'EVO-LOG B2B Partner Gateway',
    version: 'v1.2',
    webhooks_count: 0,
    supported_events: []
  });
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Tracking console
  const [trackQuery, setTrackQuery] = useState('');
  const [trackResult, setTrackResult] = useState<any>(null);
  const [tracking, setTracking] = useState(false);

  // Formulaire Webhook
  const [formData, setFormData] = useState({
    nom: 'Webhook Système Client SAP',
    url_webhook: 'https://client-erp.cm/api/v1/evo-log-events',
    evenements: ['container.gate_in', 'customs.cleared', 'transport.delivered'],
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resOver, resHooks] = await Promise.allSettled([
        partnerB2BAPI.getOverview(),
        partnerB2BAPI.getWebhooks()
      ]);

      if (resOver.status === 'fulfilled' && resOver.value.data) {
        setOverview(resOver.value.data);
      }
      if (resHooks.status === 'fulfilled' && resHooks.value.data) {
        setWebhooks(resHooks.value.data || []);
      }
    } catch (err) {
      console.error('Erreur chargement API Partenaires:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleTrack = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackQuery.trim()) return;
    setTracking(true);
    try {
      const res = await partnerB2BAPI.track(trackQuery.trim());
      setTrackResult(res.data);
    } catch (err: any) {
      setTrackResult({ found: false, message: 'Référence non trouvée' });
    } finally {
      setTracking(false);
    }
  };

  const handleCreateWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await partnerB2BAPI.createWebhook(formData);
      setIsModalOpen(false);
      await fetchData();
    } catch (err) {
      console.error('Erreur enregistrement webhook:', err);
    }
  };

  const handleDeleteWebhook = async (id: number) => {
    if (!confirm('Supprimer ce webhook ?')) return;
    try {
      await partnerB2BAPI.deleteWebhook(id);
      await fetchData();
    } catch (err) {
      console.error('Erreur suppression webhook:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Code className="w-3.5 h-3.5" /> Intégration Développeurs & Partenaires B2B
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Portail API B2B & Webhooks Événementiels
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Documentation API REST, abonnements Webhooks et console de tracking multi-modale pour vos systèmes tiers (SAP, Oracle, Odoo).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchData()}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-sm shadow-lg shadow-cyan-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Enregistrer un Webhook
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Passerelle B2B Active</span>
            <Globe className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            REST & Webhooks
          </div>
          <div className="text-xs text-slate-500 mt-1">SLA 99.99% haute disponibilité</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Webhooks Enregistrés</span>
            <Webhook className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {webhooks.length}
          </div>
          <div className="text-xs text-slate-500 mt-1">Écouteurs d'événements actifs</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Authentification API</span>
            <Key className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            Bearer JWT
          </div>
          <div className="text-xs text-slate-500 mt-1">Chiffrement AES-256 bits</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Types d'Événements</span>
            <Code className="w-4 h-4 text-violet-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {overview.supported_events?.length || 7}
          </div>
          <div className="text-xs text-slate-500 mt-1">Gate In/Out, Douane, e-POD</div>
        </div>
      </div>

      {/* Live Tracking Console */}
      <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-3xl shadow-xl space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Terminal className="w-5 h-5 text-cyan-400" /> Console de Test API Tracking (B2B)
        </h3>
        <p className="text-xs text-slate-400">
          Simulez un appel API pour rechercher un conteneur, un dossier de transit ou un numéro de BL :
        </p>

        <form onSubmit={handleTrack} className="flex gap-3 max-w-xl">
          <input
            type="text"
            placeholder="ex: MSKU-908123, DOS-2026-001, BSC-CM..."
            value={trackQuery}
            onChange={(e) => setTrackQuery(e.target.value)}
            className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
          <button
            type="submit"
            disabled={tracking}
            className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold rounded-xl flex items-center gap-2 disabled:opacity-50 transition-all"
          >
            {tracking ? 'Recherche...' : <><Search className="w-4 h-4" /> Interroger API</>}
          </button>
        </form>

        {trackResult && (
          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto">
            <pre>{JSON.stringify(trackResult, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Webhooks List */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="p-5 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <h3 className="font-bold text-white text-sm flex items-center gap-2">
            <Webhook className="w-4 h-4 text-emerald-400" /> Webhooks Actifs
          </h3>
          <span className="text-xs text-slate-500">{webhooks.length} abonnement(s)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">Nom Webhook</th>
                <th className="py-4 px-5">URL Endpoint</th>
                <th className="py-4 px-5">Événements Écoutés</th>
                <th className="py-4 px-5">Succès / Échecs</th>
                <th className="py-4 px-5">Statut</th>
                <th className="py-4 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-cyan-500" />
                    Chargement des webhooks...
                  </td>
                </tr>
              ) : webhooks.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    Aucun webhook configuré pour le moment.
                  </td>
                </tr>
              ) : (
                webhooks.map((w) => (
                  <tr key={w.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-bold text-white text-xs">
                      {w.nom}
                    </td>
                    <td className="py-4 px-5 font-mono text-xs text-cyan-400 max-w-xs truncate">
                      {w.url_webhook}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {w.evenements}
                    </td>
                    <td className="py-4 px-5 font-mono text-xs">
                      <span className="text-emerald-400">{w.nombre_reussites || 0}</span> / <span className="text-rose-400">{w.nombre_echecs || 0}</span>
                    </td>
                    <td className="py-4 px-5">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                        <CheckCircle2 className="w-3 h-3" /> Actif
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      <button
                        onClick={() => handleDeleteWebhook(w.id)}
                        className="text-xs text-rose-400 hover:text-rose-300 font-medium"
                      >
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Enregistrement Webhook */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Webhook className="w-5 h-5 text-cyan-400" /> Enregistrer un Webhook B2B
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateWebhook} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Nom de l'Intégration Webhook</label>
                <input
                  type="text"
                  required
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">URL Endpoint HTTPS Cible</label>
                <input
                  type="url"
                  required
                  placeholder="https://votre-systeme.com/webhooks/evo-log"
                  value={formData.url_webhook}
                  onChange={(e) => setFormData({ ...formData, url_webhook: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold shadow-lg shadow-cyan-600/20 transition-all"
                >
                  Activer le Webhook
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

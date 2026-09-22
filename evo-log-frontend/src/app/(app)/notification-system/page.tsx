'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Bell, Search, Plus, CheckCircle2, Clock, AlertTriangle,
  Smartphone, Mail, MessageSquare, Send, RefreshCw, X, Radio
} from 'lucide-react';
import { notificationSystemAPI } from '@/lib/api-client';

interface NotificationItem {
  id: number;
  numero_notification: string;
  destinataire_id?: number;
  type_canal: string;
  categorie: string;
  titre: string;
  corps: string;
  priorite: string;
  statut: string;
  date_envoi?: string;
}

export default function NotificationSystemPage() {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [stats, setStats] = useState({
    total_notifications: 0,
    distribuees: 0,
    en_attente: 0,
    echecs: 0,
    taux_delivrance_pourcent: 100.0,
    canaux: [] as { canal: string; count: number }[],
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [canalFilter, setCanalFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Formulaire d'envoi
  const [formData, setFormData] = useState({
    type_canal: 'whatsapp',
    categorie: 'alerte',
    titre: 'Alerte Quai Maritime - Déchargement Terminé',
    corps: 'Le conteneur MSKU-908123 a été dépoté avec succès au Magasin 3. BAE délivré.',
    priorite: 'haute',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        notificationSystemAPI.getAll({
          search: search || undefined,
          canal: canalFilter || undefined
        }),
        notificationSystemAPI.getStats()
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement notifications:', err);
    } finally {
      setLoading(false);
    }
  }, [search, canalFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await notificationSystemAPI.send(formData);
      setIsModalOpen(false);
      await fetchData();
    } catch (err) {
      console.error('Erreur envoi notification:', err);
    }
  };

  const getCanalIcon = (canal: string) => {
    switch (canal.toLowerCase()) {
      case 'whatsapp': return <MessageSquare className="w-4 h-4 text-emerald-400" />;
      case 'sms': return <Smartphone className="w-4 h-4 text-amber-400" />;
      case 'email': return <Mail className="w-4 h-4 text-blue-400" />;
      default: return <Bell className="w-4 h-4 text-violet-400" />;
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Radio className="w-3.5 h-3.5" /> Passerelle Multi-Canal • WhatsApp, SMS & In-App
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Centre de Notifications & Alertes Multi-Canaux
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Diffusion omnicanale des alertes opérationnelles, statuts de conteneurs, avis de passage et règlements.
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
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm shadow-lg shadow-violet-600/20 transition-all"
          >
            <Send className="w-4 h-4" /> Diffuser une Notification
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Messages Diffusés</span>
            <Bell className="w-4 h-4 text-violet-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_notifications}
          </div>
          <div className="text-xs text-slate-500 mt-1">Sur tous canaux confondus</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Taux de Délivrance</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {stats.taux_delivrance_pourcent}%
          </div>
          <div className="text-xs text-slate-500 mt-1">{stats.distribuees} messages confirmés reçus</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Files d'Attente</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            {stats.en_attente}
          </div>
          <div className="text-xs text-slate-500 mt-1">En cours de routage opérateur</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Canaux Opérationnels</span>
            <Radio className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.canaux.length || 4}
          </div>
          <div className="text-xs text-slate-500 mt-1">WhatsApp Business, SMS, Webhook</div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher par titre, contenu, N° notif..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={canalFilter}
            onChange={(e) => setCanalFilter(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="">Tous les canaux</option>
            <option value="whatsapp">WhatsApp Business API</option>
            <option value="sms">SMS Passerelle Locale</option>
            <option value="email">Email</option>
            <option value="in_app">Notification In-App</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">N° Notification</th>
                <th className="py-4 px-5">Canal</th>
                <th className="py-4 px-5">Titre & Message</th>
                <th className="py-4 px-5">Catégorie</th>
                <th className="py-4 px-5">Date d'Envoi</th>
                <th className="py-4 px-5">Priorité</th>
                <th className="py-4 px-5 text-right">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-violet-500" />
                    Chargement des notifications...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    Aucune notification enregistrée.
                  </td>
                </tr>
              ) : (
                items.map((n) => (
                  <tr key={n.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono text-xs font-bold text-violet-400">
                      {n.numero_notification}
                    </td>
                    <td className="py-4 px-5">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-xs font-bold text-slate-300 capitalize">
                        {getCanalIcon(n.type_canal)}
                        {n.type_canal}
                      </span>
                    </td>
                    <td className="py-4 px-5">
                      <div className="font-bold text-white text-xs">{n.titre}</div>
                      <div className="text-xs text-slate-400 max-w-sm truncate">{n.corps}</div>
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300 capitalize">
                      {n.categorie}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-400">
                      {n.date_envoi || 'Aujourd\'hui'}
                    </td>
                    <td className="py-4 px-5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                        n.priorite === 'critique' || n.priorite === 'haute'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        {n.priorite}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                        <CheckCircle2 className="w-3 h-3" /> Délivré
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Envoi Notification */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Send className="w-5 h-5 text-violet-400" /> Diffuser une Notification
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSend} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Canal de Diffusion</label>
                  <select
                    value={formData.type_canal}
                    onChange={(e) => setFormData({ ...formData, type_canal: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  >
                    <option value="whatsapp">WhatsApp Business API</option>
                    <option value="sms">SMS Rapide</option>
                    <option value="email">Email</option>
                    <option value="in_app">Notification In-App</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Priorité</label>
                  <select
                    value={formData.priorite}
                    onChange={(e) => setFormData({ ...formData, priorite: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  >
                    <option value="normale">Normale</option>
                    <option value="haute">Haute</option>
                    <option value="critique">Critique (Alerte Immédiate)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Titre du Message</label>
                <input
                  type="text"
                  required
                  value={formData.titre}
                  onChange={(e) => setFormData({ ...formData, titre: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Corps de la Notification</label>
                <textarea
                  rows={3}
                  required
                  value={formData.corps}
                  onChange={(e) => setFormData({ ...formData, corps: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
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
                  className="px-5 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-bold shadow-lg shadow-violet-600/20 transition-all"
                >
                  Diffuser Immédiatement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

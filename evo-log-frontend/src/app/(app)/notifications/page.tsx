'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Bell, Mail, MessageSquare, Send, RefreshCw, PlusCircle,
  CheckCircle2, Clock, Users, Smartphone, AlertTriangle, X, Save
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [campagnes, setCampagnes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNotifForm, setShowNotifForm] = useState(false);
  const [newNotif, setNewNotif] = useState({
    type: 'in_app',
    destinataire_id: '',
    sujet: '',
    contenu: '',
    priorite: 'normale',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resNotifs, resTpls, resCamp] = await Promise.allSettled([
        apiClient.get('/api/v1/notifications/notifications', { params: { limit: 50 } }),
        apiClient.get('/api/v1/notifications/templates', { params: { limit: 20 } }),
        apiClient.get('/api/v1/notifications/campagnes', { params: { limit: 10 } })
      ]);
      if (resNotifs.status === 'fulfilled' && resNotifs.value.data)
        setNotifications(resNotifs.value.data?.data || resNotifs.value.data || []);
      if (resTpls.status === 'fulfilled' && resTpls.value.data)
        setTemplates(resTpls.value.data?.data || resTpls.value.data || []);
      if (resCamp.status === 'fulfilled' && resCamp.value.data)
        setCampagnes(resCamp.value.data?.data || resCamp.value.data || []);
    } catch (err) {
      console.error('Notifications fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreateNotif = async () => {
    try {
      await apiClient.post('/api/v1/notifications/notifications', {
        ...newNotif,
        destinataire_id: parseInt(newNotif.destinataire_id) || 1,
      });
      setShowNotifForm(false);
      fetchData();
    } catch (err) { console.error('Erreur création notification:', err); }
  };

  const handleEnvoyer = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/notifications/notifications/${id}/envoyer`);
      fetchData();
    } catch (err) { console.error('Erreur envoi:', err); }
  };

  const getTypeBadge = (t: string) => {
    switch (t) {
      case 'email': return { color: 'text-blue-400 bg-blue-500/20 border-blue-500/30', icon: Mail };
      case 'sms': return { color: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30', icon: Smartphone };
      case 'whatsapp': return { color: 'text-green-400 bg-green-500/20 border-green-500/30', icon: MessageSquare };
      default: return { color: 'text-cyan-400 bg-cyan-500/20 border-cyan-500/30', icon: Bell };
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Bell className="w-3.5 h-3.5" /> Notifications Multi-Canal — Email, SMS, WhatsApp, Push, In-App
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Centre de Notifications & Campagnes</h1>
          <p className="text-xs text-slate-400 mt-1">Gestion des notifications internes, alertes opérationnelles, campagnes email/SMS massives et préférences utilisateurs.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => setShowNotifForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shadow-lg shadow-sky-900/20 transition-all">
            <PlusCircle className="w-4 h-4" /> Nouvelle Notification
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Notifications', value: notifications.length, icon: Bell, color: 'text-sky-400' },
          { label: 'Envoyées', value: notifications.filter(n => n.statut === 'envoye').length, icon: CheckCircle2, color: 'text-emerald-400' },
          { label: 'En Attente', value: notifications.filter(n => n.statut === 'en_attente' || !n.statut).length, icon: Clock, color: 'text-amber-400' },
          { label: 'Templates', value: templates.length, icon: MessageSquare, color: 'text-purple-400' },
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

      {showNotifForm && (
        <div className="bg-slate-900/90 border border-sky-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Créer une Notification</h2>
            <button onClick={() => setShowNotifForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'destinataire_id', label: 'ID Destinataire', type: 'number' },
              { key: 'sujet', label: 'Sujet', type: 'text' },
              { key: 'contenu', label: 'Contenu', type: 'text' },
            ].map(f => (
              <div key={f.key} className={f.key === 'contenu' ? 'md:col-span-2' : ''}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input type={f.type} value={(newNotif as any)[f.key]} onChange={(e) => setNewNotif({ ...newNotif, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-sky-500 transition-colors" />
              </div>
            ))}
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Canal</label>
              <select value={newNotif.type} onChange={(e) => setNewNotif({ ...newNotif, type: e.target.value })}
                className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-sky-500">
                <option value="in_app">In-App</option>
                <option value="email">Email</option>
                <option value="sms">SMS</option>
                <option value="whatsapp">WhatsApp</option>
                <option value="push">Push</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Priorité</label>
              <select value={newNotif.priorite} onChange={(e) => setNewNotif({ ...newNotif, priorite: e.target.value })}
                className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-sky-500">
                <option value="faible">Faible</option>
                <option value="normale">Normale</option>
                <option value="haute">Haute</option>
                <option value="urgente">Urgente</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowNotifForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreateNotif} className="px-5 py-2.5 rounded-2xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold flex items-center gap-2">
              <Save className="w-4 h-4" /> Créer
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <Bell className="w-5 h-5 text-sky-400" />
            <h2 className="text-base font-black text-white">Notifications Récentes</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center"><RefreshCw className="w-5 h-5 animate-spin text-sky-400 mx-auto mb-2 mt-2" /></div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucune notification.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {notifications.slice(0, 8).map((n: any) => {
                const badge = getTypeBadge(n.type);
                const Icon = badge.icon;
                return (
                  <div key={n.id} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                    <div className="flex items-start gap-3">
                      <div className={`p-1.5 rounded-lg border ${badge.color}`}>
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <span className="text-sm font-bold text-white">{n.sujet || 'Notification'}</span>
                        <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">{n.contenu}</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">Dest: #{n.destinataire_id}</p>
                      </div>
                    </div>
                    {n.statut !== 'envoye' ? (
                      <button onClick={() => handleEnvoyer(n.id)} className="px-3 py-1.5 rounded-xl bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 border border-sky-500/30 text-xs font-bold flex items-center gap-1.5 transition-all">
                        <Send className="w-3.5 h-3.5" /> Envoyer
                      </button>
                    ) : (
                      <span className="px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Envoyé</span>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <Users className="w-5 h-5 text-purple-400" />
            <h2 className="text-base font-black text-white">Templates & Campagnes</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center"><RefreshCw className="w-5 h-5 animate-spin text-sky-400 mx-auto mb-2 mt-2" /></div>
          ) : templates.length === 0 && campagnes.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucun template ni campagne configuré.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {templates.slice(0, 5).map((t: any) => (
                <div key={`tpl-${t.id}`} className="p-4 hover:bg-slate-800/40 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-bold text-white">{t.nom}</span>
                      <p className="text-xs text-slate-400 mt-0.5">Template {t.canal || t.type} • Variables: {(t.variables || []).length}</p>
                    </div>
                    <span className="px-2 py-1 rounded-lg text-[10px] font-bold border bg-purple-500/20 text-purple-400 border-purple-500/30">Template</span>
                  </div>
                </div>
              ))}
              {campagnes.slice(0, 3).map((c: any) => (
                <div key={`camp-${c.id}`} className="p-4 hover:bg-slate-800/40 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-bold text-white">{c.nom}</span>
                      <p className="text-xs text-slate-400 mt-0.5">Campagne • {c.nb_destinataires || 0} destinataires</p>
                    </div>
                    <span className={`px-2 py-1 rounded-lg text-[10px] font-bold border ${c.statut === 'envoyée' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'}`}>
                      {c.statut || 'Planifiée'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

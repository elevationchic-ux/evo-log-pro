'use client';

import React, { useState, useEffect } from 'react';
import { Bell, ShieldAlert, AlertTriangle, Info, CheckCircle2, Search, Filter, Trash2 } from 'lucide-react';

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  timestamp: string;
  agency: string;
  read: boolean;
}

const INITIAL_NOTIFICATIONS: NotificationItem[] = [
  {
    id: 'NOTIF-001',
    title: 'Tentative d\'accès non autorisée',
    message: 'Échec d\'authentification répétitif sur le compte MAGASINIER_DLA depuis l\'IP 192.168.1.104.',
    severity: 'CRITICAL',
    timestamp: '2026-07-23T21:15:00Z',
    agency: 'Douala Port Agency',
    read: false,
  },
  {
    id: 'NOTIF-002',
    title: 'Alerte Seuil Carburant FuelGuard',
    message: 'Le tracteur LT-902-BB présente une baisse anormale du niveau de carburant (-45L en 10 min).',
    severity: 'WARNING',
    timestamp: '2026-07-23T20:45:00Z',
    agency: 'Chantier Kribi',
    read: false,
  },
  {
    id: 'NOTIF-003',
    title: 'Nouveau Bon d\'Enlèvement Validé',
    message: 'Le BL #BL-2026-089 a été validé par la douane et autorisé à la sortie Gate Porte 2.',
    severity: 'INFO',
    timestamp: '2026-07-23T19:30:00Z',
    agency: 'Douala Port Agency',
    read: true,
  },
  {
    id: 'NOTIF-004',
    title: 'Inspection QHSE Requise',
    message: 'Inspection périodique de sécurité du hangar MAG3 planifiée pour demain à 08h00.',
    severity: 'WARNING',
    timestamp: '2026-07-23T18:10:00Z',
    agency: 'Magasin Central Mag3',
    read: true,
  },
  {
    id: 'NOTIF-005',
    title: 'Sauvegarde BDD Réussie',
    message: 'La sauvegarde automatique de la base de données PostgreSQL EVO-LOG ERP s\'est achevée avec succès.',
    severity: 'INFO',
    timestamp: '2026-07-23T16:00:00Z',
    agency: 'Système Central',
    read: true,
  },
];

export default function NotificationsPage() {
  const [mounted, setMounted] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>(INITIAL_NOTIFICATIONS);
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">Chargement du Centre de Notifications...</div>;

  const handleMarkAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    console.log("Toutes les notifications ont été marquées comme lues.");
  };

  const handleClearRead = () => {
    setNotifications(prev => prev.filter(n => !n.read));
    console.log("Notifications lues supprimées.");
  };

  const handleToggleRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: !n.read } : n));
  };

  const filtered = notifications.filter(n => {
    const matchesSev = filterSeverity === 'ALL' || n.severity === filterSeverity;
    const matchesSearch = (n.title + ' ' + n.message + ' ' + n.agency).toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSev && matchesSearch;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm dark:shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-semibold mb-2 border border-indigo-500/20">
            <Bell className="w-3.5 h-3.5" />
            Sécurité & Monitoring • Centre de Notifications
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-slate-100">Centre de Notifications & Alertes</h1>
          <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">Supervision temps réel des événements critiques, alertes QHSE et notifications système.</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleMarkAllRead}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-bold text-slate-800 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-all cursor-pointer"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Tout marquer comme lu ({unreadCount})
          </button>
          <button
            onClick={handleClearRead}
            className="inline-flex items-center gap-2 px-3 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-950 hover:bg-red-50 dark:hover:bg-red-950/30 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 border border-slate-300 dark:border-slate-800 transition-all cursor-pointer"
          >
            <Trash2 className="w-4 h-4" />
            Nettoyer
          </button>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-sm">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
          <Filter className="w-4 h-4 text-slate-500 dark:text-slate-400 shrink-0" />
          {['ALL', 'CRITICAL', 'WARNING', 'INFO'].map(sev => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                filterSeverity === sev
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-slate-100 dark:bg-slate-950 text-slate-700 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-800'
              }`}
            >
              {sev === 'ALL' && 'Toutes les Alertes'}
              {sev === 'CRITICAL' && '🚨 Critiques'}
              {sev === 'WARNING' && '⚠️ Avertissements'}
              {sev === 'INFO' && 'ℹ️ Informations'}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher une alerte..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-900 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="p-12 text-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl text-slate-500 text-sm">
            Aucune notification trouvée.
          </div>
        ) : (
          filtered.map(item => {
            const isCritical = item.severity === 'CRITICAL';
            const isWarning = item.severity === 'WARNING';

            return (
              <div
                key={item.id}
                onClick={() => handleToggleRead(item.id)}
                className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                  !item.read
                    ? isCritical
                      ? 'bg-red-50 dark:bg-red-950/20 border-red-300 dark:border-red-500/40 shadow-sm'
                      : isWarning
                      ? 'bg-amber-50 dark:bg-amber-950/20 border-amber-300 dark:border-amber-500/40 shadow-sm'
                      : 'bg-indigo-50 dark:bg-indigo-950/20 border-indigo-300 dark:border-indigo-500/40 shadow-sm'
                    : 'bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 opacity-80 hover:opacity-100'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${
                    isCritical
                      ? 'bg-red-100 dark:bg-red-500/10 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-500/30'
                      : isWarning
                      ? 'bg-amber-100 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-500/30'
                      : 'bg-indigo-100 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30'
                  }`}>
                    {isCritical && <ShieldAlert className="w-5 h-5 animate-pulse" />}
                    {isWarning && <AlertTriangle className="w-5 h-5" />}
                    {!isCritical && !isWarning && <Info className="w-5 h-5" />}
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-slate-900 dark:text-slate-100 text-sm">{item.title}</span>
                      {!item.read && (
                        <span className="text-[9px] font-black uppercase px-2 py-0.5 rounded-full bg-indigo-600 text-white">
                          Nouveau
                        </span>
                      )}
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-950 text-slate-700 dark:text-slate-400 border border-slate-200 dark:border-slate-800">
                        {item.agency}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{item.message}</p>
                  </div>
                </div>

                <div className="text-right text-[11px] font-mono text-slate-500 shrink-0">
                  {new Date(item.timestamp).toLocaleString('fr-FR')}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

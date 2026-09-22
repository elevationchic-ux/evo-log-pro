'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Bell, AlertTriangle, CheckCircle2, ShieldAlert, XCircle,
  Filter, RefreshCw, Clock, ArrowRight, Eye, Check, X
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface AlertItem {
  id: number;
  type_alerte: string;
  gravite: 'faible' | 'moyenne' | 'haute' | 'critique';
  description: string;
  concerne_type: string;
  concerne_id: number;
  valeur_actuelle: number | null;
  valeur_seuil: number | null;
  date_alerte: string;
  statut: 'active' | 'resolue' | 'ignoree';
  date_resolution: string | null;
  resolution: string | null;
}

interface AlertSummary {
  total_actives: number;
  critique: number;
  haute: number;
  nouvelles_24h: number;
  notifications_non_lues: number;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [summary, setSummary] = useState<AlertSummary>({
    total_actives: 0,
    critique: 0,
    haute: 0,
    nouvelles_24h: 0,
    notifications_non_lues: 0
  });
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('active');
  const [graviteFilter, setGraviteFilter] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resSummary] = await Promise.allSettled([
        apiClient.get('/api/v1/alerts', {
          params: {
            statut: statusFilter || undefined,
            gravite: graviteFilter || undefined,
            limit: 50
          }
        }),
        apiClient.get('/api/v1/alerts/summary')
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setAlerts(resList.value.data.data || []);
      }
      if (resSummary.status === 'fulfilled' && resSummary.value.data) {
        setSummary(resSummary.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement alertes:', err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, graviteFilter]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const handleResoudre = async (id: number) => {
    setActionLoading(id);
    try {
      await apiClient.post(`/api/v1/alerts/${id}/resoudre`, {
        resolution: 'Traité et régularisé par opérateur'
      });
      fetchAlerts();
    } catch (err) {
      console.error('Erreur résolution alerte:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleIgnorer = async (id: number) => {
    setActionLoading(id);
    try {
      await apiClient.post(`/api/v1/alerts/${id}/ignorer`);
      fetchAlerts();
    } catch (err) {
      console.error('Erreur ignorer alerte:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const getGraviteBadge = (g: string) => {
    switch (g) {
      case 'critique':
        return { bg: 'bg-rose-500/20', text: 'text-rose-400', border: 'border-rose-500/40', label: 'Critique' };
      case 'haute':
        return { bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/40', label: 'Haute' };
      case 'moyenne':
        return { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/40', label: 'Moyenne' };
      default:
        return { bg: 'bg-slate-500/20', text: 'text-slate-400', border: 'border-slate-500/40', label: 'Faible' };
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold uppercase tracking-wider mb-2">
            <ShieldAlert className="w-3.5 h-3.5" /> Centre d'Alertes Opérationnelles & Déviations KPI
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Supervision & Alertes Système
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Détection automatique des anomalies sur séjours portuaires, franchises surestaries, carburant, et dédouanement.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchAlerts}
            className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all shadow-md active:scale-95"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </button>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Total Alertes Actives</span>
            <Bell className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-black text-white mt-2">{summary.total_actives}</p>
          <p className="text-[11px] text-slate-400 mt-1">Surveillées par le moteur de règles</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Alertes Critiques</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl font-black text-rose-400 mt-2">{summary.critique}</p>
          <p className="text-[11px] text-slate-400 mt-1">Action immédiate nécessaire</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Gravité Haute</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-black text-amber-400 mt-2">{summary.haute}</p>
          <p className="text-[11px] text-slate-400 mt-1">Dépassement de seuils d'avertissement</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">Nouvelles (24h)</span>
            <Clock className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black text-emerald-400 mt-2">{summary.nouvelles_24h}</p>
          <p className="text-[11px] text-slate-400 mt-1">Générées durant la dernière journée</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 p-4 rounded-3xl">
        <div className="flex items-center gap-2">
          {['active', 'resolue', 'ignoree', ''].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
                statusFilter === s
                  ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-900/30'
                  : 'bg-slate-800/80 text-slate-400 hover:text-white'
              }`}
            >
              {s === 'active' ? 'Actives' : s === 'resolue' ? 'Résolues' : s === 'ignoree' ? 'Ignorées' : 'Toutes'}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={graviteFilter}
            onChange={(e) => setGraviteFilter(e.target.value)}
            className="bg-slate-950/60 border border-slate-800 text-xs text-slate-300 rounded-xl px-3 py-1.5 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Toutes gravités</option>
            <option value="critique">Critique</option>
            <option value="haute">Haute</option>
            <option value="moyenne">Moyenne</option>
            <option value="faible">Faible</option>
          </select>
        </div>
      </div>

      {/* Alert List */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-12 text-center text-slate-400 flex flex-col items-center gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
            <span>Chargement des alertes depuis la base de données...</span>
          </div>
        ) : alerts.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
            <p className="font-bold text-white">Aucune alerte correspondante</p>
            <p className="text-xs text-slate-500 mt-1">Tous les indicateurs sont conformes aux tolérances configurées.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {alerts.map((alert) => {
              const badge = getGraviteBadge(alert.gravite);
              return (
                <div key={alert.id} className="p-5 hover:bg-slate-800/40 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className={`mt-1 px-2.5 py-1 rounded-xl text-[10px] font-black uppercase tracking-wider border ${badge.bg} ${badge.border} ${badge.text}`}>
                      {badge.label}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{alert.type_alerte}</span>
                        <span className="text-xs text-slate-500">• {alert.concerne_type} #{alert.concerne_id}</span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1">{alert.description}</p>
                      <div className="flex items-center gap-4 text-[11px] text-slate-500 mt-2">
                        <span>Détectée: {alert.date_alerte ? new Date(alert.date_alerte).toLocaleString('fr-FR') : '-'}</span>
                        {alert.valeur_actuelle !== null && (
                          <span>Valeur: <strong className="text-slate-300">{alert.valeur_actuelle}</strong> / Seuil: {alert.valeur_seuil}</span>
                        )}
                        {alert.resolution && (
                          <span className="text-emerald-400">Résolution: {alert.resolution}</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {alert.statut === 'active' && (
                    <div className="flex items-center gap-2 self-end md:self-center">
                      <button
                        onClick={() => handleResoudre(alert.id)}
                        disabled={actionLoading === alert.id}
                        className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5 transition-all"
                      >
                        <Check className="w-3.5 h-3.5" />
                        Résoudre
                      </button>
                      <button
                        onClick={() => handleIgnorer(alert.id)}
                        disabled={actionLoading === alert.id}
                        className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-all"
                      >
                        <X className="w-3.5 h-3.5" />
                        Ignorer
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

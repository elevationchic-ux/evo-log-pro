'use client';

import React, { useState, useEffect } from 'react';
import { ShieldAlert, Activity, AlertTriangle, CheckCircle2, Server, Bell } from 'lucide-react';
import { auditAPI } from '@/lib/api-client';
import api from '@/lib/api';
import { useSettings } from '@/components/layout/SettingsProvider';

interface SecurityIncident {
  id: string;
  source: string;
  type: string;
  target: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  status: string;
  ip: string;
  date: string;
}

interface AlertsSummary {
  total_actives: number;
  critique: number;
  haute: number;
  nouvelles_24h: number;
  notifications_non_lues: number;
}

export default function SecurityAlertMonitoringPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [mounted, setMounted] = useState(false);
  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);
  const [summary, setSummary] = useState<AlertsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const chargerIncidents = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [res, sumRes] = await Promise.all([
        auditAPI.getLogs({ limit: 50 }),
        api.get('/api/v1/alerts/summary').catch(() => null),
      ]);
      if (sumRes?.data) setSummary(sumRes.data);
      const raw = res?.data?.data ?? res?.data ?? [];
      const list = Array.isArray(raw) ? raw : (Array.isArray(raw?.items) ? raw.items : []);
      setIncidents(list.map((l: any): SecurityIncident => {
        const sevRaw = String(l.severity ?? l.niveau ?? l.level ?? '').toUpperCase();
        const severity: SecurityIncident['severity'] =
          sevRaw.includes('CRIT') || sevRaw.includes('HIGH') || sevRaw === 'ERREUR' ? 'CRITICAL'
            : sevRaw.includes('WARN') || sevRaw.includes('AVERT') ? 'WARNING'
              : 'INFO';
        return {
          id: String(l.id ?? l.reference ?? ''),
          source: l.source ?? l.module ?? 'Système',
          type: l.type ?? l.action ?? l.event ?? 'Événement',
          target: l.target ?? l.endpoint ?? l.path ?? '',
          severity,
          status: l.status ?? l.statut ?? 'LOGGÉ',
          ip: l.ip ?? l.ip_address ?? '',
          date: l.created_at ?? l.timestamp ?? l.date ?? '',
        };
      }));
    } catch {
      setLoadError(t("Le journal des anomalies n'a pas pu être chargé. Vérifiez votre connexion et réessayez.", "The anomaly log could not be loaded. Check your connection and try again."));
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setMounted(true);
    chargerIncidents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">{t('Chargement du Monitoring de Sécurité...', 'Loading Security Monitoring...')}</div>;

  const blockedCount = incidents.filter(i => i.severity === 'CRITICAL').length;
  const rbacCount = incidents.filter(i => i.type.toLowerCase().includes('accès') || i.type.toLowerCase().includes('rbac') || i.type.toLowerCase().includes('access')).length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-semibold mb-2 border border-red-500/20">
            <ShieldAlert className="w-3.5 h-3.5" />
            {t('Sécurité SI • Surveillance & Télémétrie en Temps Réel', 'IT Security • Real-time Monitoring & Telemetry')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">{t('Monitoring des Anomalies & Sécurité', 'Anomaly & Security Monitoring')}</h1>
          <p className="text-slate-400 text-sm mt-1">{t('Supervision des tentatives d\'intrusion, accès non autorisés et alertes système.', 'Oversight of intrusion attempts, unauthorized access and system alerts.')}</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={chargerIncidents}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-bold border border-emerald-500/20 transition-colors"
          >
            <Server className="w-4 h-4 animate-pulse" /> {t('Rafraîchir le monitoring', 'Refresh monitoring')}
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="w-10 h-10 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 flex items-center justify-center mb-3">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <p className="text-xs text-slate-400 font-bold uppercase">{t('Anomalies Critiques', 'Critical Anomalies')}</p>
          <p className="text-2xl font-black text-slate-100 font-mono mt-1">{loading ? '…' : `${blockedCount}`}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mb-3">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <p className="text-xs text-slate-400 font-bold uppercase">{t('Alertes RBAC', 'RBAC Alerts')}</p>
          <p className="text-2xl font-black text-amber-400 font-mono mt-1">{loading ? '…' : `${rbacCount}`}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mb-3">
            <Activity className="w-5 h-5" />
          </div>
          <p className="text-xs text-slate-400 font-bold uppercase">{t('Alertes Actives', 'Active Alerts')}</p>
          <p className="text-2xl font-black text-slate-100 font-mono mt-1">{loading ? '…' : `${summary?.total_actives ?? 0}`}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mb-3">
            <Bell className="w-5 h-5" />
          </div>
          <p className="text-xs text-slate-400 font-bold uppercase">{t('Nouvelles (24h)', 'New (24h)')}</p>
          <p className="text-2xl font-black text-emerald-400 font-mono mt-1">{loading ? '…' : `${summary?.nouvelles_24h ?? 0}`}</p>
        </div>
      </div>

      {/* Incident Log Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-slate-100 text-base">{t('Journal des Anomalies Détectées (SOC Log)', 'Detected Anomalies Log (SOC Log)')}</h3>
          <span className="text-xs font-mono text-slate-400">{t("Source : journal d'audit backend", 'Source: backend audit log')}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">{t('ID / Origine', 'ID / Origin')}</th>
                <th className="px-6 py-4">{t("Type d'Anomalie", 'Anomaly Type')}</th>
                <th className="px-6 py-4">{t('Cible Endpoint', 'Target Endpoint')}</th>
                <th className="px-6 py-4">{t('IP / Horodatage', 'IP / Timestamp')}</th>
                <th className="px-6 py-4 text-right">{t('Action Prise', 'Action Taken')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {incidents.map((inc) => (
                <tr key={inc.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-6 py-4 font-bold text-indigo-400">
                    {inc.id} <span className="block text-[10px] text-slate-500 font-sans">{inc.source}</span>
                  </td>
                  <td className="px-6 py-4 text-slate-200 font-sans font-semibold">
                    {inc.type}
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {inc.target}
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    <div>{inc.ip || ''}</div>
                    <div className="text-[10px] text-slate-500">{inc.date ? new Date(inc.date).toLocaleString('fr-FR') : ''}</div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold ${inc.severity === 'CRITICAL'
                        ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                        : inc.severity === 'WARNING'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      }`}>
                      {inc.status}
                    </span>
                  </td>
                </tr>
              ))}
              {loading && (
                <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-400 text-sm">{t('Chargement du journal des anomalies…', 'Loading anomaly log…')}</td></tr>
              )}
              {!loading && loadError && (
                <tr><td colSpan={5} className="px-6 py-12 text-center text-red-400 text-sm flex flex-col items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  {loadError}
                  <button onClick={chargerIncidents} className="px-3 py-1.5 rounded-lg border border-slate-700 text-xs font-bold text-slate-200 hover:bg-slate-800">{t('Réessayer', 'Retry')}</button>
                </td></tr>
              )}
              {!loading && !loadError && incidents.length === 0 && (
                <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-400 text-sm">
                  <CheckCircle2 className="w-6 h-6 mx-auto mb-2 text-emerald-400" />
                  {t("Aucune anomalie détectée sur la période. Le journal d'audit ne remonte aucun incident.", 'No anomaly detected for the period. The audit log reports no incident.')}
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

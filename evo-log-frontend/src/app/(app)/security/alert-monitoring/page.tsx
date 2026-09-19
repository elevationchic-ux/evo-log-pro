'use client';

import React, { useState, useEffect } from 'react';
import { ShieldAlert, Zap, Activity, Lock, AlertTriangle, CheckCircle2, Server, Eye } from 'lucide-react';

export default function SecurityAlertMonitoringPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">Chargement du Monitoring de Sécurité...</div>;

  const incidents = [
    { id: 'SEC-901', source: 'FastAPI Rate Limiting', type: 'Intrusion Bruteforce', target: '/api/v1/auth/login', severity: 'CRITICAL', status: 'BLOQUÉ', ip: '197.234.221.14', date: 'Il y a 12 min' },
    { id: 'SEC-902', source: 'Audit RBAC Middleware', type: 'Accès Non Autorisé', target: '/admin/configuration-des-roles-rbac', severity: 'WARNING', status: 'LOGGÉ', ip: '10.0.4.12', date: 'Il y a 34 min' },
    { id: 'SEC-903', source: 'PostgreSQL Database', type: 'Connexion Anormale', target: 'PostgreSQL Port 5432', severity: 'INFO', status: 'RESOLU', ip: '127.0.0.1', date: 'Il y a 2h' },
    { id: 'SEC-904', source: 'FuelGuard Telemetry', type: 'Anomalie Télémétrique', target: 'Capteur Réservoir #9', severity: 'WARNING', status: 'SOUS_ENQUÊTE', ip: '10.8.0.5', date: 'Il y a 3h' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-semibold mb-2 border border-red-500/20">
            <ShieldAlert className="w-3.5 h-3.5" />
            Sécurité SI • Surveillance & Télémétrie en Temps Réel
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Monitoring des Anomalies & Sécurité</h1>
          <p className="text-slate-400 text-sm mt-1">Supervision des tentatives d'intrusion, accès non autorisés et alertes système.</p>
        </div>

        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
            <Server className="w-4 h-4 animate-pulse" /> SOC Actif (0 Vulnérabilités Majeures)
          </span>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="w-10 h-10 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 flex items-center justify-center mb-3">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <p className="text-xs text-slate-400 font-bold uppercase">Attaques Bloquées (24h)</p>
          <p className="text-2xl font-black text-slate-100 font-mono mt-1">142 IPs</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mb-3">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <p className="text-xs text-slate-400 font-bold uppercase">Alertes RBAC</p>
          <p className="text-2xl font-black text-amber-400 font-mono mt-1">8 Refus</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mb-3">
            <Activity className="w-5 h-5" />
          </div>
          <p className="text-xs text-slate-400 font-bold uppercase">Lattence API Moyenne</p>
          <p className="text-2xl font-black text-emerald-400 font-mono mt-1">14 ms</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mb-3">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <p className="text-xs text-slate-400 font-bold uppercase">Santé Chiffrement SSL/TLS</p>
          <p className="text-2xl font-black text-slate-100 font-mono mt-1">TLS 1.3 OK</p>
        </div>
      </div>

      {/* Incident Log Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-slate-100 text-base">Journal des Anomalies Détectées (SOC Log)</h3>
          <span className="text-xs font-mono text-slate-400">Monitoring Actif • Uptime 99.98%</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">ID / Origine</th>
                <th className="px-6 py-4">Type d'Anomalie</th>
                <th className="px-6 py-4">Cible Endpoint</th>
                <th className="px-6 py-4">IP / Horodatage</th>
                <th className="px-6 py-4 text-right">Action Prise</th>
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
                    <div>{inc.ip}</div>
                    <div className="text-[10px] text-slate-500">{inc.date}</div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold ${
                      inc.severity === 'CRITICAL'
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
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

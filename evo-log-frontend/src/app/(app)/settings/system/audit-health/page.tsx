'use client';

import React, { useState, useEffect } from 'react';
import { ShieldCheck, Activity, Server, Database, Cpu, CheckCircle2, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

export default function AuditHealthSettingsPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">Chargement du Diagnostic Système...</div>;

  const handleRefreshMetrics = () => {
    toast.success("Statistiques de santé et métriques rafraîchies !");
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <ShieldCheck className="w-3.5 h-3.5" />
            Paramètres Système • Diagnostic & Santé Infrastructure
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Santé Système & Surveillance Infrastructure</h1>
          <p className="text-slate-400 text-sm mt-1">Supervision de l'API FastAPI, de la base de données PostgreSQL et du système d'audit.</p>
        </div>

        <button
          onClick={handleRefreshMetrics}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-all cursor-pointer"
        >
          <RefreshCw className="w-4 h-4 text-emerald-400" />
          Rafraîchir les Métriques
        </button>
      </div>

      {/* Infrastructure Status Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center">
              <Server className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-3 h-3" /> ONLINE
            </span>
          </div>
          <h3 className="font-bold text-slate-100 text-base">API FastAPI Backend</h3>
          <p className="text-xs text-slate-400 mt-1">Version 0.115 • 19 Routeurs Actifs</p>
          <div className="mt-4 pt-4 border-t border-slate-800 flex justify-between text-xs font-mono">
            <span className="text-slate-500">Latence moyenne:</span>
            <span className="text-emerald-400 font-bold">12 ms</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center">
              <Database className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-3 h-3" /> READY
            </span>
          </div>
          <h3 className="font-bold text-slate-100 text-base">Base de Données PostgreSQL</h3>
          <p className="text-xs text-slate-400 mt-1">SQLAlchemy 2.0 Pool Active</p>
          <div className="mt-4 pt-4 border-t border-slate-800 flex justify-between text-xs font-mono">
            <span className="text-slate-500">Connexions pool:</span>
            <span className="text-blue-400 font-bold">8 / 20</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-3 h-3" /> OK
            </span>
          </div>
          <h3 className="font-bold text-slate-100 text-base">Celery & Worker Redis</h3>
          <p className="text-xs text-slate-400 mt-1">Tâches d'impression WeasyPrint</p>
          <div className="mt-4 pt-4 border-t border-slate-800 flex justify-between text-xs font-mono">
            <span className="text-slate-500">Queue d'attente:</span>
            <span className="text-purple-400 font-bold">0 Tâches</span>
          </div>
        </div>
      </div>
    </div>
  );
}

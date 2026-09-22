'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Settings, CheckCircle2, AlertTriangle, Database,
  Server, HardDrive, Wifi, RefreshCw, Download, ShieldAlert, ArrowRight
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/components/shared/AuthProvider';
import { adminAPI } from '@/lib/api-client';

interface SystemHealth {
  service: string;
  status: 'OK' | 'DEGRADED' | 'DOWN';
  uptime: string;
  responseMs: number;
  lastCheck: string;
}

export default function AdminTenantSystemAdmin() {
  const { user } = useAuth();
  const [health, setHealth] = useState<SystemHealth[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminAPI.getSystemHealth();
      const s = res.data?.services || [];
      if (Array.isArray(s) && s.length > 0) {
        setHealth(s);
      }
    } catch (err) {
      console.error('Failed to load system health', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);


  const isSuperAdmin = Boolean(
    (user as any)?.is_superuser ||
    user?.roles?.some(r => r.toUpperCase() === 'SUPER_ADMIN' || r.toUpperCase() === 'SUPERADMIN')
  );

  if (!isSuperAdmin) {
    return (
      <div className="max-w-2xl mx-auto my-12 bg-slate-900/90 border border-red-500/40 rounded-3xl p-8 text-center space-y-4 shadow-2xl backdrop-blur-xl">
        <div className="w-16 h-16 rounded-2xl bg-red-500/15 border border-red-500/30 text-red-400 flex items-center justify-center mx-auto">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <span className="text-xs font-black uppercase tracking-widest text-red-400 bg-red-500/10 px-3 py-1 rounded-full border border-red-500/20">
          Accès Restreint • Super Administrateur SaaS
        </span>
        <h2 className="text-2xl font-black text-slate-100">Zone de Gouvernance Plateforme CADC</h2>
        <p className="text-xs text-slate-400 leading-relaxed max-w-lg mx-auto">
          Votre compte est restreint au périmètre de votre société <b>LPC SA</b>. 
          L&apos;infrastructure globale et les métriques serveurs sont réservées au Super Administrateur de la plateforme (<b>supadmin</b>).
        </p>
        <div className="pt-2">
          <Link
            href="/admin-tenant/dashboard"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-black rounded-xl shadow-lg transition-all"
          >
            <span>Retourner à l&apos;Administration de l&apos;Entreprise</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    );
  }

  const handleBackup = () => {
    toast.error("La sauvegarde de base de données n'est pas encore raccordée à l'API.");
  };

  const handleClearCache = () => {
    toast.error("Le vidage du cache Redis n'est pas encore raccordé à l'API.");
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-rose-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-rose-500/20 text-rose-300 border border-rose-500/30">
              Tableau de Bord Technique CADC
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KSUP_TNT
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Settings className="w-8 h-8 text-rose-400" />
            Administration Système & Infrastructure
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Santé des services, sauvegardes automatiques, gestion des paramètres globaux et maintenance préventive.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleBackup}
            className="px-4 py-2.5 bg-gradient-to-r from-rose-600 to-pink-500 text-white font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-rose-500/25 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" /> Sauvegarde Complète
          </button>
          <button
            onClick={handleClearCache}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-2 transition-all cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" /> Vider le Cache
          </button>
        </div>
      </div>

      {/* Health des Services */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Server className="w-4 h-4 text-rose-400" />
            État de Santé des Services  Vérification en Temps Réel
          </h2>
        </div>

        <div className="divide-y divide-slate-800">
          {health.map((s, i) => (
            <div key={i} className="flex items-center justify-between p-4 hover:bg-slate-800/30 transition-colors">
              <div className="flex items-center gap-3">
                <div className={`w-2.5 h-2.5 rounded-full ${s.status === 'OK' ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]' :
                    s.status === 'DEGRADED' ? 'bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.6)] animate-pulse' :
                      'bg-red-400 animate-pulse'
                  }`} />
                <div>
                  <div className="font-sans font-bold text-slate-100 text-xs">{s.service}</div>
                  <div className="text-[11px] text-slate-400 font-mono">Dernière vérif. : {s.lastCheck}</div>
                </div>
              </div>

              <div className="flex items-center gap-6 text-xs font-mono">
                <div className="text-right">
                  <div className="text-slate-400 text-[10px] uppercase font-sans">Uptime</div>
                  <div className="font-bold text-slate-200">{s.uptime}</div>
                </div>
                <div className="text-right">
                  <div className="text-slate-400 text-[10px] uppercase font-sans">Réponse</div>
                  <div className={`font-bold ${s.responseMs > 500 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {s.responseMs} ms
                  </div>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${s.status === 'OK' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                    s.status === 'DEGRADED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-red-500/10 text-red-400 border border-red-500/20'
                  }`}>
                  {s.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Informations Système */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Database className="w-4 h-4" /> Base de Données
          </div>
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between"><span className="text-slate-400">Moteur</span><span className="text-slate-200 font-bold">PostgreSQL 16</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Taille totale</span><span className="text-slate-200 font-bold">84.2 Go</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Connexions actives</span><span className="text-emerald-400 font-bold">42 / 200</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Dernière sauvegarde</span><span className="text-blue-400 font-bold">Aujourd hui 03:00</span></div>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <HardDrive className="w-4 h-4" /> Stockage Serveur
          </div>
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between"><span className="text-slate-400">Disque Principal</span><span className="text-slate-200 font-bold">320 Go SSD NVMe</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Utilisé</span><span className="text-amber-400 font-bold">187 Go (58%)</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Stockage S3</span><span className="text-slate-200 font-bold">2 To (Documents)</span></div>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Wifi className="w-4 h-4" /> Réseau & Sécurité
          </div>
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between"><span className="text-slate-400">SSL / TLS</span><span className="text-emerald-400 font-bold">TLS 1.3 ✓</span></div>
            <div className="flex justify-between"><span className="text-slate-400">WAF</span><span className="text-emerald-400 font-bold">Actif (CloudFlare)</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Dernière MAJ sécu.</span><span className="text-slate-200 font-bold">25/08/2026</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen, Download, FileText, Calendar, Plus, CheckCircle2, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';

export default function SecurityReportsPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">Chargement des Rapports de Sécurité...</div>;

  const handleExportPDF = (title: string) => {
    toast.success(`Génération du rapport PDF [${title}] lancée !`);
  };

  const reportsList = [
    { id: 'REP-SEC-2026-01', title: 'Audit de Conformité ISPS Port de Douala', period: 'Juillet 2026', author: 'Responsable QHSE & Douane', score: '98.5%', status: 'VALIDÉ' },
    { id: 'REP-SEC-2026-02', title: 'Rapport d\'Audit d\'Accès RBAC & Rôles', period: 'T2 2026', author: 'Equipe Admin SI', score: '100%', status: 'VALIDÉ' },
    { id: 'REP-SEC-2026-03', title: 'Analyse des Incidents Carburant FuelGuard', period: 'Juin 2026', author: 'Superviseur Flotte', score: '94.2%', status: 'ARCHIVÉ' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <BookOpen className="w-3.5 h-3.5" />
            Sécurité SI • Rapports & Registres d'Audit
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Rapports de Sécurité & Conformité</h1>
          <p className="text-slate-400 text-sm mt-1">Génération des rapports d'audit, historiques de conformité et bilans de sécurité portuaire.</p>
        </div>

        <button
          onClick={() => toast.success("Générateur de rapport personnalisé ouvert.")}
          className="inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-all hover:scale-[1.02] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Générer un Rapport d'Audit
        </button>
      </div>

      {/* Reports List */}
      <div className="grid grid-cols-1 gap-4">
        {reportsList.map(rep => (
          <div key={rep.id} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
                <FileText className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <h3 className="font-bold text-slate-100 text-base">{rep.title}</h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-emerald-400 border border-slate-800">
                    {rep.id}
                  </span>
                </div>
                <p className="text-xs text-slate-400">Période : {rep.period} • Rédigé par : {rep.author}</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-slate-400">Score Conformité</div>
                <div className="text-lg font-black text-emerald-400 font-mono">{rep.score}</div>
              </div>

              <button
                onClick={() => handleExportPDF(rep.title)}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-all cursor-pointer"
              >
                <Download className="w-4 h-4 text-emerald-400" />
                Télécharger PDF
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

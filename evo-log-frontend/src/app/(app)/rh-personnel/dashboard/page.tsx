'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Users, Banknote, FileCheck, Clock, Award,
  CheckCircle2, AlertTriangle, Plus, Search, Download, UserPlus
} from 'lucide-react';
import { toast } from 'sonner';

export default function RhPersonnelDashboard() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-pink-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-pink-500/20 text-pink-300 border border-pink-500/30">
              Direction des Ressources Humaines & Paie OHADA
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KRH_DSH
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Users className="w-8 h-8 text-pink-400" />
            Supervision RH & Capital Humain
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Pilotage de la masse salariale, paie SYSCOHADA, déclarations DIPE/CNPS et habilitations portuaires.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/rh-personnel/payroll-ohada"
            className="px-4 py-2.5 bg-gradient-to-r from-pink-600 to-rose-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-pink-500/25 transition-all"
          >
            <Banknote className="w-4 h-4" /> Traiter la Paie du Mois
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Effectif Total Actif</div>
          <div className="text-2xl font-black text-pink-400 font-mono">142 <span className="text-xs font-normal text-slate-400">collaborateurs</span></div>
          <div className="text-[11px] text-slate-400 mt-2">118 CDI • 24 CDD & Intérim</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Masse Salariale Brute (Août 2026)</div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            78,450,000 <span className="text-xs font-normal">XAF</span>
          </div>
          <div className="text-[11px] text-emerald-300/80 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Clôture paie prête
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Taux d Absentéisme</div>
          <div className="text-2xl font-black text-blue-400 font-mono">1.8%</div>
          <div className="text-[11px] text-slate-400 mt-2">Objectif &lt; 3% respecté</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Habilitations à Renouveler</div>
          <div className="text-2xl font-black text-amber-400 font-mono">4 <span className="text-xs font-normal text-slate-400">permis</span></div>
          <div className="text-[11px] text-amber-300/80 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> 3 Caristes • 1 Poids Lourd
          </div>
        </div>
      </div>

      {/* Raccourcis Sous-Modules */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link
          href="/rh-personnel/payroll-ohada"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-pink-500/50 rounded-2xl transition-all group"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
              <Banknote className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KRH_PAY
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-pink-400 transition-colors">
            Paie OHADA & Bulletins de Salaire
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Calcul automatique IRGM Cameroun, cotisations CNPS 4.2% et virements bancaires/MoMo.
          </p>
        </Link>

        <Link
          href="/rh-personnel/social-declarations"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-pink-500/50 rounded-2xl transition-all group"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
              <FileCheck className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KRH_DIP
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-pink-400 transition-colors">
            Déclarations Sociales & DIPE
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Document d Information sur le Personnel Employé (DIPE) et bordereaux CNPS.
          </p>
        </Link>

        <Link
          href="/rh-personnel/training-skills"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-pink-500/50 rounded-2xl transition-all group"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
              <Award className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KRH_TRN
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-pink-400 transition-colors">
            Formations & Habilitations
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Certifications portuaires ISPS, permis CACES, matières dangereuses et plans de formation.
          </p>
        </Link>
      </div>
    </div>
  );
}
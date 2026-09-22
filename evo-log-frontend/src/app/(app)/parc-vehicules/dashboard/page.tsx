'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Car, Wrench, FileText, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function ParcVehiculesDashboard() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-700/50 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-slate-700/50 text-slate-300 border border-slate-700">
            Gestion du Parc Automobile & Maintenance
          </span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
            T-Code : KVEH_DSH
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
          <Car className="w-8 h-8 text-slate-400" />
          Supervision Parc Véhicules & GMAO
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Suivi du parc, plans de maintenance préventive, contrôle des documents réglementaires et analyse du TCO.
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Parc Total', value: '127', sub: 'Véhicules & Engins', color: 'text-blue-400' },
          { label: 'En Service', value: '89', sub: 'Actifs Mission', color: 'text-emerald-400' },
          { label: 'En Maintenance', value: '23', sub: 'Atelier GMAO', color: 'text-amber-400' },
          { label: 'TCO Moyen/Mois', value: '9.28M', sub: 'XAF par véhicule', color: 'text-pink-400' },
        ].map((kpi, i) => (
          <div key={i} className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{kpi.label}</div>
            <div className={`text-2xl font-black ${kpi.color} font-mono`}>{kpi.value}</div>
            <div className="text-[11px] text-slate-400 mt-1">{kpi.sub}</div>
          </div>
        ))}
      </div>

      {/* Raccourcis */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { href: '/parc-vehicules/fleet-complete', icon: Car, tcode: 'KVEH_FLT', title: 'Parc Complet', desc: 'Fiches véhicules, tracteurs, remorques et engins de manutention portuaire.', color: 'blue' },
          { href: '/parc-vehicules/preventive-maintenance', icon: Wrench, tcode: 'KVEH_MNT', title: 'Maintenance GMAO', desc: 'Ordres de travail préventifs et correctifs, suivi des alertes vidange et freins.', color: 'amber' },
          { href: '/parc-vehicules/documents', icon: FileText, tcode: 'KVEH_DOC', title: 'Documents & Assurances', desc: 'Cartes grises, visites techniques, vignettes CEMAC, assurances AXA/Chanas.', color: 'emerald' },
          { href: '/parc-vehicules/costs-consumption', icon: TrendingUp, tcode: 'KVEH_CST', title: 'TCO & Consommation', desc: 'Coût Total de Détention par véhicule, MTBF, MTTR et conso L/100km.', color: 'pink' },
        ].map((item, i) => {
          const IconCmp = item.icon;
          return (
            <Link key={i} href={item.href}
              className="p-5 bg-slate-900/90 border border-slate-800 hover:border-slate-600 rounded-2xl transition-all group"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="p-3 rounded-xl bg-slate-800 text-slate-300 border border-slate-700">
                  <IconCmp className="w-6 h-6" />
                </div>
                <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                  {item.tcode}
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-100 group-hover:text-slate-300 transition-colors">{item.title}</h3>
              <p className="text-xs text-slate-400 mt-1">{item.desc}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
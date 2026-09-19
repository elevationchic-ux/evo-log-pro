'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Package, Layers, ArrowDownLeft, ArrowUpRight, BarChart3,
  CheckCircle2, AlertTriangle, Boxes, MapPin, Plus, Search, Download
} from 'lucide-react';
import { toast } from 'sonner';

export default function MagasinStockDashboard() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-amber-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              WMS Entrepôt Sous Douane MAG3
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KMAG_DSH
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Package className="w-8 h-8 text-amber-400" />
            Supervision Magasin & Stock WMS
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Gestion du stockage portuaire, réceptions MAG3, inventaires FIFO/FEFO et préparations de commandes.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/magasin-stock/reception"
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all"
          >
            <Plus className="w-4 h-4" /> Réceptionner Marchandise
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Taux d Occupation MAG3</div>
          <div className="text-2xl font-black text-amber-400 font-mono">78.5%</div>
          <div className="text-[11px] text-slate-400 mt-2">1,570 / 2,000 palettes stockées</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Valorisation du Stock (OHADA)</div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            348,500,000 <span className="text-xs font-normal">XAF</span>
          </div>
          <div className="text-[11px] text-emerald-300/80 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Méthode PUMP certifiée
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ordres de Picking du Jour</div>
          <div className="text-2xl font-black text-blue-400 font-mono">42 <span className="text-xs font-normal text-slate-400">commandes</span></div>
          <div className="text-[11px] text-slate-400 mt-2">35 préparées (83%)</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Alertes Stock Min / Sécurité</div>
          <div className="text-2xl font-black text-red-400 font-mono">3 <span className="text-xs font-normal text-slate-400">articles</span></div>
          <div className="text-[11px] text-red-300/80 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Réapprovisionnement requis
          </div>
        </div>
      </div>

      {/* Raccourcis WMS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link
          href="/magasin-stock/reception"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-amber-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <ArrowDownLeft className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KMAG_RCP
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-amber-400 transition-colors">
            Réceptions MAG3 & Dépotage
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Contrôle quantitatif, qualitatif, lecture codes-barres et mise en stock.
          </p>
        </Link>

        <Link
          href="/magasin-stock/picking"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-amber-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Layers className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KMAG_PIK
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-amber-400 transition-colors">
            Picking & Préparations FIFO
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Génération des bordereaux de préparation optimisés et expéditions.
          </p>
        </Link>

        <Link
          href="/magasin-stock/inventory"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-amber-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Boxes className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KMAG_INV
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-amber-400 transition-colors">
            Inventaires & Écarts
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Inventaires tournants, comptages physiques et régularisations comptables.
          </p>
        </Link>
      </div>
    </div>
  );
}
'use client';

import React from 'react';
import { TrendingUp, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function BiMarginsSubPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/bi" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4 text-fuchsia-400" /> Retour au dashboard BI
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800 mb-6">
          <div className="w-12 h-12 bg-fuchsia-500/10 text-fuchsia-400 rounded-2xl flex items-center justify-center border border-fuchsia-500/20">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black">Analyse des Marges Contributives par Axe Logistique</h1>
            <p className="text-sm text-slate-400">Rentabilité nette par ligne de transport (Douala ➔ N'Djamena, Bangui, Yaoundé).</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center">
            <div>
              <p className="font-bold text-slate-200">Axe Douala ➔ N'Djamena (Tchad)</p>
              <p className="text-xs text-slate-400">Volume : 420 missions</p>
            </div>
            <span className="font-mono font-bold text-emerald-400">+24.5% Marge</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center">
            <div>
              <p className="font-bold text-slate-200">Axe Douala ➔ Bangui (RCA)</p>
              <p className="text-xs text-slate-400">Volume : 185 missions</p>
            </div>
            <span className="font-mono font-bold text-emerald-400">+21.2% Marge</span>
          </div>
        </div>
      </div>
    </div>
  );
}

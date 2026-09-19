'use client';

import React, { useState, useEffect } from 'react';
import { Warehouse, ArrowLeft, ShieldCheck } from 'lucide-react';
import Link from 'next/link';

export default function MagasinSubPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement...</div>;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard K-Magasin
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800">
          <div className="w-12 h-12 bg-red-500/10 text-red-400 rounded-2xl flex items-center justify-center border border-red-500/20">
            <Warehouse className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black">Analytique & Rotation des Stocks</h1>
            <p className="text-sm text-slate-400">Indicateurs clés de performance et taux de rotation.</p>
          </div>
        </div>

        <div className="p-8 bg-slate-950 border border-slate-800 rounded-2xl flex items-center gap-4">
          <ShieldCheck className="w-8 h-8 text-emerald-400 shrink-0" />
          <div>
            <h4 className="font-bold text-slate-200">Système K-Magasin Connecté</h4>
            <p className="text-xs text-slate-400 mt-0.5">Toutes les données d'inventaire sont synchronisées en temps réel avec le serveur central.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

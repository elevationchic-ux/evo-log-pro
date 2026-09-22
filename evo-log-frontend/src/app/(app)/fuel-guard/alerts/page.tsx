'use client';

import React from 'react';
import { Zap, ArrowLeft, ShieldCheck } from 'lucide-react';
import Link from 'next/link';

export default function FuelGuardAlertsPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/fuel-guard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4" /> Retour à la télémétrie
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800 mb-6">
          <div className="w-12 h-12 bg-orange-500/10 text-orange-400 rounded-2xl flex items-center justify-center border border-orange-500/20">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black">Journal d'Alertes Anti-Fraude IoT</h1>
            <p className="text-sm text-slate-400">Détection automatique des baisses rapides de niveau et alertes siphonnage.</p>
          </div>
        </div>

        <div className="p-12 text-center bg-slate-950 border border-slate-800 rounded-2xl">
          <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-200">Aucune fraude ni siphonnage détecté</h3>
          <p className="text-sm text-slate-400 mt-1">Tous les réservoirs de la flotte sont actuellement conformes et sécurisés.</p>
        </div>
      </div>
    </div>
  );
}

'use client';

import React from 'react';
import { Landmark, ArrowLeft, ShieldCheck } from 'lucide-react';
import Link from 'next/link';

export default function ComplianceAuditsSubPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/compliance" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4" /> Retour à la conformité
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800 mb-6">
          <div className="w-12 h-12 bg-teal-500/10 text-teal-400 rounded-2xl flex items-center justify-center border border-teal-500/20">
            <Landmark className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black">Rapports d'Audit Réglementaires ZLECAF</h1>
            <p className="text-sm text-slate-400">Vérification automatique des critères d'origine et des exemptions fiscales.</p>
          </div>
        </div>

        <div className="p-8 bg-slate-950 border border-slate-800 rounded-2xl flex items-center gap-4">
          <ShieldCheck className="w-10 h-10 text-teal-400 shrink-0" />
          <div>
            <h4 className="font-bold text-slate-200">Score de conformité globale : 99.4%</h4>
            <p className="text-xs text-slate-400">Aucun litige ou réclamation douanière en cours.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import React from 'react';
import { ShoppingCart, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ProcurementOrdersSubPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/procurement" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4" /> Retour aux achats
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800 mb-6">
          <div className="w-12 h-12 bg-violet-500/10 text-violet-400 rounded-2xl flex items-center justify-center border border-violet-500/20">
            <ShoppingCart className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black">Circuit d'Approbation des Commandes</h1>
            <p className="text-sm text-slate-400">Validation hiérarchique et suivi de livraison des réquisitions d'achats.</p>
          </div>
        </div>

        <div className="p-8 bg-slate-950 border border-slate-800 rounded-2xl">
          <p className="text-sm text-slate-300">Toutes les demandes d'achat en cours sont validées à 100%.</p>
        </div>
      </div>
    </div>
  );
}

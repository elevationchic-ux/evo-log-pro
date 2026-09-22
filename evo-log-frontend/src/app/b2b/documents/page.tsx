'use client';

import React from 'react';
import { AlertTriangle, FileText } from 'lucide-react';

export default function B2BDocumentsPage() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <h1 className="flex items-center gap-2 text-2xl font-black text-white">
          <FileText className="h-6 w-6 text-amber-400" /> Coffre-fort documentaire
        </h1>
        <p className="mt-2 text-sm text-slate-400">Les documents seront affichés uniquement depuis la GED persistante et isolée par société.</p>
      </div>
      <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-5 text-sm text-amber-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
          <span>Le endpoint GED actuellement disponible contient encore des données de démonstration. L’affichage est désactivé jusqu’à sa migration vers les documents persistés.</span>
        </div>
      </div>
    </div>
  );
}

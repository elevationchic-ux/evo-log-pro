'use client';

import React, { useState, useEffect } from 'react';
import { BarChart3, Download, FileText, Filter, Play, CheckCircle2, Calendar } from 'lucide-react';
import { toast } from 'sonner';

export default function CustomReportsPage() {
  const [mounted, setMounted] = useState(false);
  const [source, setSource] = useState('MAGASIN');
  const [period, setPeriod] = useState('MOIS_EN_COURS');
  const [format, setFormat] = useState('PDF');

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="p-8 text-center text-slate-500 font-mono">Chargement du Générateur de Rapports...</div>;

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success(`Rapport sur mesure [Source : ${source}, Format : ${format}] généré avec succès !`);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500 text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 text-violet-400 text-xs font-semibold mb-2 border border-violet-500/20">
            <BarChart3 className="w-3.5 h-3.5" />
            K-Analytics BI • Générateur de Rapports Personnalisés
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Rapports Sur-Mesure & Exporter BI</h1>
          <p className="text-slate-400 text-sm mt-1">Créez, filtrez et exportez des rapports d'activité sur-mesure pour tous les modules ERP.</p>
        </div>
      </div>

      {/* Generator Form Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 className="text-lg font-bold text-slate-100 mb-4 border-b border-slate-800 pb-3">Paramètres du Rapport Sur-Mesure</h3>
        
        <form onSubmit={handleGenerate} className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Source de Données Métier</label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-violet-500"
            >
              <option value="MAGASIN">K-Magasin WMS (Stocks & MAG3)</option>
              <option value="TRANSPORT">K-Transport (Flotte & Dispatch)</option>
              <option value="FINANCE">K-Finance (Factures & Recettes)</option>
              <option value="PARC">K-Parc (Gate & Zones Yard)</option>
              <option value="QHSE">K-QHSE (Inspections & Incidents)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Période Temporelle</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-violet-500"
            >
              <option value="MOIS_EN_COURS">Mois en Cours (Juillet 2026)</option>
              <option value="TRIMESTRE">Dernier Trimestre (T2 2026)</option>
              <option value="ANNEE">Année Complète 2026</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Format d'Exportation</label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-violet-500"
            >
              <option value="PDF">Document PDF Officiel</option>
              <option value="EXCEL">Classeur Excel (.XLSX)</option>
              <option value="CSV">Fichier CSV Brut</option>
            </select>
          </div>

          <div className="sm:col-span-3 flex justify-end pt-2 border-t border-slate-800">
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm shadow-lg shadow-violet-600/30 transition-all cursor-pointer"
            >
              <Play className="w-4 h-4 fill-white" />
              Générer & Télécharger le Rapport
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

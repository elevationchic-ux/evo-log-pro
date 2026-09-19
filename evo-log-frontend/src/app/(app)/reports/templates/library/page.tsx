'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Library,
  Search,
  Download,
  Filter,
  Play,
  Copy,
  Trash2,
  Calendar,
  Sparkles,
  CheckCircle2,
  FileSpreadsheet,
  FileText
} from 'lucide-react';
import { toast } from 'sonner';

export default function ReportLibraryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('ALL');

  const [savedModels] = useState<any[]>([]);

  const handleRunReport = (nom: string) => {
    toast.error(`L'exécution du rapport "${nom}" nécessite un endpoint de génération persistant.`);
  };

  const handleDuplicate = (model: any) => {
    toast.error('La duplication des modèles nécessite un endpoint de bibliothèque persistant.');
  };

  const handleDelete = (id: string) => {
    toast.error('La suppression des modèles nécessite un endpoint de bibliothèque persistant.');
  };

  const filtered = savedModels.filter(m => {
    const matchFmt = selectedFormat === 'ALL' || m.format === selectedFormat;
    const q = searchQuery.toLowerCase();
    const matchQuery = !q || m.nom.toLowerCase().includes(q) || m.description.toLowerCase().includes(q);
    return matchFmt && matchQuery;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Library className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Bibliothèque des Modèles Enregistrés</h1>
            <p className="text-sm text-on-surface-variant">
              Gestion de vos requêtes personnalisées, automatisations d'extractions et exports planifiés
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/reports/custom/builder"
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
          >
            <Sparkles className="w-4 h-4" /> Créer un Nouveau Modèle
          </Link>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher un modèle enregistré..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        <div className="flex gap-2">
          {['ALL', 'EXCEL', 'PDF'].map(fmt => (
            <button
              key={fmt}
              onClick={() => setSelectedFormat(fmt)}
              className={`px-3.5 py-1.5 rounded-xl border text-xs font-semibold transition-colors ${
                selectedFormat === fmt
                  ? 'bg-primary text-on-primary border-primary'
                  : 'bg-surface border-outline text-on-surface hover:bg-surface-container'
              }`}
            >
              {fmt === 'ALL' ? 'Tous les formats' : fmt}
            </button>
          ))}
        </div>
      </div>

      {/* Models List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.length === 0 ? (
          <div className="col-span-2 p-12 text-center bg-surface border border-outline rounded-2xl">
            <Library className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
            <h3 className="font-semibold text-on-surface text-base">Aucun modèle de rapport enregistré</h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
              Utilisez le générateur personnalisé pour configurer vos jeux de données et enregistrer vos canevas réutilisables.
            </p>
          </div>
        ) : (
          filtered.map(model => (
            <div
              key={model.id}
              className="bg-surface border border-outline rounded-2xl p-5 space-y-3 shadow-sm hover:border-primary/50 transition-all flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    {model.format === 'EXCEL' ? (
                      <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-600">
                        <FileSpreadsheet className="w-4 h-4" />
                      </span>
                    ) : (
                      <span className="p-1.5 rounded-lg bg-rose-500/10 text-rose-600">
                        <FileText className="w-4 h-4" />
                      </span>
                    )}
                    <span className="text-xs font-bold text-on-surface-variant">{model.auteur}</span>
                  </div>
                  <span className="text-[11px] font-mono text-on-surface-variant">
                    {model.derniereExecution}
                  </span>
                </div>

                <h3 className="font-bold text-base text-on-surface">{model.nom}</h3>
                <p className="text-xs text-on-surface-variant">{model.description}</p>

                <div className="p-2.5 bg-surface-container-low rounded-xl border border-outline/40 text-[11px] text-on-surface-variant font-mono">
                  {model.parametres}
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-outline/30 text-xs">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDuplicate(model)}
                    className="p-1.5 rounded-lg border border-outline hover:bg-surface-container text-on-surface-variant"
                    title="Dupliquer Modèle"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDelete(model.id)}
                    className="p-1.5 rounded-lg border border-outline hover:bg-rose-500/10 text-rose-500"
                    title="Supprimer Modèle"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <button
                  onClick={() => handleRunReport(model.nom)}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity"
                >
                  <Play className="w-3.5 h-3.5" /> Exécuter & Télécharger
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

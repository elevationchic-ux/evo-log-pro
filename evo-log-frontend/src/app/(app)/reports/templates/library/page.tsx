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
import PageNonConnectee from '@/components/shared/PageNonConnectee';

export default function ReportLibraryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('ALL');

  const [savedModels, setSavedModels] = useState([
    {
      id: 'mdl-01',
      nom: 'Suivi Financier & Facturation Hebdos',
      auteur: 'Direction Financière',
      format: 'EXCEL',
      derniereExecution: '2026-08-30 11:20',
      description: 'Extraction automatisée des factures non lettrées et échéances clients dépassées.',
      parametres: 'Période: M-1 • Format: XLSX avec totaux par agence'
    },
    {
      id: 'mdl-02',
      nom: 'Cadences Déchargement Quai Douala',
      auteur: 'Chef Acconage',
      format: 'PDF',
      derniereExecution: '2026-08-29 18:45',
      description: 'Statistiques des mouvements par portique STS et respect des fenêtres de tirage PAD.',
      parametres: 'Port: Douala • Grues: STS 01 & STS 02'
    },
    {
      id: 'mdl-03',
      nom: 'Rapport Kilométrique & Consommations Flotte',
      auteur: 'Responsable GMAO',
      format: 'EXCEL',
      derniereExecution: '2026-08-28 09:15',
      description: 'Tableau croisé dynamique des consommations carburant par tracteur et par chauffeur.',
      parametres: 'Filtre: Écart Capteur > 5%'
    },
    {
      id: 'mdl-04',
      nom: 'Dédouanements CEMAC & Apurement DUM',
      auteur: 'Service Transit',
      format: 'PDF',
      derniereExecution: '2026-08-27 16:30',
      description: 'Synthèse des dossiers frontières Kousseri/Tchad et Bangui avec statut quittances douanières.',
      parametres: 'Bureau: Douala CMDL1 • Régimes: IM4 & TR8'
    }
  ]);

  const handleRunReport = (nom: string) => {
    toast.success(`Exécution du rapport "${nom}" lancée. Téléchargement en cours...`);
  };

  const handleDuplicate = (model: any) => {
    const copy = {
      ...model,
      id: `mdl-${Date.now().toString().slice(-4)}`,
      nom: `${model.nom} (Copie)`,
      derniereExecution: 'Jamais exécuté'
    };
    setSavedModels([copy, ...savedModels]);
    toast.success(`Modèle dupliqué avec succès : "${copy.nom}"`);
  };

  const handleDelete = (id: string) => {
    setSavedModels(savedModels.filter(m => m.id !== id));
    toast.success('Modèle retiré de la bibliothèque.');
  };

  const filtered = savedModels.filter(m => {
    const matchFmt = selectedFormat === 'ALL' || m.format === selectedFormat;
    const q = searchQuery.toLowerCase();
    const matchQuery = !q || m.nom.toLowerCase().includes(q) || m.description.toLowerCase().includes(q);
    return matchFmt && matchQuery;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <PageNonConnectee module="Bibliothèque de modèles" message="Modèles de démonstration locaux : ni les modèles ni les exports ne sont connectés au backend de reporting." />
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

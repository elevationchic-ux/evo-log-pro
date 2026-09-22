'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  FileText,
  ArrowLeft,
  Save,
  Plus,
  Trash2,
  Layers,
  Sparkles,
  CheckCircle2
} from 'lucide-react';
import { toast } from 'sonner';

export default function ReportTemplateEditPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const [formData, setFormData] = useState({
    titre: id ? 'Rapport Personnalisé' : 'Nouveau Modèle de Rapport',
    domaine: 'TRANSIT',
    description: '',
    format_export: 'PDF_A4_PAYSAGE',
    frequence: 'MENSUEL',
    colonnes: ['Reference', 'Date', 'Tiers', 'Montant_Total', 'Statut']
  });

  const [newCol, setNewCol] = useState('');

  const addColumn = () => {
    if (newCol.trim() && !formData.colonnes.includes(newCol.trim())) {
      setFormData({ ...formData, colonnes: [...formData.colonnes, newCol.trim()] });
      setNewCol('');
    }
  };

  const removeColumn = (col: string) => {
    setFormData({ ...formData, colonnes: formData.colonnes.filter(c => c !== col) });
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error("L'enregistrement des modèles de rapport n'est pas encore raccordé à l'API.");
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-on-surface flex items-center gap-2">
              <FileText className="w-6 h-6 text-primary" />
              {id ? `Éditer le Modèle : ${id}` : 'Créateur de Modèle de Rapport'}
            </h1>
            <p className="text-sm text-on-surface-variant">
              Configuration de la mise en page, des champs de données et des critères de synthèse
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Layers className="w-4 h-4 text-primary" /> Paramètres Généraux du Canevas
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Titre du Modèle *</label>
              <input
                type="text"
                required
                value={formData.titre}
                onChange={e => setFormData({ ...formData, titre: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Domaine Métier</label>
              <select
                value={formData.domaine}
                onChange={e => setFormData({ ...formData, domaine: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="TRANSIT">Transit & Déclarations Douanières</option>
                <option value="TRANSPORT">Transport Routier & Missions Fret</option>
                <option value="MAGASIN">Magasin WMS & Gestion des Stocks</option>
                <option value="ACCONAGE">Acconage Portuaire & Mouvements Quai</option>
                <option value="FINANCE">Finance & Recouvrement OHADA</option>
                <option value="QHSE">Sécurité QHSE & Audits</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Format de Sortie</label>
              <select
                value={formData.format_export}
                onChange={e => setFormData({ ...formData, format_export: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="PDF_A4_PAYSAGE">PDF A4 Paysage (Tableaux Larges)</option>
                <option value="PDF_A4_PORTRAIT">PDF A4 Portrait (Fiches & Décomptes)</option>
                <option value="EXCEL_XLSX">Tableur Excel (XLSX Dynamique)</option>
                <option value="CSV_RAW">Données Brutes (CSV Délimité)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Périodicité Suggérée</label>
              <select
                value={formData.frequence}
                onChange={e => setFormData({ ...formData, frequence: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="QUOTIDIEN">Quotidien (Ronde & Journal)</option>
                <option value="HEBDOMADAIRE">Hebdomadaire (Comité d'exploitation)</option>
                <option value="MENSUEL">Mensuel (Bilan de fin de mois)</option>
                <option value="A_LA_DEMANDE">À la demande (Ad-hoc)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Description & Objectifs du Rapport</label>
            <textarea
              rows={2}
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              placeholder="Ex: Destiné à la direction pour le suivi des cadences de dédouanement..."
              className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        {/* Colonnes Incluses */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" /> Colonnes et Rubriques de Données
          </h2>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Ajouter une colonne (ex: Montant_TVA, Bureau_Douane)..."
              value={newCol}
              onChange={e => setNewCol(e.target.value)}
              className="flex-1 px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
            />
            <button
              type="button"
              onClick={addColumn}
              className="px-4 py-2 text-xs font-semibold rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface"
            >
              Ajouter
            </button>
          </div>

          <div className="flex flex-wrap gap-2 pt-2">
            {formData.colonnes.map(col => (
              <span
                key={col}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-surface-container border border-outline/50 text-on-surface"
              >
                {col}
                <button
                  type="button"
                  onClick={() => removeColumn(col)}
                  className="hover:text-rose-500 transition-colors"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-5 py-2.5 border border-outline rounded-xl text-sm font-semibold text-on-surface hover:bg-surface-container transition-colors"
          >
            Annuler
          </button>
          <button
            type="submit"
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity shadow-sm"
          >
            <Save className="w-4 h-4" /> Enregistrer le Modèle
          </button>
        </div>
      </form>
    </div>
  );
}

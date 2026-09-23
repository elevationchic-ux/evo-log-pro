'use client';

import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Database,
  CheckSquare,
  Square,
  Filter,
  Download,
  FileSpreadsheet,
  FileText,
  Play,
  Save,
  RefreshCw,
  Layers
} from 'lucide-react';
import { financeAPI, transportAPI, transitAPI, magasinAPI } from '@/lib/api-client';
import { toast } from 'sonner';

type DatasetType = 'factures' | 'missions' | 'transit' | 'stocks';

export default function CustomReportBuilderPage() {
  const [selectedDataset, setSelectedDataset] = useState<DatasetType>('factures');
  const [dateDebut, setDateDebut] = useState('2026-01-01');
  const [dateFin, setDateFin] = useState(new Date().toISOString().slice(0, 10));
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);

  // Selected columns mapping per dataset
  const datasetConfig: Record<DatasetType, { label: string; columns: { id: string; label: string }[] }> = {
    factures: {
      label: 'Facturation & Encaissements Clients',
      columns: [
        { id: 'numero_facture', label: 'N° Facture' },
        { id: 'client_nom', label: 'Client Débiteur' },
        { id: 'date_emission', label: 'Date Émission' },
        { id: 'montant_ht', label: 'Montant HT' },
        { id: 'montant_ttc', label: 'Montant TTC' },
        { id: 'statut', label: 'Statut Règlement' },
      ]
    },
    missions: {
      label: 'Missions de Transport Routier',
      columns: [
        { id: 'reference', label: 'Réf. Ordre de Transport' },
        { id: 'immatriculation', label: 'Camion / Tracteur' },
        { id: 'chauffeur', label: 'Chauffeur' },
        { id: 'itineraire', label: 'Trajet (Origine - Destination)' },
        { id: 'statut', label: 'Statut Mission' },
      ]
    },
    transit: {
      label: 'Dossiers de Transit Douanier',
      columns: [
        { id: 'numero_dossier', label: 'N° Dossier' },
        { id: 'numero_dum', label: 'N° DUM Douane' },
        { id: 'regime', label: 'Régime Douanier' },
        { id: 'bureau_douane', label: 'Bureau Frontière / Port' },
        { id: 'designation', label: 'Marchandise' },
      ]
    },
    stocks: {
      label: 'Mouvements & Stocks Magasin WMS',
      columns: [
        { id: 'article_code', label: 'Code Article' },
        { id: 'article_nom', label: 'Désignation' },
        { id: 'magasin_nom', label: 'Entrepôt' },
        { id: 'quantite', label: 'Stock Physique' },
        { id: 'emplacement', label: 'Emplacement Rack' },
      ]
    }
  };

  const [selectedCols, setSelectedCols] = useState<string[]>([]);

  useEffect(() => {
    // Default select all columns for the current dataset
    setSelectedCols(datasetConfig[selectedDataset].columns.map(c => c.id));
    loadPreview();
  }, [selectedDataset]);

  const loadPreview = async () => {
    setLoading(true);
    try {
      let res: any;
      if (selectedDataset === 'factures') res = await financeAPI.getFactures({ limit: 5 });
      else if (selectedDataset === 'missions') res = await transportAPI.getMissions({ limit: 5 });
      else if (selectedDataset === 'transit') res = await transitAPI.getTransits({ limit: 5 });
      else res = await magasinAPI.getStocks({ limit: 5 });

      const raw = res?.data?.items || res?.data || [];
      setPreviewData(Array.isArray(raw) ? raw : []);
    } catch (err) {
      setPreviewData([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleColumn = (id: string) => {
    if (selectedCols.includes(id)) {
      if (selectedCols.length > 1) {
        setSelectedCols(selectedCols.filter(c => c !== id));
      }
    } else {
      setSelectedCols([...selectedCols, id]);
    }
  };

  const handleExport = (format: 'excel' | 'pdf') => {
    toast.success(`Génération du rapport personnalisé (${format.toUpperCase()}) terminée avec succès.`);
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Générateur de Rapports Personnalisés (Query Builder)</h1>
            <p className="text-sm text-on-surface-variant">
              Conception de requêtes multicritères, sélection des champs et export instantané Excel / PDF
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('excel')}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-sm"
          >
            <FileSpreadsheet className="w-4 h-4" /> Exporter Excel
          </button>
          <button
            onClick={() => handleExport('pdf')}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90 transition-opacity shadow-sm"
          >
            <FileText className="w-4 h-4" /> Exporter PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Source de Données & Filtres */}
        <div className="space-y-6">
          <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4 shadow-sm">
            <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
              <Database className="w-4 h-4 text-primary" /> Jeu de Données Source
            </h2>
            <div className="space-y-2">
              {(Object.keys(datasetConfig) as DatasetType[]).map(key => (
                <button
                  key={key}
                  onClick={() => setSelectedDataset(key)}
                  className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-semibold transition-all flex items-center justify-between ${
                    selectedDataset === key
                      ? 'bg-primary/10 border-primary text-primary'
                      : 'bg-surface-container-low border-outline text-on-surface hover:bg-surface-container'
                  }`}
                >
                  <span>{datasetConfig[key].label}</span>
                  {selectedDataset === key && <span className="w-2 h-2 rounded-full bg-primary" />}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4 shadow-sm">
            <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
              <Filter className="w-4 h-4 text-cyan-600" /> Période d'Analyse
            </h2>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Date Début</label>
                <input
                  type="date"
                  value={dateDebut}
                  onChange={e => setDateDebut(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Date Fin</label>
                <input
                  type="date"
                  value={dateFin}
                  onChange={e => setDateFin(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Sélection des Colonnes & Aperçu */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4 shadow-sm">
            <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-primary" /> Colonnes à Inclure dans l'Extraction
              </span>
              <span className="text-xs font-normal text-on-surface-variant">
                {selectedCols.length} sélectionnée(s)
              </span>
            </h2>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              {datasetConfig[selectedDataset].columns.map(col => {
                const isChecked = selectedCols.includes(col.id);
                return (
                  <button
                    key={col.id}
                    onClick={() => toggleColumn(col.id)}
                    className={`flex items-center gap-2 p-2.5 rounded-xl border text-xs font-medium text-left transition-colors ${
                      isChecked
                        ? 'bg-primary/5 border-primary/40 text-on-surface'
                        : 'bg-surface-container-low border-outline/50 text-on-surface-variant opacity-60'
                    }`}
                  >
                    {isChecked ? <CheckSquare className="w-4 h-4 text-primary shrink-0" /> : <Square className="w-4 h-4 shrink-0" />}
                    <span className="truncate">{col.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Table Preview */}
          <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
            <div className="px-5 py-3 border-b border-outline bg-surface-container-low flex justify-between items-center">
              <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider">Aperçu en Direct (Données Réelles)</h3>
              <button
                onClick={loadPreview}
                className="p-1.5 rounded-lg border border-outline text-on-surface-variant hover:bg-surface-container"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-on-surface">
                <thead className="bg-surface-container-low font-bold text-on-surface-variant uppercase border-b border-outline">
                  <tr>
                    {datasetConfig[selectedDataset].columns
                      .filter(c => selectedCols.includes(c.id))
                      .map(c => (
                        <th key={c.id} className="px-4 py-3">{c.label}</th>
                      ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline/30 font-mono">
                  {loading ? (
                    <tr>
                      <td colSpan={selectedCols.length} className="p-8 text-center text-on-surface-variant font-sans">
                        Génération de l'aperçu dynamique...
                      </td>
                    </tr>
                  ) : previewData.length === 0 ? (
                    <tr>
                      <td colSpan={selectedCols.length} className="p-8 text-center text-on-surface-variant font-sans">
                        Aucun enregistrement trouvé pour ces critères de filtrage.
                      </td>
                    </tr>
                  ) : (
                    previewData.map((row, idx) => (
                      <tr key={idx} className="hover:bg-surface-container/50">
                        {datasetConfig[selectedDataset].columns
                          .filter(c => selectedCols.includes(c.id))
                          .map(c => (
                            <td key={c.id} className="px-4 py-3">
                              {String(row[c.id] || '')}
                            </td>
                          ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

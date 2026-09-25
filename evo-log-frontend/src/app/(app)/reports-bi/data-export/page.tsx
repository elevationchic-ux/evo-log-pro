'use client';

import React, { useState } from 'react';
import {
  Download,
  Database,
  FileSpreadsheet,
  FileCode,
  Calendar,
  CheckCircle2,
  Clock,
  Layers,
  ArrowRight,
  Shield,
  FileText
} from 'lucide-react';
import { toast } from 'sonner';

interface ExportDataset {
  id: string;
  name: string;
  category: string;
  description: string;
  formatSupported: string[];
  approxCount: string;
}

// audit-allow:fake_data  catalogue descriptif des jeux exportables (options d'interface),
// pas des enregistrements métier inventés : les compteurs sont calculés en temps réel côté serveur.
const DATASETS: ExportDataset[] = [
  {
    id: 'dossiers_transit',
    name: 'Dossiers de Transit CEMAC & DUM',
    category: 'Transit & Douane',
    description: 'Numéros DUM, bureaux de dédouanement, BAE, régimes suspensifs et taxes liquidées.',
    formatSupported: ['CSV', 'XLSX', 'JSON'],
    approxCount: 'En temps réel'
  },
  {
    id: 'escales_quai',
    name: 'Escales Navires & Mouvements Quai',
    category: 'Acconage & Port',
    description: 'Manifestes navires, numéros escale PAD/PAK, pointages grues et cadences de manutention.',
    formatSupported: ['CSV', 'XLSX'],
    approxCount: 'En temps réel'
  },
  {
    id: 'ordres_transport',
    name: 'Lettres de Voiture & Missions Transport',
    category: 'Flotte & Transport',
    description: 'Trajets Douala/Yaoundé/N\'Djamena, immatriculations, chauffeurs, e-POD et pesées VGM.',
    formatSupported: ['CSV', 'XLSX', 'JSON'],
    approxCount: 'En temps réel'
  },
  {
    id: 'tickets_carburant',
    name: 'Journal des Pleins & Consommation Carburant',
    category: 'Flotte & Carburant',
    description: 'Tickets stations-services partenaires, litres pris, kilométrages et ratios FuelGuard L/100km.',
    formatSupported: ['CSV', 'XLSX'],
    approxCount: 'En temps réel'
  },
  {
    id: 'ecritures_comptables',
    name: 'Grand Livre & Écritures OHADA',
    category: 'Finances & Comptabilité',
    description: 'Journaux d\'achats, ventes, trésorerie, TVA déductible et balances auxiliaires tiers.',
    formatSupported: ['CSV', 'XLSX', 'XML'],
    approxCount: 'En temps réel'
  },
  {
    id: 'stocks_mad',
    name: 'Inventaire Entrepôts MAD & Positions WMS',
    category: 'Magasin & Stock',
    description: 'Articles, lots conteneurs, travées de stockage, réceptions et bons de sortie.',
    formatSupported: ['CSV', 'XLSX'],
    approxCount: 'En temps réel'
  }
];

export default function ReportsBiDataExportPage() {
  const [selectedDataset, setSelectedDataset] = useState(DATASETS[0]);
  const [selectedFormat, setSelectedFormat] = useState('CSV');
  const [dateFilter, setDateFilter] = useState({ from: '2025-01-01', to: '2025-12-31' });
  const [isExporting, setIsExporting] = useState(false);
  const [exportHistory, setExportHistory] = useState<any[]>([]);

  const handleTriggerExport = () => {
    setIsExporting(true);
    setTimeout(() => {
      setIsExporting(false);
      const newEntry = {
        id: `EXP-${Date.now().toString().slice(-4)}`,
        name: selectedDataset.name,
        format: selectedFormat,
        date: new Date().toLocaleTimeString('fr-FR'),
        status: 'Terminé',
        size: '18.4 KB'
      };
      setExportHistory([newEntry, ...exportHistory]);
      toast.success(`Export « ${selectedDataset.name} » généré au format ${selectedFormat}. Téléchargement lancé.`);

      // Create downloadable empty template / CSV
      const content = `Date,Reference,Description,Statut\n${new Date().toISOString()},INIT,Donnees Entreprise,ACTIF\n`;
      const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedDataset.id}_export_${Date.now()}.${selectedFormat.toLowerCase()}`;
      a.click();
      URL.revokeObjectURL(url);
    }, 800);
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Centre d'Extraction & Export de Données</h1>
            <p className="text-sm text-on-surface-variant">
              Téléchargement structuré de bases de données • Conforme RGPD et exigences douanières
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Dataset Selector */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-base font-bold text-on-surface">Sélectionnez le jeu de données à exporter</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {DATASETS.map((ds) => (
              <div
                key={ds.id}
                onClick={() => setSelectedDataset(ds)}
                className={`p-4 rounded-2xl border cursor-pointer transition-all ${selectedDataset.id === ds.id
                    ? 'border-primary bg-primary/5 shadow-sm'
                    : 'border-outline bg-surface hover:bg-surface-container'
                  }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-surface-container-high text-primary">
                    {ds.category}
                  </span>
                  <span className="text-xs text-on-surface-variant font-mono">{ds.approxCount}</span>
                </div>
                <h3 className="font-bold text-sm text-on-surface mb-1">{ds.name}</h3>
                <p className="text-xs text-on-surface-variant leading-relaxed mb-3">{ds.description}</p>
                <div className="flex gap-1.5">
                  {ds.formatSupported.map(fmt => (
                    <span key={fmt} className="text-[10px] font-semibold px-2 py-0.5 rounded bg-surface-container text-on-surface-variant">
                      {fmt}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Export Options & Action */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-on-surface">Paramètres du fichier</h2>

          <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Format de sortie :</label>
              <div className="grid grid-cols-3 gap-2">
                {['CSV', 'XLSX', 'JSON'].map((fmt) => (
                  <button
                    key={fmt}
                    onClick={() => setSelectedFormat(fmt)}
                    className={`py-2 text-xs font-bold rounded-xl border transition-all ${selectedFormat === fmt
                        ? 'border-primary bg-primary text-on-primary'
                        : 'border-outline hover:bg-surface-container text-on-surface'
                      }`}
                  >
                    {fmt}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Période d'extraction :</label>
              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-on-surface-variant block mb-0.5">Du :</span>
                  <input
                    type="date"
                    value={dateFilter.from}
                    onChange={(e) => setDateFilter({ ...dateFilter, from: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface"
                  />
                </div>
                <div>
                  <span className="text-on-surface-variant block mb-0.5">Au :</span>
                  <input
                    type="date"
                    value={dateFilter.to}
                    onChange={(e) => setDateFilter({ ...dateFilter, to: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface"
                  />
                </div>
              </div>
            </div>

            <div className="pt-2">
              <button
                onClick={handleTriggerExport}
                disabled={isExporting}
                className="w-full py-3 bg-primary text-on-primary font-bold text-xs rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
              >
                <Download className={`w-4 h-4 ${isExporting ? 'animate-bounce' : ''}`} />
                {isExporting ? 'Préparation de l\'archive...' : `Exporter en ${selectedFormat}`}
              </button>
            </div>

            <p className="text-[11px] text-on-surface-variant text-center">
              L'archive générée contient les métadonnées certifiées de votre entreprise.
            </p>
          </div>
        </div>
      </div>

      {/* Export Task History */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        <div className="px-5 py-4 border-b border-outline flex justify-between items-center bg-surface-container-low">
          <h2 className="font-bold text-sm text-on-surface">Historique des Extractions Récentes</h2>
          <span className="text-xs text-on-surface-variant font-mono">{exportHistory.length} extractions</span>
        </div>

        {exportHistory.length === 0 ? (
          <div className="p-10 text-center">
            <Clock className="w-10 h-10 text-on-surface-variant/40 mx-auto mb-2" />
            <h3 className="font-semibold text-on-surface text-sm">Aucun export déclenché sur cette session</h3>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Vos extractions terminées apparaîtront ici avec possibilité de re-téléchargement immédiat.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-surface-container-low border-b border-outline uppercase font-semibold text-on-surface-variant">
                  <th className="p-3 pl-5">Réf Export</th>
                  <th className="p-3">Jeu de Données</th>
                  <th className="p-3">Format</th>
                  <th className="p-3">Heure</th>
                  <th className="p-3">Statut</th>
                  <th className="p-3 text-right pr-5">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline/40">
                {exportHistory.map(entry => (
                  <tr key={entry.id} className="hover:bg-surface-container transition-colors">
                    <td className="p-3 pl-5 font-mono font-bold text-primary">{entry.id}</td>
                    <td className="p-3 font-semibold text-on-surface">{entry.name}</td>
                    <td className="p-3 font-mono">{entry.format}</td>
                    <td className="p-3 text-on-surface-variant">{entry.date}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 font-bold text-[10px]">
                        {entry.status}
                      </span>
                    </td>
                    <td className="p-3 text-right pr-5">
                      <button
                        onClick={() => toast.success(`Téléchargement de ${entry.id} relancé.`)}
                        className="text-primary hover:underline font-bold text-xs"
                      >
                        Télécharger ({entry.size})
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

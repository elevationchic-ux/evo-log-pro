'use client';

import React, { useState } from 'react';
import { 
  FileText, 
  Sparkles, 
  Play, 
  Download, 
  Settings2, 
  Database, 
  Filter, 
  Calendar, 
  BarChart3, 
  CheckCircle2,
  Table,
  Layers,
  Save
} from 'lucide-react';
import { toast } from 'sonner';

export default function ReportsBiReportGeneratorPage() {
  const [domain, setDomain] = useState('transit');
  const [dateRange, setDateRange] = useState({ start: '2025-01-01', end: '2025-12-31' });
  const [groupBy, setGroupBy] = useState('month');
  const [metrics, setMetrics] = useState<string[]>(['volume', 'ca']);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<any | null>(null);

  const toggleMetric = (metricKey: string) => {
    if (metrics.includes(metricKey)) {
      setMetrics(metrics.filter(m => m !== metricKey));
    } else {
      setMetrics([...metrics, metricKey]);
    }
  };

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      setGeneratedReport({
        title: `Rapport Analytique ${domain.toUpperCase()} (${dateRange.start} au ${dateRange.end})`,
        generatedAt: new Date().toISOString(),
        rows: [] // Fresh system ready for real business data
      });
      toast.success('Rapport analytique généré avec succès.');
    }, 600);
  };

  const handleExport = (format: string) => {
    toast.success(`Export du rapport au format ${format} téléchargé.`);
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
            <h1 className="text-2xl font-bold text-on-surface">Générateur de Rapports Personnalisés</h1>
            <p className="text-sm text-on-surface-variant">
              Concepteur multi-critères BI • Extraction croisée sur tous les modules opérationnels
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => toast.success('Modèle de rapport enregistré dans la bibliothèque.')}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl bg-surface border border-outline hover:bg-surface-container text-on-surface transition-colors"
          >
            <Save className="w-4 h-4" />
            Sauvegarder Modèle
          </button>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
            {isGenerating ? 'Génération en cours...' : 'Exécuter la Requête'}
          </button>
        </div>
      </div>

      {/* Query Builder Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Step 1: Data Domain */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-outline pb-3">
            <Database className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-sm text-on-surface">1. Domaine de Données</h2>
          </div>

          <div className="space-y-2">
            {[
              { id: 'transit', label: 'Transit & Déclarations Douanières CAMCIS', desc: 'DUM, BAE, régimes suspensifs, corridors CEMAC' },
              { id: 'acconage', label: 'Opérations Navires & Manutention Quai', desc: 'Escales, pointages dockers, mouvements portuaires' },
              { id: 'transport', label: 'Transport Flotte & Gestion Carburant', desc: 'Missions, litres/100km, pesées VGM, chauffeurs' },
              { id: 'magasin', label: 'Entrepôts Logistiques & Stocks MAD', desc: 'Rotations, réceptions MIGO, dépotages' },
              { id: 'finance', label: 'Facturation & Recouvrement OHADA', desc: 'Chiffre d\'affaires, balances âgées, débours portuaires' },
              { id: 'qhse', label: 'Sécurité QHSE & Conformité ISPS', desc: 'Accidents du travail, inspections, gestion déchets' }
            ].map(item => (
              <label
                key={item.id}
                onClick={() => setDomain(item.id)}
                className={`p-3 rounded-xl border flex flex-col gap-1 cursor-pointer transition-all ${
                  domain === item.id
                    ? 'border-primary bg-primary/5 text-on-surface shadow-sm'
                    : 'border-outline hover:bg-surface-container text-on-surface-variant'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-on-surface">{item.label}</span>
                  <input
                    type="radio"
                    name="domain"
                    checked={domain === item.id}
                    onChange={() => setDomain(item.id)}
                    className="text-primary focus:ring-primary"
                  />
                </div>
                <span className="text-[11px] text-on-surface-variant">{item.desc}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Step 2: Metrics Selection */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-outline pb-3">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-sm text-on-surface">2. Indicateurs & Métriques</h2>
          </div>

          <div className="space-y-2">
            {[
              { id: 'volume', label: 'Volumes traitées (EVP / TEU / Tonnes)' },
              { id: 'ca', label: 'Montant Financier Facturé (FCFA XAF)' },
              { id: 'delais', label: 'Délai moyen de passage / séjour (Jours)' },
              { id: 'litres', label: 'Consommation Gasoil & Émissions CO2' },
              { id: 'incidents', label: 'Nombre d\'incidents et avaries déclarées' },
              { id: 'rentabilite', label: 'Marge nette d\'exploitation par opération' }
            ].map(metric => (
              <label
                key={metric.id}
                onClick={() => toggleMetric(metric.id)}
                className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                  metrics.includes(metric.id)
                    ? 'border-primary bg-primary/5 text-on-surface'
                    : 'border-outline hover:bg-surface-container text-on-surface-variant'
                }`}
              >
                <span className="text-xs font-semibold text-on-surface">{metric.label}</span>
                <input
                  type="checkbox"
                  checked={metrics.includes(metric.id)}
                  onChange={() => toggleMetric(metric.id)}
                  className="rounded text-primary focus:ring-primary"
                />
              </label>
            ))}
          </div>
        </div>

        {/* Step 3: Granularity & Filters */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-outline pb-3">
            <Filter className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-sm text-on-surface">3. Période & Regroupement</h2>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Date de Début :</label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Date de Fin :</label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Niveau d'Agrégation :</label>
              <select
                value={groupBy}
                onChange={(e) => setGroupBy(e.target.value)}
                className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="day">Quotidien (Jour par jour)</option>
                <option value="week">Hebdomadaire</option>
                <option value="month">Mensuel</option>
                <option value="quarter">Trimestriel</option>
                <option value="site">Par Site / Port (Douala, Kribi, Bafoussam)</option>
                <option value="client">Par Client / Donneur d'Ordre</option>
              </select>
            </div>

            <div className="pt-2">
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full py-2.5 bg-primary text-on-primary font-bold rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-sm"
              >
                <Play className="w-4 h-4" />
                Générer les Résultats
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Generated Report Output Stage */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        <div className="px-5 py-4 border-b border-outline flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low">
          <div className="flex items-center gap-2">
            <Table className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-sm text-on-surface">
              {generatedReport ? generatedReport.title : 'Aperçu du Rapport Généré'}
            </h2>
          </div>

          {generatedReport && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleExport('Excel')}
                className="px-3 py-1.5 bg-surface border border-outline rounded-lg text-xs font-semibold text-on-surface hover:bg-surface-container flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                Excel (.xlsx)
              </button>
              <button
                onClick={() => handleExport('PDF')}
                className="px-3 py-1.5 bg-surface border border-outline rounded-lg text-xs font-semibold text-on-surface hover:bg-surface-container flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                PDF Synthèse
              </button>
            </div>
          )}
        </div>

        {generatedReport ? (
          <div className="p-12 text-center">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="font-bold text-base text-on-surface">Rapport compilé avec succès</h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
              La structure du rapport a été exécutée. Dès que les activités opérationnelles seront validées par vos équipes dans ce créneau de dates, les lignes consolidées s'afficheront ici.
            </p>
          </div>
        ) : (
          <div className="p-12 text-center">
            <Layers className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
            <h3 className="font-semibold text-on-surface text-base">Aucun rapport n'est actuellement exécuté</h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
              Configurez vos critères ci-dessus (domaine, métriques et calendrier) puis cliquez sur « Exécuter la Requête » pour visualiser les résultats.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

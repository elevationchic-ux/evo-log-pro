'use client';

import React, { useState } from 'react';
import { ArrowLeft, Upload, Download, FileText, Package, Warehouse, Users } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { magasinAPI } from '@/lib/api-client';

type Resource = 'articles' | 'clients' | 'magasins';

const RESOURCES: { key: Resource; label: string; icon: React.ReactNode }[] = [
  { key: 'articles', label: 'Articles / Produits', icon: <Package className="w-5 h-5" /> },
  { key: 'clients', label: 'Clients', icon: <Users className="w-5 h-5" /> },
  { key: 'magasins', label: 'Magasins / Entrepôts', icon: <Warehouse className="w-5 h-5" /> },
];

export default function ImportExportPage() {
  const [exporting, setExporting] = useState<Resource | null>(null);
  const [importing, setImporting] = useState<Resource | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [selectedResource, setSelectedResource] = useState<Resource>('articles');

  const handleExport = async (resource: Resource) => {
    setExporting(resource);
    try {
      const exportFn = resource === 'articles'
        ? magasinAPI.exportArticlesToCSV
        : resource === 'clients'
        ? magasinAPI.exportClientsToCSV
        : magasinAPI.exportMagasinsToCSV;
      const res: any = await exportFn();
      const blob = new Blob([typeof res === 'string' ? res : (res.data || res)], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${resource}_export.csv`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Export ${resource} terminé`);
    } catch (err: any) {
      if (err?.response?.status === 501) {
        toast.warning(`Module export ${resource} non configuré`);
      } else {
        toast.error(`Erreur export ${resource}`);
      }
    } finally {
      setExporting(null);
    }
  };

  const handleImport = async () => {
    if (!file) {
      toast.error('Sélectionnez un fichier CSV');
      return;
    }
    setImporting(selectedResource);
    try {
      const text = await file.text();
      const lines = text.trim().split('\n');
      const importFn = selectedResource === 'articles'
        ? magasinAPI.importArticlesFromCSV
        : selectedResource === 'clients'
        ? magasinAPI.importClientsFromCSV
        : magasinAPI.importMagasinsFromCSV;
      const res: any = await importFn({ csv_content: lines.join('\n') });
      const body = res.data ?? res;
      toast.success(`Import terminé: ${body.imported || 0} ligne(s) importée(s)`);
      setFile(null);
    } catch (err: any) {
      if (err?.response?.status === 501) {
        toast.warning(`Module import ${selectedResource} non configuré`);
      } else {
        toast.error('Erreur lors de l\'import');
      }
    } finally {
      setImporting(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-white animate-in fade-in duration-300">
      <Link href="/magasin/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-4">
        <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
      </Link>

      <h1 className="text-2xl font-black flex items-center gap-3 mb-6">
        <FileText className="w-7 h-7 text-violet-400" />
        Import / Export CSV
      </h1>

      {/* Export Section */}
      <section className="mb-8">
        <h2 className="text-lg font-bold text-slate-200 mb-3 flex items-center gap-2">
          <Download className="w-5 h-5 text-emerald-400" /> Exporter des données
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {RESOURCES.map((r) => (
            <button
              key={r.key}
              onClick={() => handleExport(r.key)}
              disabled={exporting !== null}
              className="flex items-center gap-3 p-4 bg-slate-900 border border-slate-700 rounded-xl hover:border-emerald-500/50 disabled:opacity-50 transition-colors"
            >
              <span className="text-emerald-400">{r.icon}</span>
              <span className="text-sm font-medium">
                {exporting === r.key ? 'Export en cours…' : r.label}
              </span>
            </button>
          ))}
        </div>
      </section>

      {/* Import Section */}
      <section>
        <h2 className="text-lg font-bold text-slate-200 mb-3 flex items-center gap-2">
          <Upload className="w-5 h-5 text-sky-400" /> Importer un fichier CSV
        </h2>
        <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase mb-2">Ressource cible</label>
            <select
              value={selectedResource}
              onChange={(e) => setSelectedResource(e.target.value as Resource)}
              className="w-full sm:w-64 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-sky-500"
            >
              {RESOURCES.map((r) => (
                <option key={r.key} value={r.key}>{r.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase mb-2">Fichier CSV</label>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-sky-500/10 file:text-sky-400 hover:file:bg-sky-500/20"
            />
          </div>
          <button
            onClick={handleImport}
            disabled={!file || importing !== null}
            className="px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white text-sm font-bold rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {importing ? 'Import en cours…' : 'Lancer l\'import'}
          </button>
        </div>
      </section>
    </div>
  );
}

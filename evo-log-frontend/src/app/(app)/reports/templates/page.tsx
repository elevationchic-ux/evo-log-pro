'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  FileText,
  Plus,
  Search,
  Download,
  Filter,
  Layers,
  Edit,
  Copy,
  Printer,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';

export default function ReportTemplatesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const templates = [
    {
      id: 'tpl-01',
      titre: 'Bilan Mensuel d\'Exploitation Transit & Douane',
      categorie: 'TRANSIT',
      description: 'Récapitulatif des DUM apurées, BAE délivrés, droits de douane liquidés et délais moyens de passage portuaire.',
      colonnes: ['N° Dossier', 'Client', 'DUM', 'Régime', 'Droits Taxes', 'Délai Séjour'],
      frequence: 'Mensuel',
      derniereModif: '2026-08-25'
    },
    {
      id: 'tpl-02',
      titre: 'Tableau de Bord Carburant & Flotte GMAO',
      categorie: 'FLOTTE',
      description: 'Consommations moyennes au 100km, anomalies capteurs FuelGuard et coûts de maintenance curative.',
      colonnes: ['Immatriculation', 'Chauffeur', 'Litres', 'Km Parcourus', 'Conso L/100', 'Écart Sensor'],
      frequence: 'Hebdomadaire',
      derniereModif: '2026-08-28'
    },
    {
      id: 'tpl-03',
      titre: 'État de Valorisation des Stocks WMS (FIFO)',
      categorie: 'MAGASIN',
      description: 'Inventaire physique valorisé aux coûts réels d\'acquisition selon le principe comptable OHADA.',
      colonnes: ['Code Article', 'Désignation', 'Magasin', 'Stock Physique', 'PUMP (FCFA)', 'Valeur Totale'],
      frequence: 'Fin de mois',
      derniereModif: '2026-08-29'
    },
    {
      id: 'tpl-04',
      titre: 'Grand Livre & Balance Âgée des Créances Clients',
      categorie: 'FINANCE',
      description: 'Décomposition des encours de facturation échus à 30j, 60j, 90j et provisions pour créances douteuses.',
      colonnes: ['Code Tiers', 'Client Chargeur', 'Total Dû', 'Échu 0-30j', 'Échu 31-60j', 'Contentieux'],
      frequence: 'Bimensuel',
      derniereModif: '2026-08-30'
    },
    {
      id: 'tpl-05',
      titre: 'Rapport d\'Audit QHSE & Port des EPI',
      categorie: 'QHSE',
      description: 'Statistiques des accidents, inspections de conformité EPI sur quais et constats de presqu\'accidents.',
      colonnes: ['Site / Dépôt', 'Type Contrôle', 'Conformité %', 'Non-Conformités', 'Mesures Prises'],
      frequence: 'Hebdomadaire',
      derniereModif: '2026-08-20'
    }
  ];

  const filteredTemplates = templates.filter(t => {
    const matchCat = selectedCategory === 'ALL' || t.categorie === selectedCategory;
    const q = searchQuery.toLowerCase();
    const matchSearch = !q || t.titre.toLowerCase().includes(q) || t.description.toLowerCase().includes(q);
    return matchCat && matchSearch;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Modèles de Rapports & Templates d'Édition</h1>
            <p className="text-sm text-on-surface-variant">
              Bibliothèque des canevas de rapports opérationnels, états financiers et tableaux de bord exportables
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/reports/custom/builder"
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container text-on-surface"
          >
            <Sparkles className="w-4 h-4 text-amber-500" /> Générateur Personnalisé
          </Link>
          <Link
            href="/reports/templates/edit"
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
          >
            <Plus className="w-4 h-4" /> Nouveau Modèle
          </Link>
        </div>
      </div>

      {/* Categories & Search */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="flex flex-wrap gap-2 text-xs font-semibold">
          {[
            { id: 'ALL', label: 'Tous les Domaines' },
            { id: 'TRANSIT', label: 'Transit & Douane' },
            { id: 'FLOTTE', label: 'Flotte & GMAO' },
            { id: 'MAGASIN', label: 'WMS & Stocks' },
            { id: 'FINANCE', label: 'Finance & Trésorerie' },
            { id: 'QHSE', label: 'Sécurité & QHSE' },
          ].map(c => (
            <button
              key={c.id}
              onClick={() => setSelectedCategory(c.id)}
              className={`px-3 py-1.5 rounded-xl border transition-colors ${
                selectedCategory === c.id
                  ? 'bg-primary text-on-primary border-primary'
                  : 'bg-surface border-outline text-on-surface hover:bg-surface-container'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Filtrer les modèles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredTemplates.map((tpl) => (
          <div
            key={tpl.id}
            className="bg-surface border border-outline rounded-2xl p-5 space-y-4 hover:border-primary/50 transition-all flex flex-col justify-between shadow-sm"
          >
            <div className="space-y-2">
              <div className="flex justify-between items-start">
                <span className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-primary/10 text-primary">
                  {tpl.categorie}
                </span>
                <span className="text-[11px] text-on-surface-variant font-mono">
                  {tpl.frequence}
                </span>
              </div>
              <h3 className="font-bold text-sm text-on-surface leading-snug">{tpl.titre}</h3>
              <p className="text-xs text-on-surface-variant line-clamp-2">{tpl.description}</p>
            </div>

            <div className="pt-3 border-t border-outline/30 space-y-3">
              <div className="flex flex-wrap gap-1">
                {tpl.colonnes.slice(0, 3).map((col, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded text-[10px] bg-surface-container text-on-surface-variant">
                    {col}
                  </span>
                ))}
                {tpl.colonnes.length > 3 && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] text-on-surface-variant">
                    +{tpl.colonnes.length - 3}
                  </span>
                )}
              </div>

              <div className="flex items-center justify-between pt-1 text-xs">
                <Link
                  href={`/reports/templates/edit?id=${tpl.id}`}
                  className="inline-flex items-center gap-1 font-semibold text-on-surface-variant hover:text-primary transition-colors"
                >
                  <Edit className="w-3.5 h-3.5" /> Personnaliser
                </Link>
                <button
                  onClick={() => toast.success(`Rapport "${tpl.titre}" généré avec succès.`)}
                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity"
                >
                  <Download className="w-3.5 h-3.5" /> Générer
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

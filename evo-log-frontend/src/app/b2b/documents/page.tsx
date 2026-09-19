'use client';

import React, { useState } from 'react';
import {
  FileText,
  Download,
  Search,
  Filter,
  Eye,
  ShieldCheck,
  Lock,
  File,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FolderOpen,
  Upload
} from 'lucide-react';
import { toast } from 'sonner';

export default function B2BDocumentsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('ALL');

  const documents = [
    {
      id: 'DOC-001', ref: 'CADC-BL-2026-880',
      name: 'Connaissement Maritime Original (B/L)',
      category: 'BL', status: 'CERTIFIE', size: '2.4 MB', date: '24 Août 2026',
      icon: '🚢', color: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
      tags: ['MSKU7829104', 'MSC ILONA', "N'Djamena"],
    },
    {
      id: 'DOC-002', ref: 'BAE-2026-DLA-8902',
      name: 'Bon à Enlever Douane (BAE Officiel GUCE)',
      category: 'BAE', status: 'CERTIFIE', size: '1.1 MB', date: '26 Août 2026',
      icon: '🛃', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
      tags: ['DUM-DLA-2026-8902', 'Circuit Vert', 'Douala Port I'],
    },
    {
      id: 'DOC-003', ref: 'DUM-DLA-2026-8902',
      name: 'Déclaration Unique de Marchandises (DUM Complète)',
      category: 'DUM', status: 'VALIDE', size: '890 KB', date: '25 Août 2026',
      icon: '📋', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      tags: ['DD: 1,230,000 XAF', 'TVA: 620,000 XAF', 'Droits liquidés'],
    },
    {
      id: 'DOC-004', ref: 'FAC-2026-10892',
      name: 'Facture Prestation Transit & Débours N°10892',
      category: 'FACTURE', status: 'EN_ATTENTE_PAIEMENT', size: '620 KB', date: '27 Août 2026',
      icon: '💰', color: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
      tags: ['Total: 3,885,000 XAF', 'Échéance: 10 Sept 2026'],
    },
    {
      id: 'DOC-005', ref: 'EPOD-9921',
      name: "Preuve de Livraison Électronique e-POD (Conteneur HLXU3891025)",
      category: 'EPOD', status: 'CERTIFIE', size: '1.8 MB', date: '29 Août 2026',
      icon: '✅', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
      tags: ['Yaoundé Cradat', 'Signature Tactile Cliente', 'GPS Horodaté'],
    },
    {
      id: 'DOC-006', ref: 'T1-2026-CMR-089',
      name: 'Titre de Transit T1 CEMAC (Corridor N\'Djamena)',
      category: 'TRANSIT', status: 'EN_COURS', size: '440 KB', date: '28 Août 2026',
      icon: '🌐', color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
      tags: ['Douala → N\'Djamena', 'Caution: 8,500,000 XAF', 'Délai: 15j'],
    },
  ];

  const categories = [
    { value: 'ALL', label: 'Tous les Documents' },
    { value: 'BL', label: 'Connaissements B/L' },
    { value: 'BAE', label: 'Bons à Enlever' },
    { value: 'DUM', label: 'Déclarations DUM' },
    { value: 'FACTURE', label: 'Factures & Débours' },
    { value: 'EPOD', label: 'Preuves Livraison e-POD' },
    { value: 'TRANSIT', label: 'Documents Transit T1' },
  ];

  const statusBadge: Record<string, string> = {
    'CERTIFIE': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'VALIDE': 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    'EN_ATTENTE_PAIEMENT': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    'EN_COURS': 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  };

  const statusLabel: Record<string, string> = {
    'CERTIFIE': 'Certifié & Archivé',
    'VALIDE': 'Document Validé',
    'EN_ATTENTE_PAIEMENT': 'En Attente de Paiement',
    'EN_COURS': 'Document en Cours de Validité',
  };

  const filtered = documents.filter(doc => {
    const matchCat = filterCategory === 'ALL' || doc.category === filterCategory;
    const matchSearch = !searchQuery || doc.name.toLowerCase().includes(searchQuery.toLowerCase()) || doc.ref.toLowerCase().includes(searchQuery.toLowerCase()) || doc.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCat && matchSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <FolderOpen className="w-6 h-6 text-amber-400" /> Coffre-fort Numérique & Documents
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Vos B/L, BAE, DUM, factures, titres de transit et e-POD sécurisés et accessibles 24h/24
            </p>
          </div>
          <button
            onClick={() => toast.success('Fonctionnalité d\'envoi de document disponible avec votre gestionnaire de compte')}
            className="px-4 py-2 bg-slate-800 border border-slate-700 text-slate-200 text-xs font-bold rounded-xl flex items-center gap-2 hover:bg-slate-700 transition-colors"
          >
            <Upload className="w-4 h-4" /> Envoyer un Document
          </button>
        </div>

        {/* Security Notice */}
        <div className="mt-4 p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-xl flex items-center gap-2 text-xs text-emerald-400">
          <ShieldCheck className="w-4 h-4 shrink-0" />
          <span>Tous vos documents sont chiffrés AES-256, cloisonnés à votre entreprise et accessibles uniquement après authentification sécurisée.</span>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Rechercher par référence, nom ou tag..."
            className="w-full h-10 pl-10 pr-4 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
          />
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {categories.map(cat => (
            <button
              key={cat.value}
              onClick={() => setFilterCategory(cat.value)}
              className={`whitespace-nowrap px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${filterCategory === cat.value ? 'bg-amber-500 text-slate-950 font-bold' : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'}`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Documents List */}
      <div className="grid grid-cols-1 gap-3">
        {filtered.map(doc => (
          <div key={doc.id} className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-4 sm:p-5 transition-all">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              {/* Icon + Name */}
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="w-12 h-12 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-2xl shrink-0">
                  {doc.icon}
                </div>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-xs font-mono font-bold text-amber-300">{doc.ref}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${statusBadge[doc.status]}`}>
                      {statusLabel[doc.status]}
                    </span>
                  </div>
                  <div className="text-sm font-bold text-white truncate">{doc.name}</div>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {doc.tags.map((tag, i) => (
                      <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Meta & Actions */}
              <div className="flex items-center gap-2 shrink-0">
                <div className="text-right mr-2">
                  <div className="text-xs text-slate-500 font-mono">{doc.size}</div>
                  <div className="text-[11px] text-slate-500">{doc.date}</div>
                </div>
                <button
                  onClick={() => toast.success(`Prévisualisation de ${doc.name}`)}
                  className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
                  title="Prévisualiser"
                >
                  <Eye className="w-4 h-4" />
                </button>
                <button
                  onClick={() => toast.success(`Téléchargement de ${doc.name} démarré`)}
                  className="p-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-xl border border-amber-500/30 transition-colors"
                  title="Télécharger"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-16 text-slate-500">
            <File className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm font-medium">Aucun document trouvé pour cette recherche</p>
          </div>
        )}
      </div>
    </div>
  );
}

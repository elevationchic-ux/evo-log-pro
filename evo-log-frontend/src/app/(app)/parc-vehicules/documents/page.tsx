'use client';

import React, { useState, useEffect } from 'react';
import { 
  FolderArchive, 
  FileText, 
  Upload, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Trash2, 
  Plus, 
  CheckCircle2, 
  AlertCircle,
  Truck,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

interface FleetDocument {
  id: string;
  immatriculation: string;
  titre: string;
  categorie: 'CARTE_GRISE' | 'ASSURANCE' | 'VISITE_TECHNIQUE' | 'ADR_MATIERES_DANGEREUSES' | 'HOMOLOGATION_CHASSIS';
  dateEmission: string;
  dateExpiration: string;
  tailleFichier: string;
  statut: 'VALIDE' | 'A_RENOUVELER';
}

export default function ParcVehiculesDocumentsPage() {
  const [documents, setDocuments] = useState<FleetDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCat, setFilterCat] = useState('ALL');
  const [showUploadModal, setShowUploadModal] = useState(false);

  const [form, setForm] = useState({
    immatriculation: '',
    titre: '',
    categorie: 'CARTE_GRISE',
    dateEmission: new Date().toISOString().split('T')[0],
    dateExpiration: '',
    fichierNom: ''
  });

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.immatriculation || !form.titre) {
      toast.error('Veuillez renseigner l\'immatriculation et l\'intitulé du document.');
      return;
    }

    const created: FleetDocument = {
      id: Date.now().toString(),
      immatriculation: form.immatriculation.toUpperCase(),
      titre: form.titre,
      categorie: form.categorie as any,
      dateEmission: form.dateEmission,
      dateExpiration: form.dateExpiration || '2026-12-31',
      tailleFichier: '1.8 MB (PDF)',
      statut: 'VALIDE'
    };

    setDocuments([created, ...documents]);
    setShowUploadModal(false);
    setForm({
      immatriculation: '',
      titre: '',
      categorie: 'CARTE_GRISE',
      dateEmission: new Date().toISOString().split('T')[0],
      dateExpiration: '',
      fichierNom: ''
    });
    toast.success(`Document « ${created.titre} » numérisé et classé dans le dossier de ${created.immatriculation}.`);
  };

  const filteredDocs = documents.filter(d => {
    const matchesSearch = 
      d.immatriculation.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.titre.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = filterCat === 'ALL' || d.categorie === filterCat;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <FolderArchive className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">GED Flotte & Classeur Numérique des Véhicules</h1>
            <p className="text-sm text-on-surface-variant">
              Centralisation dématérialisée des pièces administratives, polices d'assurance et certificats ADR
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
          >
            <Upload className="w-4 h-4" />
            Numériser un Document
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par immatriculation ou nom du document..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline text-xs rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={filterCat}
            onChange={(e) => setFilterCat(e.target.value)}
            className="bg-surface-container-low border border-outline text-xs rounded-xl px-3 py-2 text-on-surface focus:outline-none focus:border-primary"
          >
            <option value="ALL">Toutes les catégories de pièces</option>
            <option value="CARTE_GRISE">Cartes Grises Numérisées</option>
            <option value="ASSURANCE">Polices d'Assurance CEMAC</option>
            <option value="VISITE_TECHNIQUE">Certificats de Visite Technique</option>
            <option value="ADR_MATIERES_DANGEREUSES">Conformité ADR Hydrocarbures</option>
            <option value="HOMOLOGATION_CHASSIS">Homologations Constructeur</option>
          </select>
        </div>
      </div>

      {/* Document Grid / Clean Slate State */}
      {filteredDocs.length === 0 ? (
        <div className="bg-surface border border-outline rounded-2xl p-12 text-center shadow-sm">
          <FolderArchive className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
          <h3 className="font-semibold text-on-surface text-base">Le classeur numérique de flotte est vide</h3>
          <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
            Archivez ici les scans haute fidélité des cartes grises, attestations d'assurance et certificats de contrôle technique pour vos audits de conformité routière.
          </p>
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95"
          >
            + Téléverser le Premier Document
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocs.map(doc => (
            <div
              key={doc.id}
              className="bg-surface border border-outline rounded-2xl p-5 hover:border-primary transition-all shadow-sm space-y-3"
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 bg-primary/10 rounded-xl text-primary">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-on-surface">{doc.titre}</h3>
                    <span className="font-mono text-xs font-semibold text-primary">{doc.immatriculation}</span>
                  </div>
                </div>
                <span className="text-[10px] font-mono text-on-surface-variant bg-surface-container px-2 py-0.5 rounded">
                  {doc.tailleFichier}
                </span>
              </div>

              <div className="space-y-1 text-xs text-on-surface-variant">
                <div className="flex justify-between">
                  <span>Catégorie :</span>
                  <span className="font-semibold text-on-surface">{doc.categorie}</span>
                </div>
                <div className="flex justify-between">
                  <span>Date d'émission :</span>
                  <span className="text-on-surface">{doc.dateEmission}</span>
                </div>
                <div className="flex justify-between">
                  <span>Échéance :</span>
                  <span className="font-bold text-primary">{doc.dateExpiration}</span>
                </div>
              </div>

              <div className="pt-2 border-t border-outline/50 flex justify-between items-center">
                <button
                  onClick={() => toast.success(`Ouverture du document ${doc.titre} en haute résolution...`)}
                  className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                >
                  <Eye className="w-3.5 h-3.5" /> Voir
                </button>
                <button
                  onClick={() => toast.success(`Téléchargement de ${doc.titre}`)}
                  className="p-1.5 hover:bg-surface-container rounded-lg text-on-surface-variant hover:text-on-surface"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <h3 className="font-bold text-on-surface text-base">Numériser une Pièce Administrative</h3>
              <button onClick={() => setShowUploadModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Immatriculation du Véhicule * :</label>
                <input
                  type="text"
                  placeholder="Ex: LT-TR-4589"
                  value={form.immatriculation}
                  onChange={(e) => setForm({ ...form, immatriculation: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono uppercase focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Intitulé du Document * :</label>
                <input
                  type="text"
                  placeholder="Ex: Carte Grise Originale / Police AXA 2025"
                  value={form.titre}
                  onChange={(e) => setForm({ ...form, titre: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Catégorie :</label>
                <select
                  value={form.categorie}
                  onChange={(e) => setForm({ ...form, categorie: e.target.value })}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="CARTE_GRISE">Carte Grise</option>
                  <option value="ASSURANCE">Assurance CEMAC</option>
                  <option value="VISITE_TECHNIQUE">Visite Technique</option>
                  <option value="ADR_MATIERES_DANGEREUSES">Certificat ADR</option>
                  <option value="HOMOLOGATION_CHASSIS">Homologation Constructeur</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Date d'Émission :</label>
                  <input
                    type="date"
                    value={form.dateEmission}
                    onChange={(e) => setForm({ ...form, dateEmission: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Date d'Expiration :</label>
                  <input
                    type="date"
                    value={form.dateExpiration}
                    onChange={(e) => setForm({ ...form, dateExpiration: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="p-4 border border-dashed border-outline rounded-xl text-center">
                <Upload className="w-8 h-8 text-on-surface-variant/50 mx-auto mb-1" />
                <span className="text-[11px] text-on-surface-variant block">Sélectionnez le fichier PDF ou JPEG numérisé</span>
                <input
                  type="file"
                  onChange={(e) => setForm({ ...form, fichierNom: e.target.files?.[0]?.name || '' })}
                  className="mt-2 text-[10px] text-on-surface-variant"
                />
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 border border-outline rounded-xl text-on-surface hover:bg-surface-container font-semibold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90"
                >
                  Classer le Document
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

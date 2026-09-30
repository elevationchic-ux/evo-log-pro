'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  FolderArchive,
  FileText,
  Upload,
  Search,
  ExternalLink,
  Plus,
  Loader2,
  Truck,
} from 'lucide-react';
import { toast } from 'sonner';
import { fleetAPI } from '@/lib/api-client';

interface FleetDocument {
  id: number;
  vehicule_id?: number | null;
  type_document?: string | null;
  nom_fichier?: string | null;
  url?: string | null;
  date_expiration?: string | null;
  statut?: string | null;
  created_at?: string | null;
}

interface Vehicule {
  id: number;
  immatriculation: string;
  marque?: string | null;
}

const CATEGORIES: Record<string, string> = {
  CARTE_GRISE: 'Carte Grise',
  ASSURANCE: "Assurance CEMAC",
  VISITE_TECHNIQUE: 'Visite Technique',
  ADR_MATIERES_DANGEREUSES: 'Certificat ADR',
  HOMOLOGATION_CHASSIS: 'Homologation Constructeur',
};

const fmtDate = (iso?: string | null) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? String(iso) : d.toLocaleDateString('fr-FR');
};

// Statut derive HONNETEMENT de la seule date persistee : aucune valeur n'est
// inventee quand la piece n'a pas d'echeance enregistree.
const statutDocument = (dateExp?: string | null) => {
  if (!dateExp) return { label: 'Sans échéance enregistrée', cls: 'text-on-surface-variant' };
  const d = new Date(dateExp);
  if (Number.isNaN(d.getTime())) return { label: '', cls: 'text-on-surface-variant' };
  const jours = Math.ceil((d.getTime() - Date.now()) / 86_400_000);
  if (jours < 0) return { label: 'Expiré', cls: 'text-red-400 font-bold' };
  if (jours <= 60) return { label: 'À renouveler', cls: 'text-amber-400 font-bold' };
  return { label: 'Valide', cls: 'text-emerald-400 font-bold' };
};

const emptyForm = () => ({
  vehiculeId: '',
  categorie: 'CARTE_GRISE',
  dateExpiration: '',
});

export default function ParcVehiculesDocumentsPage() {
  const [documents, setDocuments] = useState<FleetDocument[]>([]);
  const [vehicules, setVehicules] = useState<Vehicule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCat, setFilterCat] = useState('ALL');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [fichier, setFichier] = useState<File | null>(null);

  const [form, setForm] = useState(emptyForm());

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [docsRes, vehsRes] = await Promise.all([
        fleetAPI.getDocuments(),
        fleetAPI.getVehicles({ limit: 500 }),
      ]);
      const docsBody = docsRes.data ?? docsRes;
      const vehsBody = vehsRes.data ?? vehsRes;
      setDocuments(Array.isArray(docsBody?.items) ? docsBody.items : []);
      setVehicules(Array.isArray(vehsBody?.items) ? vehsBody.items : []);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Impossible de charger le classeur numérique.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const immatParId = useCallback(
    (id?: number | null) => {
      if (id == null) return 'Véhicule non lié';
      return vehicules.find(v => v.id === id)?.immatriculation || `#${id}`;
    },
    [vehicules],
  );

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.vehiculeId) {
      toast.error('Sélectionnez un véhicule du parc.');
      return;
    }
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('vehicule_id', String(form.vehiculeId));
      fd.append('type_document', form.categorie);
      if (form.dateExpiration) fd.append('date_expiration', new Date(form.dateExpiration).toISOString());
      if (fichier) fd.append('file', fichier);
      await fleetAPI.uploadDocument(fd);
      setShowUploadModal(false);
      setForm(emptyForm());
      setFichier(null);
      toast.success('Pièce enregistrée dans le dossier du véhicule.');
      await load();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : "Échec de l'enregistrement de la pièce.");
    } finally {
      setUploading(false);
    }
  };

  const filteredDocs = documents.filter(d => {
    const q = searchTerm.toLowerCase();
    const matchesSearch =
      immatParId(d.vehicule_id).toLowerCase().includes(q) ||
      String(d.nom_fichier || '').toLowerCase().includes(q) ||
      String(CATEGORIES[d.type_document || ''] || d.type_document || '').toLowerCase().includes(q);
    const matchesCat = filterCat === 'ALL' || d.type_document === filterCat;
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
            Enregistrer une Pièce
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par immatriculation ou document..."
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
            {Object.entries(CATEGORIES).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="bg-surface border border-outline rounded-2xl p-12 text-center text-on-surface-variant flex items-center justify-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-primary" /> Chargement du classeur numérique…
        </div>
      ) : error ? (
        <div className="bg-surface border border-outline rounded-2xl p-12 text-center">
          <h3 className="font-semibold text-on-surface text-base">Données indisponibles</h3>
          <p className="text-xs text-on-surface-variant mt-1">{error}</p>
          <button onClick={load} className="mt-4 px-4 py-2 rounded-xl bg-primary text-on-primary text-xs font-bold hover:opacity-95 cursor-pointer">
            Réessayer
          </button>
        </div>
      ) : filteredDocs.length === 0 ? (
        <div className="bg-surface border border-outline rounded-2xl p-12 text-center shadow-sm">
          <FolderArchive className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
          <h3 className="font-semibold text-on-surface text-base">Le classeur numérique de flotte est vide</h3>
          <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
            Archivez ici les pièces administratives (cartes grises, attestations d'assurance, contrôles techniques) pour vos audits de conformité routière.
          </p>
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95 inline-flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" /> Enregistrer la première pièce
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocs.map(doc => {
            const statut = statutDocument(doc.date_expiration);
            const libelle = CATEGORIES[doc.type_document || ''] || doc.type_document || 'Pièce';
            return (
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
                      <h3 className="font-bold text-sm text-on-surface">{libelle}</h3>
                      <span className="font-mono text-xs font-semibold text-primary inline-flex items-center gap-1">
                        <Truck className="w-3 h-3" /> {immatParId(doc.vehicule_id)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-1 text-xs text-on-surface-variant">
                  <div className="flex justify-between">
                    <span>Fichier :</span>
                    <span className="text-on-surface truncate max-w-[60%]" title={doc.nom_fichier || ''}>
                      {doc.nom_fichier || 'Nom non enregistré'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Échéance :</span>
                    <span className="text-on-surface">{fmtDate(doc.date_expiration)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Statut :</span>
                    <span className={statut.cls}>{statut.label}</span>
                  </div>
                </div>

                {doc.url ? (
                  <div className="pt-2 border-t border-outline/50">
                    <a
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1"
                    >
                      <ExternalLink className="w-3.5 h-3.5" /> Ouvrir le document
                    </a>
                  </div>
                ) : (
                  <p className="pt-2 border-t border-outline/50 text-[11px] text-on-surface-variant/70">
                    Métadonnée enregistrée  binaire stocké dans la GED dédiée.
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <h3 className="font-bold text-on-surface text-base">Enregistrer une Pièce Administrative</h3>
              <button onClick={() => setShowUploadModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Véhicule du parc * :</label>
                <select
                  value={form.vehiculeId}
                  onChange={(e) => setForm({ ...form, vehiculeId: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                >
                  <option value=""> Sélectionner un véhicule </option>
                  {vehicules.map(v => (
                    <option key={v.id} value={v.id}>{v.immatriculation}{v.marque ? `  ${v.marque}` : ''}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Catégorie de pièce :</label>
                <select
                  value={form.categorie}
                  onChange={(e) => setForm({ ...form, categorie: e.target.value })}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                >
                  {Object.entries(CATEGORIES).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Date d'expiration :</label>
                <input
                  type="date"
                  value={form.dateExpiration}
                  onChange={(e) => setForm({ ...form, dateExpiration: e.target.value })}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div className="p-4 border border-dashed border-outline rounded-xl text-center">
                <Upload className="w-8 h-8 text-on-surface-variant/50 mx-auto mb-1" />
                <span className="text-[11px] text-on-surface-variant block">
                  {fichier ? fichier.name : 'Sélectionnez le fichier PDF ou JPEG numérisé'}
                </span>
                <input
                  type="file"
                  onChange={(e) => setFichier(e.target.files?.[0] || null)}
                  className="mt-2 text-[11px] text-on-surface-variant"
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
                  disabled={uploading}
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90 disabled:opacity-60 inline-flex items-center gap-1.5"
                >
                  {uploading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {uploading ? 'Enregistrement…' : 'Enregistrer la pièce'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

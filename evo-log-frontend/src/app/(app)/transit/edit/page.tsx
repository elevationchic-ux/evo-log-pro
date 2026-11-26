'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  FileText,
  ArrowLeft,
  Save,
  Package,
  ShieldCheck,
  Building,
  Anchor
} from 'lucide-react';
import { transitAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function TransitEditPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const [loading, setLoading] = useState(!!id);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    numero_dossier: '',
    numero_dum: '',
    regime: 'IM4 - Importation Directe',
    bureau_douane: 'Douala Port (CMDL1)',
    client_nom: '',
    navire: '',
    port_chargement: '',
    designation: '',
    poids_brut: '',
    nb_conteneurs: 1,
    position_sh: '',
    valeur_fob: '',
    droits_taxes: '',
    instructions: ''
  });

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    transitAPI.getTransit(Number(id))
      .then((res) => {
        const d = res.data;
        if (d) {
          setFormData({
            numero_dossier: d.numero_dossier || '',
            numero_dum: d.numero_dum || d.reference || '',
            regime: d.regime || 'IM4 - Importation Directe',
            bureau_douane: d.bureau_douane || 'Douala Port (CMDL1)',
            client_nom: d.client_nom || '',
            navire: d.navire || '',
            port_chargement: d.port_chargement || '',
            designation: d.designation || '',
            poids_brut: d.poids_brut ? String(d.poids_brut) : '',
            nb_conteneurs: d.nb_conteneurs || 1,
            position_sh: d.position_sh || '',
            valeur_fob: d.valeur_fob ? String(d.valeur_fob) : '',
            droits_taxes: d.droits_taxes ? String(d.droits_taxes) : '',
            instructions: d.instructions || ''
          });
        }
      })
      .catch(() => {
        toast.error("Impossible de charger les données du dossier de transit.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (id) {
        await transitAPI.updateTransit(Number(id), formData);
        toast.success("Dossier de transit mis à jour avec succès.");
      } else {
        await transitAPI.createTransit(formData);
        toast.success("Nouveau dossier de transit créé.");
      }
      router.push('/transit');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement du dossier de transit.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 max-w-4xl mx-auto space-y-4 animate-pulse">
        <div className="h-8 bg-surface-container rounded w-1/3" />
        <div className="h-64 bg-surface-container rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
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
              {id ? `Modifier le Dossier Transit #${id}` : 'Créer un Dossier de Transit'}
            </h1>
            <p className="text-sm text-on-surface-variant">
              Déclaration douanière, DUM Camcis / Sydonia, formalités de dédouanement et BAE
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Douane & Références */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-primary" /> Références Douane & Régime
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">N° Dossier Interne *</label>
              <input
                type="text"
                required
                value={formData.numero_dossier}
                onChange={(e) => setFormData({ ...formData, numero_dossier: e.target.value })}
                placeholder="Ex: TR-2025-0042"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">N° DUM (Camcis / Sydonia)</label>
              <input
                type="text"
                value={formData.numero_dum}
                onChange={(e) => setFormData({ ...formData, numero_dum: e.target.value })}
                placeholder="Ex: DUM C1042-2025"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Régime Douanier</label>
              <select
                value={formData.regime}
                onChange={(e) => setFormData({ ...formData, regime: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="IM4 - Importation Directe">IM4 - Mise à la consommation directe</option>
                <option value="TR8 - Transit CEMAC (Tchad/RCA)">TR8 - Transit CEMAC (Tchad / Centrafrique)</option>
                <option value="EX1 - Exportation Définitive">EX1 - Exportation définitive</option>
                <option value="AT5 - Admission Temporaire">AT5 - Admission temporaire</option>
                <option value="ED3 - Entrepôt de Douane">ED3 - Entrepôt sous douane</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Bureau de Dédouanement</label>
              <input
                type="text"
                value={formData.bureau_douane}
                onChange={(e) => setFormData({ ...formData, bureau_douane: e.target.value })}
                placeholder="Ex: Douala Port, Kribi Port, Yaoundé Nsimalen"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        {/* Marchandise & Expédition */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Package className="w-4 h-4 text-primary" /> Marchandise & Déclaration
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Désignation Commerciale *</label>
              <input
                type="text"
                required
                value={formData.designation}
                onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
                placeholder="Ex: Pièces détachées pour engins miniers"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Position SH / Code SH</label>
              <input
                type="text"
                value={formData.position_sh}
                onChange={(e) => setFormData({ ...formData, position_sh: e.target.value })}
                placeholder="Ex: 8474.90.00"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Nombre Conteneurs</label>
              <input
                type="number"
                min={1}
                value={formData.nb_conteneurs}
                onChange={(e) => setFormData({ ...formData, nb_conteneurs: Number(e.target.value) })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Poids Brut (kg)</label>
              <input
                type="text"
                value={formData.poids_brut}
                onChange={(e) => setFormData({ ...formData, poids_brut: e.target.value })}
                placeholder="Ex: 18500"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Valeur FOB (FCFA)</label>
              <input
                type="text"
                value={formData.valeur_fob}
                onChange={(e) => setFormData({ ...formData, valeur_fob: e.target.value })}
                placeholder="Ex: 45000000"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
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
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {submitting ? 'Enregistrement...' : id ? 'Mettre à jour le Dossier' : 'Créer le Dossier Transit'}
          </button>
        </div>
      </form>
    </div>
  );
}

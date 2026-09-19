'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Anchor,
  ArrowLeft,
  Save,
  Ship,
  Layers,
  AlertCircle
} from 'lucide-react';
import { acconageAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function AcconageEditPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const [loading, setLoading] = useState(!!id);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    nom_navire: '',
    armateur: '',
    quai: 'Quai Conteneurs PAD',
    type_operation: 'DECHARGEMENT_CONTENEUR',
    nombre_conteneurs: 1,
    nb_20ft: 0,
    nb_40ft: 0,
    tonnage: '',
    grues: 'Portique STS 01',
    cadence: '20',
    remarques: ''
  });

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    acconageAPI.getAcconage(Number(id))
      .then((res) => {
        const d = res.data;
        if (d) {
          setFormData({
            nom_navire: d.nom_navire || '',
            armateur: d.armateur || '',
            quai: d.quai || 'Quai Conteneurs PAD',
            type_operation: d.type_operation || 'DECHARGEMENT_CONTENEUR',
            nombre_conteneurs: d.nombre_conteneurs || 1,
            nb_20ft: d.nb_20ft || 0,
            nb_40ft: d.nb_40ft || 0,
            tonnage: d.tonnage || '',
            grues: d.grues || 'Portique STS 01',
            cadence: d.cadence || '20',
            remarques: d.remarques || ''
          });
        }
      })
      .catch(() => {
        toast.error("Impossible de charger les données de l'escale.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (id) {
        await acconageAPI.updateAcconage(Number(id), formData);
        toast.success("Opération d'acconage mise à jour avec succès.");
      } else {
        await acconageAPI.createAcconage(formData);
        toast.success("Nouvelle opération d'acconage enregistrée.");
      }
      router.push('/acconage');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement de l'opération.");
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
              <Ship className="w-6 h-6 text-cyan-600" />
              {id ? `Modifier l'Opération Acconage #${id}` : "Nouvelle Opération d'Acconage"}
            </h1>
            <p className="text-sm text-on-surface-variant">
              Planification des mouvements bord/terre, grues et pointage dockers
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Anchor className="w-4 h-4 text-primary" /> Informations du Navire et du Poste
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Nom du Navire *</label>
              <input
                type="text"
                required
                value={formData.nom_navire}
                onChange={(e) => setFormData({ ...formData, nom_navire: e.target.value })}
                placeholder="Ex: MSC TOKYO IV, CMA CGM DAKAR"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Armateur / Ligne Maritime</label>
              <input
                type="text"
                value={formData.armateur}
                onChange={(e) => setFormData({ ...formData, armateur: e.target.value })}
                placeholder="Ex: MSC, Maersk, Grimaldi, CMA-CGM"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Poste à Quai</label>
              <input
                type="text"
                value={formData.quai}
                onChange={(e) => setFormData({ ...formData, quai: e.target.value })}
                placeholder="Ex: Quai Conteneurs PAD n°14"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Type d'Opération</label>
              <select
                value={formData.type_operation}
                onChange={(e) => setFormData({ ...formData, type_operation: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="DECHARGEMENT_CONTENEUR">Déchargement Conteneurs (Import)</option>
                <option value="CHARGEMENT_CONTENEUR">Chargement Conteneurs (Export)</option>
                <option value="TRANSPORDEMENT">Transbordement Quai à Quai</option>
                <option value="VRAC_CONVENTIONNEL">Vrac & Marchandises Conventionnelles</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-600" /> Volumes & Moyens Portiques
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Total EVP / TEU *</label>
              <input
                type="number"
                required
                min={1}
                value={formData.nombre_conteneurs}
                onChange={(e) => setFormData({ ...formData, nombre_conteneurs: Number(e.target.value) })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Conteneurs 20ft</label>
              <input
                type="number"
                min={0}
                value={formData.nb_20ft}
                onChange={(e) => setFormData({ ...formData, nb_20ft: Number(e.target.value) })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Conteneurs 40ft</label>
              <input
                type="number"
                min={0}
                value={formData.nb_40ft}
                onChange={(e) => setFormData({ ...formData, nb_40ft: Number(e.target.value) })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Grues & Portiques Affectés</label>
              <input
                type="text"
                value={formData.grues}
                onChange={(e) => setFormData({ ...formData, grues: e.target.value })}
                placeholder="Ex: STS 01 + Grue Mobile Gottwald"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Cadence Cible (mvts/heure)</label>
              <input
                type="number"
                value={formData.cadence}
                onChange={(e) => setFormData({ ...formData, cadence: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Tonnage Estimé (Tonnes)</label>
              <input
                type="text"
                value={formData.tonnage}
                onChange={(e) => setFormData({ ...formData, tonnage: e.target.value })}
                placeholder="Ex: 450"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Instructions Manutention & Remarques</label>
            <textarea
              rows={3}
              value={formData.remarques}
              onChange={(e) => setFormData({ ...formData, remarques: e.target.value })}
              placeholder="Spécifications particulières (matières dangereuses IMDG, reefer branchés quai...)"
              className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
            />
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
            {submitting ? 'Enregistrement...' : id ? 'Mettre à jour l\'Escale' : 'Créer l\'Opération d\'Acconage'}
          </button>
        </div>
      </form>
    </div>
  );
}

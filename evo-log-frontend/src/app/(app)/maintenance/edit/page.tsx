'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Wrench,
  ArrowLeft,
  Save,
  Truck,
  Layers,
  AlertTriangle
} from 'lucide-react';
import { maintenanceAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function MaintenanceEditPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const [loading, setLoading] = useState(!!id);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    immatriculation_camion: '',
    type_maintenance: 'CURATIVE',
    priorite: 'NORMALE',
    description: '',
    pieces: '',
    kilometrage: '',
    statut: 'EN_COURS'
  });

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    maintenanceAPI.getMaintenance(Number(id))
      .then((res) => {
        const d = res.data;
        if (d) {
          setFormData({
            immatriculation_camion: d.immatriculation_camion || d.vehicule_immatriculation || '',
            type_maintenance: d.type_maintenance || 'CURATIVE',
            priorite: d.priorite || 'NORMALE',
            description: d.description || '',
            pieces: d.pieces || '',
            kilometrage: d.kilometrage ? String(d.kilometrage) : '',
            statut: d.statut || 'EN_COURS'
          });
        }
      })
      .catch(() => {
        toast.error("Impossible de charger l'ordre de travail.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (id) {
        await maintenanceAPI.updateMaintenance(Number(id), formData);
        toast.success("Ordre de travail GMAO mis à jour avec succès.");
      } else {
        await maintenanceAPI.createMaintenance(formData);
        toast.success("Nouvel ordre de travail atelier créé.");
      }
      router.push('/maintenance');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement de l'ordre GMAO.");
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
              <Wrench className="w-6 h-6 text-amber-600" />
              {id ? `Modifier l'Ordre de Travail #${id}` : 'Créer un Ordre de Travail GMAO'}
            </h1>
            <p className="text-sm text-on-surface-variant">
              Planification des réparations, révisions périodiques et immobilisations atelier
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Truck className="w-4 h-4 text-primary" /> Véhicule & Diagnostic d'Entrée
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Immatriculation Véhicule *</label>
              <input
                type="text"
                required
                value={formData.immatriculation_camion}
                onChange={(e) => setFormData({ ...formData, immatriculation_camion: e.target.value })}
                placeholder="Ex: LT-809-BA, RC-1234-A"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Type de Maintenance</label>
              <select
                value={formData.type_maintenance}
                onChange={(e) => setFormData({ ...formData, type_maintenance: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="PREVENTIVE">Maintenance Préventive (Vidange, Freins, Filtres)</option>
                <option value="CURATIVE">Maintenance Curative (Panne, Réparation d'urgence)</option>
                <option value="VISITE_TECHNIQUE">Préparation Visite Technique & Antipollution</option>
                <option value="PNEUMATIQUE">Remplacement / Permutation Pneumatiques</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Priorité d'Intervention</label>
              <select
                value={formData.priorite}
                onChange={(e) => setFormData({ ...formData, priorite: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="BASSE">Basse (Entretien de routine)</option>
                <option value="NORMALE">Normale (Planifié semaine en cours)</option>
                <option value="URGENTE">Urgente (Camion immobilisé en ligne)</option>
                <option value="CRITIQUE">Critique (Sécurité / Risque majeur)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Statut Atelier</label>
              <select
                value={formData.statut}
                onChange={(e) => setFormData({ ...formData, statut: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="EN_ATTENTE">En attente de prise en charge</option>
                <option value="EN_COURS">En cours d'intervention</option>
                <option value="ATTENTE_PIECES">En attente de pièces détachées</option>
                <option value="TERMINE">Travaux terminés & validés</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Kilométrage Actuel Compteur</label>
              <input
                type="number"
                value={formData.kilometrage}
                onChange={(e) => setFormData({ ...formData, kilometrage: e.target.value })}
                placeholder="Ex: 145200"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Description de la Panne / Travaux Demandés *</label>
            <textarea
              rows={3}
              required
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Ex: Fuite d'huile carter inférieur, bruit anormal pont arrière..."
              className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Pièces Rechange Magasin Imputées</label>
            <input
              type="text"
              value={formData.pieces}
              onChange={(e) => setFormData({ ...formData, pieces: e.target.value })}
              placeholder="Ex: Filtre à gazole Bosch, Jeu plaquettes avant..."
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
            {submitting ? 'Enregistrement...' : id ? 'Mettre à jour l\'OT' : 'Créer l\'Ordre de Travail'}
          </button>
        </div>
      </form>
    </div>
  );
}

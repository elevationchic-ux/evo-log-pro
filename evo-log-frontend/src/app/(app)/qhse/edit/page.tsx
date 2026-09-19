'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  ShieldCheck,
  ArrowLeft,
  Save,
  MapPin,
  FileText,
  AlertTriangle
} from 'lucide-react';
import { qhseAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function QhseEditPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');

  const [loading, setLoading] = useState(!!id);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    site_location: '',
    niveau_risque: 'FAIBLE',
    type_controle: 'INSPECTION_ROUTINE',
    conformite_epi: true,
    inspecteur: '',
    observations: '',
    actions_correctives: ''
  });

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    qhseAPI.getQhseRecord(Number(id))
      .then((res) => {
        const d = res.data;
        if (d) {
          setFormData({
            site_location: d.site_location || '',
            niveau_risque: d.niveau_risque || 'FAIBLE',
            type_controle: d.type_controle || 'INSPECTION_ROUTINE',
            conformite_epi: d.conformite_epi ?? true,
            inspecteur: d.inspecteur || '',
            observations: d.observations || '',
            actions_correctives: d.actions_correctives || ''
          });
        }
      })
      .catch(() => {
        toast.error("Impossible de charger le rapport QHSE.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (id) {
        await qhseAPI.updateQhseRecord(Number(id), formData);
        toast.success("Rapport QHSE mis à jour avec succès.");
      } else {
        await qhseAPI.createQhseRecord(formData);
        toast.success("Nouveau rapport QHSE enregistré.");
      }
      router.push('/qhse');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement QHSE.");
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
              <ShieldCheck className="w-6 h-6 text-emerald-600" />
              {id ? `Modifier le Rapport QHSE #${id}` : 'Nouveau Rapport d\'Inspection QHSE'}
            </h1>
            <p className="text-sm text-on-surface-variant">
              Contrôle qualité, hygiène, sécurité au travail et respect des normes environnementales
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-primary" /> Périmètre & Caractéristiques de l'Inspection
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Site / Emplacement *</label>
              <input
                type="text"
                required
                value={formData.site_location}
                onChange={(e) => setFormData({ ...formData, site_location: e.target.value })}
                placeholder="Ex: Dépôt Douala Youpwé, Terminal Conteneurs Kribi"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Niveau de Risque Identifié</label>
              <select
                value={formData.niveau_risque}
                onChange={(e) => setFormData({ ...formData, niveau_risque: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="FAIBLE">Faible (Aucun danger immédiat)</option>
                <option value="MOYEN">Moyen (Point de vigilance à traiter)</option>
                <option value="ELEVE">Élevé (Arrêt partiel ou intervention requise)</option>
                <option value="CRITIQUE">Critique (Danger imminent pour le personnel)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Type de Contrôle</label>
              <select
                value={formData.type_controle}
                onChange={(e) => setFormData({ ...formData, type_controle: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="INSPECTION_ROUTINE">Inspection de Routine Quotidienne / Hebdo</option>
                <option value="CONTROLE_EPI">Audit Spécifique Dotation & Port des EPI</option>
                <option value="INCIDENT_MATERIEL">Enquête suite à Incident Matériel / Accident</option>
                <option value="AUDIT_CERTIFICATION">Audit Norme ISO 14001 / ISO 45001</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Nom de l'Inspecteur / Auditeur</label>
              <input
                type="text"
                value={formData.inspecteur}
                onChange={(e) => setFormData({ ...formData, inspecteur: e.target.value })}
                placeholder="Ex: Responsable Sécurité QHSE"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-600" /> Constats & Plan d'Action
          </h2>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Observations & Remarques *</label>
            <textarea
              rows={3}
              required
              value={formData.observations}
              onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
              placeholder="Ex: Tous les chauffeurs portent leurs gilets haute visibilité et chaussures de sécurité..."
              className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Actions Correctives Recommandées</label>
            <textarea
              rows={3}
              value={formData.actions_correctives}
              onChange={(e) => setFormData({ ...formData, actions_correctives: e.target.value })}
              placeholder="Ex: Renouveler les 2 extincteurs CO2 du quai nord avant la fin de semaine..."
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
            {submitting ? 'Enregistrement...' : id ? 'Mettre à jour le Rapport' : 'Enregistrer le Rapport QHSE'}
          </button>
        </div>
      </form>
    </div>
  );
}

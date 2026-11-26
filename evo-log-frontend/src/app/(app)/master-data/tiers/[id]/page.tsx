'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Users,
  ArrowLeft,
  Building,
  FileText,
  DollarSign,
  Phone,
  Mail,
  MapPin,
  Save,
  CheckCircle2,
  AlertTriangle,
  CreditCard
} from 'lucide-react';
import { tiersAPI, financeAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function TiersDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [tier, setTier] = useState<any | null>(null);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    nom: '',
    raison_sociale: '',
    type: 'CLIENT',
    nif: '',
    rccm: '',
    telephone: '',
    email: '',
    adresse: '',
    plafond_credit: '5000000',
    delai_paiement: '30'
  });

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.allSettled([
      tiersAPI.getTiersById(Number(id)),
      financeAPI.getFactures({ tiers_id: Number(id) })
    ]).then(([tierRes, invRes]) => {
      if (tierRes.status === 'fulfilled') {
        const d = tierRes.value.data;
        setTier(d);
        setFormData({
          nom: d.nom || d.raison_sociale || '',
          raison_sociale: d.raison_sociale || d.nom || '',
          type: d.type || 'CLIENT',
          nif: d.nif || '',
          rccm: d.rccm || '',
          telephone: d.telephone || '',
          email: d.email || '',
          adresse: d.adresse || '',
          plafond_credit: d.plafond_credit ? String(d.plafond_credit) : '5000000',
          delai_paiement: d.delai_paiement ? String(d.delai_paiement) : '30'
        });
      } else {
        setError('Tiers introuvable ou erreur de chargement.');
      }

      if (invRes.status === 'fulfilled') {
        const raw = invRes.value.data?.items || invRes.value.data || [];
        setInvoices(Array.isArray(raw) ? raw : []);
      }
    }).finally(() => setLoading(false));
  }, [id]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await tiersAPI.updateTiers(Number(id), formData);
      toast.success('Fiche tiers mise à jour avec succès.');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur lors de la mise à jour du tiers.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 max-w-5xl mx-auto space-y-4 animate-pulse">
        <div className="h-8 bg-surface-container rounded w-1/3" />
        <div className="h-64 bg-surface-container rounded-2xl" />
      </div>
    );
  }

  if (error || !tier) {
    return (
      <div className="p-8 max-w-lg mx-auto text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold">Fiche Tiers Introuvable</h2>
        <p className="text-sm text-on-surface-variant">{error || "Ce compte de tiers n'existe pas."}</p>
        <button
          onClick={() => router.push('/master-data')}
          className="px-4 py-2 bg-primary text-on-primary rounded-xl text-xs font-semibold"
        >
          Retour au Master Data
        </button>
      </div>
    );
  }

  const totalFacture = invoices.reduce((s, i) => s + Number(i.montant_ttc || i.montant || 0), 0);

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-on-surface flex items-center gap-2">
              <Building className="w-6 h-6 text-primary" />
              {tier.nom || tier.raison_sociale || `Tiers #${id}`}
            </h1>
            <p className="text-sm text-on-surface-variant">
              Type : {tier.type || 'Compte B2B'} • NIF : {tier.nif || 'Non communiqué'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonne de gauche: Formulaire */}
        <form onSubmit={handleSave} className="lg:col-span-2 space-y-6">
          <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
            <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
              <Building className="w-4 h-4 text-primary" /> Identité & Informations Légales
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Raison Sociale / Nom *</label>
                <input
                  type="text"
                  required
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Catégorie Tiers</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="CLIENT">Client Chargeur</option>
                  <option value="FOURNISSEUR">Fournisseur / Sous-traitant</option>
                  <option value="TRANSPORTEUR">Transporteur Partenaire</option>
                  <option value="TRANSITAIRE">Transitaire Confrère</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Numéro NIF</label>
                <input
                  type="text"
                  value={formData.nif}
                  onChange={(e) => setFormData({ ...formData, nif: e.target.value })}
                  placeholder="Ex: M051200023456P"
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">RCCM</label>
                <input
                  type="text"
                  value={formData.rccm}
                  onChange={(e) => setFormData({ ...formData, rccm: e.target.value })}
                  placeholder="Ex: RC/DLA/2021/B/145"
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Téléphone</label>
                <input
                  type="text"
                  value={formData.telephone}
                  onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Email Professionnel</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Adresse Siège Social</label>
                <input
                  type="text"
                  value={formData.adresse}
                  onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
                  placeholder="Ex: Boulevard de la Liberté, Akwa - Douala"
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            </div>
          </div>

          <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
            <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-primary" /> Conditions Commerciales & Plafond Crédit
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Plafond Crédit Autorisé (FCFA)</label>
                <input
                  type="number"
                  value={formData.plafond_credit}
                  onChange={(e) => setFormData({ ...formData, plafond_credit: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Délai de Paiement Accordé (Jours)</label>
                <input
                  type="number"
                  value={formData.delai_paiement}
                  onChange={(e) => setFormData({ ...formData, delai_paiement: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Enregistrement...' : 'Enregistrer les Modifications'}
            </button>
          </div>
        </form>

        {/* Colonne de droite: Factures et Encours */}
        <div className="space-y-6">
          <div className="bg-surface border border-outline rounded-2xl p-5 space-y-3">
            <h3 className="font-bold text-sm text-on-surface flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-emerald-600" /> Synthèse Financière
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-outline/30">
                <span className="text-on-surface-variant">Total Facturé :</span>
                <span className="font-bold text-on-surface font-mono">{totalFacture.toLocaleString('fr-FR')} FCFA</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-outline/30">
                <span className="text-on-surface-variant">Plafond Risque :</span>
                <span className="font-bold text-on-surface font-mono">{Number(formData.plafond_credit).toLocaleString('fr-FR')} FCFA</span>
              </div>
            </div>
          </div>

          <div className="bg-surface border border-outline rounded-2xl p-5 space-y-3">
            <h3 className="font-bold text-sm text-on-surface flex items-center gap-2">
              <FileText className="w-4 h-4 text-primary" /> Factures Associées
            </h3>
            <div className="space-y-2">
              {invoices.length === 0 ? (
                <p className="text-xs text-on-surface-variant text-center py-4">
                  Aucune facture rattachée à ce tiers.
                </p>
              ) : (
                invoices.slice(0, 5).map((inv, idx) => (
                  <div key={inv.id || idx} className="p-2.5 bg-surface-container-low rounded-xl text-xs space-y-1">
                    <div className="flex justify-between font-bold text-on-surface">
                      <span>{inv.numero_facture || `FAC-${inv.id}`}</span>
                      <span className="font-mono text-primary">{Number(inv.montant_ttc || inv.montant || 0).toLocaleString('fr-FR')} FCFA</span>
                    </div>
                    <div className="flex justify-between text-[11px] text-on-surface-variant">
                      <span>{inv.date_emission || 'Date courante'}</span>
                      <span className="font-semibold text-emerald-600">{inv.statut || 'VALIDÉE'}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

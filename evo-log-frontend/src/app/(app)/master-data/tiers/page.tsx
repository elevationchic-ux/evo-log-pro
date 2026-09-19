'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { tiersAPI, financeAPI } from '@/lib/api-client'
import type { Tier } from '@/types/master-data'
import GenericDataPage from '@/components/ui/GenericDataPage'
import { Building2, Users, Briefcase, CreditCard, X, AlertCircle, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'
import { CardSkeletonLoader } from '@/components/ui/Loaders'

// ── Validation Schema (Zod) ───────────────────────────────────────────────────
const tierSchema = z.object({
  raison_sociale: z.string().min(2, "La raison sociale est requise"),
  sigle_ou_enseigne: z.string().optional(),
  type: z.enum(['client', 'supplier', 'partner']),
  niu: z.string().min(1, "Le NIU est requis"),
  rccm: z.string().optional(),
  registre_commerce: z.string().optional(),
  regime_fiscal: z.string().optional(),
  email: z.string().email("Email invalide").optional().or(z.literal('')),
  telephone: z.string().optional(),
  adresse_physique: z.string().optional(),
  ville: z.string().optional(),
  pays: z.string().optional(),
  autorise_acconage: z.boolean().default(false),
  autorise_transit: z.boolean().default(false),
  autorise_parc_stockage: z.boolean().default(false),
  autorise_manutention: z.boolean().default(false),
  autorise_transport: z.boolean().default(false),
  compte_collectif_syscohada: z.string().optional(),
  limite_credit_maximum: z.coerce.number().min(0).default(0),
  delai_paiement_jours: z.coerce.number().min(0).default(30),
  statut: z.string().optional().default('ACTIF')
})

type TierFormValues = z.infer<typeof tierSchema>

// ── KPI Card component ─────────────────────────────────────────────────────────
function KpiCard({ label, value, icon, color }: { label: string; value: string | number; icon: React.ReactNode; color: string }) {
  return (
    <div className={`bg-white rounded-2xl border border-gray-100 shadow-sm p-5 relative overflow-hidden group hover:shadow-md transition-all`}>
      <div className={`absolute right-0 top-0 w-20 h-20 ${color} rounded-bl-full -z-0 opacity-50 transition-transform group-hover:scale-110`} />
      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-3">
          {icon}
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">{label}</span>
        </div>
        <p className="text-2xl font-black text-gray-900">{value}</p>
      </div>
    </div>
  )
}

// ── Modal de création ───────────────────────────────────────────────────────────
function CreateTierModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const queryClient = useQueryClient()
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(tierSchema),
    defaultValues: {
      type: 'client',
      regime_fiscal: 'Réel - Grandes Entreprises',
      ville: 'Douala',
      pays: 'Cameroun',
      compte_collectif_syscohada: '411100',
      limite_credit_maximum: 0,
      delai_paiement_jours: 30,
      autorise_acconage: false,
      autorise_transit: false,
      autorise_parc_stockage: false,
      autorise_manutention: false,
      autorise_transport: false,
      statut: 'ACTIF'
    }
  })

  const mutation = useMutation({
    mutationFn: (data: any) => tiersAPI.createTiers(data),
    onSuccess: () => {
      toast.success('Tier créé avec succès !')
      queryClient.invalidateQueries({ queryKey: ['tiers'] })
      reset()
      onClose()
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail)) {
        const messages = detail.map((e: any) => `${e.loc[e.loc.length - 1]}: ${e.msg}`).join(', ');
        toast.error(`Erreur de validation : ${messages}`);
      } else {
        toast.error(detail || 'Erreur lors de la création du tier.');
      }
    }
  })

  const onSubmit = (data: TierFormValues) => {
    const payload = {
      ...data,
      sigle_ou_enseigne: data.sigle_ou_enseigne || null,
      rccm: data.rccm || null,
      registre_commerce: data.registre_commerce || null,
      email: data.email || null,
      telephone: data.telephone || null,
      adresse: data.adresse_physique, // compatibilité
      autorise_magasinage: data.autorise_parc_stockage, // compatibilité
      compte_syscohada: data.compte_collectif_syscohada, // compatibilité
      limite_credit_xaf: data.limite_credit_maximum, // compatibilité
    }
    mutation.mutate(payload)
  }

  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[60] animate-in fade-in duration-200" onClick={onClose} />
      <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg animate-in zoom-in-95 fade-in duration-300 overflow-hidden flex flex-col max-h-[90vh]">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-white shrink-0">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 rounded-xl">
                <Building2 className="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Nouveau Tier</h3>
                <p className="text-sm text-gray-500">Ajouter un partenaire d'affaires</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-xl text-gray-400 hover:text-gray-600 transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit as any)} className="p-6 space-y-4 overflow-y-auto flex-1">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-semibold text-gray-700">Raison Sociale *</label>
                <input
                  type="text"
                  {...register('raison_sociale')}
                  className={`w-full px-4 py-2.5 rounded-xl border ${errors.raison_sociale ? 'border-red-500' : 'border-gray-200'} focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm`}
                  placeholder="Ex: SABC Cameroun"
                />
                {errors.raison_sociale && <p className="text-xs text-red-500">{errors.raison_sociale.message}</p>}
              </div>
              <div className="space-y-1">
                <label className="text-sm font-semibold text-gray-700">Sigle / Enseigne</label>
                <input
                  type="text"
                  {...register('sigle_ou_enseigne')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm"
                  placeholder="Ex: SABC"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-semibold text-gray-700">NIU *</label>
                <input
                  type="text"
                  {...register('niu')}
                  className={`w-full px-4 py-2.5 rounded-xl border ${errors.niu ? 'border-red-500' : 'border-gray-200'} focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm`}
                  placeholder="Obligatoire"
                />
                {errors.niu && <p className="text-xs text-red-500">{errors.niu.message}</p>}
              </div>
              <div className="space-y-1">
                <label className="text-sm font-semibold text-gray-700">RCCM</label>
                <input
                  type="text"
                  {...register('rccm')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm"
                  placeholder="Ex: RC/DLA/..."
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Régime Fiscal</label>
                <input
                  type="text"
                  {...register('regime_fiscal')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Type *</label>
                <select
                  {...register('type')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm bg-white"
                >
                  <option value="client">Client</option>
                  <option value="supplier">Fournisseur</option>
                  <option value="partner">Partenaire</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  {...register('email')}
                  className={`w-full px-4 py-2.5 rounded-xl border ${errors.email ? 'border-red-500' : 'border-gray-200'} focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm`}
                  placeholder="contact@entreprise.cm"
                />
                {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Téléphone</label>
                <input
                  type="tel"
                  {...register('telephone')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-semibold text-gray-700">Adresse Physique</label>
              <textarea
                {...register('adresse_physique')}
                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm h-16"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Ville</label>
                <input
                  type="text"
                  {...register('ville')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Pays</label>
                <input
                  type="text"
                  {...register('pays')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
                />
              </div>
            </div>

            {/* Services Activés */}
            <div className="space-y-2 border-t border-gray-100 pt-4">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block">Services à la Carte</label>
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_acconage')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Acconage
                </label>
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_transit')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Transit (Douane)
                </label>
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_parc_stockage')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Parc & Stockage
                </label>
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_manutention')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Manutention
                </label>
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_transport')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Transport Routier
                </label>
              </div>
            </div>

            {/* Paramètres Financiers */}
            <div className="space-y-4 border-t border-gray-100 pt-4 pb-4">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block">Paramètres SAP FI & Crédit</label>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-500">Compte SYSCOHADA</label>
                  <input
                    type="text"
                    {...register('compte_collectif_syscohada')}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-500">Délai Paiement (Jours)</label>
                  <input
                    type="number"
                    {...register('delai_paiement_jours')}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm"
                  />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-500">Limite de Crédit Max (FCFA)</label>
                <input
                  type="number"
                  {...register('limite_credit_maximum')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm font-mono"
                />
              </div>
            </div>

            {/* Footer shrink */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100 sticky bottom-0 bg-white">
              <button
                type="button"
                onClick={onClose}
                className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-emerald-600 to-emerald-700 rounded-xl hover:from-emerald-700 hover:to-emerald-800 transition-all shadow-sm shadow-emerald-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {mutation.isPending ? 'Création...' : 'Créer le Tier'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}

// ── Modal de modification ───────────────────────────────────────────────────────
function EditTierModal({ isOpen, onClose, tier }: { isOpen: boolean; onClose: () => void; tier: any }) {
  const queryClient = useQueryClient()
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(tierSchema),
  })

  // Synchroniser les valeurs lors de l'ouverture du modal
  useEffect(() => {
    if (tier && isOpen) {
      reset({
        raison_sociale: tier.raison_sociale || '',
        sigle_ou_enseigne: tier.sigle_ou_enseigne || '',
        type: tier.type || 'client',
        niu: tier.niu || '',
        rccm: tier.rccm || '',
        registre_commerce: tier.registre_commerce || '',
        regime_fiscal: tier.regime_fiscal || 'Réel - Grandes Entreprises',
        email: tier.email || '',
        telephone: tier.telephone || '',
        adresse_physique: tier.adresse_physique || tier.adresse || '',
        ville: tier.ville || 'Douala',
        pays: tier.pays || 'Cameroun',
        autorise_acconage: !!tier.autorise_acconage,
        autorise_transit: !!tier.autorise_transit,
        autorise_parc_stockage: !!tier.autorise_parc_stockage || !!tier.autorise_magasinage,
        autorise_manutention: !!tier.autorise_manutention,
        autorise_transport: !!tier.autorise_transport,
        compte_collectif_syscohada: tier.compte_collectif_syscohada || '411100',
        limite_credit_maximum: Number(tier.limite_credit_maximum || tier.limite_credit_xaf || 0),
        delai_paiement_jours: Number(tier.delai_paiement_jours || 30),
        statut: tier.statut || 'ACTIF',
      })
    }
  }, [tier, isOpen, reset])

  const mutation = useMutation({
    mutationFn: (data: any) => tiersAPI.updateTiers(tier.id, data),
    onSuccess: () => {
      toast.success('Modifications enregistrées !')
      queryClient.invalidateQueries({ queryKey: ['tiers'] })
      onClose()
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || 'Erreur lors de la modification du tier.')
    }
  })

  const onSubmit = (data: TierFormValues) => {
    const payload = {
      ...data,
      sigle_ou_enseigne: data.sigle_ou_enseigne || null,
      rccm: data.rccm || null,
      registre_commerce: data.registre_commerce || null,
      email: data.email || null,
      telephone: data.telephone || null,
      adresse: data.adresse_physique, // compatibilité
      autorise_magasinage: data.autorise_parc_stockage, // compatibilité
      compte_syscohada: data.compte_collectif_syscohada, // compatibilité
      limite_credit_xaf: data.limite_credit_maximum, // compatibilité
    }
    mutation.mutate(payload)
  }

  if (!isOpen || !tier) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[60] animate-in fade-in duration-200" onClick={onClose} />
      <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg animate-in zoom-in-95 fade-in duration-300 overflow-hidden flex flex-col max-h-[90vh]">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-white shrink-0">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 rounded-xl">
                <Building2 className="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Modifier le Tier</h3>
                <p className="text-sm text-gray-500">Mettre à jour le profil de {tier.raison_sociale}</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-xl text-gray-400 hover:text-gray-600 transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit as any)} className="p-6 space-y-4 overflow-y-auto flex-1">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-semibold text-gray-700">Raison Sociale *</label>
                <input
                  type="text"
                  {...register('raison_sociale')}
                  className={`w-full px-4 py-2.5 rounded-xl border ${errors.raison_sociale ? 'border-red-500' : 'border-gray-200'} focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm`}
                />
                {errors.raison_sociale && <p className="text-xs text-red-500">{errors.raison_sociale.message}</p>}
              </div>
              <div className="space-y-1">
                <label className="text-sm font-semibold text-gray-700">Sigle / Enseigne</label>
                <input
                  type="text"
                  {...register('sigle_ou_enseigne')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-semibold text-gray-700">NIU *</label>
                <input
                  type="text"
                  {...register('niu')}
                  className={`w-full px-4 py-2.5 rounded-xl border ${errors.niu ? 'border-red-500' : 'border-gray-200'} focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm`}
                />
                {errors.niu && <p className="text-xs text-red-500">{errors.niu.message}</p>}
              </div>
              <div className="space-y-1">
                <label className="text-sm font-semibold text-gray-700">RCCM</label>
                <input
                  type="text"
                  {...register('rccm')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Régime Fiscal</label>
                <input
                  type="text"
                  {...register('regime_fiscal')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Statut Compte *</label>
                <select
                  {...register('statut')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm bg-white"
                >
                  <option value="EN_ATTENTE_VALIDATION">En attente validation</option>
                  <option value="ACTIF">Actif</option>
                  <option value="BLOQUE">Bloqué</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  {...register('email')}
                  className={`w-full px-4 py-2.5 rounded-xl border ${errors.email ? 'border-red-500' : 'border-gray-200'} focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm`}
                />
                {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Téléphone</label>
                <input
                  type="tel"
                  {...register('telephone')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-semibold text-gray-700">Adresse Physique</label>
              <textarea
                {...register('adresse_physique')}
                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm h-16"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Ville</label>
                <input
                  type="text"
                  {...register('ville')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Pays</label>
                <input
                  type="text"
                  {...register('pays')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
                />
              </div>
            </div>

            {/* Services Activés */}
            <div className="space-y-2 border-t border-gray-100 pt-4">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block">Services à la Carte</label>
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_acconage')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Acconage
                </label>
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_transit')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Transit (Douane)
                </label>
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_parc_stockage')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Parc & Stockage
                </label>
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_manutention')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Manutention
                </label>
                <label className="flex items-center gap-2.5 p-2.5 bg-slate-50 hover:bg-slate-100/70 rounded-xl transition-colors cursor-pointer text-sm text-slate-700">
                  <input type="checkbox" {...register('autorise_transport')} className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" /> Transport Routier
                </label>
              </div>
            </div>

            {/* Paramètres Financiers */}
            <div className="space-y-4 border-t border-gray-100 pt-4 pb-4">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block">Paramètres SAP FI & Crédit</label>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-500">Compte SYSCOHADA</label>
                  <input
                    type="text"
                    {...register('compte_collectif_syscohada')}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-500">Délai Paiement (Jours)</label>
                  <input
                    type="number"
                    {...register('delai_paiement_jours')}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm"
                  />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-500">Limite de Crédit Max (FCFA)</label>
                <input
                  type="number"
                  {...register('limite_credit_maximum')}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all text-sm font-mono"
                />
              </div>
            </div>

            {/* Footer shrink */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100 sticky bottom-0 bg-white">
              <button
                type="button"
                onClick={onClose}
                className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-emerald-600 to-emerald-700 rounded-xl hover:from-emerald-700 hover:to-emerald-800 transition-all shadow-sm shadow-emerald-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {mutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}

// ── Modal de visualisation & encours financier ─────────────────────────────────────
function ViewTierModal({ isOpen, onClose, tier }: { isOpen: boolean; onClose: () => void; tier: any }) {
  // Utilisation de useQuery pour l'encours
  const { data: encoursData, isLoading: loading } = useQuery({
    queryKey: ['encours', tier?.id],
    queryFn: async () => {
      const res = await financeAPI.getEncours(tier.id)
      return res.data
    },
    enabled: isOpen && !!tier?.id,
  })

  if (!isOpen || !tier) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[60] animate-in fade-in duration-200" onClick={onClose} />
      <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg animate-in zoom-in-95 fade-in duration-300 overflow-hidden flex flex-col max-h-[90vh]">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 bg-gradient-to-r from-slate-50 to-white shrink-0">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-slate-100 rounded-xl">
                <Building2 className="w-5 h-5 text-slate-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">{tier.raison_sociale}</h3>
                <p className="text-sm text-gray-500">Profil & Infos Financières du Tier</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-xl text-gray-400 hover:text-gray-600 transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="p-6 space-y-6 overflow-y-auto flex-1">
            {/* Infos de base */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Code Tier</span>
                <span className="text-sm text-slate-800 font-semibold">{tier.code_tiers || 'N/A'}</span>
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Type</span>
                <span className="text-sm text-slate-800 font-semibold capitalize">{tier.type || 'Client'}</span>
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">NIU (Fiscal)</span>
                <span className="text-sm text-slate-800 font-medium">{tier.niu || ''}</span>
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Régime Fiscal</span>
                <span className="text-sm text-slate-800 font-medium">{tier.regime_fiscal || 'Réel'}</span>
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Téléphone</span>
                <span className="text-sm text-slate-800 font-medium">{tier.telephone || ''}</span>
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Email</span>
                <span className="text-sm text-slate-800 font-medium break-all">{tier.email || ''}</span>
              </div>
            </div>

            {/* Localisation */}
            <div className="bg-slate-50 p-4 rounded-xl space-y-2 border border-slate-100">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Adresse & Localisation</h4>
              <p className="text-sm text-slate-700">{tier.adresse_physique || tier.adresse || 'Aucune adresse enregistrée'}</p>
              <div className="grid grid-cols-2 gap-2 text-sm text-slate-600">
                <div>Ville : <strong>{tier.ville || 'Douala'}</strong></div>
                <div>Pays : <strong>{tier.pays || 'Cameroun'}</strong></div>
              </div>
            </div>

            {/* Services Activés */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Services Activés</span>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Acconage', active: tier.autorise_acconage },
                  { label: 'Transit', active: tier.autorise_transit },
                  { label: 'Parc / Stockage', active: tier.autorise_parc_stockage || tier.autorise_magasinage },
                  { label: 'Manutention', active: tier.autorise_manutention },
                  { label: 'Transport', active: tier.autorise_transport },
                ].map((srv) => (
                  <div key={srv.label} className="flex items-center gap-2 p-2 rounded-lg border border-slate-100 bg-white shadow-sm text-sm">
                    <span className={`w-2.5 h-2.5 rounded-full ${srv.active ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.3)]' : 'bg-slate-300'}`}></span>
                    <span className={srv.active ? 'text-slate-800 font-medium' : 'text-slate-400 line-through'}>{srv.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Volet Financier */}
            <div className="border-t border-slate-100 pt-4 space-y-4">
              <h4 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-emerald-600" />
                Limite & Encours Financier
              </h4>

              {loading ? (
                <div className="h-20 flex items-center justify-center text-sm text-slate-500">
                  Chargement de l'encours...
                </div>
              ) : encoursData ? (
                <div className="space-y-3 bg-emerald-50/50 border border-emerald-100 p-4 rounded-xl">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-slate-500 block">Limite de crédit</span>
                      <strong className="text-slate-800 font-mono text-base">{(encoursData.limite_credit_xaf || 0).toLocaleString()} FCFA</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Encours actuel</span>
                      <strong className="text-slate-800 font-mono text-base">{(encoursData.encours_xaf || 0).toLocaleString()} FCFA</strong>
                    </div>
                  </div>

                  {/* Progress bar */}
                  {encoursData.limite_credit_xaf > 0 && (
                    <div className="space-y-1">
                      <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            encoursData.bloque ? 'bg-red-500' : encoursData.alerte ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${Math.min(encoursData.taux_occupation || 0, 100)}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-xs text-slate-500 font-mono">
                        <span>{Math.round(encoursData.taux_occupation || 0)}% utilisé</span>
                        <span>Délai de paiement : {tier.delai_paiement_jours || 30} jours</span>
                      </div>
                    </div>
                  )}

                  {/* Status Badges */}
                  <div className="flex gap-2 pt-1">
                    {encoursData.bloque ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-red-100 text-red-800 text-xs font-semibold">
                        <AlertCircle className="w-3.5 h-3.5" /> Compte Bloqué (Limite Dépassée)
                      </span>
                    ) : encoursData.alerte ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-semibold">
                        <AlertCircle className="w-3.5 h-3.5" /> Alerte Encours Élevé (&gt;90%)
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-semibold">
                        <CheckCircle className="w-3.5 h-3.5" /> Compte Sain
                      </span>
                    )}
                  </div>
                </div>
              ) : (
                <div className="bg-slate-50 p-4 rounded-xl text-sm text-slate-600">
                  <div className="flex justify-between font-mono">
                    <span>Limite de crédit :</span>
                    <strong>{Number(tier.limite_credit_maximum || tier.limite_credit_xaf || 0).toLocaleString()} FCFA</strong>
                  </div>
                  <div className="flex justify-between font-mono mt-1">
                    <span>Délai de paiement :</span>
                    <strong>{tier.delai_paiement_jours || 30} jours</strong>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-100 bg-slate-50 flex gap-3 shrink-0">
            <button
              onClick={onClose}
              className="w-full px-5 py-2.5 text-sm font-semibold text-slate-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all shadow-sm"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

// ── Page principale ─────────────────────────────────────────────────────────────
export default function MasterDataTiers() {
  const queryClient = useQueryClient()
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [viewModalOpen, setViewModalOpen] = useState(false)
  const [selectedTier, setSelectedTier] = useState<any>(null)

  // Remplacement de useEffect par useQuery pour le server-state
  const { data: tiers = [], isLoading: loading } = useQuery({
    queryKey: ['tiers'],
    queryFn: async () => {
      const res = await tiersAPI.getTiers()
      return res.data || []
    }
  })

  // Mutation pour la suppression
  const deleteMutation = useMutation({
    mutationFn: (id: number) => tiersAPI.deleteTiers(id),
    onSuccess: () => {
      toast.success('Tier supprimé avec succès.')
      queryClient.invalidateQueries({ queryKey: ['tiers'] })
    },
    onError: (err: any) => {
      console.error('Error deleting tier:', err)
      toast.error('Erreur lors de la suppression du tier.')
    }
  })

  const handleEditTier = (row: any) => {
    setSelectedTier(row)
    setEditModalOpen(true)
  }

  const handleViewTier = (row: any) => {
    setSelectedTier(row)
    setViewModalOpen(true)
  }

  const handleDeleteTier = (row: any) => {
    if (confirm(`Êtes-vous sûr de vouloir supprimer le tier "${row.raison_sociale}" ?`)) {
      deleteMutation.mutate(row.id)
    }
  }

  // ── KPI computations ──────────────────────────────────────────────────────
  const kpis = useMemo(() => {
    const clients = tiers.filter((t: any) => String(t.type || 'client').toLowerCase() === 'client').length
    const fournisseurs = tiers.filter((t: any) => String(t.type || 'supplier').toLowerCase() === 'supplier' || String(t.type || '').toLowerCase() === 'fournisseur').length
    const partenaires = tiers.filter((t: any) => String(t.type || 'partner').toLowerCase() === 'partner' || String(t.type || '').toLowerCase() === 'partenaire').length
    const totalCredit = tiers.reduce((sum: number, t: any) => sum + Number(t.limite_credit_maximum || t.limite_credit_xaf || 0), 0)
    return { total: tiers.length, clients, fournisseurs, partenaires, totalCredit }
  }, [tiers])

  const kpiCards = loading ? (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => <CardSkeletonLoader key={i} />)}
    </div>
  ) : (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Total Tiers" value={kpis.total} icon={<Users className="w-4 h-4 text-blue-600" />} color="bg-blue-50" />
      <KpiCard label="Clients" value={kpis.clients} icon={<Briefcase className="w-4 h-4 text-emerald-600" />} color="bg-emerald-50" />
      <KpiCard label="Fournisseurs" value={kpis.fournisseurs} icon={<Building2 className="w-4 h-4 text-amber-600" />} color="bg-amber-50" />
      <KpiCard label="Crédit Total" value={`${kpis.totalCredit.toLocaleString()} FCFA`} icon={<CreditCard className="w-4 h-4 text-purple-600" />} color="bg-purple-50" />
    </div>
  )

  const columns = [
    {
      key: 'id',
      label: 'ID',
      render: (val: any) => (
        <span className="font-mono text-xs px-2 py-1 bg-slate-100 rounded text-slate-600 font-medium">
          C-{String(val).padStart(4, '0')}
        </span>
      ),
    },
    {
      key: 'raison_sociale',
      label: 'Tier',
      render: (val: any, row: any) => (
        <div>
          <div className="font-semibold text-slate-900">{val || 'Sans nom'}</div>
          <div className="text-xs text-slate-500">{row.email || 'Aucun email'}</div>
        </div>
      ),
    },
    {
      key: 'type',
      label: 'Catégorie',
      render: (val: any) => {
        const typeStr = String(val || 'client').toLowerCase();
        const colors: Record<string, string> = {
          client: 'bg-blue-50 text-blue-700 ring-blue-600/20',
          supplier: 'bg-amber-50 text-amber-700 ring-amber-600/20',
          fournisseur: 'bg-amber-50 text-amber-700 ring-amber-600/20',
          partner: 'bg-purple-50 text-purple-700 ring-purple-600/20',
          partenaire: 'bg-purple-50 text-purple-700 ring-purple-600/20',
        }
        const style = colors[typeStr] || 'bg-slate-50 text-slate-700 ring-slate-600/20'
        return (
          <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${style}`}>
            {val ? String(val).charAt(0).toUpperCase() + String(val).slice(1) : 'Client'}
          </span>
        )
      }
    },
    {
      key: 'ville',
      label: 'Localisation',
      render: (val: any, row: any) => (
        <div className="text-sm text-slate-600">
          {val ? `${val}, ${row.pays || 'Cameroun'}` : 'Douala, Cameroun'}
        </div>
      )
    },
    {
      key: 'limite_credit_maximum',
      label: 'Crédit Max',
      render: (val: any, row: any) => {
        const numVal = Number(val || row.limite_credit_xaf || 0)
        return (
          <div className="text-sm font-medium text-slate-900 font-mono">
            {numVal > 0 ? `${numVal.toLocaleString()} XAF` : '-'}
          </div>
        )
      }
    },
    {
      key: 'statut',
      label: 'Statut',
      render: (val: any) => {
        const isActif = String(val).toUpperCase() === 'ACTIF'
        const isBloque = String(val).toUpperCase() === 'BLOQUE'
        const badgeColor = isActif 
          ? 'bg-emerald-50 text-emerald-700' 
          : isBloque 
            ? 'bg-red-50 text-red-700' 
            : 'bg-amber-50 text-amber-700'
        const dotColor = isActif 
          ? 'bg-emerald-600' 
          : isBloque 
            ? 'bg-red-600' 
            : 'bg-amber-500'
        return (
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${badgeColor}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`}></span> 
            {val ? String(val).replace(/_/g, ' ') : 'ACTIF'}
          </span>
        )
      }
    }
  ]

  return (
    <>
      <GenericDataPage
        title="Tiers (Partenaires)"
        description="Gestion centralisée des clients, fournisseurs et partenaires d'affaires avec habilitation de services et limites de crédit."
        icon={<Building2 className="w-6 h-6 text-emerald-600" />}
        columns={columns}
        data={tiers}
        isLoading={loading}
        onAdd={() => setCreateModalOpen(true)}
        primaryActionLabel="Nouveau Tier"
        kpiCards={kpiCards}
        onView={handleViewTier}
        onEdit={handleEditTier}
        onDelete={handleDeleteTier}
      />
      <CreateTierModal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
      />
      <EditTierModal
        isOpen={editModalOpen}
        onClose={() => {
          setEditModalOpen(false)
          setSelectedTier(null)
        }}
        tier={selectedTier}
      />
      <ViewTierModal
        isOpen={viewModalOpen}
        onClose={() => {
          setViewModalOpen(false)
          setSelectedTier(null)
        }}
        tier={selectedTier}
      />
    </>
  )
}

'use client';

import React, { useState, useEffect } from 'react';
import {
  Building2,
  Save,
  ShieldCheck,
  CreditCard,
  Mail,
  Phone,
  MapPin,
  FileBadge,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { adminAPI, apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

export default function CompanyProfilePage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [company, setCompany] = useState({
    raison_sociale: '',
    sigle: '',
    forme_juridique: 'SA',
    nif: '',
    rccm: '',
    agrement_douane: '',
    agrement_pad: '',
    agrement_pak: '',
    adresse: '',
    ville: 'Douala',
    pays: 'Cameroun',
    boite_postale: '',
    telephone: '',
    email: '',
    site_web: '',
    devise: 'XAF',
    taux_tva: '19.25',
    banque_principale: '',
    rib: '',
    iban: '',
    swift: ''
  });

  useEffect(() => {
    // Load company profile from tenant / global settings
    apiClient.get('/api/v1/tenant/company-profile').catch(() => {
      return apiClient.get('/api/admin/global-settings');
    }).then(res => {
      if (res?.data) {
        setCompany(prev => ({ ...prev, ...res.data }));
      }
    }).finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post('/api/v1/tenant/company-profile', company).catch(() => {
        return apiClient.post('/api/admin/global-settings', company);
      });
      toast.success("Fiche d'entreprise mise à jour avec succès !");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement de l'entreprise.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Fiche & Identité de l'Entreprise</h1>
            <p className="text-sm text-on-surface-variant">
              Raison sociale, immatriculations fiscales, agréments portuaires PAD/PAK et coordonnées bancaires
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Identité Légale */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-primary" /> Identité Corporative & Enregistrements Fiscaux
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Raison Sociale *</label>
              <input
                type="text"
                required
                value={company.raison_sociale}
                onChange={e => setCompany({ ...company, raison_sociale: e.target.value })}
                placeholder="Ex: EVO-LOGISTICS & TRANSIT CEMAC SA"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Sigle Commercial</label>
              <input
                type="text"
                value={company.sigle}
                onChange={e => setCompany({ ...company, sigle: e.target.value })}
                placeholder="Ex: EVO-LOG"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Forme Juridique</label>
              <select
                value={company.forme_juridique}
                onChange={e => setCompany({ ...company, forme_juridique: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="SA">Société Anonyme (SA)</option>
                <option value="SARL">Société à Responsabilité Limitée (SARL)</option>
                <option value="SAS">Société par Actions Simplifiée (SAS)</option>
                <option value="GIE">Groupement d'Intérêt Économique (GIE)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">NIF (Identifiant Fiscal Unique)</label>
              <input
                type="text"
                value={company.nif}
                onChange={e => setCompany({ ...company, nif: e.target.value })}
                placeholder="Ex: M010200034567P"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">N° RCCM</label>
              <input
                type="text"
                value={company.rccm}
                onChange={e => setCompany({ ...company, rccm: e.target.value })}
                placeholder="Ex: RC/DLA/2019/B/890"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
              />
            </div>
          </div>
        </div>

        {/* Agréments Portuaires & Douane */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <FileBadge className="w-4 h-4 text-cyan-600" /> Agréments Douaniers & Licences d'Exploitation
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Agrément Douane (DGD)</label>
              <input
                type="text"
                value={company.agrement_douane}
                onChange={e => setCompany({ ...company, agrement_douane: e.target.value })}
                placeholder="Ex: DEC-DGD-2021/045"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Agrément PAD (Port Douala)</label>
              <input
                type="text"
                value={company.agrement_pad}
                onChange={e => setCompany({ ...company, agrement_pad: e.target.value })}
                placeholder="Ex: PAD-ACC-2022/88"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Agrément PAK (Port Kribi)</label>
              <input
                type="text"
                value={company.agrement_pak}
                onChange={e => setCompany({ ...company, agrement_pak: e.target.value })}
                placeholder="Ex: PAK-TRANSIT-2023/12"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
              />
            </div>
          </div>
        </div>

        {/* Coordonnées & Siège */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-primary" /> Siège Social & Contacts Officiels
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Adresse Géographique</label>
              <input
                type="text"
                value={company.adresse}
                onChange={e => setCompany({ ...company, adresse: e.target.value })}
                placeholder="Ex: Zone Portuaire, Boulevard Leclerc, Akwa"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Ville / Pays</label>
              <input
                type="text"
                value={`${company.ville}, ${company.pays}`}
                disabled
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container text-on-surface-variant"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Téléphone Standard</label>
              <input
                type="text"
                value={company.telephone}
                onChange={e => setCompany({ ...company, telephone: e.target.value })}
                placeholder="Ex: +237 233 42 00 00"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Email Officiel</label>
              <input
                type="email"
                value={company.email}
                onChange={e => setCompany({ ...company, email: e.target.value })}
                placeholder="Ex: contact@evo-logistics.cm"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Site Web</label>
              <input
                type="text"
                value={company.site_web}
                onChange={e => setCompany({ ...company, site_web: e.target.value })}
                placeholder="Ex: https://evo-logistics.cm"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        {/* Paramètres Financiers & RIB */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-emerald-600" /> Coordonnées Bancaires & Mentions Facturation
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Banque Domiciliataire</label>
              <input
                type="text"
                value={company.banque_principale}
                onChange={e => setCompany({ ...company, banque_principale: e.target.value })}
                placeholder="Ex: Société Générale Cameroun"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Relevé d'Identité Bancaire (RIB CEMAC)</label>
              <input
                type="text"
                value={company.rib}
                onChange={e => setCompany({ ...company, rib: e.target.value })}
                placeholder="Ex: 10019 02345 01234567890 45"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity disabled:opacity-50 shadow-sm"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Enregistrement...' : 'Enregistrer le Profil Entreprise'}
          </button>
        </div>
      </form>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { 
  Building2, 
  Save, 
  Globe, 
  DollarSign, 
  Mail, 
  ShieldCheck, 
  MapPin, 
  FileText,
  Percent,
  CheckCircle2
} from 'lucide-react';
import { toast } from 'sonner';

export default function AdminTenantGlobalSettingsPage() {
  const [settings, setSettings] = useState({
    raisonSociale: 'CADC LOGISTICS & SHIPPING SA',
    sigle: 'CADC-ERP',
    nif: 'M051812749812P',
    rccm: 'RC/DLA/2018/B/4521',
    capitalSocial: '150000000',
    devise: 'XAF',
    tauxTva: '19.25',
    tauxPrecompte: '2.2',
    tauxCentimesAdditionnels: '10',
    adresseSiege: 'Rue Koumassi, Bonanjo, BP 4512 Douala - Cameroun',
    telephone: '+237 233 42 18 90',
    emailContact: 'direction@cadc-logistics.cm',
    agrementDouane: 'AGR-CEMAC-DLA-2021-089',
    agrementPortuairePad: 'PAD-CONC-2019-33',
    smtpHost: 'smtp.cadc-logistics.cm',
    smtpPort: '587',
    smtpUser: 'notifications@cadc-logistics.cm',
    enableSmsAlerts: true,
    enableAutoBaeSync: true
  });

  const [saving, setSaving] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      toast.success('Paramètres d\'entreprise et configurations fiscales enregistrés avec succès.');
    }, 600);
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Configuration Générale de l'Entreprise</h1>
            <p className="text-sm text-on-surface-variant">
              Raison sociale, identifiants légaux CEMAC, fiscalité DGI et paramètres de diffusion
            </p>
          </div>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-5 py-2 text-xs font-bold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity shadow-sm disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Enregistrement...' : 'Enregistrer les Modifications'}
        </button>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Identité Légale */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-outline pb-3">
            <FileText className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-base text-on-surface">1. Identification Fiscale & Juridique</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Raison Sociale Officielle :</label>
              <input
                type="text"
                value={settings.raisonSociale}
                onChange={(e) => setSettings({ ...settings, raisonSociale: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-semibold"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Sigle / Nom Commercial :</label>
              <input
                type="text"
                value={settings.sigle}
                onChange={(e) => setSettings({ ...settings, sigle: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-semibold"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Numéro d'Identifiant Fiscal (NIF Cameroun) :</label>
              <input
                type="text"
                value={settings.nif}
                onChange={(e) => setSettings({ ...settings, nif: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono font-bold uppercase"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Registre du Commerce (RCCM) :</label>
              <input
                type="text"
                value={settings.rccm}
                onChange={(e) => setSettings({ ...settings, rccm: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Agrément Douane CEMAC :</label>
              <input
                type="text"
                value={settings.agrementDouane}
                onChange={(e) => setSettings({ ...settings, agrementDouane: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Capital Social Souscrit (FCFA) :</label>
              <input
                type="text"
                value={settings.capitalSocial}
                onChange={(e) => setSettings({ ...settings, capitalSocial: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono"
              />
            </div>
          </div>
        </div>

        {/* Paramètres Fiscaux */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-outline pb-3">
            <Percent className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-base text-on-surface">2. Barème Fiscal & Monétaire OHADA</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Devise de Tenue des Comptes :</label>
              <input
                type="text"
                value={settings.devise}
                disabled
                className="w-full p-2.5 bg-surface-container border border-outline rounded-xl text-on-surface font-bold font-mono"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Taux de TVA Normal (%) :</label>
              <input
                type="text"
                value={settings.tauxTva}
                onChange={(e) => setSettings({ ...settings, tauxTva: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono font-bold"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Taux Précompte sur Achat (%) :</label>
              <input
                type="text"
                value={settings.tauxPrecompte}
                onChange={(e) => setSettings({ ...settings, tauxPrecompte: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono font-bold"
              />
            </div>
          </div>
        </div>

        {/* Notifications & Relais SMTP */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-outline pb-3">
            <Mail className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-base text-on-surface">3. Relais Notifications & Alertes Automatiques</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Serveur SMTP Émetteur :</label>
              <input
                type="text"
                value={settings.smtpHost}
                onChange={(e) => setSettings({ ...settings, smtpHost: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Port SMTP :</label>
              <input
                type="text"
                value={settings.smtpPort}
                onChange={(e) => setSettings({ ...settings, smtpPort: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono"
              />
            </div>

            <div>
              <label className="block text-on-surface-variant font-medium mb-1">Adresse Email Expéditeur :</label>
              <input
                type="email"
                value={settings.smtpUser}
                onChange={(e) => setSettings({ ...settings, smtpUser: e.target.value })}
                className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface"
              />
            </div>
          </div>

          <div className="pt-2 space-y-2">
            <label className="flex items-center gap-2.5 text-xs text-on-surface cursor-pointer">
              <input
                type="checkbox"
                checked={settings.enableSmsAlerts}
                onChange={(e) => setSettings({ ...settings, enableSmsAlerts: e.target.checked })}
                className="rounded text-primary focus:ring-primary"
              />
              <span className="font-medium">Activer les alertes SMS instantanées aux chauffeurs lors de l'affectation de mission</span>
            </label>

            <label className="flex items-center gap-2.5 text-xs text-on-surface cursor-pointer">
              <input
                type="checkbox"
                checked={settings.enableAutoBaeSync}
                onChange={(e) => setSettings({ ...settings, enableAutoBaeSync: e.target.checked })}
                className="rounded text-primary focus:ring-primary"
              />
              <span className="font-medium">Synchroniser immédiatement la délivrance du BAE Douane avec les autorisations de sortie quai</span>
            </label>
          </div>
        </div>
      </form>
    </div>
  );
}

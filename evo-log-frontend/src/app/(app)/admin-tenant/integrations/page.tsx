'use client';

/**
 * Passerelles d'intégration & connecteurs EDI.
 * ARCHITECTURE ZÉRO MOCK : le catalogue ci-dessous est une information de
 * référence figée (nom du service tiers, adresse publique de son API). L'état
 * de configuration réel (connecteur enregistré, statut, dernière synchronisation)
 * provient du backend via GET /api/v1/integration/integrations. L'enregistrement
 * d'une configuration est un appel réel (POST /api/v1/integration/integrations).
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  Key, Loader2, FileQuestion, RefreshCw, Link2,
} from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '@/lib/api-client';
import { classifyApiError } from '@/hooks/useApi';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { useSettings } from '@/components/layout/SettingsProvider';

interface ConnecteurReference {
  code: string;
  name: string;
  category: 'DOUANE' | 'PORT' | 'BANQUE' | 'EDI';
  description: string;
  endpoint: string;
}

interface IntegrationRow {
  id: number;
  code_integration: string;
  type_integration: string | null;
  nom: string | null;
  url_api: string | null;
  statut: string | null;
  actif: boolean | null;
  derniere_synchronisation: string | null;
}

// Catalogue de référence (services publics camerounais réels, adresses publiques).
const CONNECTEURS_DISPONIBLES: ConnecteurReference[] = [
  { code: 'GUCE', name: 'GUCE Cameroun (Guichet Unique)', category: 'DOUANE', description: 'Échange dématérialisé e-Force, titres de transit, manifestes électroniques et BAE.', endpoint: 'https://www.guce-network.net' },
  { code: 'CAMCIS', name: 'CAMCIS Douane Camerounaise', category: 'DOUANE', description: 'Transmission des déclarations DUM, régimes suspensifs et apurements.', endpoint: 'https://camcis.douanes.cm' },
  { code: 'PAD', name: 'Port Autonome de Douala (PAD / DIT)', category: 'PORT', description: "Interface TOS pour réservation de créneaux quai et avis d'accostage.", endpoint: 'https://www.pad-cameroun.cm' },
  { code: 'PAK', name: 'Port Autonome de Kribi (PAK / KMT)', category: 'PORT', description: 'Télétransmission des ordres de manutention et pesées VGM pont-bascule.', endpoint: 'https://port-of-kribi.com' },
  { code: 'MOMO', name: 'Orange Money & MTN MoMo Business', category: 'BANQUE', description: 'Encaissement des avances clients et paiements des frais de péage.', endpoint: 'https://api.orange.com' },
  { code: 'DGI', name: 'DGI Cameroun (Facturation Électronique FEN)', category: 'EDI', description: 'Génération et scellement fiscal des QR-Codes sur factures de débours.', endpoint: 'https://www.tdme-dgi.cm' },
];

export default function AdminTenantIntegrationsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [selectedConnector, setSelectedConnector] = useState<ConnecteurReference | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [integrations, setIntegrations] = useState<IntegrationRow[]>([]);
  const [loading, setLoading] = useState(true);

  const loadIntegrations = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/integration/integrations', { params: { limit: 200 } });
      const rows = Array.isArray(res.data) ? res.data : (res.data?.items ?? []);
      setIntegrations(rows);
    } catch (err) {
      const info = classifyApiError(err);
      toast.error(info.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadIntegrations(); }, [loadIntegrations]);

  const findIntegration = (code: string): IntegrationRow | undefined =>
    integrations.find(i => (i.code_integration || '').toUpperCase() === code.toUpperCase());

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConnector) return;
    if (!apiKeyInput.trim()) {
      toast.error(t('Une clé API ou un token EDI est requis pour enregistrer la connexion.', 'An API key or EDI token is required to save the connection.'));
      return;
    }
    setSaving(true);
    try {
      await apiClient.post('/api/v1/integration/integrations', {
        code_integration: selectedConnector.code,
        type_integration: selectedConnector.category.toLowerCase(),
        nom: selectedConnector.name,
        url_api: selectedConnector.endpoint,
        api_key: apiKeyInput.trim(),
      });
      toast.success(t(`Configuration « ${selectedConnector.name} » enregistrée.`, `Configuration "${selectedConnector.name}" saved.`));
      setSelectedConnector(null);
      setApiKeyInput('');
      await loadIntegrations();
    } catch (err) {
      const info = classifyApiError(err);
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : info.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModuleLayout
      title={t("Passerelles d'Intégration & Connecteurs EDI", 'Integration Gateways & EDI Connectors')}
      description={t('Configurez les connexions de votre entreprise aux services externes : douane (GUCE, CAMCIS), ports (PAD, PAK), paiement mobile et facturation DGI.', 'Configure your company connections to external services: customs (GUCE, CAMCIS), ports (PAD, PAK), mobile payment and DGI invoicing.')}
      help={t("Enregistrer une configuration transmet vos identifiants au serveur EVO-LOG qui les stocke de façon sécurisée. Le statut et la dernière synchronisation affichés proviennent du backend.", 'Saving a configuration transmits your credentials to the EVO-LOG server, which stores them securely. The status and last synchronization shown come from the backend.')}
    >
      <div className="flex items-center justify-end">
        <button
          onClick={loadIntegrations}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-surface-container border border-outline text-xs font-bold text-on-surface hover:bg-surface-container-low transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          {t('Actualiser', 'Refresh')}
        </button>
      </div>

      {/* Grille des connecteurs  statut réel issu du backend */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {CONNECTEURS_DISPONIBLES.map(c => {
          const integ = findIntegration(c.code);
          const configured = !!integ;
          return (
            <div
              key={c.code}
              className="bg-surface border border-outline rounded-2xl p-5 hover:border-primary transition-all shadow-sm space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex justify-between items-start gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                    {c.category}
                  </span>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1 ${
                    configured
                      ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10'
                      : 'border-outline text-on-surface-variant'
                  }`}>
                    {configured ? <Link2 className="w-3 h-3" /> : <FileQuestion className="w-3 h-3" />}
                    {configured
                      ? (integ!.statut ? integ!.statut.toUpperCase() : t('Enregistré', 'Registered'))
                      : t('À configurer', 'To configure')}
                  </span>
                </div>

                <div>
                  <h3 className="font-bold text-base text-on-surface mb-1">{t(c.name, c.name)}</h3>
                  <p className="text-xs text-on-surface-variant leading-relaxed">{t(c.description, c.description)}</p>
                </div>

                <div className="p-2.5 bg-surface-container-low rounded-xl font-mono text-[10px] text-on-surface-variant break-all">
                  {c.endpoint}
                </div>

                {configured && integ!.derniere_synchronisation && (
                  <p className="text-[10px] text-on-surface-variant">
                    {t('Dernière sync.', 'Last sync.')} : {new Date(integ!.derniere_synchronisation).toLocaleString(lang === 'en' ? 'en-US' : 'fr-FR')}
                  </p>
                )}
              </div>

              <div className="pt-3 border-t border-outline/50 flex justify-end items-center gap-2">
                <button
                  onClick={() => setSelectedConnector(c)}
                  className="px-3 py-2 bg-primary/10 text-primary hover:bg-primary/20 rounded-lg font-bold text-xs flex items-center gap-1.5"
                  aria-label={t(`Configurer la passerelle ${c.name}`, `Configure gateway ${c.name}`)}
                >
                  <Key className="w-3.5 h-3.5" />
                  {configured ? t('Mettre à jour les clés', 'Update keys') : t('Configurer les clés', 'Configure keys')}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modale de configuration  envoi réel au backend */}
      {selectedConnector && (
        <div className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label={t(`Configurer ${selectedConnector.name}`, `Configure ${selectedConnector.name}`)}>
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <div>
                <span className="text-xs font-bold text-primary uppercase">{selectedConnector.category}</span>
                <h3 className="font-bold text-on-surface text-base">{selectedConnector.name}</h3>
              </div>
              <button
                onClick={() => setSelectedConnector(null)}
                className="p-2 text-on-surface-variant hover:text-on-surface rounded-lg"
                aria-label={t('Fermer', 'Close')}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveConfig} className="space-y-3 text-xs">
              <div>
                <label htmlFor="edi-key" className="block text-on-surface-variant font-medium mb-1">
                  {t("Clé API d'accès / Token EDI :", 'API access key / EDI token:')}
                </label>
                <input
                  id="edi-key"
                  type="password"
                  autoComplete="off"
                  placeholder="Bearer cadc_sec_xxxxxxxxxxxx"
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  className="w-full p-2.5 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono"
                />
              </div>

              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                {t('Endpoint enregistré', 'Registered endpoint')} : <span className="font-mono">{selectedConnector.endpoint}</span>
              </p>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedConnector(null)}
                  className="px-4 py-2 border border-outline rounded-xl text-on-surface hover:bg-surface-container font-semibold"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
                >
                  {saving && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {saving ? t('Transmission…', 'Transmitting…') : t('Enregistrer les clés', 'Save keys')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </ModuleLayout>
  );
}

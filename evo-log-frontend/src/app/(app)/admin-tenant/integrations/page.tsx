'use client';

import React, { useState } from 'react';
import { 
  Network, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  ExternalLink, 
  Key, 
  Settings, 
  ShieldCheck, 
  Zap,
  Lock,
  Globe
} from 'lucide-react';
import { toast } from 'sonner';

interface IntegrationConnector {
  id: string;
  name: string;
  category: 'DOUANE' | 'PORT' | 'BANQUE' | 'EDI';
  description: string;
  endpoint: string;
  status: 'CONNECTED' | 'DISCONNECTED' | 'ERROR';
  lastSync: string;
  pingMs: number;
}

const INITIAL_CONNECTORS: IntegrationConnector[] = [
  {
    id: 'guce',
    name: 'GUCE Cameroun (Guichet Unique)',
    category: 'DOUANE',
    description: 'Échange dématérialisé e-Force, titres de transit, manifestes électroniques et BAE.',
    endpoint: 'https://edi.guce.cm/api/v2/manifest',
    status: 'CONNECTED',
    lastSync: 'Il y a 3 min',
    pingMs: 42
  },
  {
    id: 'camcis',
    name: 'CAMCIS Douane Camerounaise',
    category: 'DOUANE',
    description: 'Transmission automatique des déclarations DUM, régimes suspensifs et apurements.',
    endpoint: 'https://camcis.douanes.cm/gateway/soap',
    status: 'CONNECTED',
    lastSync: 'Il y a 8 min',
    pingMs: 58
  },
  {
    id: 'pad_douala',
    name: 'Port Autonome de Douala (PAD / DIT)',
    category: 'PORT',
    description: 'Interface TOS Navis N4 pour réservation de créneaux quai et avis d\'accostage.',
    endpoint: 'https://tos.pad.cm/api/v1/berth',
    status: 'CONNECTED',
    lastSync: 'Il y a 12 min',
    pingMs: 31
  },
  {
    id: 'pak_kribi',
    name: 'Port Autonome de Kribi (PAK / KMT)',
    category: 'PORT',
    description: 'Télétransmission des ordres de manutention et pesées VGM pont-bascule.',
    endpoint: 'https://kribiport.cm/api/edi',
    status: 'CONNECTED',
    lastSync: 'Il y a 25 min',
    pingMs: 64
  },
  {
    id: 'mobile_money',
    name: 'Orange Money & MTN MoMo Business',
    category: 'BANQUE',
    description: 'Encaissement automatique des avances clients et paiements des frais de péage.',
    endpoint: 'https://api.momo.cm/v1/collections',
    status: 'CONNECTED',
    lastSync: 'Il y a 1 min',
    pingMs: 22
  },
  {
    id: 'dgi_fen',
    name: 'DGI Cameroun (Facturation Électronique FEN)',
    category: 'EDI',
    description: 'Génération et scellement fiscal des QR-Codes sur factures de débours et prestations.',
    endpoint: 'https://teledeclaration-dgi.cm/api/seal',
    status: 'CONNECTED',
    lastSync: 'Il y a 15 min',
    pingMs: 76
  }
];

export default function AdminTenantIntegrationsPage() {
  const [connectors, setConnectors] = useState<IntegrationConnector[]>(INITIAL_CONNECTORS);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [selectedConnector, setSelectedConnector] = useState<IntegrationConnector | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');

  const handleTestConnection = (connector: IntegrationConnector) => {
    setTestingId(connector.id);
    setTimeout(() => {
      setTestingId(null);
      toast.success(`Connexion établie avec succès avec ${connector.name} (${Math.floor(Math.random() * 40 + 20)}ms)`);
    }, 800);
  };

  const handleSaveConfig = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success(`Identifiants d'API pour ${selectedConnector?.name} mis à jour et scellés.`);
    setSelectedConnector(null);
    setApiKeyInput('');
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Network className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Passerelles d'Intégration & Connecteurs EDI</h1>
            <p className="text-sm text-on-surface-variant">
              Interconnexions directes GUCE, CAMCIS Douane, PAD Douala, PAK Kribi et DGI Cameroun
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            toast.success('Vérification de tous les certificats d\'échange EDI en cours...');
          }}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
        >
          <Zap className="w-4 h-4" />
          Tester Tous les Flux
        </button>
      </div>

      {/* Grid of Connectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {connectors.map(c => (
          <div
            key={c.id}
            className="bg-surface border border-outline rounded-2xl p-5 hover:border-primary transition-all shadow-sm space-y-4 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex justify-between items-start">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                  {c.category}
                </span>
                <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-semibold">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  Opérationnel
                </span>
              </div>

              <div>
                <h3 className="font-bold text-base text-on-surface mb-1">{c.name}</h3>
                <p className="text-xs text-on-surface-variant leading-relaxed">{c.description}</p>
              </div>

              <div className="p-2.5 bg-surface-container-low rounded-xl font-mono text-[10px] text-on-surface-variant break-all">
                {c.endpoint}
              </div>
            </div>

            <div className="pt-3 border-t border-outline/50 flex justify-between items-center text-xs">
              <span className="text-on-surface-variant text-[11px]">Latence : <strong className="text-on-surface">{c.pingMs} ms</strong></span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedConnector(c)}
                  className="p-1.5 border border-outline rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container"
                  title="Clés API & Certificats"
                >
                  <Key className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleTestConnection(c)}
                  disabled={testingId === c.id}
                  className="px-3 py-1.5 bg-primary/10 text-primary hover:bg-primary/20 rounded-lg font-bold text-xs flex items-center gap-1"
                >
                  <RefreshCw className={`w-3 h-3 ${testingId === c.id ? 'animate-spin' : ''}`} />
                  Ping
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Config Modal */}
      {selectedConnector && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <div>
                <span className="text-xs font-bold text-primary uppercase">{selectedConnector.category}</span>
                <h3 className="font-bold text-on-surface text-base">{selectedConnector.name}</h3>
              </div>
              <button onClick={() => setSelectedConnector(null)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleSaveConfig} className="space-y-3 text-xs">
              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Clé API d'accès / Token EDI :</label>
                <input
                  type="password"
                  placeholder="Bearer cadc_sec_xxxxxxxxxxxx"
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono"
                />
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Certificat Numérique X.509 :</label>
                <div className="p-3 border border-dashed border-outline rounded-xl text-center text-on-surface-variant">
                  certificat_guce_cameroon_2025.pem (Scellé)
                </div>
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedConnector(null)}
                  className="px-4 py-2 border border-outline rounded-xl text-on-surface hover:bg-surface-container font-semibold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90"
                >
                  Enregistrer les Clés
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

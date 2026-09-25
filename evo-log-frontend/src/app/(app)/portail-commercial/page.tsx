'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp, Calculator, FileText, Users, PlusCircle,
  RefreshCw, DollarSign, ArrowRight, CheckCircle2, Clock,
  MapPin, Send, Download, Tag, Award, Percent
} from 'lucide-react';
import { cotationsAPI, partnerB2BAPI, tiersAPI, apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

interface DevisItem {
  id: number;
  reference?: string;
  client_nom?: string;
  corridor?: string;
  type_cargaison?: string;
  montant_total?: number;
  devise?: string;
  statut?: string;
  created_at?: string;
}

export default function PortailCommercialPage() {
  const [activeTab, setActiveTab] = useState<'simulateur' | 'pipeline' | 'clients' | 'commissions'>('simulateur');
  const [devisList, setDevisList] = useState<DevisItem[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Simulateur state
  const [simForm, setSimForm] = useState({
    corridor: 'DOUALA_NDJAMENA',
    type_conteneur: '40_DRY',
    poids_tonnes: '24',
    valeur_marchandise_xaf: '45000000',
    inclure_assurance: true,
    marge_commerciale_pct: '15',
  });

  const [calculResult, setCalculResult] = useState<any>(null);

  const calculateCotation = () => {
    const poids = parseFloat(simForm.poids_tonnes) || 1;
    const valeur = parseFloat(simForm.valeur_marchandise_xaf) || 10000000;
    const marge = parseFloat(simForm.marge_commerciale_pct) || 15;

    // Barèmes réels corridors CEMAC
    const tarifBaseCorridor = simForm.corridor === 'DOUALA_NDJAMENA' ? 3850000 : 3400000;
    const passagePortuairePAD = 450000;
    const droitsDouaneEstimes = valeur * 0.18; // TEC CEMAC moyen
    const fraisTransitDUM = 250000;
    const assurance = simForm.inclure_assurance ? valeur * 0.004 : 0;

    const coutTotalRevient = tarifBaseCorridor + passagePortuairePAD + fraisTransitDUM + assurance;
    const prixVenteFinal = coutTotalRevient * (1 + marge / 100);
    const margeNetteXAF = prixVenteFinal - coutTotalRevient;

    setCalculResult({
      tarifBaseCorridor,
      passagePortuairePAD,
      droitsDouaneEstimes,
      fraisTransitDUM,
      assurance,
      coutTotalRevient,
      prixVenteFinal,
      margeNetteXAF,
    });
  };

  useEffect(() => {
    calculateCotation();
  }, [simForm]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resDevis, resClients] = await Promise.all([
        cotationsAPI.getCotations(),
        tiersAPI.getClients(),
      ]);

      const listDevis = Array.isArray(resDevis.data) ? resDevis.data : (resDevis.data?.items || []);
      setDevisList(listDevis);

      const listClients = Array.isArray(resClients.data) ? resClients.data : (resClients.data?.items || []);
      setClients(listClients);
    } catch (err: any) {
      toast.error('Erreur chargement données commerciales');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleEmitDevis = async () => {
    try {
      await partnerB2BAPI.submitCotation({
        origine: 'Port Autonome de Douala',
        destination: simForm.corridor.replace('_', ' - '),
        type_conteneur: simForm.type_conteneur,
        poids_kg: (parseFloat(simForm.poids_tonnes) || 20) * 1000,
        montant_total: calculResult?.prixVenteFinal,
      });
      toast.success('Offre commerciale enregistrée et prête à être transmise au client');
      fetchData();
      setActiveTab('pipeline');
    } catch (err: any) {
      toast.error('Erreur création devis');
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-amber-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white border border-amber-900/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs font-bold uppercase tracking-wider">
            <TrendingUp className="w-3.5 h-3.5" /> Portail Collaborateur Commercial
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Espace Chargé d’Affaires & Devis CEMAC
          </h1>
          <p className="text-sm text-slate-300">
            Simulateur instantané de cotation transit & transport, pipeline de vente et portefeuille clients.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold border border-slate-700 transition-colors shadow-sm self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Actualiser
        </button>
      </div>

      {/* Tabs */}
      <div className="flex overflow-x-auto gap-2 p-1.5 bg-slate-900 rounded-2xl border border-slate-700">
        {[
          { id: 'simulateur', label: 'Simulateur Cotation Express', icon: Calculator },
          { id: 'pipeline', label: 'Pipeline Commercial & Devis', icon: FileText, count: devisList.length },
          { id: 'clients', label: 'Portefeuille Clients', icon: Users, count: clients.length },
          { id: 'commissions', label: 'Commissions & Objectifs', icon: Award },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-slate-900 text-slate-200 shadow-md border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/10'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-mono ${
                  isActive ? 'bg-slate-900 text-white' : 'bg-slate-700 text-slate-300'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Onglet 1 : Simulateur Cotation Express */}
      {activeTab === 'simulateur' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-4 shadow-sm">
            <h2 className="text-base font-bold text-slate-200 flex items-center gap-2 pb-3 border-b border-slate-700">
              <Calculator className="w-5 h-5 text-amber-600" /> Paramètres de l’Opération Logistique
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-300 block mb-1">Corridor Logistique</label>
                <select
                  value={simForm.corridor}
                  onChange={(e) => setSimForm({ ...simForm, corridor: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-amber-500 outline-none"
                >
                  <option value="DOUALA_NDJAMENA">Douala → N’Djamena (Tchad) - Corridor 1 850 km</option>
                  <option value="DOUALA_BANGUI">Douala → Bangui (RCA) - Corridor 1 450 km</option>
                  <option value="KRIBI_YAOUNDE">Port de Kribi → Yaoundé - Desserte Nationale</option>
                  <option value="DOUALA_LOCAL">Livraison Urbaine & Périphérie Douala</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-300 block mb-1">Type de Conteneur / Fret</label>
                  <select
                    value={simForm.type_conteneur}
                    onChange={(e) => setSimForm({ ...simForm, type_conteneur: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-amber-500 outline-none"
                  >
                    <option value="40_DRY">Conteneur 40' Dry Standard</option>
                    <option value="20_DRY">Conteneur 20' Dry Standard</option>
                    <option value="40_REEFER">Conteneur 40' Reefer Frigorifique</option>
                    <option value="CONVOI_EXCEPTIONNEL">Convoi Exceptionnel / Colis Lourd</option>
                  </select>
                </div>

                <div>
                  <label className="font-bold text-slate-300 block mb-1">Poids Brut (Tonnes)</label>
                  <input
                    type="number"
                    value={simForm.poids_tonnes}
                    onChange={(e) => setSimForm({ ...simForm, poids_tonnes: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-amber-500 outline-none font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-300 block mb-1">Valeur Marchandise CAF (XAF)</label>
                <input
                  type="number"
                  value={simForm.valeur_marchandise_xaf}
                  onChange={(e) => setSimForm({ ...simForm, valeur_marchandise_xaf: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-amber-500 outline-none font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-3 pt-1">
                <div>
                  <label className="font-bold text-slate-300 block mb-1">Marge Commerciale (%)</label>
                  <input
                    type="number"
                    value={simForm.marge_commerciale_pct}
                    onChange={(e) => setSimForm({ ...simForm, marge_commerciale_pct: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-amber-500 outline-none font-mono"
                  />
                </div>

                <div className="flex items-center pt-5">
                  <label className="flex items-center gap-2 cursor-pointer font-bold text-slate-300">
                    <input
                      type="checkbox"
                      checked={simForm.inclure_assurance}
                      onChange={(e) => setSimForm({ ...simForm, inclure_assurance: e.target.checked })}
                      className="rounded text-amber-600 w-4 h-4"
                    />
                    Assurance Ad Valorem
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Résultat Chiffré */}
          <div className="bg-gradient-to-br from-slate-900 to-amber-950 text-white rounded-2xl p-6 space-y-6 shadow-xl border border-amber-900/50 flex flex-col justify-between">
            <div className="space-y-4">
              <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">
                Décomposition Tarifaire Immédiate
              </span>

              <div className="space-y-2.5 text-xs">
                <div className="flex justify-between text-slate-300">
                  <span>Fret Routier Corridor CEMAC :</span>
                  <span className="font-mono font-bold text-white">{calculResult?.tarifBaseCorridor.toLocaleString()} XAF</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Passage Portuaire & Manutention Quai :</span>
                  <span className="font-mono font-bold text-white">{calculResult?.passagePortuairePAD.toLocaleString()} XAF</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Honoraires Déclaration & Transit DUM :</span>
                  <span className="font-mono font-bold text-white">{calculResult?.fraisTransitDUM.toLocaleString()} XAF</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Assurance Faculté Transportée :</span>
                  <span className="font-mono font-bold text-white">{calculResult?.assurance.toLocaleString()} XAF</span>
                </div>
                <div className="pt-2 border-t border-slate-800 flex justify-between text-slate-400">
                  <span>Coût de revient total :</span>
                  <span className="font-mono font-bold">{calculResult?.coutTotalRevient.toLocaleString()} XAF</span>
                </div>
                <div className="flex justify-between text-emerald-400 font-bold">
                  <span>Marge Commerciale ({simForm.marge_commerciale_pct}%) :</span>
                  <span className="font-mono">+{calculResult?.margeNetteXAF.toLocaleString()} XAF</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-amber-900/60 space-y-3">
              <div className="flex items-baseline justify-between">
                <span className="text-xs font-bold text-slate-300">PRIX PROPOSÉ CLIENT :</span>
                <span className="text-2xl font-mono font-black text-amber-400">
                  {calculResult?.prixVenteFinal.toLocaleString()} XAF
                </span>
              </div>

              <button
                onClick={handleEmitDevis}
                className="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 text-xs font-black uppercase tracking-wider transition-colors shadow-lg shadow-amber-500/20"
              >
                Générer et Transmettre le Devis Client
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Onglet 2 : Pipeline Commercial */}
      {activeTab === 'pipeline' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-700 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Vos Devis Émis & Négociations en Cours ({devisList.length})
            </h2>
          </div>

          <div className="divide-y divide-slate-800">
            {devisList.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                Aucun devis récent dans le pipeline.
              </div>
            ) : (
              devisList.map((d) => (
                <div key={d.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/80">
                  <div>
                    <div className="text-xs font-bold text-slate-200">Devis #{d.reference || `DEV-${d.id}`}</div>
                    <div className="text-[11px] text-slate-400">Client : {d.client_nom || 'Importateur CEMAC'}</div>
                    <div className="text-[10px] text-slate-400">Corridor : {d.corridor || 'Douala - N’Djamena'}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-mono font-bold text-slate-200">
                      {d.montant_total ? d.montant_total.toLocaleString() : '4 850 000'} XAF
                    </div>
                    <span className="text-[10px] font-bold text-emerald-600">Offre transmise</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Onglet 3 : Portefeuille Clients */}
      {activeTab === 'clients' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-700">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Comptes & Importateurs Suivis ({clients.length})
            </h2>
          </div>

          <div className="divide-y divide-slate-800">
            {clients.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                Aucun compte client assigné.
              </div>
            ) : (
              clients.map((c) => (
                <div key={c.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/80">
                  <div>
                    <div className="text-xs font-bold text-slate-200">{c.nom || c.raison_sociale || `Client #${c.id}`}</div>
                    <div className="text-[11px] text-slate-500">Ville : {c.ville || 'Douala'} • Téléphone : {c.telephone || '+237 6XX XX XX XX'}</div>
                  </div>
                  <div>
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-300">
                      Compte Actif
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Onglet 4 : Commissions & Objectifs */}
      {activeTab === 'commissions' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-6 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 text-slate-950 shadow-md space-y-1">
              <span className="text-xs font-black uppercase tracking-wider">Chiffre d’Affaires Réalisé</span>
              <div className="text-3xl font-black">48 500 000 XAF</div>
              <p className="text-xs font-bold opacity-80">Objectif mensuel : 50M XAF (97% atteint)</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-700 shadow-sm space-y-1">
              <span className="text-xs font-bold text-slate-500 uppercase">Commission Estimée</span>
              <div className="text-3xl font-black text-emerald-600">1 455 000 XAF</div>
              <p className="text-xs text-slate-500">Taux de commissionnement : 3%</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-700 shadow-sm space-y-1">
              <span className="text-xs font-bold text-indigo-600 uppercase">Contrats Signés</span>
              <div className="text-3xl font-black text-indigo-600">12 Dossiers</div>
              <p className="text-xs text-slate-500">Corridors Tchad et RCA</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

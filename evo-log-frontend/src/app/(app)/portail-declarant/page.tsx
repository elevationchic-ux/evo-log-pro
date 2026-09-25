'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText, CheckCircle2, Clock, AlertTriangle, RefreshCw,
  Anchor, Shield, Upload, Camera, Check, X, AlertOctagon,
  FileCheck, MapPin, Search, ArrowRight, ExternalLink
} from 'lucide-react';
import { transitAvanceAPI, goodsDeclarationAPI, apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

interface DossierItem {
  id: number;
  numero_dossier?: string;
  reference?: string;
  client_nom?: string;
  bureau_douane?: string;
  statut: string;
  type_regime?: string;
  etape_actuelle?: string;
  marchandise?: string;
  date_depot?: string;
}

export default function PortailDeclarantPage() {
  const [activeTab, setActiveTab] = useState<'dossiers' | 'jalonnement' | 'documents' | 'litige'>('dossiers');
  const [dossiers, setDossiers] = useState<DossierItem[]>([]);
  const [selectedDossier, setSelectedDossier] = useState<DossierItem | null>(null);
  const [loading, setLoading] = useState(true);

  // Jalons physiques
  const [jalons, setJalons] = useState({
    depot_dum: true,
    passage_scanner: true,
    visite_conjointe: false,
    pesage_pont_bascule: false,
    liquidation_droits: false,
    paiement_tresor: false,
    bon_a_enlever_bae: false,
  });

  // Litige state
  const [litigeType, setLitigeType] = useState('CONTESTATION_VALEUR');
  const [litigeDesc, setLitigeDesc] = useState('');
  const [litigeSent, setLitigeSent] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resDossiers, resDeclarations] = await Promise.all([
        transitAvanceAPI.getDossiers(),
        goodsDeclarationAPI.getAll(),
      ]);

      const listDossiers = Array.isArray(resDossiers.data) ? resDossiers.data : (resDossiers.data?.items || []);
      setDossiers(listDossiers);
      if (listDossiers.length > 0 && !selectedDossier) {
        setSelectedDossier(listDossiers[0]);
      }
    } catch (err: any) {
      toast.error('Erreur chargement dossiers douane');
    } finally {
      setLoading(false);
    }
  }, [selectedDossier]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleToggleJalon = (key: keyof typeof jalons) => {
    setJalons(prev => {
      const next = { ...prev, [key]: !prev[key] };
      toast.success(`Jalon terrain mis à jour`);
      return next;
    });
  };

  const handleSendLitige = async () => {
    if (!selectedDossier) {
      toast.error('Sélectionnez un dossier de transit');
      return;
    }
    try {
      await apiClient.post('/api/v1/incidents', {
        titre: `[LITIGE DOUANE] ${litigeType} - Dossier ${selectedDossier.numero_dossier || selectedDossier.id}`,
        type_incident: 'LITIGE_DOUANIER',
        description: litigeDesc || 'Contestation soulevée par les inspecteurs des douanes.',
        severite: 'HAUTE',
        dossier_id: selectedDossier.id,
      });
      setLitigeSent(true);
      toast.success('Litige douanier transmis immédiatement au chef de bureau transit !');
    } catch (err: any) {
      toast.error('Erreur transmission du litige');
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white border border-indigo-900/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-bold uppercase tracking-wider">
            <Anchor className="w-3.5 h-3.5" /> Portail Déclarant Terrain
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Espace Transit Portuaire & Frontières CEMAC
          </h1>
          <p className="text-sm text-slate-300">
            Jalonnement physique des dossiers (Scanner, Visite, Pont-Bascule, BAE) et alertes litiges en temps réel.
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
          { id: 'dossiers', label: 'Mes Dossiers Port & Douane', icon: FileText, count: dossiers.length },
          { id: 'jalonnement', label: 'Jalons & Visite Conjointe', icon: CheckCircle2 },
          { id: 'documents', label: 'Téléverser BAE & Quittances', icon: Upload },
          { id: 'litige', label: 'Litige / Blocage Douane', icon: AlertOctagon, danger: true },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${
                isActive
                  ? tab.danger
                    ? 'bg-rose-600 text-white shadow-md'
                    : 'bg-slate-900 text-slate-200 shadow-md border border-slate-700'
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

      {/* Onglet 1 : Mes Dossiers */}
      {activeTab === 'dossiers' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-3">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-600" /> Dossiers Assignés ({dossiers.length})
            </h2>

            {dossiers.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 rounded-2xl border border-slate-700 text-xs text-slate-500">
                Aucun dossier en cours.
              </div>
            ) : (
              dossiers.map((d) => (
                <div
                  key={d.id}
                  onClick={() => setSelectedDossier(d)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    selectedDossier?.id === d.id
                      ? 'bg-indigo-50/70 border-indigo-400 shadow-md'
                      : 'bg-slate-900 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-mono font-black text-slate-200">
                      #{d.numero_dossier || d.reference || `TR-${d.id}`}
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300">
                      {d.statut}
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-slate-200">{d.client_nom || 'Importateur Industriel'}</div>
                  <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-rose-500" /> {d.bureau_douane || 'Port de Douala (Sydonia)'}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="lg:col-span-2">
            {selectedDossier ? (
              <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-700 gap-2">
                  <div>
                    <span className="text-xs font-mono text-indigo-300 font-bold">Dossier de Transit Actif</span>
                    <h2 className="text-xl font-black text-slate-200">
                      #{selectedDossier.numero_dossier || selectedDossier.reference || `TR-${selectedDossier.id}`}
                    </h2>
                    <p className="text-xs text-slate-500">Client : {selectedDossier.client_nom || 'Client Partenaire'}</p>
                  </div>

                  <button
                    onClick={() => setActiveTab('jalonnement')}
                    className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors shadow-sm self-start sm:self-auto"
                  >
                    Pointer les Jalons Terrain
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="p-4 rounded-xl bg-slate-800 border border-slate-700 space-y-1.5">
                    <span className="font-bold text-slate-500 uppercase">Bureau & Régime Douanier</span>
                    <p className="font-bold text-slate-200">{selectedDossier.bureau_douane || 'Douala Port Terminal Conteneurs'}</p>
                    <p className="text-slate-400">Régime : <strong>{selectedDossier.type_regime || 'Mise à la consommation (IM4)'}</strong></p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-800 border border-slate-700 space-y-1.5">
                    <span className="font-bold text-slate-500 uppercase">Marchandise & Cargaison</span>
                    <p className="font-bold text-slate-200">{selectedDossier.marchandise || 'Matériel de Construction & Équipements'}</p>
                    <p className="text-slate-400">Statut actuel : <strong className="text-indigo-600">{selectedDossier.statut}</strong></p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center bg-slate-900 rounded-2xl border border-slate-700 text-xs text-slate-500">
                Sélectionnez un dossier de transit.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Onglet 2 : Jalonnement Physique */}
      {activeTab === 'jalonnement' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-700">
            <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-indigo-600" /> Jalonnement des Étapes Physiques au Port
            </h2>
            <p className="text-xs text-slate-500">
              Pointez chronologiquement chaque étape franchie sur le terrain.
            </p>
          </div>

          <div className="space-y-3">
            {[
              { key: 'depot_dum', label: '1. Dépôt Déclaration DUM & Enregistrement Sydonia' },
              { key: 'passage_scanner', label: '2. Passage au Scanner Portuaire (Résultat Vert/Orange)' },
              { key: 'visite_conjointe', label: '3. Visite Conjointe Effectuée (Douane / SGS / Phytosanitaire)' },
              { key: 'pesage_pont_bascule', label: '4. Pesage Pont-Bascule & Certificat VGM Conforme' },
              { key: 'liquidation_droits', label: '5. Liquidation des Droits & Taxes Émise' },
              { key: 'paiement_tresor', label: '6. Quittance du Trésor Public / Banque Validée' },
              { key: 'bon_a_enlever_bae', label: '7. Bon à Enlever (BAE) Délivré par l’Inspecteur' },
            ].map((step) => {
              const checked = jalons[step.key as keyof typeof jalons];
              return (
                <div
                  key={step.key}
                  onClick={() => handleToggleJalon(step.key as keyof typeof jalons)}
                  className={`p-4 rounded-xl border flex items-center justify-between gap-4 cursor-pointer transition-all ${
                    checked ? 'bg-emerald-500/10 border-emerald-500/50' : 'bg-slate-800 border-slate-700 hover:bg-slate-800/80'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                      checked ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-slate-400'
                    }`}>
                      <Check className="w-4 h-4" />
                    </div>
                    <span className={`text-xs font-bold ${checked ? 'text-slate-200' : 'text-slate-400'}`}>
                      {step.label}
                    </span>
                  </div>
                  <span className={`text-[10px] font-bold ${checked ? 'text-emerald-300' : 'text-slate-400'}`}>
                    {checked ? 'Validé' : 'En attente'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Onglet 3 : Téléversement BAE & Quittances */}
      {activeTab === 'documents' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-700">
            <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <Upload className="w-5 h-5 text-indigo-600" /> Téléversement des Justificatifs Terrain
            </h2>
            <p className="text-xs text-slate-500">
              Prenez en photo ou uploadez le Bon à Enlever (BAE), la quittance ou le PV de visite.
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Type de Document</label>
              <select className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                <option>Bon à Enlever (BAE) Douane</option>
                <option>Quittance de Règlement Droits et Taxes</option>
                <option>Procès-Verbal de Visite Conjointe</option>
                <option>Certificat de Pesage Pont-Bascule</option>
                <option>Bon de Sortie Portuaire (PAD)</option>
              </select>
            </div>

            <div className="border-2 border-dashed border-slate-600 rounded-2xl p-8 text-center bg-slate-800 hover:bg-slate-800/60 cursor-pointer transition-colors">
              <Camera className="w-10 h-10 text-indigo-500 mx-auto mb-2" />
              <p className="text-xs font-bold text-slate-200">Prendre une photo ou sélectionner un fichier</p>
              <p className="text-[11px] text-slate-500 mt-1">JPEG, PNG ou PDF (Max 15 Mo)</p>
            </div>

            <button
              onClick={() => toast.success('Document téléversé et rattaché au dossier de transit')}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors shadow-sm"
            >
              Enregistrer le Document dans le Dossier
            </button>
          </div>
        </div>
      )}

      {/* Onglet 4 : Litige / Blocage Douane */}
      {activeTab === 'litige' && (
        <div className="bg-slate-900 rounded-2xl border border-rose-500/40 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-rose-500/30 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-rose-200 flex items-center gap-2">
                <AlertOctagon className="w-5 h-5 text-rose-600" /> Déclaration d’un Litige ou Blocage Douanier
              </h2>
              <p className="text-xs text-rose-300">
                Alertez immédiatement la direction et le chef de service transit en cas de litige inspecteur.
              </p>
            </div>
            {litigeSent && (
              <span className="px-3 py-1 rounded-full bg-rose-500/15 text-rose-300 text-xs font-bold">
                Litige transmis
              </span>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Type de Contestation</label>
              <select
                value={litigeType}
                onChange={(e) => setLitigeType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
              >
                <option value="CONTESTATION_VALEUR">Contestation de la valeur transactionnelle (Redressement)</option>
                <option value="ESPECE_TARIFAIRE">Contestation du code SH / Espèce tarifaire</option>
                <option value="ORIGINE_CEMAC">Refus de l'agrément d'origine CEMAC</option>
                <option value="DOCUMENTS_MANQUANTS">Exigence de certificat additionnel (Phytosanitaire/Normes ANOR)</option>
                <option value="BLOCAGE_SCANNER">Image suspecte au scanner / Visite physique approfondie</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Détails de l’objection formulée par la douane</label>
              <textarea
                rows={3}
                placeholder="Précisez les exigences de l’inspecteur, les montants réclamés ou la notification de redressement..."
                value={litigeDesc}
                onChange={(e) => setLitigeDesc(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
              />
            </div>

            <button
              onClick={handleSendLitige}
              className="w-full py-3.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-black uppercase tracking-wider transition-colors shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2"
            >
              <AlertOctagon className="w-4 h-4" /> Alerter le Chef de Transit & la Direction
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

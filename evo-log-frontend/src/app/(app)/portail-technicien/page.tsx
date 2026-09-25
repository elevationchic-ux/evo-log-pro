'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Wrench, CheckCircle2, Clock, AlertTriangle, RefreshCw,
  Cpu, ClipboardList, Package, Save, ArrowRight, ShieldCheck,
  Camera, Check, X, Layers
} from 'lucide-react';
import { maintenanceGMAOAPI } from '@/lib/api-client';
import { toast } from 'sonner';

interface WorkOrder {
  id: number;
  numero_ot?: string;
  titre: string;
  equipement_nom?: string;
  immatriculation?: string;
  type_maintenance: string; // PREVENTIF ou CURATIF
  priorite: string;
  statut: string;
  description?: string;
  technicien_nom?: string;
  date_prevue?: string;
}

export default function PortailTechnicienPage() {
  const [activeTab, setActiveTab] = useState<'ot' | 'rapport' | 'pieces' | 'equipements'>('ot');
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [selectedOT, setSelectedOT] = useState<WorkOrder | null>(null);
  const [equipments, setEquipments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Rapport intervention state
  const [rapportForm, setRapportForm] = useState({
    duree_heures: '2.5',
    diagnostic: 'Usure anormale des plaquettes de frein essieu arrière gauche suite à parcours corridor Douala-Bangui.',
    travaux_effectues: 'Remplacement du jeu de plaquettes de frein, purge du circuit pneumatique et graissage des étriers.',
    pieces_utilisees: '2x Plaquettes de frein réf PL-558, 1L liquide de frein DOT4',
    statut_final: 'TERMINE',
  });
  const [submittingRapport, setSubmittingRapport] = useState(false);

  // Demande pièces state
  const [piecesForm, setPiecesForm] = useState({
    article: 'Filtre à gazole double cartouche',
    quantite: '2',
    urgence: 'URGENT',
    equipement: 'Tracteur Renault Kerax LT-TRUCK-889',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resOT, resEq] = await Promise.all([
        maintenanceGMAOAPI.getWorkOrders(),
        maintenanceGMAOAPI.getEquipment(),
      ]);

      const listOT = Array.isArray(resOT.data) ? resOT.data : (resOT.data?.items || []);
      setWorkOrders(listOT);
      if (listOT.length > 0 && !selectedOT) {
        setSelectedOT(listOT[0]);
      }

      const listEq = Array.isArray(resEq.data) ? resEq.data : (resEq.data?.items || []);
      setEquipments(listEq);
    } catch (err: any) {
      toast.error('Erreur de chargement GMAO');
    } finally {
      setLoading(false);
    }
  }, [selectedOT]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSubmitRapport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOT) {
      toast.error('Sélectionnez un ordre de travail');
      return;
    }
    setSubmittingRapport(true);
    try {
      await maintenanceGMAOAPI.updateWorkOrder(selectedOT.id, {
        statut: rapportForm.statut_final,
        description: `${selectedOT.description || ''}\n\n[RAPPORT INTERVENTION] : ${rapportForm.travaux_effectues} (Durée: ${rapportForm.duree_heures}h). Pièces: ${rapportForm.pieces_utilisees}`,
      });
      toast.success('Rapport d’intervention validé et clôturé avec succès');
      fetchData();
      setActiveTab('ot');
    } catch (err: any) {
      toast.error('Erreur enregistrement rapport');
    } finally {
      setSubmittingRapport(false);
    }
  };

  const handleDemandePieces = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('Demande de pièces transmise au magasin de pièces détachées');
    setPiecesForm({
      article: '',
      quantite: '1',
      urgence: 'NORMAL',
      equipement: '',
    });
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-purple-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white border border-purple-900/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30 text-xs font-bold uppercase tracking-wider">
            <Wrench className="w-3.5 h-3.5" /> Portail Technicien GMAO
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Espace Atelier Mécanique & Maintenance
          </h1>
          <p className="text-sm text-slate-300">
            Gestion de vos Ordres de Travail (OT), rapports d’intervention terrain et demandes de pièces au magasin.
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
          { id: 'ot', label: 'Mes Ordres de Travail (OT)', icon: ClipboardList, count: workOrders.length },
          { id: 'rapport', label: 'Saisir Rapport d’Intervention', icon: Save },
          { id: 'pieces', label: 'Demande Pièces Magasin', icon: Package },
          { id: 'equipements', label: 'Parc Équipements', icon: Cpu, count: equipments.length },
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

      {/* Onglet 1 : Mes OT */}
      {activeTab === 'ot' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-3">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Wrench className="w-4 h-4 text-purple-600" /> Vos Interventions ({workOrders.length})
            </h2>

            {workOrders.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 rounded-2xl border border-slate-700 text-xs text-slate-500">
                Aucun ordre de travail assigné.
              </div>
            ) : (
              workOrders.map((ot) => (
                <div
                  key={ot.id}
                  onClick={() => setSelectedOT(ot)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    selectedOT?.id === ot.id
                      ? 'bg-purple-50/70 border-purple-400 shadow-md'
                      : 'bg-slate-900 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-mono font-black text-slate-200">
                      #{ot.numero_ot || `OT-${ot.id}`}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      ot.type_maintenance === 'CURATIF' ? 'bg-rose-500/15 text-rose-300' : 'bg-blue-500/15 text-blue-300'
                    }`}>
                      {ot.type_maintenance}
                    </span>
                  </div>
                  <div className="text-xs font-bold text-slate-200">{ot.titre}</div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Équipement : {ot.equipement_nom || ot.immatriculation || 'Tracteur Flotte'}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="lg:col-span-2">
            {selectedOT ? (
              <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-700 gap-2">
                  <div>
                    <span className="text-xs font-mono text-purple-300 font-bold">Ordre de Travail Sélectionné</span>
                    <h2 className="text-xl font-black text-slate-200">{selectedOT.titre}</h2>
                    <p className="text-xs text-slate-500">N° #{selectedOT.numero_ot || `OT-${selectedOT.id}`}</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('rapport')}
                    className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold transition-colors shadow-sm self-start sm:self-auto"
                  >
                    Rédiger le Rapport
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="p-4 rounded-xl bg-slate-800 border border-slate-700 space-y-1.5">
                    <span className="font-bold text-slate-500 uppercase">Détails Véhicule / Équipement</span>
                    <p className="font-bold text-slate-200">{selectedOT.equipement_nom || selectedOT.immatriculation || 'Tracteur Routier'}</p>
                    <p className="text-slate-400">Priorité : <strong className="text-rose-600">{selectedOT.priorite}</strong></p>
                    <p className="text-slate-400">Statut : <strong>{selectedOT.statut}</strong></p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-800 border border-slate-700 space-y-1.5">
                    <span className="font-bold text-slate-500 uppercase">Consignes d’Intervention</span>
                    <p className="text-slate-300 leading-relaxed">{selectedOT.description || 'Contrôle complet et révision'}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center bg-slate-900 rounded-2xl border border-slate-700 text-xs text-slate-500">
                Sélectionnez un ordre de travail pour afficher ses détails.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Onglet 2 : Rapport d'Intervention */}
      {activeTab === 'rapport' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-700">
            <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <Save className="w-5 h-5 text-purple-600" /> Saisie du Compte-Rendu d’Intervention
            </h2>
            <p className="text-xs text-slate-500">
              Clôturez l’intervention en consignant les pièces utilisées et le temps passé.
            </p>
          </div>

          <form onSubmit={handleSubmitRapport} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">OT Concerne</label>
              <input
                type="text"
                disabled
                value={selectedOT ? `#${selectedOT.numero_ot || selectedOT.id} - ${selectedOT.titre}` : 'Aucun OT sélectionné'}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-400 font-semibold"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Temps Passé (Heures)</label>
                <input
                  type="number"
                  step="0.5"
                  required
                  value={rapportForm.duree_heures}
                  onChange={(e) => setRapportForm({ ...rapportForm, duree_heures: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-purple-500 outline-none font-mono"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Statut Final</label>
                <select
                  value={rapportForm.statut_final}
                  onChange={(e) => setRapportForm({ ...rapportForm, statut_final: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-purple-500 outline-none"
                >
                  <option value="TERMINE">Intervention Terminée (Opérationnel)</option>
                  <option value="EN_ATTENTE_PIECES">En Attente de Pièces de Rechange</option>
                  <option value="A_ESSAYER">Travaux Finis - En Attente d'Essai Route</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Diagnostic Réalisé</label>
              <textarea
                rows={2}
                value={rapportForm.diagnostic}
                onChange={(e) => setRapportForm({ ...rapportForm, diagnostic: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Détail des Travaux Effectués</label>
              <textarea
                rows={3}
                value={rapportForm.travaux_effectues}
                onChange={(e) => setRapportForm({ ...rapportForm, travaux_effectues: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Pièces Consommées</label>
              <input
                type="text"
                value={rapportForm.pieces_utilisees}
                onChange={(e) => setRapportForm({ ...rapportForm, pieces_utilisees: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={submittingRapport || !selectedOT}
              className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white text-xs font-bold transition-colors shadow-sm"
            >
              {submittingRapport ? 'Enregistrement...' : 'Enregistrer le Rapport d’Intervention'}
            </button>
          </form>
        </div>
      )}

      {/* Onglet 3 : Demande Pièces Magasin */}
      {activeTab === 'pieces' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-700">
            <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <Package className="w-5 h-5 text-indigo-600" /> Demande de Pièces au Magasin
            </h2>
            <p className="text-xs text-slate-500">
              Commandez en direct les pièces nécessaires auprès du responsable de stock pièces détachées.
            </p>
          </div>

          <form onSubmit={handleDemandePieces} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Désignation / Référence Pièce</label>
              <input
                type="text"
                required
                placeholder="Ex: Filtre à gazole, Courroie alternateur..."
                value={piecesForm.article}
                onChange={(e) => setPiecesForm({ ...piecesForm, article: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Quantité Souhaitée</label>
                <input
                  type="number"
                  required
                  value={piecesForm.quantite}
                  onChange={(e) => setPiecesForm({ ...piecesForm, quantite: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none font-mono"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Degré d'Urgence</label>
                <select
                  value={piecesForm.urgence}
                  onChange={(e) => setPiecesForm({ ...piecesForm, urgence: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="NORMAL">Normal (Stock magasin)</option>
                  <option value="URGENT">Urgent (Camion immobilisé)</option>
                  <option value="CRITIQUE">Critique (Blocage corridor)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Véhicule / Équipement Destinataire</label>
              <input
                type="text"
                placeholder="Ex: LT-TRUCK-889"
                value={piecesForm.equipement}
                onChange={(e) => setPiecesForm({ ...piecesForm, equipement: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors shadow-sm"
            >
              Transmettre la Demande au Magasin
            </button>
          </form>
        </div>
      )}

      {/* Onglet 4 : Parc Équipements */}
      {activeTab === 'equipements' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-700 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Parc des Véhicules & Équipements GMAO ({equipments.length})
            </h2>
          </div>

          <div className="divide-y divide-slate-800">
            {equipments.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                Aucun équipement enregistré.
              </div>
            ) : (
              equipments.map((eq) => (
                <div key={eq.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/80">
                  <div>
                    <div className="text-xs font-bold text-slate-200">{eq.nom || eq.immatriculation || `Équipement #${eq.id}`}</div>
                    <div className="text-[11px] text-slate-500">Catégorie : {eq.categorie || 'Poids Lourd'} • Marque : {eq.marque || 'Renault / Mercedes'}</div>
                  </div>
                  <div className="text-right">
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                      eq.statut === 'OPERATIONNEL' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'
                    }`}>
                      {eq.statut || 'EN SERVICE'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Warehouse, Package, CheckCircle2, Clock, AlertTriangle,
  RefreshCw, Check, ArrowRight, ShieldCheck, Box, Search,
  QrCode, ClipboardList, Layers, Truck, X
} from 'lucide-react';
import { removalSlipAPI, receptionMag3API, apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { TermDefinition } from '@/components/shared/TermDefinition';

interface PickingOrder {
  id: number;
  reference: string;
  client: string;
  destination: string;
  articles: Array<{
    code: string;
    designation: string;
    emplacement: string;
    lot: string;
    quantite: number;
    picked: boolean;
  }>;
  statut: string;
}

interface ReceptionItem {
  id: number;
  numero_bl: string;
  fournisseur: string;
  nb_colis: number;
  conteneur_ref?: string;
  statut: string;
  date_arrivee?: string;
}

export default function PortailMagasinierPage() {
  const [activeTab, setActiveTab] = useState<'picking' | 'reception' | 'inventaire' | 'chariot'>('picking');
  const [loading, setLoading] = useState(true);

  // Picking state
  const [pickingOrders, setPickingOrders] = useState<PickingOrder[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<PickingOrder | null>(null);

  // Reception state
  const [receptions, setReceptions] = useState<ReceptionItem[]>([]);

  // Chariot checklist
  const [chariotChecklist, setChariotChecklist] = useState({
    batterie_fluides: true,
    fourches_chaines: true,
    freins_direction: true,
    klaxon_gyrophare: true,
    extincteur_embarque: true,
    ceinture_securite: true,
  });
  const [chariotValidated, setChariotValidated] = useState(false);

  // Inventaire state
  const [inventaireItems, setInventaireItems] = useState([
    { id: 1, code: 'ART-CEMAC-01', designation: 'Huile Moteur 15W40 200L', emplacement: 'A-03-N2', qte_theorique: 42, qte_reelle: '' },
    { id: 2, code: 'ART-CEMAC-02', designation: 'Filtre à Gazole Poids Lourd', emplacement: 'B-12-N1', qte_theorique: 120, qte_reelle: '' },
    { id: 3, code: 'ART-CEMAC-03', designation: 'Pneu Poids Lourd 315/80 R22.5', emplacement: 'C-01-SOL', qte_theorique: 18, qte_reelle: '' },
  ]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resSlips, resReceptions] = await Promise.all([
        removalSlipAPI.getAll(),
        receptionMag3API.getAll(),
      ]);

      const rawSlips = resSlips?.data?.items || resSlips?.data || [];
      const formattedPicking: PickingOrder[] = rawSlips.map((s: any, idx: number) => ({
        id: s.id || idx + 1,
        reference: s.numero_bon || `BE-${s.id}`,
        client: s.client_nom || s.destinataire || 'Client Industriel',
        destination: s.destination || 'Zone Expédition Quai 4',
        statut: s.statut || 'EN_COURS',
        articles: [
          {
            code: 'ART-PKG-01',
            designation: 'Sacs Polypropylène 50kg',
            emplacement: `Allée A - Travée 0${idx + 1} - Niv 2`,
            lot: 'LOT-2026-F01',
            quantite: 50,
            picked: false,
          },
          {
            code: 'ART-PKG-02',
            designation: 'Huile Industrielle Fût 200L',
            emplacement: `Allée B - Travée 0${idx + 2} - Niv 1`,
            lot: 'LOT-2026-F02',
            quantite: 10,
            picked: false,
          },
        ],
      }));

      setPickingOrders(formattedPicking);
      if (formattedPicking.length > 0 && !selectedOrder) {
        setSelectedOrder(formattedPicking[0]);
      }

      const rawRec = resReceptions?.data?.items || resReceptions?.data || [];
      setReceptions(rawRec);
    } catch (err: any) {
      toast.error('Erreur chargement données entrepôt');
    } finally {
      setLoading(false);
    }
  }, [selectedOrder]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleTogglePick = (articleIndex: number) => {
    if (!selectedOrder) return;
    const updated = { ...selectedOrder };
    updated.articles[articleIndex].picked = !updated.articles[articleIndex].picked;
    setSelectedOrder(updated);

    const allDone = updated.articles.every((a) => a.picked);
    if (allDone) {
      toast.error('Le prélèvement doit être confirmé par le service WMS persistant.');
    }
  };

  const handleValidateReception = async (id: number) => {
    try {
      await receptionMag3API.validate(id);
      toast.error('La réception quai doit être validée par le service WMS persistant.');
      fetchData();
    } catch (err: any) {
      toast.error('Erreur lors de la validation de réception');
    }
  };

  const handleSaveInventaire = () => {
    toast.error('Le comptage doit être enregistré par le service inventaire persistant.');
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-cyan-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white border border-cyan-900/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-bold uppercase tracking-wider">
            <Warehouse className="w-3.5 h-3.5" /> Portail Magasinier & Quai
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Espace Opérateur Logistique & Stock
          </h1>
          <p className="text-sm text-slate-300">
            Préparation de commandes (Picking FEFO), pointage des réceptions quai, inventaires et sécurité engins.
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
      <div className="flex overflow-x-auto gap-2 p-1.5 bg-slate-100 rounded-2xl border border-slate-200">
        {[
          { id: 'picking', label: 'Ordres de Préparation (Picking)', icon: Package, count: pickingOrders.length },
          { id: 'reception', label: 'Réceptions & Dépotage Quai', icon: Truck, count: receptions.length },
          { id: 'inventaire', label: 'Inventaire Tournant', icon: ClipboardList },
          { id: 'chariot', label: 'Checklist Engin / Chariot', icon: ShieldCheck },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-white text-slate-900 shadow-md border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-mono ${
                  isActive ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-700'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Onglet 1 : Picking */}
      {activeTab === 'picking' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-3">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <Package className="w-4 h-4 text-cyan-600" /> Ordres de Sortie à Préparer ({pickingOrders.length})
            </h2>

            {pickingOrders.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-xs text-slate-500">
                Aucun ordre de préparation en attente.
              </div>
            ) : (
              pickingOrders.map((o) => (
                <div
                  key={o.id}
                  onClick={() => setSelectedOrder(o)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    selectedOrder?.id === o.id
                      ? 'bg-cyan-50/70 border-cyan-400 shadow-md'
                      : 'bg-white border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-mono font-black text-slate-900">#{o.reference}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-100 text-cyan-800">
                      {o.statut}
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-slate-800">{o.client}</div>
                  <div className="text-[11px] text-slate-500 mt-1">Dest : {o.destination}</div>
                </div>
              ))
            )}
          </div>

          <div className="lg:col-span-2">
            {selectedOrder ? (
              <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
                  <div>
                    <span className="text-xs font-mono text-cyan-700 font-bold">Bon de Préparation</span>
                    <h2 className="text-xl font-black text-slate-900">#{selectedOrder.reference}</h2>
                    <p className="text-xs text-slate-500">Client : {selectedOrder.client}</p>
                  </div>
                  <button
                    onClick={() => toast.error('La mise à quai doit être confirmée par le service WMS persistant.')}
                    className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-bold transition-colors shadow-sm self-start sm:self-auto"
                  >
                    Valider le Bon de Sortie
                  </button>
                </div>

                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1.5">
                    Articles à Prélever (<TermDefinition term="FEFO" /> / <TermDefinition term="FIFO" />)
                  </h3>
                  {selectedOrder.articles.map((art, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleTogglePick(idx)}
                      className={`p-4 rounded-xl border flex items-center justify-between gap-4 cursor-pointer transition-all ${
                        art.picked
                          ? 'bg-emerald-50 border-emerald-300'
                          : 'bg-slate-50 border-slate-200 hover:bg-slate-100/80'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                          art.picked ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-600'
                        }`}>
                          <Check className="w-4 h-4" />
                        </div>
                        <div>
                          <div className={`text-xs font-bold ${art.picked ? 'line-through text-slate-400' : 'text-slate-900'}`}>
                            {art.designation}
                          </div>
                          <div className="text-[11px] text-slate-500 font-mono">
                            Emplacement : <strong className="text-indigo-600">{art.emplacement}</strong> • Lot : {art.lot}
                          </div>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="text-sm font-mono font-bold text-slate-900">Qté : {art.quantite}</div>
                        <span className={`text-[10px] font-bold ${art.picked ? 'text-emerald-600' : 'text-slate-400'}`}>
                          {art.picked ? 'Prélevé' : 'À prélever'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 text-xs text-slate-500">
                Sélectionnez un ordre de préparation.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Onglet 2 : Réceptions Quai */}
      {activeTab === 'reception' && (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
              Réceptions Quai & Dépotage Conteneurs ({receptions.length})
            </h2>
          </div>

          <div className="divide-y divide-slate-100">
            {receptions.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                Aucune réception en attente de déchargement.
              </div>
            ) : (
              receptions.map((r) => (
                <div key={r.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/80">
                  <div className="space-y-1">
                    <div className="text-xs font-bold text-slate-900">BL #{r.numero_bl}</div>
                    <div className="text-[11px] text-slate-600">Fournisseur : {r.fournisseur}</div>
                    {r.conteneur_ref && (
                      <div className="text-[10px] font-mono text-indigo-600">Conteneur : {r.conteneur_ref}</div>
                    )}
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right text-xs">
                      <div className="font-bold text-slate-900">{r.nb_colis} Colis</div>
                      <span className="text-[10px] font-mono text-emerald-600 font-bold">{r.statut}</span>
                    </div>

                    <button
                      onClick={() => handleValidateReception(r.id)}
                      className="px-3 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-bold transition-colors shadow-sm"
                    >
                      Pointer Réception
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Onglet 3 : Inventaire Tournant */}
      {activeTab === 'inventaire' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 max-w-3xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-100">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <ClipboardList className="w-5 h-5 text-indigo-600" /> Missions d’Inventaire Tournant
            </h2>
            <p className="text-xs text-slate-500">
              Comptage physique aveugle sur les emplacements assignés du jour.
            </p>
          </div>

          <div className="space-y-3">
            {inventaireItems.map((item, idx) => (
              <div key={item.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="text-xs font-bold text-slate-900">{item.designation}</div>
                  <div className="text-[11px] text-indigo-600 font-mono">Emplacement : {item.emplacement}</div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500">Qté comptée :</span>
                  <input
                    type="number"
                    inputMode="numeric"
                    placeholder="Saisir..."
                    value={item.qte_reelle}
                    onChange={(e) => {
                      const updated = [...inventaireItems];
                      updated[idx].qte_reelle = e.target.value;
                      setInventaireItems(updated);
                    }}
                    className="w-24 px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-indigo-500 outline-none font-mono"
                  />
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleSaveInventaire}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors shadow-sm"
          >
            Enregistrer et Transmettre le Comptage
          </button>
        </div>
      )}

      {/* Onglet 4 : Checklist Chariot */}
      {activeTab === 'chariot' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" /> Prise de Poste Chariot Élévateur & Gerbeur
              </h2>
              <p className="text-xs text-slate-500">
                Contrôle préventif obligatoire avant mise en mouvement des engins de levage.
              </p>
            </div>
            {chariotValidated && (
              <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                Engin Validé
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { key: 'batterie_fluides', label: 'Niveau Batterie / Carburant & Huile' },
              { key: 'fourches_chaines', label: 'État des Fourches & Chaînes de Mât' },
              { key: 'freins_direction', label: 'Freinage de Service & Direction' },
              { key: 'klaxon_gyrophare', label: 'Avertisseur Sonore & Gyrophare' },
              { key: 'extincteur_embarque', label: 'Extincteur Présent & Plombé' },
              { key: 'ceinture_securite', label: 'Ceinture de Sécurité Fonctionnelle' },
            ].map((item) => (
              <label
                key={item.key}
                className={`flex items-start gap-3 p-3.5 rounded-xl border cursor-pointer transition-all ${
                  chariotChecklist[item.key as keyof typeof chariotChecklist]
                    ? 'bg-emerald-50/60 border-emerald-300'
                    : 'bg-rose-50/60 border-rose-300'
                }`}
              >
                <input
                  type="checkbox"
                  checked={chariotChecklist[item.key as keyof typeof chariotChecklist]}
                  onChange={(e) => setChariotChecklist({ ...chariotChecklist, [item.key]: e.target.checked })}
                  className="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                />
                <span className="text-xs font-semibold text-slate-900">{item.label}</span>
              </label>
            ))}
          </div>

          <button
            onClick={() => {
              setChariotValidated(true);
              toast.error('Le contrôle engin doit être archivé par le service maintenance persistant.');
            }}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors shadow-sm"
          >
            Valider la Prise de Poste de l’Engin
          </button>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Warehouse, Package, CheckCircle2, Clock, AlertTriangle,
  RefreshCw, Check, ArrowRight, ShieldCheck, Box, Search,
  QrCode, ClipboardList, Layers, Truck, X
} from 'lucide-react';
import { removalSlipAPI, receptionMag3API, magasinAPI } from '@/lib/api-client';
import api from '@/lib/api';
import { toast } from 'sonner';
import { TermDefinition } from '@/components/shared/TermDefinition';

// Échappement HTML pour la fiche imprimable (données saisies par l'opérateur).
function esc(v: unknown): string {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

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

interface InventaireItem {
  id: number;
  code: string;
  designation: string;
  emplacement: string;
  qte_theorique: number;
  qte_reelle: string;
}

export default function PortailMagasinierPage() {
  const [activeTab, setActiveTab] = useState<'picking' | 'reception' | 'inventaire' | 'chariot'>('picking');
  const [loading, setLoading] = useState(true);

  // Picking state
  const [pickingOrders, setPickingOrders] = useState<PickingOrder[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<PickingOrder | null>(null);
  const [validatingBon, setValidatingBon] = useState(false);

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

  // Inventaire state  alimenté depuis les stocks réels (magasinAPI.getStocks)
  const [inventaireItems, setInventaireItems] = useState<InventaireItem[]>([]);
  const [inventaireLoading, setInventaireLoading] = useState(false);
  const [regularisant, setRegularisant] = useState(false);
  const inventaireLoadedRef = useRef(false);

  const loadInventaire = useCallback(async () => {
    setInventaireLoading(true);
    try {
      const res = await magasinAPI.getStocks({ limit: 100 });
      const stocks = Array.isArray(res?.data) ? res.data : res?.data?.items || [];
      setInventaireItems(
        stocks.map((st: any) => ({
          id: st.id,
          code: st.code_article || '',
          designation: st.designation || '',
          emplacement: st.emplacement || '',
          qte_theorique: Number(st.quantite_disponible ?? 0),
          qte_reelle: '',
        }))
      );
      inventaireLoadedRef.current = true;
    } catch {
      toast.error('Erreur chargement des stocks pour l\'inventaire');
    } finally {
      setInventaireLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'inventaire' && !inventaireLoadedRef.current && !inventaireLoading) {
      loadInventaire();
    }
  }, [activeTab, inventaireLoading, loadInventaire]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resSlips, resReceptions] = await Promise.all([
        removalSlipAPI.getAll(),
        receptionMag3API.getAll(),
      ]);

      const rawSlips = resSlips?.data?.items || resSlips?.data || [];
      // Lignes réelles : chaque bon est rechargé via son détail (removalSlipAPI.getById)
      // car la liste ne retourne que nombre_lignes. Aucun article n'est inventé.
      const formattedPicking: PickingOrder[] = await Promise.all(
        rawSlips.map(async (s: any, idx: number) => {
          let articles: PickingOrder['articles'] = [];
          try {
            const detail = await removalSlipAPI.getById(s.id);
            const lignes = detail?.data?.lignes || [];
            articles = lignes.map((l: any) => ({
              code: l.code_article || '',
              designation: l.designation || 'Article sans désignation',
              emplacement: l.emplacement || '',
              lot: l.numero_lot || '',
              quantite: Number(l.quantite_sortie) || 0,
              picked: false,
            }));
          } catch {
            // Détail inaccessible : afficher le bon sans lignes plutôt que d'inventer des articles
          }
          return {
            id: s.id || idx + 1,
            reference: s.numero_bon || `BE-${s.id}`,
            client: s.client_nom || s.destinataire || '',
            destination: s.destination || s.entrepot_nom || '',
            statut: s.statut || 'EN_COURS',
            articles,
          };
        })
      );

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
      toast.success('Tous les articles ont été prélevés ! Commande prête pour mise à quai.');
    }
  };

  const handleValidateReception = async (id: number) => {
    try {
      await receptionMag3API.validate(id);
      toast.success('Réception quai validée et enregistrée en stock');
      fetchData();
    } catch (err: any) {
      toast.error('Erreur lors de la validation de réception');
    }
  };

  const handleValidateBonSortie = async () => {
    if (!selectedOrder) return;
    setValidatingBon(true);
    try {
      await removalSlipAPI.validate(selectedOrder.id);
      toast.success(`Bon #${selectedOrder.reference} validé : stock décrémenté en entrepôt`);
      await fetchData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur lors de la validation du bon de sortie');
    } finally {
      setValidatingBon(false);
    }
  };

  const handleSaveInventaire = async () => {
    const counted = inventaireItems.filter((i) => i.qte_reelle !== '');
    if (counted.length === 0) {
      toast.error('Aucun comptage saisi : entrez au moins une quantité physique.');
      return;
    }
    setRegularisant(true);
    try {
      // Régularisation réelle côté backend : calcul des écarts et génération du PV OHADA
      // (POST /api/v1/magasin-wms-avance/inventaire/regulariser).
      const campagne_id = Math.floor(Date.now() / 1000) % 100000;
      const res = await api.post('/api/v1/magasin-wms-avance/inventaire/regulariser', {
        campagne_id,
        lignes_comptage: counted.map((i) => ({
          article_code: i.code,
          emplacement: i.emplacement,
          quantite_physique: Number(i.qte_reelle) || 0,
          quantite_theorique: i.qte_theorique,
        })),
      });
      const r = res.data || {};
      toast.success(
        `Inventaire régularisé : ${r.nb_articles_controles ?? counted.length} article(s) contrôlé(s), ${r.nb_ecarts_detectes ?? 0} écart(s). PV ${r.pv_reference ?? ''}`
      );
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur lors de la régularisation de l\'inventaire');
    } finally {
      setRegularisant(false);
    }
  };

  // Fiche de prise de poste : génération d'un document signé imprimable (registre GMAO papier).
  const handleValiderChariot = () => {
    setChariotValidated(true);
    const libelles: Record<string, string> = {
      batterie_fluides: 'Niveau Batterie / Carburant & Huile',
      fourches_chaines: 'État des Fourches & Chaînes de Mât',
      freins_direction: 'Freinage de Service & Direction',
      klaxon_gyrophare: 'Avertisseur Sonore & Gyrophare',
      extincteur_embarque: 'Extincteur Présent & Plombé',
      ceinture_securite: 'Ceinture de Sécurité Fonctionnelle',
    };
    const win = window.open('', '_blank', 'width=800,height=600');
    if (!win) {
      toast.success('Prise de poste validée pour cette session.');
      return;
    }
    const lignes = Object.entries(chariotChecklist)
      .map(([k, v]) => `<tr><td>${esc(libelles[k] || k)}</td><td style="text-align:center;font-weight:bold;color:${v ? '#047857' : '#b91c1c'}">${v ? 'CONFORME' : 'NON CONFORME'}</td></tr>`)
      .join('');
    win.document.write(`<!DOCTYPE html><html lang="fr"><head><title>Fiche de Prise de Poste Engin</title></head>
      <body style="font-family:Arial,sans-serif;padding:32px;color:#0f172a">
        <h1>Fiche de Prise de Poste  Engin de Manutention</h1>
        <p><strong>Date :</strong> ${esc(new Date().toLocaleString('fr-FR'))}</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%;margin-top:16px">
          <thead><tr><th>Point de contrôle</th><th>Résultat</th></tr></thead>
          <tbody>${lignes}</tbody>
        </table>
        <p style="margin-top:48px">Signature du magasinier : ______________________ &nbsp;&nbsp;&nbsp; Visa responsable de quai : ______________________</p>
        <script>window.print()</script>
      </body></html>`);
    win.document.close();
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
      <div className="flex overflow-x-auto gap-2 p-1.5 bg-slate-800/50 rounded-2xl border border-slate-700">
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
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${isActive
                  ? 'bg-slate-800 text-white shadow-md border border-slate-700'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-mono ${isActive ? 'bg-slate-200 text-slate-900' : 'bg-slate-700 text-slate-300'
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
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Package className="w-4 h-4 text-cyan-400" /> Ordres de Sortie à Préparer ({pickingOrders.length})
            </h2>

            {pickingOrders.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 rounded-2xl border border-slate-700 text-xs text-slate-500">
                Aucun ordre de préparation en attente.
              </div>
            ) : (
              pickingOrders.map((o) => (
                <div
                  key={o.id}
                  onClick={() => setSelectedOrder(o)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${selectedOrder?.id === o.id
                      ? 'bg-cyan-900/30 border-cyan-500 shadow-md'
                      : 'bg-slate-900 border-slate-700 hover:border-slate-600'
                    }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-mono font-black text-white">#{o.reference}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300">
                      {o.statut}
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-slate-200">{o.client}</div>
                  <div className="text-[11px] text-slate-500 mt-1">Dest : {o.destination}</div>
                </div>
              ))
            )}
          </div>

          <div className="lg:col-span-2">
            {selectedOrder ? (
              <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
                  <div>
                    <span className="text-xs font-mono text-cyan-400 font-bold">Bon de Préparation</span>
                    <h2 className="text-xl font-black text-white">#{selectedOrder.reference}</h2>
                    <p className="text-xs text-slate-500">Client : {selectedOrder.client}</p>
                  </div>
                  <button
                    onClick={handleValidateBonSortie}
                    disabled={validatingBon || selectedOrder.statut === 'valide'}
                    className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-bold transition-colors shadow-sm self-start sm:self-auto"
                  >
                    {validatingBon
                      ? 'Validation…'
                      : selectedOrder.statut === 'valide'
                        ? 'Bon déjà validé'
                        : 'Valider le Bon de Sortie'}
                  </button>
                </div>

                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1.5">
                    Articles à Prélever (<TermDefinition term="FEFO" /> / <TermDefinition term="FIFO" />)
                  </h3>
                  {selectedOrder.articles.length === 0 && (
                    <div className="p-6 text-center text-xs text-slate-500 border border-dashed border-slate-700 rounded-xl">
                      Aucune ligne enregistrée sur ce bon. Saisir les articles via le module
                      Bons de Sortie avant préparation.
                    </div>
                  )}
                  {selectedOrder.articles.map((art, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleTogglePick(idx)}
                      className={`p-4 rounded-xl border flex items-center justify-between gap-4 cursor-pointer transition-all ${art.picked
                          ? 'bg-emerald-900/20 border-emerald-700'
                          : 'bg-slate-800 border-slate-700 hover:bg-slate-700/80'
                        }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${art.picked ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-slate-400'
                          }`}>
                          <Check className="w-4 h-4" />
                        </div>
                        <div>
                          <div className={`text-xs font-bold ${art.picked ? 'line-through text-slate-400' : 'text-white'}`}>
                            {art.designation}
                          </div>
                          <div className="text-[11px] text-slate-500 font-mono">
                            Emplacement : <strong className="text-indigo-400">{art.emplacement}</strong> • Lot : {art.lot}
                          </div>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="text-sm font-mono font-bold text-white">Qté : {art.quantite}</div>
                        <span className={`text-[10px] font-bold ${art.picked ? 'text-emerald-600' : 'text-slate-400'}`}>
                          {art.picked ? 'Prélevé' : 'À prélever'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-12 text-center bg-slate-900 rounded-2xl border border-slate-700 text-xs text-slate-500">
                Sélectionnez un ordre de préparation.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Onglet 2 : Réceptions Quai */}
      {activeTab === 'reception' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-800">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Réceptions Quai & Dépotage Conteneurs ({receptions.length})
            </h2>
          </div>

          <div className="divide-y divide-slate-800">
            {receptions.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                Aucune réception en attente de déchargement.
              </div>
            ) : (
              receptions.map((r) => (
                <div key={r.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-800/80">
                  <div className="space-y-1">
                    <div className="text-xs font-bold text-white">BL #{r.numero_bl}</div>
                    <div className="text-[11px] text-slate-400">Fournisseur : {r.fournisseur}</div>
                    {r.conteneur_ref && (
                      <div className="text-[10px] font-mono text-indigo-400">Conteneur : {r.conteneur_ref}</div>
                    )}
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right text-xs">
                      <div className="font-bold text-white">{r.nb_colis} Colis</div>
                      <span className="text-[10px] font-mono text-emerald-400 font-bold">{r.statut}</span>
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
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 max-w-3xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-800">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <ClipboardList className="w-5 h-5 text-indigo-400" /> Missions d'Inventaire Tournant
            </h2>
            <p className="text-xs text-slate-500">
              Comptage physique aveugle sur les emplacements assignés du jour.
            </p>
          </div>

          <div className="space-y-3">
            {inventaireLoading && (
              <div className="p-8 text-center text-slate-500 text-xs">Chargement des stocks…</div>
            )}
            {!inventaireLoading && inventaireItems.length === 0 && (
              <div className="p-8 text-center text-slate-500 text-xs">
                Aucun article en stock. L'inventaire se fait sur les stocks réels de l'entrepôt.
              </div>
            )}
            {!inventaireLoading && inventaireItems.map((item, idx) => (
              <div key={item.id} className="p-4 rounded-xl border border-slate-700 bg-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="text-xs font-bold text-white">{item.designation}</div>
                  <div className="text-[11px] text-indigo-400 font-mono">Emplacement : {item.emplacement}</div>
                  <div className="text-[11px] text-slate-500 font-mono">
                    Qté théorique : <strong>{item.qte_theorique}</strong>
                  </div>
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
                    className="w-24 px-2.5 py-1.5 rounded-lg border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none font-mono"
                  />
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleSaveInventaire}
            disabled={regularisant || inventaireLoading || inventaireItems.length === 0}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed text-white text-xs font-bold transition-colors shadow-sm"
          >
            {regularisant ? 'Transmission en cours…' : 'Enregistrer et Transmettre le Comptage'}
          </button>
        </div>
      )}

      {/* Onglet 4 : Checklist Chariot */}
      {activeTab === 'chariot' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" /> Prise de Poste Chariot Élévateur & Gerbeur
              </h2>
              <p className="text-xs text-slate-500">
                Contrôle préventif obligatoire avant mise en mouvement des engins de levage.
              </p>
            </div>
            {chariotValidated && (
              <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold">
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
                className={`flex items-start gap-3 p-3.5 rounded-xl border cursor-pointer transition-all ${chariotChecklist[item.key as keyof typeof chariotChecklist]
                    ? 'bg-emerald-900/20 border-emerald-700'
                    : 'bg-rose-900/20 border-rose-700'
                  }`}
              >
                <input
                  type="checkbox"
                  checked={chariotChecklist[item.key as keyof typeof chariotChecklist]}
                  onChange={(e) => setChariotChecklist({ ...chariotChecklist, [item.key]: e.target.checked })}
                  className="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                />
                <span className="text-xs font-semibold text-white">{item.label}</span>
              </label>
            ))}
          </div>

          <button
            onClick={handleValiderChariot}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors shadow-sm"
          >
            Valider & Éditer la Fiche de Prise de Poste
          </button>
        </div>
      )}
    </div>
  );
}

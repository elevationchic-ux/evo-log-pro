'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { magasinAPI, apiClient } from '@/lib/api-client';
import {
  Warehouse, Package, TrendingUp, AlertTriangle, Search, Plus,
  MapPin, RefreshCw, Eye, ArrowRight, BarChart3,
  Layers, Box, ShoppingCart, QrCode, Truck, ShieldCheck, X
} from 'lucide-react';
import { toast } from 'sonner';

type RecentMovement = {
  id: string | number;
  type: string;
  ref: string;
  desc: string;
  qte: number;
  unite: string;
  from: string;
  to: string;
  agent: string;
  heure: string;
};

export default function WMSDashboardPage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'overview' | 'movements' | 'crossdock' | 'rop'>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modals state
  const [isRFModalOpen, setIsRFModalOpen] = useState(false);
  const [isCrossDockModalOpen, setIsCrossDockModalOpen] = useState(false);
  const [rfCode, setRfCode] = useState('PAL-2026-089');
  const [rfLocation, setRfLocation] = useState('A02-R04-N01');
  
  // Crossdock form
  const [manifesteRef, setManifesteRef] = useState('MAN-2026-PAD-042');
  const [camionImmat, setCamionImmat] = useState('LT-774-CK');
  const [colisDesc, setColisDesc] = useState('Pièces industrielles en transit direct N\'Djamena');

  useEffect(() => {
    setMounted(true);
  }, []);

  // Live queries
  const { data: stocksData, isLoading: isLoadingStocks } = useQuery({
    queryKey: ['magasin-stocks'],
    queryFn: async () => {
      try {
        const res = await magasinAPI.getStocks();
        return res.data?.items || res.data || (Array.isArray(res) ? res : []);
      } catch (e) {
        return [];
      }
    },
    enabled: mounted,
  });

  // Occupation reelle par entrepot (agregat DB, pas les litteraux JSX d'avant).
  const { data: occupationData } = useQuery({
    queryKey: ['magasin-occupation'],
    queryFn: async () => {
      try {
        const res = await apiClient.get('/api/v1/magasin/entrepots/occupation');
        return res.data?.zones || [];
      } catch (e) {
        return [];
      }
    },
    enabled: mounted,
  });

  const { data: kpisData } = useQuery({
    queryKey: ['magasin-kpis'],
    queryFn: async () => {
      try {
        const res = await magasinAPI.getKpis();
        return res.data || res;
      } catch (e) {
        return null;
      }
    },
    enabled: mounted,
  });

  const { data: ropData, refetch: refetchROP } = useQuery({
    queryKey: ['magasin-rop'],
    queryFn: async () => {
      try {
        const res = await magasinAPI.getROPAnalysis('ART-CPA-425');
        return res.data || res;
      } catch (e) {
        return null;
      }
    },
    enabled: mounted,
  });

  // RF Scan mutation
  const rfScanMutation = useMutation({
    mutationFn: async (payload: { code_scanne: string; emplacement_cible: string }) => {
      const res = await magasinAPI.scanRFBarcode(payload);
      return res.data || res;
    },
    onSuccess: (data: any) => {
      toast.success(data?.message || 'Scan RF validé avec succès !');
      setIsRFModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ['magasin-stocks'] });
    },
    onError: () => {
      toast.error('Erreur lors du scan code-barres.');
    }
  });

  // Cross dock mutation
  const crossDockMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await magasinAPI.executeCrossDocking(payload);
      return res.data || res;
    },
    onSuccess: (data: any) => {
      if (data?.statut === 'non_persiste') {
        toast.info(
          `Cross-dock calcule : ${data?.nb_colis ?? '?'} colis, ${data?.poids_total_kg ?? '?'} kg (manifeste ${data?.manifeste_origine ?? '-'}) \u2014 op\u00e9ration non persist\u00e9e en base.`
        );
      } else {
        toast.success(`Cross-docking ${data?.cross_dock_ref} enregistr\u00e9.`);
      }
      setIsCrossDockModalOpen(false);
    },
    onError: () => {
      toast.error('Erreur lors de l\'exécution du cross-docking.');
    }
  });

  // StockResponse (contrat emis par /api/v1/magasin/stocks) ne contient ni
  // zone/allee/travee/niveau, ni temperature, ni methode_valorisation, ni
  // seuil_alerte : l'ancien mapping les reclamait puis FABRIQUAIT les defauts
  // ('A'/'01', 100 unites, seuil 20, 'FIFO'). L'adresse reelle est le champ
  // `emplacement` (chaine), le seuil bas est `quantite_minimum`.
  const stockItems = Array.isArray(stocksData) && stocksData.length > 0 
    ? stocksData.map((s: any) => ({
        ref: s.code_article || '',
        desc: s.designation || s.description || '',
        emplacement: s.emplacement || '',
        qte: s.quantite_disponible ?? 0,
        unite: s.unite_mesure || '',
        seuil: s.quantite_minimum ?? null,
        valeur: (s.quantite_disponible ?? 0) * (s.prix_unitaire ?? 0),
        statut: s.quantite_minimum != null && (s.quantite_disponible ?? 0) <= s.quantite_minimum ? 'ALERTE' : 'OK'
      }))
    : [];

  const kpis = [
    { label: 'Articles en Stock', value: kpisData?.nb_articles != null ? String(kpisData.nb_articles) : '0', sub: 'Référentiel stocks réel', icon: Package, color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20', trend: '' },
    { label: 'Mouvements Aujourd’hui', value: kpisData?.mouvements_jour != null ? String(kpisData.mouvements_jour) : '0', sub: 'Mouvements persistés', icon: ArrowRight, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20', trend: '' },
    { label: 'Valeur Totale Stock', value: kpisData?.valeur_stock != null ? `${Number(kpisData.valeur_stock).toLocaleString('fr-FR')} FCFA` : '0', sub: 'Valorisation WMS', icon: TrendingUp, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20', trend: '' },
    { label: 'Alertes Stock Bas', value: kpisData?.nb_alertes_min != null ? String(kpisData.nb_alertes_min) : '0', sub: 'Sous seuil minimum', icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20', trend: '' },
  ];

  const recentMovements: RecentMovement[] = [];

  const filteredItems = stockItems.filter(item =>
    !searchQuery ||
    item.ref.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.desc.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const statut: Record<string, string> = {
    'OK': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'ALERTE': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    'CRITIQUE': 'bg-red-500/10 text-red-400 border-red-500/30',
  };

  const mvtType: Record<string, string> = {
    'ENTRÉE': 'bg-emerald-500/10 text-emerald-400',
    'SORTIE': 'bg-red-500/10 text-red-400',
    'TRANSFERT': 'bg-blue-500/10 text-blue-400',
  };

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Magasin WMS...</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Warehouse className="w-6 h-6 text-amber-400" /> Gestion d'Entrepôt & WMS Industriel
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Stock temps réel · Adressage 3D · FIFO/FEFO · Cross-Docking direct · Scanners RF / PDA · ROP Wilson</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setIsRFModalOpen(true)}
            className="px-4 py-2.5 bg-blue-500/10 border border-blue-500/30 text-blue-400 font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-blue-500/20 transition-colors shadow"
          >
            <QrCode className="w-4 h-4" /> Douchette RF Scan
          </button>
          <button
            onClick={() => setIsCrossDockModalOpen(true)}
            className="px-4 py-2.5 bg-purple-500/10 border border-purple-500/30 text-purple-400 font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-purple-500/20 transition-colors shadow"
          >
            <Truck className="w-4 h-4" /> Cross-Docking Quai
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        {kpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div key={i} className={`${kpi.bg} border rounded-2xl p-4`}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${kpi.color}`} />
                <span className="text-xs font-medium text-slate-400 truncate">{kpi.label}</span>
              </div>
              <div className={`text-2xl font-black ${kpi.color} font-mono`}>{kpi.value}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">{kpi.sub}</div>
              <div className={`text-[11px] ${kpi.color} mt-1 font-mono opacity-70`}>{kpi.trend}</div>
            </div>
          );
        })}
      </div>

      {/* Zone utilization bar  branches sur /magasin/entrepots/occupation.
          Avant : 88/62/45/78/55% en dur dans le JSX, quels que soient la base
          et le tenant. L'occupation en % n'est affichee que si une capacite
          est enregistree (occupancy non-null), sinon articles + valeur reelles. */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow">
        <div className="text-xs font-bold text-slate-300 uppercase mb-3">Occupation par Entrepôt (données réelles)</div>
        <div className="space-y-2">
          {(occupationData || []).length === 0 ? (
            <p className="text-[11px] text-slate-500">Aucun entrepôt avec capacite enregistree.</p>
          ) : (
            occupationData.map((z: any, i: number) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-52 text-[11px] text-slate-400 shrink-0 truncate">{z.zone}</div>
                {z.occupancy != null ? (
                  <>
                    <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                      <div className="h-full bg-amber-500 rounded-full transition-all" style={{ width: `${z.occupancy}%` }}></div>
                    </div>
                    <div className="w-8 text-[11px] font-mono text-slate-400 text-right">{z.occupancy}%</div>
                  </>
                ) : (
                  <>
                    <div className="flex-1 text-[11px] text-slate-500">{z.nb_articles} articles · {Number(z.valeur_stockee || 0).toLocaleString('fr-FR')} FCFA stockes</div>
                    <div className="w-8 text-[11px] font-mono text-slate-500 text-right"></div>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-2">
        {[
          { id: 'overview', label: 'Stock en Temps Réel' },
          { id: 'movements', label: 'Mouvements du Jour' },
          { id: 'rop', label: 'Analyse Réappro & Wilson (ROP)' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${activeTab === tab.id ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30' : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Stock Table */}
      {activeTab === 'overview' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex gap-3 items-center">
            <div className="relative flex-1 max-w-xs">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Référence ou désignation..."
                className="w-full h-9 pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-left">
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Référence</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Description</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Emplacement</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Quantité</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden md:table-cell">Valeur</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Statut</th>
                  <th className="px-4 py-3 text-slate-400 font-semibold uppercase"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredItems.map(item => (
                  <tr key={item.ref} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-amber-300">{item.ref}</td>
                    <td className="px-4 py-3 text-slate-200 max-w-52 truncate font-medium">{item.desc}</td>
                    <td className="px-4 py-3 font-mono text-slate-400">{item.emplacement || ''}</td>
                    <td className="px-4 py-3">
                      <div className={`font-mono font-bold ${item.statut === 'CRITIQUE' ? 'text-red-400' : item.statut === 'ALERTE' ? 'text-amber-400' : 'text-slate-200'}`}>
                        {item.qte.toLocaleString()} {item.unite}
                      </div>
                      <div className="text-[11px] text-slate-500">{item.seuil != null ? `Seuil: ${item.seuil}` : 'Seuil: non défini'}</div>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <span className="text-[11px] font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">{item.valeur.toLocaleString('fr-FR')} FCFA</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${statut[item.statut] || 'bg-slate-800 text-slate-300'}`}>
                        {item.statut}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button onClick={() => toast.info(`Détail article ${item.ref}`)} className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg">
                        <Eye className="w-3.5 h-3.5 text-amber-400" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Movements Tab */}
      {activeTab === 'movements' && (
        <div className="space-y-2">
          {recentMovements.map(mvt => (
            <div key={mvt.id} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center gap-3">
              <span className={`text-[11px] font-black px-2.5 py-1 rounded-lg ${mvtType[mvt.type]}`}>{mvt.type}</span>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-bold text-slate-200">{mvt.desc} <span className="font-mono text-amber-300">({mvt.ref})</span></div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  {mvt.from} → {mvt.to} • Qté: <strong className="text-white">{mvt.qte} {mvt.unite}</strong> • Agent: {mvt.agent}
                </div>
              </div>
              <div className="text-[11px] font-mono text-slate-500">{mvt.heure} • {mvt.id}</div>
            </div>
          ))}
        </div>
      )}

      {/* ROP Analysis Tab */}
      {activeTab === 'rop' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-amber-400" /> Calculateur Mathématique de Réapprovisionnement (Formule de Wilson & Seuil ROP)
            </h3>
            <button
              onClick={() => refetchROP()}
              className="px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold rounded-lg hover:bg-amber-500/20"
            >
              Recalculer
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400">Stock de Sécurité Déterministe</div>
              <div className="text-2xl font-black text-amber-400 font-mono mt-1">
                {ropData?.stock_securite_calcule ?? ''} {ropData?.stock_securite_calcule != null ? 'Unités' : ''}
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Niveau de service 95% (Z = 1.645) sur délai fournisseur de 14j.</p>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400">Point de Commande (ROP)</div>
              <div className="text-2xl font-black text-cyan-400 font-mono mt-1">
                {ropData?.point_de_commande_rop ?? ''} {ropData?.point_de_commande_rop != null ? 'Unités' : ''}
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Déclencheur automatique de bon de commande fournisseur.</p>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400">Quantité Économique Wilson (EOQ)</div>
              <div className="text-2xl font-black text-emerald-400 font-mono mt-1">
                {ropData?.quantite_economique_commande_wilson ?? ''} {ropData?.quantite_economique_commande_wilson != null ? 'Unités' : ''}
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Minimisation des coûts de possession et passation.</p>
            </div>
          </div>
        </div>
      )}

      {/* RF SCAN MODAL */}
      {isRFModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <QrCode className="w-5 h-5 text-blue-400" /> Terminal RF Douchette (Code 128 / QR)
              </h3>
              <button onClick={() => setIsRFModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-slate-400">
              Scannez le code-barres de la palette ou de l'article pour vérifier l'emplacement de stockage alloué.
            </p>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Code-barres / Tag Scanné</label>
                <input
                  type="text"
                  value={rfCode}
                  onChange={e => setRfCode(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-sm font-mono text-cyan-300 focus:outline-none focus:border-blue-500"
                  placeholder="PAL-2026-001..."
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Emplacement Rack Cible (Optionnel)</label>
                <input
                  type="text"
                  value={rfLocation}
                  onChange={e => setRfLocation(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-sm font-mono text-slate-300 focus:outline-none focus:border-blue-500"
                  placeholder="A01-R02-N03"
                />
              </div>
            </div>
            <div className="pt-2 flex justify-end gap-2">
              <button
                onClick={() => setIsRFModalOpen(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
              >
                Annuler
              </button>
              <button
                disabled={rfScanMutation.isPending}
                onClick={() => rfScanMutation.mutate({ code_scanne: rfCode, emplacement_cible: rfLocation })}
                className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-blue-600/30 flex items-center gap-2"
              >
                {rfScanMutation.isPending ? 'Validation scan...' : 'Valider le Scan Cariste'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CROSS-DOCKING MODAL */}
      {isCrossDockModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Truck className="w-5 h-5 text-purple-400" /> Opération de Cross-Docking Direct Quai-Camion
              </h3>
              <button onClick={() => setIsCrossDockModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-slate-400">
              Transbordement immédiat depuis le conteneur maritime vers le camion de livraison sans mise en rack en entrepôt.
            </p>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Référence Manifeste / Connaissement Origine</label>
                <input
                  type="text"
                  value={manifesteRef}
                  onChange={e => setManifesteRef(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-sm font-mono text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Immatriculation Camion Destination</label>
                <input
                  type="text"
                  value={camionImmat}
                  onChange={e => setCamionImmat(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-sm font-mono text-purple-300 focus:outline-none focus:border-purple-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Description du Lot Colis / Marchandise</label>
                <input
                  type="text"
                  value={colisDesc}
                  onChange={e => setColisDesc(e.target.value)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>
            </div>
            <div className="pt-2 flex justify-end gap-2">
              <button
                onClick={() => setIsCrossDockModalOpen(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
              >
                Annuler
              </button>
              <button
                disabled={crossDockMutation.isPending}
                onClick={() => crossDockMutation.mutate({
                  manifeste_ref: manifesteRef,
                  camion_immat: camionImmat,
                  colis: [{ colis_ref: 'COLIS-XDOCK-01', description: colisDesc, poids_kg: 3200.0 }]
                })}
                className="px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-purple-600/30 flex items-center gap-2"
              >
                {crossDockMutation.isPending ? 'Exécution...' : 'Exécuter le Cross-Docking'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

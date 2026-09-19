'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText, Search, Plus, CheckCircle2, Clock, AlertTriangle,
  Scale, Shield, RefreshCw, X, DollarSign, Calculator, Landmark
} from 'lucide-react';
import { goodsDeclarationAPI } from '@/lib/api-client';

interface DUMItem {
  id: number;
  numero_dum: string;
  type_operation: string;
  regime_douanier: string;
  bureau_douane: string;
  date_depot?: string;
  declarant: string;
  importateur: string;
  marchandise: string;
  nomenclature?: string;
  poids_brut?: number;
  valeur_douane_xaf?: number;
  droits_douane?: number;
  tva?: number;
  montant_total?: number;
  statut: string;
  reference_sydonia?: string;
}

export default function GoodsDeclarationPage() {
  const [items, setItems] = useState<DUMItem[]>([]);
  const [stats, setStats] = useState({
    total_declarations: 0,
    en_attente: 0,
    validees: 0,
    liquidees: 0,
    valeur_douane_totale_xaf: 0,
    recettes_fiscales_totales_xaf: 0,
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statutFilter, setStatutFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [liquidatingId, setLiquidatingId] = useState<number | null>(null);

  // Formulaire de saisie
  const [formData, setFormData] = useState({
    type_operation: 'import',
    regime_douanier: 'Mise à la consommation (IM4)',
    bureau_douane: 'DLA-PORT VII (Sydonia / Camcis)',
    declarant: 'SOCIETE CAMEROUNAISE DE TRANSIT',
    importateur: 'GROUPE TANGUY S.A.',
    marchandise: 'Pièces détachées industrielles et tubes acier',
    nomenclature: '8409.91.00',
    poids_brut: 18500,
    valeur_fob: 45000,
    valeur_caf: 52000,
    devise: 'USD',
    taux_change: 615.0,
    notes: 'Déclaration électronique soumise via Guichet Unique GUCE',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        goodsDeclarationAPI.getAll({
          search: search || undefined,
          statut: statutFilter || undefined
        }),
        goodsDeclarationAPI.getStats()
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement déclarations DUM:', err);
    } finally {
      setLoading(false);
    }
  }, [search, statutFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleLiquidate = async (id: number) => {
    try {
      setLiquidatingId(id);
      await goodsDeclarationAPI.liquidate(id);
      await fetchData();
    } catch (err) {
      console.error('Erreur liquidation DUM:', err);
    } finally {
      setLiquidatingId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await goodsDeclarationAPI.create(formData);
      setIsModalOpen(false);
      await fetchData();
    } catch (err) {
      console.error('Erreur création déclaration DUM:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Scale className="w-3.5 h-3.5" /> Douanes Camerounaises • Système CAMCIS / Sydonia World
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Déclarations de Marchandises (DUM)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Déclarations uniques de marchandises, calcul des droits de douane TEC, TVA et liquidation Trésor.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchData()}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm shadow-lg shadow-violet-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Nouvelle Déclaration DUM
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Déclarations DUM Totales</span>
            <FileText className="w-4 h-4 text-violet-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_declarations}
          </div>
          <div className="text-xs text-slate-500 mt-1">Enregistrées dans CAMCIS</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Valeur en Douane (CAF)</span>
            <Landmark className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-400 mt-2">
            {Number(stats.valeur_douane_totale_xaf).toLocaleString('fr-FR')} XAF
          </div>
          <div className="text-xs text-slate-500 mt-1">Assiette taxable globale</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Droits & Taxes Déterminés</span>
            <Calculator className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {Number(stats.recettes_fiscales_totales_xaf).toLocaleString('fr-FR')} XAF
          </div>
          <div className="text-xs text-slate-500 mt-1">TEC + TVA + Taxes communautaires</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Déclarations Liquidées</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.liquidees}
          </div>
          <div className="text-xs text-slate-500 mt-1">Quittances Trésor acquittées</div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher par DUM, déclarant, importateur, code SH..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statutFilter}
            onChange={(e) => setStatutFilter(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="">Tous les statuts</option>
            <option value="liquidé">Liquidé & Payé</option>
            <option value="en_attente">En cours d'étude</option>
            <option value="valide">Validé recevable</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">N° Déclaration DUM</th>
                <th className="py-4 px-5">Régime & Bureau</th>
                <th className="py-4 px-5">Déclarant & Importateur</th>
                <th className="py-4 px-5">Marchandise & Code SH</th>
                <th className="py-4 px-5">Droits & Taxes (XAF)</th>
                <th className="py-4 px-5">Statut Douane</th>
                <th className="py-4 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-violet-500" />
                    Chargement des déclarations DUM...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    Aucune déclaration en douane trouvée dans la base de données.
                  </td>
                </tr>
              ) : (
                items.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono">
                      <div className="font-bold text-violet-400">{d.numero_dum}</div>
                      <div className="text-[10px] text-slate-500">{d.reference_sydonia}</div>
                    </td>
                    <td className="py-4 px-5 text-xs">
                      <div className="font-semibold text-white">{d.regime_douanier}</div>
                      <div className="text-slate-400">{d.bureau_douane}</div>
                    </td>
                    <td className="py-4 px-5 text-xs">
                      <div className="font-semibold text-slate-200">{d.importateur}</div>
                      <div className="text-slate-400">{d.declarant}</div>
                    </td>
                    <td className="py-4 px-5 text-xs">
                      <div className="font-medium text-slate-300 max-w-xs truncate">{d.marchandise}</div>
                      <div className="font-mono text-cyan-400">SH: {d.nomenclature || 'Non spécifié'}</div>
                    </td>
                    <td className="py-4 px-5 font-mono text-xs">
                      <div className="font-bold text-white">
                        {d.montant_total ? Number(d.montant_total).toLocaleString('fr-FR') : '0'} XAF
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Valeur : {d.valeur_douane_xaf ? Number(d.valeur_douane_xaf).toLocaleString('fr-FR') : '0'}
                      </div>
                    </td>
                    <td className="py-4 px-5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                        d.statut === 'liquidé'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {d.statut === 'liquidé' ? (
                          <>
                            <CheckCircle2 className="w-3 h-3" /> Liquidé
                          </>
                        ) : (
                          <>
                            <Clock className="w-3 h-3" /> En cours
                          </>
                        )}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      {d.statut !== 'liquidé' && (
                        <button
                          onClick={() => handleLiquidate(d.id)}
                          disabled={liquidatingId === d.id}
                          className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-semibold shadow transition-all disabled:opacity-50"
                        >
                          {liquidatingId === d.id ? 'Liquidation...' : 'Liquider'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Création DUM */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Scale className="w-5 h-5 text-violet-400" /> Saisie Déclaration DUM (CAMCIS)
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Régime Douanier</label>
                  <input
                    type="text"
                    required
                    value={formData.regime_douanier}
                    onChange={(e) => setFormData({ ...formData, regime_douanier: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Bureau de Douane</label>
                  <input
                    type="text"
                    required
                    value={formData.bureau_douane}
                    onChange={(e) => setFormData({ ...formData, bureau_douane: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Déclarant Agréé</label>
                  <input
                    type="text"
                    required
                    value={formData.declarant}
                    onChange={(e) => setFormData({ ...formData, declarant: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Importateur Réel</label>
                  <input
                    type="text"
                    required
                    value={formData.importateur}
                    onChange={(e) => setFormData({ ...formData, importateur: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Désignation Marchandise</label>
                  <input
                    type="text"
                    required
                    value={formData.marchandise}
                    onChange={(e) => setFormData({ ...formData, marchandise: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Code Tarifaire SH CEMAC</label>
                  <input
                    type="text"
                    required
                    placeholder="ex: 8409.91.00"
                    value={formData.nomenclature}
                    onChange={(e) => setFormData({ ...formData, nomenclature: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Poids Brut (Kg)</label>
                  <input
                    type="number"
                    required
                    value={formData.poids_brut}
                    onChange={(e) => setFormData({ ...formData, poids_brut: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Valeur CAF ($)</label>
                  <input
                    type="number"
                    required
                    value={formData.valeur_caf}
                    onChange={(e) => setFormData({ ...formData, valeur_caf: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Taux Change BEAC</label>
                  <input
                    type="number"
                    required
                    value={formData.taux_change}
                    onChange={(e) => setFormData({ ...formData, taux_change: parseFloat(e.target.value) || 615.0 })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-bold shadow-lg shadow-violet-600/20 transition-all"
                >
                  Télé-transmettre la DUM
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

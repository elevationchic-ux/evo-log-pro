'use client';

import React, { useState, useEffect } from 'react';
import {
  Boxes,
  Plus,
  Search,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Download,
  Filter,
  Warehouse,
  Save,
  FileCheck
} from 'lucide-react';
import { magasinAPI, masterDataAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function MagasinInventoryPage() {
  const [loading, setLoading] = useState(true);
  const [stocks, setStocks] = useState<any[]>([]);
  const [magasins, setMagasins] = useState<any[]>([]);
  const [selectedMagasin, setSelectedMagasin] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [inventoryMode, setInventoryMode] = useState(false);
  const [counts, setCounts] = useState<{ [key: string]: number }>({});
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [stockRes, magRes] = await Promise.allSettled([
        magasinAPI.getStocks(),
        magasinAPI.getMagasins()
      ]);

      if (stockRes.status === 'fulfilled') {
        const d = stockRes.value.data?.items || stockRes.value.data || [];
        setStocks(Array.isArray(d) ? d : []);
      }
      if (magRes.status === 'fulfilled') {
        const m = magRes.value.data?.items || magRes.value.data || [];
        setMagasins(Array.isArray(m) ? m : []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredStocks = stocks.filter((st: any) => {
    const matchMag = selectedMagasin === 'ALL' || String(st.magasin_id) === selectedMagasin || st.entrepot_nom === selectedMagasin;
    const q = searchQuery.toLowerCase();
    const matchQuery = !q || (
      (st.article_code && st.article_code.toLowerCase().includes(q)) ||
      (st.article_nom && st.article_nom.toLowerCase().includes(q)) ||
      (st.zone && st.zone.toLowerCase().includes(q)) ||
      (st.emplacement && st.emplacement.toLowerCase().includes(q))
    );
    return matchMag && matchQuery;
  });

  const handleCountChange = (id: string | number, val: string) => {
    setCounts(prev => ({ ...prev, [id]: Number(val) }));
  };

  const handleValidateInventory = async () => {
    setSubmitting(true);
    try {
      // Send adjustments for all items with counts recorded
      toast.error("La validation de l'inventaire physique n'est pas encore raccordée à l'API.");
      setInventoryMode(false);
      setCounts({});
      loadData();
    } catch (err: any) {
      toast.error("Erreur lors de la validation de l'inventaire.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Boxes className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Inventaire Physique des Stocks (WMS)</h1>
            <p className="text-sm text-on-surface-variant">
              Comptage tournant, détection des écarts théorique/physique et régularisation d'entrepôt
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => loadData()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          {!inventoryMode ? (
            <button
              onClick={() => setInventoryMode(true)}
              className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
            >
              <FileCheck className="w-4 h-4" />
              Lancer Session de Comptage
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => setInventoryMode(false)}
                className="px-3 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container text-on-surface"
              >
                Annuler
              </button>
              <button
                onClick={handleValidateInventory}
                disabled={submitting}
                className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-emerald-600 text-white hover:bg-emerald-700"
              >
                <Save className="w-4 h-4" />
                Valider les Comptages
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par référence article, désignation, zone, rack..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
        <div className="sm:w-64">
          <select
            value={selectedMagasin}
            onChange={(e) => setSelectedMagasin(e.target.value)}
            className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
          >
            <option value="ALL">Tous les Magasins / Entrepôts</option>
            {magasins.map((m: any) => (
              <option key={m.id} value={String(m.id)}>
                {m.nom || m.code || `Magasin #${m.id}`}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-on-surface">
            <thead className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline">
              <tr>
                <th className="px-5 py-3">Article / Référence</th>
                <th className="px-5 py-3">Entrepôt / Emplacement</th>
                <th className="px-5 py-3 text-right">Stock Théorique</th>
                {inventoryMode && (
                  <>
                    <th className="px-5 py-3 text-right">Comptage Physique</th>
                    <th className="px-5 py-3 text-right">Écart</th>
                  </>
                )}
                <th className="px-5 py-3 text-right">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline/30">
              {loading ? (
                <tr>
                  <td colSpan={inventoryMode ? 6 : 4} className="p-12 text-center text-on-surface-variant">
                    Chargement des données de stock...
                  </td>
                </tr>
              ) : filteredStocks.length === 0 ? (
                <tr>
                  <td colSpan={inventoryMode ? 6 : 4} className="p-12 text-center">
                    <Boxes className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
                    <h3 className="font-semibold text-on-surface text-base">Aucun stock répertorié</h3>
                    <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
                      Les lignes d'inventaire apparaîtront automatiquement dès que vous réceptionnerez des marchandises ou enregistrerez des mouvements dans les magasins.
                    </p>
                  </td>
                </tr>
              ) : (
                filteredStocks.map((item: any, idx: number) => {
                  const theoric = Number(item.quantite || item.stock_actuel || 0);
                  const counted = counts[item.id] !== undefined ? counts[item.id] : theoric;
                  const ecart = counted - theoric;
                  return (
                    <tr key={item.id || idx} className="hover:bg-surface-container/50 transition-colors">
                      <td className="px-5 py-3.5">
                        <div className="font-bold text-on-surface">
                          {item.article_code || item.reference || `ART-${item.article_id || item.id}`}
                        </div>
                        <div className="text-xs text-on-surface-variant">
                          {item.article_nom || item.designation || 'Marchandise générale'}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-xs">
                        <div className="font-medium text-on-surface">{item.magasin_nom || item.entrepot_nom || 'Magasin Central'}</div>
                        <div className="text-on-surface-variant">Zone: {item.zone || 'A'} • Rack: {item.emplacement || 'R01'}</div>
                      </td>
                      <td className="px-5 py-3.5 text-right font-mono font-bold text-on-surface">
                        {theoric} {item.unite || 'U'}
                      </td>
                      {inventoryMode && (
                        <>
                          <td className="px-5 py-3.5 text-right">
                            <input
                              type="number"
                              value={counts[item.id] !== undefined ? counts[item.id] : theoric}
                              onChange={(e) => handleCountChange(item.id, e.target.value)}
                              className="w-24 px-2 py-1 text-right text-sm font-mono font-bold bg-surface border border-outline rounded-lg focus:outline-none focus:border-primary"
                            />
                          </td>
                          <td className="px-5 py-3.5 text-right font-mono font-bold">
                            {ecart === 0 ? (
                              <span className="text-emerald-600">0</span>
                            ) : ecart > 0 ? (
                              <span className="text-blue-600">+{ecart}</span>
                            ) : (
                              <span className="text-rose-600">{ecart}</span>
                            )}
                          </td>
                        </>
                      )}
                      <td className="px-5 py-3.5 text-right">
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600">
                          <CheckCircle2 className="w-3 h-3" /> Conforme
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

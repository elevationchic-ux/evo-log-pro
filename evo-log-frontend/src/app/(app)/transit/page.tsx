'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transitAPI } from '@/lib/api-client';
import { Shield, Plus, Search, CheckCircle2, Globe, FileCheck, X } from 'lucide-react';
import { toast } from 'sonner';

export default function TransitPage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [declarationType, setDeclarationType] = useState('IM4_MISE_A_CONSOMMATION');
  const [declarationRef, setDeclarationRef] = useState('DEC-2026-9081');
  const [valueCaf, setValueCaf] = useState('18500000');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['transit'],
    queryFn: async () => {
      const res = await transitAPI.getTransits();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await transitAPI.createTransit(payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success("Déclaration douanière enregistrée !");
      queryClient.invalidateQueries({ queryKey: ['transit'] });
      setIsModalOpen(false);
      setDeclarationRef('');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création.");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      type_declaration: declarationType,
      reference_declaration: declarationRef || 'DEC-2026-9081',
      valeur_caf_xaf: Number(valueCaf),
    });
  };

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Transit...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.reference_declaration || '') + ' ' + String(i.type_declaration || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-semibold mb-2 border border-blue-500/20">
            <Globe className="w-3.5 h-3.5" />
            K-Transit • Douane, Déclarations & Corridors Transfrontaliers
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Déclarations Douanières & Transit SYDONIA</h1>
          <p className="text-slate-400 text-sm mt-1">Gestion des régimes suspendus, liquidation des droits et transit Tchad/RCA.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-blue-600/30 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          Déposer une Déclaration
        </button>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Registre des Déclarations en Douane
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par référence..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">N° Déclaration SYDONIA</th>
                <th className="px-6 py-4">Régime Douanier</th>
                <th className="px-6 py-4 text-right">Valeur CAF (XAF)</th>
                <th className="px-6 py-4 text-right">Statut Liquidation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={4} className="p-12 text-center text-slate-400">Chargement des déclarations...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucune déclaration trouvée.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 flex items-center gap-2 font-mono">
                      <FileCheck className="w-4 h-4 text-blue-400" />
                      {item.reference_declaration || `DEC-2026-00${item.id}`}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      {item.type_declaration || 'IM4_MISE_A_CONSOMMATION'}
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-blue-400">
                      {Number(item.valeur_caf_xaf || 18500000).toLocaleString()} XAF
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> LIQUIDÉ & BAE
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold">Déposer une Déclaration en Douane</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">N° Déclaration / Référence SYDONIA</label>
                <input
                  type="text"
                  required
                  value={declarationRef}
                  onChange={(e) => setDeclarationRef(e.target.value)}
                  placeholder="ex: DEC-2026-9081"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Régime Douanier</label>
                <select
                  value={declarationType}
                  onChange={(e) => setDeclarationType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                >
                  <option value="IM4_MISE_A_CONSOMMATION">IM4 - Mise à la consommation</option>
                  <option value="IT_TRANSIT_INTERNATIONAL">IT - Transit International (Tchad/RCA)</option>
                  <option value="C2_ENTREPOT_DOUANE">C2 - Entrepôt de Douane</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Valeur CAF Déclarée (XAF)</label>
                <input
                  type="number"
                  required
                  value={valueCaf}
                  onChange={(e) => setValueCaf(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/30"
                >
                  {createMutation.isPending ? 'Enregistrement...' : 'Valider la Déclaration'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

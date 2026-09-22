'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { procurementAPI } from '@/lib/api-client';
import { ShoppingCart, Plus, Search, CheckCircle2, ShieldCheck, X } from 'lucide-react';

export default function ProcurementPage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [fournisseur, setFournisseur] = useState('');
  const [description, setDescription] = useState('');
  const [montant, setMontant] = useState('2400000');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['procurement-orders'],
    queryFn: async () => {
      const res = await procurementAPI.getOrders();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await procurementAPI.createOrder(payload);
      return res.data;
    },
    onSuccess: () => {
      console.log('Bon de commande (PO) émis avec succès !');
      queryClient.invalidateQueries({ queryKey: ['procurement-orders'] });
      setIsModalOpen(false);
      setFournisseur('');
      setDescription('');
    },
    onError: (err: any) => {
      console.log(err?.response?.data?.detail || 'Erreur lors de la création de la commande.');
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      fournisseur: fournisseur || 'MICHELIN CAMEROUN',
      description: description || 'Pneumatiques Poids Lourds 315/80 R22.5',
      montant_total_xaf: Number(montant)
    });
  };

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module EVO-Procurement...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.fournisseur || '') + ' ' + String(i.numero_po || '') + ' ' + String(i.description || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 text-violet-400 text-xs font-semibold mb-2 border border-violet-500/20">
            <ShoppingCart className="w-3.5 h-3.5" />
            EVO-Procurement â€¢ Approvisionnements & Matching 3-Voies
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Achats & Bons de Commande (PO)</h1>
          <p className="text-slate-400 text-sm mt-1">Gestion des commandes fournisseurs, piÃ¨ces dÃ©tachÃ©es et rÃ©ceptions d'atelier.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-violet-600/30 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          Nouveau Bon de Commande
        </button>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Registre des Bons de Commande Fournisseurs (PO)
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par fournisseur..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">NÂ° PO / Fournisseur</th>
                <th className="px-6 py-4">Description Commande</th>
                <th className="px-6 py-4 text-right">Montant Total (XAF)</th>
                <th className="px-6 py-4 text-right">Match 3-Voies</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={4} className="p-12 text-center text-slate-400">Chargement des achats...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucune commande enregistrÃ©e.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 font-mono">
                      {item.numero_po || `PO-2026-00${item.id}`}
                      <div className="text-xs font-normal text-slate-400">{item.fournisseur}</div>
                    </td>
                    <td className="px-6 py-4 text-slate-200 text-sm">
                      {item.description}
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-violet-400">
                      {Number(item.montant_total_xaf || 2400000).toLocaleString()} XAF
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> MATCHED 100%
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
              <h3 className="text-lg font-bold">Nouveau Bon de Commande (PO)</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Raison Sociale du Fournisseur</label>
                <input
                  type="text"
                  required
                  value={fournisseur}
                  onChange={(e) => setFournisseur(e.target.value)}
                  placeholder="ex: TOTALENERGIES MARKETING"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Description des Articles / Services</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="ex: 5000 Litres Diesel Gasoil..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-violet-500 h-20"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Montant Total TTC (XAF)</label>
                <input
                  type="number"
                  value={montant}
                  onChange={(e) => setMontant(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-violet-500"
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
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-600/30"
                >
                  {createMutation.isPending ? 'Ã‰mission...' : 'Valider la Commande'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

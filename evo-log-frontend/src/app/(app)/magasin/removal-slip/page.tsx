'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { FileText, Plus, Search, Calendar, CheckCircle, Clock, X } from 'lucide-react';
import { toast } from 'sonner';

export default function RemovalSlipPage() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form states
  const [reference, setReference] = useState('');
  const [clientName, setClientName] = useState('');
  const [cargoDesc, setCargoDesc] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['removal-slips'],
    queryFn: async () => {
      const res = await apiClient.get('/api/v1/magasin/removal-slips');
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
  });

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await apiClient.post('/api/v1/magasin/removal-slips', payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success("Bon d'enlèvement généré avec succès !");
      queryClient.invalidateQueries({ queryKey: ['removal-slips'] });
      setIsModalOpen(false);
      setReference('');
      setClientName('');
      setCargoDesc('');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création du bon d'enlèvement.");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      reference: reference || `BE-${Date.now().toString().slice(-6)}`,
      client: clientName || 'Client Général',
      description: cargoDesc,
      statut: 'EMIS'
    });
  };

  const slips = Array.isArray(data) ? data : [];

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl text-white shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <FileText className="w-3.5 h-3.5" />
            Gestion Entrepôt Mag3 • Bons d'Enlèvement
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Bons d'Enlèvement (BE)</h1>
          <p className="text-slate-400 text-sm mt-1">Émission et suivi des bons de sortie de marchandise en Magasin.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          Émettre un Bon d'Enlèvement
        </button>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            Liste des Bons de Sortie
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono">
              {slips.length} enregistrements
            </span>
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">N° Référence BE</th>
                <th className="px-6 py-4">Client Beneficiaire</th>
                <th className="px-6 py-4">Détails Marchandise</th>
                <th className="px-6 py-4 text-right">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr>
                  <td colSpan={4} className="p-12 text-center text-slate-400">
                    <div className="inline-block animate-spin w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full mr-2" />
                    Chargement des bons d'enlèvement...
                  </td>
                </tr>
              ) : slips.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-slate-500">
                    Aucun bon d'enlèvement enregistré.
                  </td>
                </tr>
              ) : (
                slips.map((slip: any, idx: number) => (
                  <tr key={slip.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100">
                      {slip.reference || slip.numero_be || `BE-${slip.id}`}
                      <div className="text-xs font-normal text-slate-400 flex items-center gap-1 mt-0.5">
                        <Calendar className="w-3 h-3 text-slate-500" />
                        {slip.created_at ? new Date(slip.created_at).toLocaleDateString() : 'Aujourd\'hui'}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">{slip.client || slip.tiers_nom || 'CFAO LOGISTICS'}</td>
                    <td className="px-6 py-4 text-slate-300">{slip.description || slip.nature_fret || 'Marchandises sous douane'}</td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle className="w-3 h-3" /> VALIDE
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Creation BE */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold">Émission d'un Bon d'Enlèvement</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Référence BE (optionnelle)</label>
                <input
                  type="text"
                  value={reference}
                  onChange={(e) => setReference(e.target.value)}
                  placeholder="ex: BE-2026-0094"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Nom / Raison Sociale Client</label>
                <input
                  type="text"
                  required
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="ex: CFAO LOGISTICS"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Description des Colis / Palette</label>
                <textarea
                  value={cargoDesc}
                  onChange={(e) => setCargoDesc(e.target.value)}
                  placeholder="ex: 12 Palettes Pièces de rechange"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500 h-24"
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
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30"
                >
                  {createMutation.isPending ? 'Émission...' : 'Générer le Bon'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

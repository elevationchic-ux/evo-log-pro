'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cotationsAPI } from '@/lib/api-client';
import { Tag, Plus, Search, Calendar, CheckCircle2, Calculator, ArrowRight, X } from 'lucide-react';
import { toast } from 'sonner';
import Link from 'next/link';

export default function CotationsPage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [clientNom, setClientNom] = useState('');
  const [origine, setOrigine] = useState('Port de Douala');
  const [destination, setDestination] = useState('N\'Djamena (Tchad)');
  const [natureFret, setNatureFret] = useState('Conteneur 40ft High Cube');
  const [montantEstime, setMontantEstime] = useState('4850000');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['cotations'],
    queryFn: async () => {
      const res = await cotationsAPI.getCotations();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await cotationsAPI.createCotation(payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success('Devis de cotation émis avec succès !');
      queryClient.invalidateQueries({ queryKey: ['cotations'] });
      setIsModalOpen(false);
      setClientNom('');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || 'Erreur lors de l\'émission de la cotation.');
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      client_nom: clientNom || 'CFAO LOGISTICS CAMEROUN',
      origine,
      destination,
      nature_fret: natureFret,
      montant_estime_xaf: Number(montantEstime),
      marge_nette_pct: 18.5
    });
  };

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Cotation...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.client_nom || '') + ' ' + String(i.reference || '') + ' ' + String(i.destination || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl text-white shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <Tag className="w-3.5 h-3.5" />
            K-Cotation • Moteur de Tarification & Devis Express
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Tarification & Devis Multimodaux</h1>
          <p className="text-slate-400 text-sm mt-1">Calculateur de marge nette, surestaries et offres commerciales B2B.</p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/cotations/calculateur"
            className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold px-4 py-3 rounded-xl text-sm border border-slate-700 transition-all"
          >
            <Calculator className="w-4 h-4 text-emerald-400" />
            Calculateur IA
          </Link>

          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-4 h-4" />
            Émettre un Devis
          </button>
        </div>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Registre des Cotations & Offres Commerciales
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par client..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">N° Devis / Client</th>
                <th className="px-6 py-4">Trajet & Nature Fret</th>
                <th className="px-6 py-4 text-right">Montant Estimé (XAF)</th>
                <th className="px-6 py-4 text-right">Statut Offre</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr>
                  <td colSpan={4} className="p-12 text-center text-slate-400">
                    Chargement des cotations...
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-slate-500">
                    Aucune cotation enregistrée.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100">
                      {item.reference || `COT-2026-00${item.id}`}
                      <div className="text-xs font-normal text-slate-400 flex items-center gap-1 mt-0.5">
                        {item.client_nom || 'Client B2B'}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      {item.origine} ➔ {item.destination}
                      <div className="text-xs text-slate-400">{item.nature_fret}</div>
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-emerald-400">
                      {Number(item.montant_estime_xaf || 4850000).toLocaleString()} XAF
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> ACCEPTÉ
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
              <h3 className="text-lg font-bold">Émission d'un Devis de Cotation</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Raison Sociale du Client B2B</label>
                <input
                  type="text"
                  required
                  value={clientNom}
                  onChange={(e) => setClientNom(e.target.value)}
                  placeholder="ex: CFAO LOGISTICS"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Origine</label>
                  <input
                    type="text"
                    value={origine}
                    onChange={(e) => setOrigine(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Destination</label>
                  <input
                    type="text"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Montant Estimé (XAF)</label>
                <input
                  type="number"
                  value={montantEstime}
                  onChange={(e) => setMontantEstime(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
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
                  {createMutation.isPending ? 'Émission...' : 'Émettre le Devis'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

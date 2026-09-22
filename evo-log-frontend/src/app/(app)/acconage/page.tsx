'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { acconageAPI } from '@/lib/api-client';
import { Anchor, Plus, Search, CheckCircle2, Ship, Package, X } from 'lucide-react';
import { toast } from 'sonner';

export default function AcconagePage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [vesselName, setVesselName] = useState('');
  const [operationType, setOperationType] = useState('DECHARGEMENT_CONTENEUR');
  const [containerCount, setContainerCount] = useState(1);
  const [notes, setNotes] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['acconage'],
    queryFn: async () => {
      const res = await acconageAPI.getAcconages();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await acconageAPI.createAcconage(payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success("Opération d'acconage enregistrée avec succès !");
      queryClient.invalidateQueries({ queryKey: ['acconage'] });
      setIsModalOpen(false);
      setVesselName('');
      setNotes('');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement.");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      nom_navire: vesselName || 'MSC TOKYO IV',
      type_operation: operationType,
      nombre_conteneurs: Number(containerCount),
      remarques: notes || 'RAS grue de quai',
    });
  };

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Acconage...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.nom_navire || '') + ' ' + String(i.type_operation || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-semibold mb-2 border border-cyan-500/20">
            <Anchor className="w-3.5 h-3.5" />
            K-Acconage • Gestion de Quai & Manutention Portuaire
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Manutention & Operations de Quai</h1>
          <p className="text-slate-400 text-sm mt-1">Suivi des chargements, déchargements et grutage au Port de Douala.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-cyan-600/30 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          Enregistrer une Opération
        </button>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Journal des Opérations d'Acconage
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par navire..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Navire / Escalier</th>
                <th className="px-6 py-4">Type d'Opération</th>
                <th className="px-6 py-4 text-center">Nombre Conteneurs</th>
                <th className="px-6 py-4 text-right">Statut Quai</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={4} className="p-12 text-center text-slate-400">Chargement de l'acconage...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucune opération d'acconage trouvée.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 flex items-center gap-2">
                      <Ship className="w-4 h-4 text-cyan-400" />
                      {item.nom_navire || 'MSC TOKYO IV'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      {item.type_operation || 'DECHARGEMENT_CONTENEUR'}
                    </td>
                    <td className="px-6 py-4 text-center font-mono font-bold text-cyan-400">
                      {item.nombre_conteneurs || 12} TEU
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> TERMINÉ
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
              <h3 className="text-lg font-bold">Enregistrement Opération Acconage</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Nom du Navire / Porte-Conteneurs</label>
                <input
                  type="text"
                  required
                  value={vesselName}
                  onChange={(e) => setVesselName(e.target.value)}
                  placeholder="ex: CMA CGM BENIN"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Type d'Opération</label>
                  <select
                    value={operationType}
                    onChange={(e) => setOperationType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="DECHARGEMENT_CONTENEUR">Déchargement Conteneurs</option>
                    <option value="CHARGEMENT_CONTENEUR">Chargement Conteneurs</option>
                    <option value="MANUTENTION_VRAC">Manutention Vrac</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Nombre d'Unités (TEU)</label>
                  <input
                    type="number"
                    min={1}
                    value={containerCount}
                    onChange={(e) => setContainerCount(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Remarques / Grue de quai</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="ex: Grue Gottwald #2 affectée"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-cyan-500 h-20"
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
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-600/30"
                >
                  {createMutation.isPending ? 'Enregistrement...' : 'Valider L\'Opération'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

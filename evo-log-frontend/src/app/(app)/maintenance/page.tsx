'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { maintenanceAPI } from '@/lib/api-client';
import { Wrench, Plus, Search, CheckCircle2, Clock, Truck, X } from 'lucide-react';
import { toast } from 'sonner';

export default function MaintenancePage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [truckId, setTruckId] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('NORMALE');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['maintenance'],
    queryFn: async () => {
      const res = await maintenanceAPI.getMaintenances();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await maintenanceAPI.createMaintenance(payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success("Ordre de travail atelier enregistré !");
      queryClient.invalidateQueries({ queryKey: ['maintenance'] });
      setIsModalOpen(false);
      setTruckId('');
      setDescription('');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création de l'ordre.");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      immatriculation_camion: truckId || 'LT-901-BA',
      description: description || 'Vidange moteur 50.000km',
      priorite: priority,
    });
  };

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Maintenance...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.immatriculation_camion || '') + ' ' + String(i.description || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 text-xs font-semibold mb-2 border border-amber-500/20">
            <Wrench className="w-3.5 h-3.5" />
            K-Maintenance • Gestion de l'Atelier Logistique & Pneumatiques
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Maintenance & Ordres de Travail (OT)</h1>
          <p className="text-slate-400 text-sm mt-1">Planification des entretiens préventifs, curatifs et stock de pièces détachees.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-amber-600 hover:bg-amber-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-amber-600/30 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          Créer un Ordre de Travail
        </button>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Ordres de Travail Atelier en Cours
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par camion..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Véhicule / Immatriculation</th>
                <th className="px-6 py-4">Nature de la Réparation</th>
                <th className="px-6 py-4 text-center">Priorité</th>
                <th className="px-6 py-4 text-right">Statut Intervention</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={4} className="p-12 text-center text-slate-400">Chargement de l'atelier...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucun ordre de travail enregistré.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 flex items-center gap-2 font-mono">
                      <Truck className="w-4 h-4 text-amber-400" />
                      {item.immatriculation_camion || 'LT-901-BA'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      {item.description || 'Vidange moteur 50.000km'}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {item.priorite || 'NORMALE'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> APPRÊTÉ
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
              <h3 className="text-lg font-bold">Nouveau Bon d'Intervention Atelier</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Immatriculation Véhicule</label>
                <input
                  type="text"
                  required
                  value={truckId}
                  onChange={(e) => setTruckId(e.target.value)}
                  placeholder="ex: LT-901-BA"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Description des Travaux à Effectuer</label>
                <textarea
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="ex: Remplacement plaquettes de frein avant..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-amber-500 h-20"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Niveau de Priorité</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                >
                  <option value="NORMALE">Normale</option>
                  <option value="URGENTE">Urgente (Immobilisation)</option>
                  <option value="PREVENTIVE">Préventive (Visite périodique)</option>
                </select>
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
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-amber-600 hover:bg-amber-500 text-white shadow-lg shadow-amber-600/30"
                >
                  {createMutation.isPending ? 'Création...' : 'Créer l\'Ordre'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

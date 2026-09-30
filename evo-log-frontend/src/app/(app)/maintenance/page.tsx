'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { maintenanceAPI, parcAPI } from '@/lib/api-client';
import { Wrench, Plus, Search, Clock, Truck, X } from 'lucide-react';
import { toast } from 'sonner';

// Couleur du badge d'atelier selon le statut reellement persiste. Une valeur
// absente de la base reste grisee : elle n'est pas requalifiee « apprete ».
// L'orange est reserve a l'identite du module : « attente pieces » est note
// violet pour ne pas confondre etat metier et couleur de rubrique.
function statutBadge(statut?: string): string {
  const s = String(statut || '').toUpperCase();
  if (s === 'TERMINE') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  if (s === 'EN_COURS') return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  if (s === 'ATTENTE_PIECES') return 'bg-violet-500/10 text-violet-400 border-violet-500/20';
  if (s === 'ANNULE') return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
  return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
}

// Priorite telle que stockee (basse / normale / urgente / critique). Rien n'est
// colore par defaut : une priorite non renseignee reste grise.
function prioriteBadge(priorite?: string): string {
  const p = String(priorite || '').toUpperCase();
  if (p === 'CRITIQUE') return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
  if (p === 'URGENTE') return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  if (p === 'NORMALE' || p === 'BASSE') return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
  return 'bg-slate-500/10 text-slate-500 border-slate-600/40';
}

export default function MaintenancePage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form states : le vehicule est choisi dans le parc, plus saisi en libre.
  const [vehiculeId, setVehiculeId] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('NORMALE');
  const [typeMaintenance, setTypeMaintenance] = useState('PREVENTIVE');

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

  // Camions reellement au parc : un ordre de travail ne peut etre ouvert que sur
  // un vehicule existant, la plaque n'est donc plus saisie a la main.
  const { data: vehiculesData, isLoading: vehiculesLoading } = useQuery({
    queryKey: ['parc-vehicules'],
    queryFn: async () => {
      const res = await parcAPI.getVehicules({ limit: 500 });
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted && isModalOpen,
  });
  const vehicules = Array.isArray(vehiculesData) ? vehiculesData : [];

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await maintenanceAPI.createMaintenance(payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success("Ordre de travail atelier enregistré !");
      queryClient.invalidateQueries({ queryKey: ['maintenance'] });
      setIsModalOpen(false);
      setVehiculeId('');
      setDescription('');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création de l'ordre.");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!vehiculeId) {
      toast.error("Aucun vehicule selectionne : un ordre de travail s'ouvre sur un camion du parc.");
      return;
    }
    const vehicule = vehicules.find((v: any) => String(v.id) === vehiculeId);
    createMutation.mutate({
      vehicule_id: Number(vehiculeId),
      immatriculation_camion: vehicule?.immatriculation,
      description: description.trim(),
      priorite: priority,
      type_maintenance: typeMaintenance,
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
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 text-orange-400 text-xs font-semibold mb-2 border border-orange-500/20">
            <Wrench className="w-3.5 h-3.5" />
            K-Maintenance • Gestion de l'Atelier Logistique & Pneumatiques
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Maintenance & Ordres de Travail (OT)</h1>
          <p className="text-slate-400 text-sm mt-1">Planification des entretiens préventifs, curatifs et stock de pièces détachees.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-orange-600 hover:bg-orange-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-orange-600/30 transition-all hover:scale-[1.02]"
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
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-orange-500"
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
                <th className="px-6 py-4 text-right">Fiche</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={5} className="p-12 text-center text-slate-400">Chargement de l'atelier...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={5} className="p-8 text-center text-slate-500">Aucun ordre de travail enregistré.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 flex items-center gap-2 font-mono">
                      <Truck className="w-4 h-4 text-orange-400" />
                      {item.immatriculation_camion || item.vehicule || '—'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      {item.description || '—'}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${prioriteBadge(item.priorite)}`}>
                        {item.priorite || 'NON RENSEIGNÉE'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border ${statutBadge(item.statut)}`}>
                        {item.statut || 'PLANIFIÉ'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <Link
                        href={`/maintenance/view?id=${item.id}`}
                        className="text-xs font-semibold text-orange-400 hover:text-orange-300"
                      >
                        Ouvrir
                      </Link>
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
        <div className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold">Nouveau Bon d'Intervention Atelier</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Camion du parc</label>
                {vehiculesLoading ? (
                  <div className="w-full px-4 py-2.5 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-500">
                    Chargement du parc…
                  </div>
                ) : vehicules.length === 0 ? (
                  <div className="w-full px-4 py-2.5 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-400">
                    Aucun véhicule au parc —{' '}
                    <Link href="/parc" className="text-orange-400 font-semibold hover:text-orange-300">
                      enregistrer un véhicule
                    </Link>
                  </div>
                ) : (
                  <select
                    required
                    value={vehiculeId}
                    onChange={(e) => setVehiculeId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-orange-500 font-mono"
                  >
                    <option value="">— Sélectionner un camion —</option>
                    {vehicules.map((v: any) => (
                      <option key={v.id} value={String(v.id)}>
                        {v.immatriculation}
                        {v.type_vehicule ? ` • ${v.type_vehicule}` : ''}
                        {v.marque || v.modele ? ` • ${[v.marque, v.modele].filter(Boolean).join(' ')}` : ''}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Description des Travaux à Effectuer</label>
                <textarea
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="ex: Remplacement plaquettes de frein avant..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-orange-500 h-20"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Nature de l'intervention</label>
                  <select
                    value={typeMaintenance}
                    onChange={(e) => setTypeMaintenance(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-orange-500"
                  >
                    <option value="PREVENTIVE">Préventive (vidange, filtres)</option>
                    <option value="CURATIVE">Curative (panne, réparation)</option>
                    <option value="VISITE_TECHNIQUE">Visite technique / antipollution</option>
                    <option value="PNEUMATIQUE">Pneumatiques</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Niveau de Priorité</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-orange-500"
                  >
                    <option value="NORMALE">Normale</option>
                    <option value="URGENTE">Urgente (immobilisation)</option>
                    <option value="CRITIQUE">Critique (sécurité)</option>
                  </select>
                </div>
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
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-orange-600 hover:bg-orange-500 text-white shadow-lg shadow-orange-600/30"
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

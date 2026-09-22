'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { qhseAPI } from '@/lib/api-client';
import { ShieldCheck, Plus, Search, CheckCircle2, ShieldAlert, X } from 'lucide-react';
import { toast } from 'sonner';

export default function QhsePage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [siteLocation, setSiteLocation] = useState('Dépôt Douala Youpwé');
  const [riskLevel, setRiskLevel] = useState('FAIBLE');
  const [observations, setObservations] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['qhse'],
    queryFn: async () => {
      const res = await qhseAPI.getQhseRecords();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await qhseAPI.createQhseRecord(payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success("Rapport d'inspection QHSE enregistré !");
      queryClient.invalidateQueries({ queryKey: ['qhse'] });
      setIsModalOpen(false);
      setObservations('');
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement.");
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      site_location: siteLocation,
      niveau_risque: riskLevel,
      observations: observations || 'Contrôle EPI chauffeur conforme à 100%',
    });
  };

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-QHSE...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.site_location || '') + ' ' + String(i.observations || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 text-xs font-semibold mb-2 border border-rose-500/20">
            <ShieldCheck className="w-3.5 h-3.5" />
            K-QHSE • Qualité, Hygiène, Sécurité & Environnement
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Gestion Sécurité & Inspections QHSE</h1>
          <p className="text-slate-400 text-sm mt-1">Conformité ISO 45001, audit EPI et gestion des risques de transport.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-rose-600/30 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          Rédiger un Rapport QHSE
        </button>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Registre des Inspections & Contrôles QHSE
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par site..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Site / Zone de Contrôle</th>
                <th className="px-6 py-4">Observations Auditeur</th>
                <th className="px-6 py-4 text-center">Niveau Risque</th>
                <th className="px-6 py-4 text-right">Statut Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={4} className="p-12 text-center text-slate-400">Chargement du QHSE...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucune inspection enregistrée.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100 flex items-center gap-2">
                      <ShieldAlert className="w-4 h-4 text-rose-400" />
                      {item.site_location || 'Dépôt Douala Youpwé'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      {item.observations || 'Contrôle EPI chauffeur conforme à 100%'}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {item.niveau_risque || 'FAIBLE'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> AUDITÉ
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
              <h3 className="text-lg font-bold">Rapport d'Inspection QHSE</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Localisation du Site</label>
                <input
                  type="text"
                  required
                  value={siteLocation}
                  onChange={(e) => setSiteLocation(e.target.value)}
                  placeholder="ex: Port de Douala quai 14"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-rose-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Niveau de Risque Identifié</label>
                <select
                  value={riskLevel}
                  onChange={(e) => setRiskLevel(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-rose-500"
                >
                  <option value="FAIBLE">Faible (Vert)</option>
                  <option value="MOYEN">Moyen (Orange)</option>
                  <option value="CRITIQUE">Critique (Rouge - Arrêt travail)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Observations & Remarques d'Audit</label>
                <textarea
                  required
                  value={observations}
                  onChange={(e) => setObservations(e.target.value)}
                  placeholder="ex: Vérification extinction extincteurs et harnais..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-rose-500 h-20"
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
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/30"
                >
                  {createMutation.isPending ? 'Enregistrement...' : 'Valider le Rapport'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

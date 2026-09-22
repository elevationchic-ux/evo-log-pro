'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Anchor, Plus, RefreshCw, Search, ArrowLeft,
  Activity, Play, CheckCircle2, Pause
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

interface OperationQuai {
  id: number;
  navire_nom: string;
  quai: string;
  grue_assignee: string;
  equipe_dockers: string;
  statut: string;
  mouvements_prevus: number;
  mouvements_realises: number;
  cadence_horaire: number;
  heure_debut?: string;
}

export default function PortOperationsQuaiPage() {
  const [operations, setOperations] = useState<OperationQuai[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    navire_nom: '',
    quai: 'Poste 14 - Quai Conteneurs Douala',
    grue_assignee: 'Grue Mobile Gottwald 01',
    equipe_dockers: 'Équipe Alpha (Shift A)',
    mouvements_prevus: 180,
    cadence_horaire: 22,
  });

  const fetchOperations = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/acconage-avance/grues');
      if (Array.isArray(res.data) && res.data.length > 0) {
        setOperations(res.data.map((g: any) => ({
          id: g.id,
          navire_nom: g.navire_actuel || 'Navire Porte-Conteneurs',
          quai: g.emplacement || 'Poste 14',
          grue_assignee: g.nom || 'Portique Quai',
          equipe_dockers: 'Équipe Quai',
          statut: g.en_service ? 'EN_COURS' : 'A_L_ARRET',
          mouvements_prevus: 150,
          mouvements_realises: 85,
          cadence_horaire: 24
        })));
      } else {
        setOperations([]);
      }
    } catch {
      setOperations([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOperations();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/api/v1/acconage-avance/grues', {
        nom: formData.grue_assignee,
        emplacement: formData.quai,
        capacite_tonnes: 65.0,
        en_service: true
      });
      toast.success('Grue enregistrée avec succès');
      fetchOperations();
    } catch {
      toast.error("L'enregistrement des opérations de quai n'est pas encore disponible.");
    }
    setIsModalOpen(false);
  };

  const filtered = operations.filter(op =>
    op.navire_nom.toLowerCase().includes(search.toLowerCase()) ||
    op.quai.toLowerCase().includes(search.toLowerCase()) ||
    op.grue_assignee.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Opérations Portuaires
        </Link>
        <span>/</span>
        <span className="text-white">Opérations de Quai & Manutention</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-sky-500/10 text-sky-400 rounded-xl border border-sky-500/20">
            <Anchor className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Opérations de Quai & Manutention Portuaire
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30 font-mono">
                KACC_OPS
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Pilotage des grues mobiles, affectation des shifts dockers et cadences de déchargement/chargement
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchOperations}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            Actualiser
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm shadow-lg shadow-sky-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Lancer un Shift Quai
          </button>
        </div>
      </div>

      {/* Main Table card */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Rechercher navire, quai, engin..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-sky-400" />
            Chargement des opérations de quai...
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Anchor className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucune opération de quai active</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Aucun shift ou engin de levage n'est actuellement affecté sur les quais. Lancez une opération pour coordonner les dockers et grues.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Lancer une première opération de quai
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Navire à Quai</th>
                  <th className="py-3 px-4">Poste & Grue</th>
                  <th className="py-3 px-4">Équipe Dockers</th>
                  <th className="py-3 px-4">Progression Manutention</th>
                  <th className="py-3 px-4">Cadence</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(op => {
                  const pct = Math.min(100, Math.round(((op.mouvements_realises || 0) / (op.mouvements_prevus || 1)) * 100));
                  return (
                    <tr key={op.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-4 font-semibold text-white">
                        {op.navire_nom}
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        <span className="text-slate-300 block font-medium">{op.quai}</span>
                        <span className="text-sky-400">{op.grue_assignee}</span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 text-xs">
                        {op.equipe_dockers}
                      </td>
                      <td className="py-3.5 px-4 w-48">
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="font-mono text-white">{op.mouvements_realises} / {op.mouvements_prevus} TC</span>
                          <span className="text-slate-400">{pct}%</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-sky-500 rounded-full transition-all" style={{ width: `${pct}%` }} />
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-xs text-emerald-400">
                        {op.cadence_horaire} mvts/h
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                          op.statut === 'EN_COURS'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}>
                          {op.statut}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => {
                            setOperations(prev => prev.map(item => item.id === op.id ? { ...item, mouvements_realises: item.mouvements_realises + 1 } : item));
                          }}
                          className="px-2.5 py-1 bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 text-xs rounded border border-sky-500/30 transition"
                        >
                          +1 Mouvement
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Lancement Opération */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Anchor className="w-5 h-5 text-sky-400" />
              Affecter un Shift & Engin de Levage
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Coordination de la manutention quai pour un navire à quai
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Navire concerné *</label>
                <input
                  type="text"
                  required
                  value={formData.navire_nom}
                  onChange={e => setFormData({ ...formData, navire_nom: e.target.value })}
                  placeholder="Ex: MSC MANUELA, CMA CGM TOURVILLE"
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Poste à Quai</label>
                  <input
                    type="text"
                    value={formData.quai}
                    onChange={e => setFormData({ ...formData, quai: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Engin / Grue de Levage</label>
                  <select
                    value={formData.grue_assignee}
                    onChange={e => setFormData({ ...formData, grue_assignee: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  >
                    <option value="Grue Mobile Gottwald 01">Grue Mobile Gottwald 01 (100T)</option>
                    <option value="Grue Mobile Gottwald 02">Grue Mobile Gottwald 02 (100T)</option>
                    <option value="Portique Quai Kalmar P1">Portique Quai Kalmar P1</option>
                    <option value="Reachstacker Terex Quai">Reachstacker Terex 45T</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Équipe de Dockers</label>
                <select
                  value={formData.equipe_dockers}
                  onChange={e => setFormData({ ...formData, equipe_dockers: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                >
                  <option value="Équipe Alpha (Shift Jour 07h-19h)">Équipe Alpha (Shift Jour 07h-19h)</option>
                  <option value="Équipe Bravo (Shift Nuit 19h-07h)">Équipe Bravo (Shift Nuit 19h-07h)</option>
                  <option value="Équipe Renfort Quai 14">Équipe Renfort Quai 14</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Mouvements Prévus (TC)</label>
                  <input
                    type="number"
                    value={formData.mouvements_prevus}
                    onChange={e => setFormData({ ...formData, mouvements_prevus: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Cadence Cible (mvts/h)</label>
                  <input
                    type="number"
                    value={formData.cadence_horaire}
                    onChange={e => setFormData({ ...formData, cadence_horaire: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Démarrer le Shift
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
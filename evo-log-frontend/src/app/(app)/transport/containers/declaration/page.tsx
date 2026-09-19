'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Box, Plus, Search, ArrowLeft, CheckCircle2,
  AlertTriangle, FileCheck, ShieldAlert
} from 'lucide-react';

interface ContainerEIR {
  id: number;
  numero_eir: string;
  numero_conteneur: string;
  type_operation: 'ENTREE_PORT' | 'SORTIE_PORT';
  etat_general: 'BON_ETAT' | 'AVARIE_MINEURE' | 'DOMMAGE_STRUCTUREL';
  numero_scelle: string;
  camion_immatriculation: string;
  date_constat: string;
  inspecteur: string;
  remarques: string;
}

export default function TransportContainersDeclarationPage() {
  const [eirList, setEirList] = useState<ContainerEIR[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    numero_conteneur: '',
    type_operation: 'SORTIE_PORT' as 'ENTREE_PORT' | 'SORTIE_PORT',
    etat_general: 'BON_ETAT' as 'BON_ETAT' | 'AVARIE_MINEURE' | 'DOMMAGE_STRUCTUREL',
    numero_scelle: 'CMA-984210',
    camion_immatriculation: 'LT 521 DE',
    remarques: 'Scellé intègre, portes étanches, absence de perforation',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const id = Date.now();
    const newEIR: ContainerEIR = {
      id,
      numero_eir: `EIR-2026-${String(eirList.length + 1).padStart(4, '0')}`,
      numero_conteneur: formData.numero_conteneur.toUpperCase(),
      type_operation: formData.type_operation,
      etat_general: formData.etat_general,
      numero_scelle: formData.numero_scelle,
      camion_immatriculation: formData.camion_immatriculation,
      date_constat: new Date().toLocaleDateString('fr-FR'),
      inspecteur: 'Agent Contrôle Guérite PAD',
      remarques: formData.remarques
    };
    setEirList(prev => [newEIR, ...prev]);
    setIsModalOpen(false);
  };

  const filtered = eirList.filter(e =>
    e.numero_conteneur.toLowerCase().includes(search.toLowerCase()) ||
    e.numero_eir.toLowerCase().includes(search.toLowerCase()) ||
    e.numero_scelle.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/transport-flotte" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Transport & Flotte
        </Link>
        <span>/</span>
        <span className="text-white">Interchange Conteneurs (EIR)</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
            <Box className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Interchange Conteneurs & Constat d'État (EIR)
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono">
                KTRN_EIR
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Contrôle contradictoire de l'état des boîtes (EIR), scellés douaniers et réserves matériel à la guérite portuaire
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm shadow-lg shadow-cyan-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Établir un Constat EIR
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
              placeholder="Rechercher par N° conteneur, EIR, scellé..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 font-mono uppercase"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Box className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun constat EIR enregistré</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Votre structure n'a pas encore saisi de bordereau d'interchange conteneur pour les sorties ou entrées de parc.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Établir un premier constat EIR
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° EIR</th>
                  <th className="py-3 px-4">N° Conteneur</th>
                  <th className="py-3 px-4">Mouvement</th>
                  <th className="py-3 px-4">N° Scellé</th>
                  <th className="py-3 px-4">Camion Associé</th>
                  <th className="py-3 px-4">État de la Boîte</th>
                  <th className="py-3 px-4 rounded-r-xl">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(eir => (
                  <tr key={eir.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-cyan-400">
                      {eir.numero_eir}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-white">
                      {eir.numero_conteneur}
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className={`px-2 py-0.5 rounded font-mono ${
                        eir.type_operation === 'SORTIE_PORT' ? 'bg-blue-500/10 text-blue-400' : 'bg-purple-500/10 text-purple-400'
                      }`}>
                        {eir.type_operation === 'SORTIE_PORT' ? '↑ Sortie Quai' : '↓ Entrée Quai'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-300">
                      {eir.numero_scelle}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-200">
                      {eir.camion_immatriculation}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        eir.etat_general === 'BON_ETAT'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}>
                        {eir.etat_general}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400 font-mono">
                      {eir.date_constat}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal EIR */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Box className="w-5 h-5 text-cyan-400" />
              Établir un Constat d'Interchange (EIR)
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Constat contradictoire de l'état du conteneur et du scellé à la guérite
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">N° Conteneur *</label>
                  <input
                    type="text"
                    required
                    value={formData.numero_conteneur}
                    onChange={e => setFormData({ ...formData, numero_conteneur: e.target.value })}
                    placeholder="Ex: TGHU 914022-8"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 font-mono uppercase"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Sens Opération</label>
                  <select
                    value={formData.type_operation}
                    onChange={e => setFormData({ ...formData, type_operation: e.target.value as any })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="SORTIE_PORT">Sortie Port (Livraison)</option>
                    <option value="ENTREE_PORT">Entrée Port (Export / Restitution vide)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">N° Plomb / Scellé</label>
                  <input
                    type="text"
                    value={formData.numero_scelle}
                    onChange={e => setFormData({ ...formData, numero_scelle: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Camion Porteur</label>
                  <input
                    type="text"
                    value={formData.camion_immatriculation}
                    onChange={e => setFormData({ ...formData, camion_immatriculation: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">État Physique Constaté</label>
                <select
                  value={formData.etat_general}
                  onChange={e => setFormData({ ...formData, etat_general: e.target.value as any })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                >
                  <option value="BON_ETAT">Bon état (Aucun dommage)</option>
                  <option value="AVARIE_MINEURE">Avarie mineure (Éraflure superficielle)</option>
                  <option value="DOMMAGE_STRUCTUREL">Dommage structurel (Paroi enfoncée / Toit)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Remarques & Réserves Chauffeur / Inspecteur</label>
                <textarea
                  rows={2}
                  value={formData.remarques}
                  onChange={e => setFormData({ ...formData, remarques: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                />
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
                  className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Valider le Constat EIR
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

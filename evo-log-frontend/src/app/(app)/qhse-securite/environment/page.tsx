'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Leaf, Plus, Search, ArrowLeft, CheckCircle2,
  Trash2, Droplets, Wind, FileText, AlertCircle
} from 'lucide-react';

interface DechetEnvironnement {
  id: number;
  bordereau_numero: string;
  type_dechet: string;
  quantite: number;
  unite: string;
  centre_traitement: string;
  date_evacuation: string;
  statut_conformite: 'VALIDE' | 'EN_COURS';
}

export default function QhseEnvironmentPage() {
  const [dechets, setDechets] = useState<DechetEnvironnement[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    type_dechet: 'Huiles de Vidange Usagées (Moteurs Engins)',
    quantite: 1200,
    unite: 'Litres',
    centre_traitement: 'Recycam Industries (Bassa Douala)',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const newD: DechetEnvironnement = {
      id: Date.now(),
      bordereau_numero: `BSDD-2026-${String(dechets.length + 1).padStart(4, '0')}`,
      ...formData,
      date_evacuation: new Date().toISOString().split('T')[0],
      statut_conformite: 'VALIDE'
    };
    setDechets(prev => [newD, ...prev]);
    setIsModalOpen(false);
  };

  const filtered = dechets.filter(d =>
    d.type_dechet.toLowerCase().includes(search.toLowerCase()) ||
    d.bordereau_numero.toLowerCase().includes(search.toLowerCase()) ||
    d.centre_traitement.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Centre Sécurité QHSE
        </Link>
        <span>/</span>
        <span className="text-white">Environnement, MARPOL & Gestion des Déchets</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-green-500/10 text-green-400 rounded-xl border border-green-500/20">
            <Leaf className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Management Environnemental & Norme MARPOL
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/30 font-mono">
                KQHS_ENV
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Traçabilité des déchets portuaires, hydrocarbures, valorisation et respect de la convention MARPOL 73/78
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-green-600 hover:bg-green-500 text-white font-medium text-sm shadow-lg shadow-green-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Émettre un Bordereau BSDD
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
              placeholder="Rechercher par type de déchet, N° bordereau..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-green-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Leaf className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun bordereau de déchet enregistré</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Votre structure n'a pas encore enregistré d'évacuation de déchets industriels ou portuaires. Émettez votre premier bordereau BSDD.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Créer un premier bordereau
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° Bordereau</th>
                  <th className="py-3 px-4">Nature du Déchet</th>
                  <th className="py-3 px-4">Quantité Évacuée</th>
                  <th className="py-3 px-4">Filière Agréée de Traitement</th>
                  <th className="py-3 px-4">Date Évacuation</th>
                  <th className="py-3 px-4 rounded-r-xl">Conformité</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(item => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-green-400">
                      {item.bordereau_numero}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {item.type_dechet}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-white text-xs">
                      {item.quantite.toLocaleString()} {item.unite}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {item.centre_traitement}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                      {item.date_evacuation}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                        <CheckCircle2 className="w-3 h-3" />
                        {item.statut_conformite}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Bordereau Déchet */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Leaf className="w-5 h-5 text-green-400" />
              Émettre un Bordereau de Suivi de Déchet (BSDD)
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Traçabilité réglementaire pour l'élimination conforme des résidus industriels
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Type de Déchet *</label>
                <select
                  value={formData.type_dechet}
                  onChange={e => setFormData({ ...formData, type_dechet: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500"
                >
                  <option value="Huiles de Vidange Usagées (Moteurs Engins)">Huiles de Vidange Usagées</option>
                  <option value="Filtres à Huile & Pièces Imbibées">Filtres à Huile & Pièces Imbibées</option>
                  <option value="Batteries au Plomb Usagées">Batteries au Plomb Usagées</option>
                  <option value="Pneumatiques Poids Lourds Réformés">Pneumatiques Poids Lourds</option>
                  <option value="Eaux Hydrocarburées de Cale MARPOL">Eaux Hydrocarburées MARPOL</option>
                  <option value="Ferrailles & Câbles de Levage">Ferrailles & Câbles de Levage</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Quantité Estimée</label>
                  <input
                    type="number"
                    value={formData.quantite}
                    onChange={e => setFormData({ ...formData, quantite: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Unité de Mesure</label>
                  <select
                    value={formData.unite}
                    onChange={e => setFormData({ ...formData, unite: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500"
                  >
                    <option value="Litres">Litres</option>
                    <option value="Kilogrammes">Kilogrammes</option>
                    <option value="Tonnes">Tonnes</option>
                    <option value="Unités">Unités</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Centre / Prestataire Agréé de Traitement</label>
                <input
                  type="text"
                  value={formData.centre_traitement}
                  onChange={e => setFormData({ ...formData, centre_traitement: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-green-500"
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
                  className="px-5 py-2 bg-green-600 hover:bg-green-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Valider le Bordereau BSDD
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

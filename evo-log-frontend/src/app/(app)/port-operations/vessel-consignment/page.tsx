'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Ship, Plus, Search, ArrowLeft, CheckCircle2,
  Clock, Fuel, Users, Anchor, FileCheck
} from 'lucide-react';

interface ConsignmentService {
  id: number;
  navire_nom: string;
  type_service: string;
  prestataire: string;
  date_demande: string;
  statut: string;
  montant_estime_xaf: number;
  commentaires?: string;
}

export default function PortOperationsVesselConsignmentPage() {
  const [services, setServices] = useState<ConsignmentService[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    navire_nom: '',
    type_service: 'Pilotage & Remorquage',
    prestataire: 'Boluda Towage Cameroun',
    montant_estime_xaf: 1850000,
    commentaires: 'Assistance entrée chenal et évitage poste 14',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const newService: ConsignmentService = {
      id: Date.now(),
      ...formData,
      date_demande: new Date().toISOString(),
      statut: 'COMMANDE'
    };
    setServices(prev => [newService, ...prev]);
    setIsModalOpen(false);
    setFormData({
      navire_nom: '',
      type_service: 'Pilotage & Remorquage',
      prestataire: 'Boluda Towage Cameroun',
      montant_estime_xaf: 1850000,
      commentaires: 'Assistance entrée chenal et évitage poste 14',
    });
  };

  const filtered = services.filter(s =>
    s.navire_nom.toLowerCase().includes(search.toLowerCase()) ||
    s.type_service.toLowerCase().includes(search.toLowerCase()) ||
    s.prestataire.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Opérations Portuaires
        </Link>
        <span>/</span>
        <span className="text-white">Consignation Navire & Services Portuaires</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
            <Ship className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Consignation Navire & Services Armateurs
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30 font-mono">
                KACC_CNS
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Assistance aux escales, pilotage, remorquage, avitaillement, soutage et relèves d'équipage maritimes
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-sm shadow-lg shadow-purple-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Commander un Service Navire
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
              placeholder="Rechercher par navire, service, prestataire..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Ship className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun service de consignation enregistré</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Votre agence maritime n'a pas encore ouvert de demande de prestation pour un navire en escale.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Commander un premier service
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Navire</th>
                  <th className="py-3 px-4">Prestation Demandée</th>
                  <th className="py-3 px-4">Prestataire Agréé</th>
                  <th className="py-3 px-4">Date Commande</th>
                  <th className="py-3 px-4">Montant Estimé (XAF)</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {s.navire_nom}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-medium text-purple-400">
                      {s.type_service}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 text-xs">
                      {s.prestataire}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {new Date(s.date_demande).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-white font-bold">
                      {s.montant_estime_xaf.toLocaleString()} XAF
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        s.statut === 'VALIDE_DEBOURS'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {s.statut}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {s.statut !== 'VALIDE_DEBOURS' && (
                        <button
                          onClick={() => {
                            setServices(prev => prev.map(item => item.id === s.id ? { ...item, statut: 'VALIDE_DEBOURS' } : item));
                          }}
                          className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs rounded border border-emerald-500/30 transition"
                        >
                          Clôturer Débours
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Commande Service */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Ship className="w-5 h-5 text-purple-400" />
              Commander une Prestation Navire
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enregistrement des débours et services aux armateurs en escale
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Navire en Escale *</label>
                <input
                  type="text"
                  required
                  value={formData.navire_nom}
                  onChange={e => setFormData({ ...formData, navire_nom: e.target.value })}
                  placeholder="Ex: CMA CGM CAMEROUN"
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Type de Prestation</label>
                  <select
                    value={formData.type_service}
                    onChange={e => setFormData({ ...formData, type_service: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="Pilotage & Remorquage">Pilotage & Remorquage</option>
                    <option value="Lamunage & Amarrage">Lamunage & Amarrage</option>
                    <option value="Soutage (Bunkering Carburant)">Soutage (Bunkering Carburant)</option>
                    <option value="Avitaillement Eau & Vivres">Avitaillement Eau & Vivres</option>
                    <option value="Relève d'Équipage & Visas">Relève d'Équipage & Visas</option>
                    <option value="Évacuation Eaux Usées MARPOL">Évacuation Eaux Usées MARPOL</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Prestataire Agréé</label>
                  <input
                    type="text"
                    value={formData.prestataire}
                    onChange={e => setFormData({ ...formData, prestataire: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Montant Estimé Débours (XAF)</label>
                <input
                  type="number"
                  value={formData.montant_estime_xaf}
                  onChange={e => setFormData({ ...formData, montant_estime_xaf: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Instructions Opérationnelles</label>
                <textarea
                  rows={2}
                  value={formData.commentaires}
                  onChange={e => setFormData({ ...formData, commentaires: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
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
                  className="px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Émettre l'Ordre de Service
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

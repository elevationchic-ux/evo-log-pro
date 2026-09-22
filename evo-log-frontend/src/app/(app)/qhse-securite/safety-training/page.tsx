'use client';

import React, { useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Users, Plus, Search, ArrowLeft, CheckCircle2,
  Calendar, Award, AlertTriangle, Shield
} from 'lucide-react';

interface HabilitationSecurite {
  id: number;
  employe_nom: string;
  matricule: string;
  type_formation: string;
  organisme_formateur: string;
  date_obtention: string;
  date_expiration: string;
  statut: 'VALIDE' | 'EXPIRATION_PROCHE' | 'EXPIRE';
}

export default function QhseSafetyTrainingPage() {
  const [formations, setFormations] = useState<HabilitationSecurite[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    employe_nom: '',
    matricule: '',
    type_formation: 'CACES R489 - Chariots Automoteurs de Manutention',
    organisme_formateur: 'APAVE Cameroun / Bureau Veritas',
    date_obtention: '2025-06-15',
    date_expiration: '2027-06-15',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error('Création indisponible : les habilitations doivent être enregistrées par une API RH persistante.');
    return;
  };

  const filtered = formations.filter(f =>
    f.employe_nom.toLowerCase().includes(search.toLowerCase()) ||
    f.matricule.toLowerCase().includes(search.toLowerCase()) ||
    f.type_formation.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Centre Sécurité QHSE
        </Link>
        <span>/</span>
        <span className="text-white">Formations & Habilitations de Sécurité</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Passeports Sécurité & Habilitations Professionnelles
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                KQHS_TRN
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Registre des certifications de sécurité portuaire, CACES, SST et habilitations aux matières dangereuses (IMDG)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm shadow-lg shadow-emerald-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Attribuer une Habilitation
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
              placeholder="Rechercher collaborateur, matricule, formation..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Award className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucune habilitation enregistrée</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Le passeport sécurité de votre structure est actuellement vide. Enregistrez les habilitations de vos premiers conducteurs ou dockers.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Attribuer une première certification
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Collaborateur</th>
                  <th className="py-3 px-4">Matricule</th>
                  <th className="py-3 px-4">Habilitation / Formation</th>
                  <th className="py-3 px-4">Organisme Certificateur</th>
                  <th className="py-3 px-4">Obtention</th>
                  <th className="py-3 px-4">Échéance Recyclage</th>
                  <th className="py-3 px-4 rounded-r-xl">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(item => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {item.employe_nom}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-emerald-400">
                      {item.matricule}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-200">
                      {item.type_formation}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {item.organisme_formateur}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                      {item.date_obtention}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-200">
                      {item.date_expiration}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                        <CheckCircle2 className="w-3 h-3" />
                        {item.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Habilitation */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Award className="w-5 h-5 text-emerald-400" />
              Attribuer une Habilitation Sécurité
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enregistrement dans le passeport de formation individuel
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Nom du Salarié *</label>
                  <input
                    type="text"
                    required
                    value={formData.employe_nom}
                    onChange={e => setFormData({ ...formData, employe_nom: e.target.value })}
                    placeholder="Ex: Jean Dupont"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Matricule Salarié *</label>
                  <input
                    type="text"
                    required
                    value={formData.matricule}
                    onChange={e => setFormData({ ...formData, matricule: e.target.value })}
                    placeholder="Ex: MAT-0142"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Type d'Habilitation / Formation</label>
                <select
                  value={formData.type_formation}
                  onChange={e => setFormData({ ...formData, type_formation: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="CACES R489 - Chariots Automoteurs">CACES R489 - Chariots Élévateurs</option>
                  <option value="CACES R484 - Ponts Roulants & Portiques">CACES R484 - Portiques & Grues</option>
                  <option value="SST - Sauveteur Secouriste du Travail">SST - Sauveteur Secouriste</option>
                  <option value="Code IMDG - Matières Dangereuses">Code IMDG - Matières Dangereuses</option>
                  <option value="Sécurité Incendie & Évacuation Quai">Sécurité Incendie & Évacuation Quai</option>
                  <option value="Sensibilisation Code ISPS Niveau 1">Sensibilisation Code ISPS</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Organisme Formateur</label>
                <input
                  type="text"
                  value={formData.organisme_formateur}
                  onChange={e => setFormData({ ...formData, organisme_formateur: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Date d'Obtention</label>
                  <input
                    type="date"
                    value={formData.date_obtention}
                    onChange={e => setFormData({ ...formData, date_obtention: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Date d'Échéance (Recyclage)</label>
                  <input
                    type="date"
                    value={formData.date_expiration}
                    onChange={e => setFormData({ ...formData, date_expiration: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
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
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Enregistrer l'Habilitation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

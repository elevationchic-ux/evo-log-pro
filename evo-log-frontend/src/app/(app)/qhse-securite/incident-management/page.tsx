'use client';

import React, { useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  AlertTriangle, Plus, Search, ArrowLeft, CheckCircle2,
  Clock, ShieldAlert, FileText, UserCheck
} from 'lucide-react';

interface IncidentInvestigation {
  id: number;
  code_incident: string;
  titre: string;
  responsable_enquete: string;
  cause_racine: string;
  action_corrective: string;
  echeance: string;
  statut: 'EN_ENQUETE' | 'PLAN_ACTION' | 'CLOTURE';
}

export default function QhseIncidentManagementPage() {
  const [investigations, setInvestigations] = useState<IncidentInvestigation[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    titre: '',
    responsable_enquete: 'Paul Nguessan (Resp. QHSE)',
    cause_racine: 'Défaut de signalisation au sol et vitesse excessive d\'un engin de manutention',
    action_corrective: 'Repeindre le balisage piéton Quai 14 et installer des ralentisseurs',
    echeance: '2026-09-30',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error('Création indisponible : les enquêtes QHSE doivent être enregistrées par une API persistante.');
    return;
  };

  const filtered = investigations.filter(i =>
    i.titre.toLowerCase().includes(search.toLowerCase()) ||
    i.code_incident.toLowerCase().includes(search.toLowerCase()) ||
    i.action_corrective.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Centre Sécurité QHSE
        </Link>
        <span>/</span>
        <span className="text-white">Gestion des Incidents & Arbre des Causes</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-red-500/10 text-red-400 rounded-xl border border-red-500/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Plan d'Actions Correctives & Préventives (CAPA)
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/30 font-mono">
                KQHS_INC
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Analyse des causes profondes (5 Pourquoi / Ishikawa), assignation des responsabilités et suivi des clôtures
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-medium text-sm shadow-lg shadow-red-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Ouvrir une Enquête CAPA
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
              placeholder="Rechercher code CAPA, titre, action..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-red-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <ShieldAlert className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun plan d'action CAPA actif</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Tous les incidents ont été traités ou aucune anomalie n'a nécessité l'ouverture d'un plan d'actions correctives.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Ouvrir un premier dossier d'enquête
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Réf. CAPA</th>
                  <th className="py-3 px-4">Titre de l'Anomalie</th>
                  <th className="py-3 px-4">Cause Racine Identifiée</th>
                  <th className="py-3 px-4">Action Corrective Retenue</th>
                  <th className="py-3 px-4">Responsable</th>
                  <th className="py-3 px-4">Échéance</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(item => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-red-400">
                      {item.code_incident}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {item.titre}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300 max-w-xs truncate">
                      {item.cause_racine}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-emerald-400 max-w-xs truncate">
                      {item.action_corrective}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {item.responsable_enquete}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono">
                      {item.echeance}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        item.statut === 'CLOTURE'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {item.statut}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {item.statut !== 'CLOTURE' && (
                        <button
                          onClick={() => {
                            setInvestigations(prev => prev.map(inv => inv.id === item.id ? { ...inv, statut: 'CLOTURE' } : inv));
                          }}
                          className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs rounded border border-emerald-500/30 transition"
                        >
                          Clôturer Action
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

      {/* Modal Enquête CAPA */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              Ouvrir un Plan d'Action CAPA
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enquête de sécurité et attribution d'actions correctives
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Titre de l'Événement *</label>
                <input
                  type="text"
                  required
                  value={formData.titre}
                  onChange={e => setFormData({ ...formData, titre: e.target.value })}
                  placeholder="Ex: Collision chariot / piéton Terre-plein Est"
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Responsable Enquête</label>
                  <input
                    type="text"
                    value={formData.responsable_enquete}
                    onChange={e => setFormData({ ...formData, responsable_enquete: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Date d'Échéance</label>
                  <input
                    type="date"
                    value={formData.echeance}
                    onChange={e => setFormData({ ...formData, echeance: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Cause Racine Déterminée (Arbre des Causes) *</label>
                <textarea
                  rows={2}
                  required
                  value={formData.cause_racine}
                  onChange={e => setFormData({ ...formData, cause_racine: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Action Corrective / Mesure d'Amélioration *</label>
                <textarea
                  rows={2}
                  required
                  value={formData.action_corrective}
                  onChange={e => setFormData({ ...formData, action_corrective: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
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
                  className="px-5 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Valider le Plan d'Action
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  ShieldAlert, Plus, RefreshCw, Search, CheckCircle2,
  AlertTriangle, ShieldCheck, Flame, Users, FileCheck,
  ArrowUpRight, Clock, HeartHandshake, Leaf
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

interface IncidentQHSE {
  id: number;
  reference: string;
  type_evenement: string;
  lieu: string;
  date_heure: string;
  gravite: 'BENIN' | 'SIGNIFICATIF' | 'GRAVE';
  arret_travail: boolean;
  statut: 'EN_COURS' | 'TRAITE' | 'CLOTURE';
  description: string;
}

export default function QhseSecuriteDashboardPage() {
  const [incidents, setIncidents] = useState<IncidentQHSE[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    type_evenement: 'Presqu\'accident (Near-Miss)',
    lieu: 'Terre-plein Conteneurs Quai 14 (Douala)',
    gravite: 'BENIN' as 'BENIN' | 'SIGNIFICATIF' | 'GRAVE',
    arret_travail: false,
    description: 'Chariot élévateur ayant frôlé un piéton hors du passage balisé ISPS',
  });

  const handleCreateIncident = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error('Création indisponible : les incidents QHSE doivent être enregistrés par une API persistante.');
    return;
  };

  const submodules = [
    { title: 'Gestion des Incidents', desc: 'Arbre des causes & actions correctives', path: '/qhse-securite/incident-management', icon: AlertTriangle, tcode: 'KQHS_INC', color: 'from-red-600 to-amber-600' },
    { title: 'Inspections Portuaires', desc: 'Contrôles de zone & sûreté Code ISPS', path: '/qhse-securite/port-inspections', icon: ShieldCheck, tcode: 'KQHS_ISP', color: 'from-blue-600 to-indigo-600' },
    { title: 'Formations & Habilitations', desc: 'Passeports sécurité, CACES, SST', path: '/qhse-securite/safety-training', icon: Users, tcode: 'KQHS_TRN', color: 'from-emerald-600 to-teal-600' },
    { title: 'Environnement & MARPOL', desc: 'Rejets soute, hydrocarbures, tri déchets', path: '/qhse-securite/environment', icon: Leaf, tcode: 'KQHS_ENV', color: 'from-green-600 to-emerald-600' },
    { title: 'Conformité Réglementaire', desc: 'Code du Travail & veille légale CEMAC', path: '/qhse-securite/ohada-compliance', icon: FileCheck, tcode: 'KQHS_OHD', color: 'from-purple-600 to-indigo-600' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Centre de Pilotage QHSE & Sûreté Portuaire
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                KQHS_DSH • Code ISPS
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Qualité, Hygiène, Sécurité au Travail, Protection de l'Environnement et Sûreté Maritime
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-medium text-sm shadow-lg shadow-red-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Déclarer un Incident / Presqu'accident
          </button>
        </div>
      </div>

      {/* Safety Scoreboard */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Jours Sans Accident LTI</span>
          <p className="text-3xl font-extrabold text-emerald-400 mt-1 font-mono">148</p>
          <span className="text-xs text-emerald-400 flex items-center gap-1 mt-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Record d'établissement : 210 jours
          </span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Taux de Fréquence (TF)</span>
          <p className="text-3xl font-extrabold text-white mt-1 font-mono">1.82</p>
          <span className="text-xs text-slate-400 mt-1 block">Objectif annuel : &lt; 2.5</span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Conformité Code ISPS</span>
          <p className="text-3xl font-extrabold text-blue-400 mt-1 font-mono">98.4%</p>
          <span className="text-xs text-blue-400 mt-1 block">Zone sous-douane PAD & PAK</span>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Habilitations Valides</span>
          <p className="text-3xl font-extrabold text-purple-400 mt-1 font-mono">94.8%</p>
          <span className="text-xs text-slate-400 mt-1 block">182 agents certifiés</span>
        </div>
      </div>

      {/* Submodules Grid */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Modules Spécialisés QHSE</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {submodules.map((sub, i) => {
            const Icon = sub.icon;
            return (
              <Link
                key={i}
                href={sub.path}
                className="group relative bg-slate-900/70 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-slate-700 transition duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className={`p-2.5 rounded-xl bg-gradient-to-br ${sub.color} text-white shadow-md`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                        {sub.tcode}
                      </span>
                      <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition" />
                    </div>
                  </div>
                  <h3 className="font-semibold text-white text-base group-hover:text-emerald-400 transition">
                    {sub.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    {sub.desc}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                  <span>Accéder au registre</span>
                  <span className="text-emerald-400 font-medium">Ouvrir →</span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Incidents Table */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <h2 className="text-lg font-semibold text-white mb-1">Registre des Signalements & Événements</h2>
        <p className="text-xs text-slate-400 mb-6">Suivi des événements indésirables, accidents et presqu'accidents</p>

        {incidents.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <ShieldCheck className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun incident de sécurité en cours</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Félicitations, aucun événement indésirable n'est ouvert pour votre structure. En cas de situation dangereuse, effectuez un signalement immédiat.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Signaler un risque / presqu'accident
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Réf. Incident</th>
                  <th className="py-3 px-4">Nature de l'Événement</th>
                  <th className="py-3 px-4">Lieu</th>
                  <th className="py-3 px-4">Gravité</th>
                  <th className="py-3 px-4">Arrêt de Travail</th>
                  <th className="py-3 px-4">Date / Heure</th>
                  <th className="py-3 px-4 rounded-r-xl">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {incidents.map(inc => (
                  <tr key={inc.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-red-400">
                      {inc.reference}
                    </td>
                    <td className="py-3.5 px-4 text-white font-medium">
                      {inc.type_evenement}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {inc.lieu}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        inc.gravite === 'GRAVE'
                          ? 'bg-red-500/20 text-red-400'
                          : inc.gravite === 'SIGNIFICATIF'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {inc.gravite}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs font-semibold">
                      {inc.arret_travail ? (
                        <span className="text-red-400">Oui (LTI)</span>
                      ) : (
                        <span className="text-emerald-400">Non</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400 font-mono">
                      {inc.date_heure}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {inc.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Signalement */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              Signaler un Événement Sécurité QHSE
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enregistrement immédiat pour déclenchement de l'arbre des causes
            </p>

            <form onSubmit={handleCreateIncident} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Type d'Événement *</label>
                <select
                  value={formData.type_evenement}
                  onChange={e => setFormData({ ...formData, type_evenement: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                >
                  <option value="Presqu'accident (Near-Miss)">Presqu'accident (Near-Miss)</option>
                  <option value="Accident du Travail (avec arrêt)">Accident du Travail (avec arrêt)</option>
                  <option value="Accident du Travail (sans arrêt)">Accident du Travail (sans arrêt)</option>
                  <option value="Déversement Hydrocarbure (Environnement)">Déversement Hydrocarbure</option>
                  <option value="Non-conformité Sûreté Code ISPS">Non-conformité Sûreté Code ISPS</option>
                  <option value="Incident Incendie / Électrique">Incident Incendie / Électrique</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Lieu Exact *</label>
                  <input
                    type="text"
                    required
                    value={formData.lieu}
                    onChange={e => setFormData({ ...formData, lieu: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Gravité Potentielle</label>
                  <select
                    value={formData.gravite}
                    onChange={e => setFormData({ ...formData, gravite: e.target.value as any })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  >
                    <option value="BENIN">Bénin (Sans dommage majeur)</option>
                    <option value="SIGNIFICATIF">Significatif (Soins médicaux)</option>
                    <option value="GRAVE">Grave (Hospitalisation / Danger mortel)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.arret_travail}
                    onChange={e => setFormData({ ...formData, arret_travail: e.target.checked })}
                    className="rounded bg-slate-800 border-slate-700 text-red-600 focus:ring-0"
                  />
                  <span>Arrêt de travail consécutif (Impact LTI)</span>
                </label>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Description des Circonstances *</label>
                <textarea
                  rows={3}
                  required
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Décrivez précisément ce qui s'est passé, les engins impliqués et les premières mesures prises..."
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
                  Enregistrer le Signalement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
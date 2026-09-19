'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  AlertTriangle, Plus, Search, ArrowLeft, CheckCircle2,
  FileText, Camera, ShieldAlert, Clock
} from 'lucide-react';

interface QuaiIncident {
  id: number;
  numero_dossier: string;
  type_incident: string;
  numero_conteneur: string;
  navire_concerne: string;
  lieu_exact: string;
  date_incident: string;
  gravite: 'FAIBLE' | 'MOYENNE' | 'CRITIQUE';
  statut: 'DECLARE' | 'ENQUETE' | 'CLOTURE';
  montant_dommage_estime_xaf: number;
  description: string;
}

export default function PortOperationsIncidentsPage() {
  const [incidents, setIncidents] = useState<QuaiIncident[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    type_incident: 'Avarie de Conteneur (Choc / Déformation)',
    numero_conteneur: '',
    navire_concerne: 'CMA CGM CAMEROUN',
    lieu_exact: 'Quai 14 - Sous portique P1',
    gravite: 'MOYENNE' as 'FAIBLE' | 'MOYENNE' | 'CRITIQUE',
    montant_dommage_estime_xaf: 450000,
    description: 'Enfoncement de la paroi latérale droite lors de la dépose par le spreader',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const id = Date.now();
    const newInc: QuaiIncident = {
      id,
      numero_dossier: `AVR-2026-${String(incidents.length + 1).padStart(4, '0')}`,
      numero_conteneur: formData.numero_conteneur.toUpperCase(),
      type_incident: formData.type_incident,
      navire_concerne: formData.navire_concerne,
      lieu_exact: formData.lieu_exact,
      date_incident: new Date().toISOString(),
      gravite: formData.gravite,
      statut: 'DECLARE',
      montant_dommage_estime_xaf: formData.montant_dommage_estime_xaf,
      description: formData.description
    };
    setIncidents(prev => [newInc, ...prev]);
    setIsModalOpen(false);
    setFormData({
      type_incident: 'Avarie de Conteneur (Choc / Déformation)',
      numero_conteneur: '',
      navire_concerne: 'CMA CGM CAMEROUN',
      lieu_exact: 'Quai 14 - Sous portique P1',
      gravite: 'MOYENNE',
      montant_dommage_estime_xaf: 450000,
      description: 'Enfoncement de la paroi latérale droite lors de la dépose par le spreader',
    });
  };

  const filtered = incidents.filter(i =>
    i.numero_conteneur.toLowerCase().includes(search.toLowerCase()) ||
    i.numero_dossier.toLowerCase().includes(search.toLowerCase()) ||
    i.type_incident.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Opérations Portuaires
        </Link>
        <span>/</span>
        <span className="text-white">Avaries Quai & Incidents de Manutention</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-red-500/10 text-red-400 rounded-xl border border-red-500/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Avaries Quai & Incidents de Manutention
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/30 font-mono">
                KACC_INC
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Déclaration des constats d'avaries sur conteneurs et cargaisons, réserves contradictoires et dossiers assurances
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-medium text-sm shadow-lg shadow-red-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Déclarer une Avarie Quai
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
              placeholder="Rechercher dossier, conteneur, type d'avarie..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-red-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <ShieldAlert className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun incident ou avarie déclaré</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              La zone de manutention ne recense aucune avarie ou litige sur conteneur en cours.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Déclarer un constat d'avarie
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° Dossier Avarie</th>
                  <th className="py-3 px-4">N° Conteneur</th>
                  <th className="py-3 px-4">Nature de l'Avarie</th>
                  <th className="py-3 px-4">Navire & Lieu Quai</th>
                  <th className="py-3 px-4">Dommage Estimé (XAF)</th>
                  <th className="py-3 px-4">Gravité</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(i => (
                  <tr key={i.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-red-400">
                      {i.numero_dossier}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-white font-bold">
                      {i.numero_conteneur}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {i.type_incident}
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="text-white block font-medium">{i.navire_concerne}</span>
                      <span className="text-slate-400">{i.lieu_exact}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-white font-bold">
                      {i.montant_dommage_estime_xaf.toLocaleString()} XAF
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        i.gravite === 'CRITIQUE'
                          ? 'bg-red-500/20 text-red-400'
                          : i.gravite === 'MOYENNE'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {i.gravite}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {i.statut}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => alert(`Téléchargement du Constat Contradictoire d'Avarie pour le conteneur ${i.numero_conteneur}`)}
                        className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition"
                        title="Télécharger Constat d'Avarie"
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Déclaration Avarie */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              Émettre un Constat d'Avarie Quai
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Constat contradictoire officiel pour réserves armateur et assurance
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
                    placeholder="Ex: CMAU 652418-0"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500 font-mono uppercase"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Navire en Escale</label>
                  <input
                    type="text"
                    value={formData.navire_concerne}
                    onChange={e => setFormData({ ...formData, navire_concerne: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Nature de l'Avarie</label>
                  <select
                    value={formData.type_incident}
                    onChange={e => setFormData({ ...formData, type_incident: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  >
                    <option value="Avarie de Conteneur (Choc / Déformation)">Choc / Déformation Paroi</option>
                    <option value="Perforation Toit / Plancher">Perforation Toit / Plancher</option>
                    <option value="Rupture de Scellé Douane / Ligne">Rupture de Scellé</option>
                    <option value="Panne Groupe Frigorifique (Reefer)">Panne Groupe Reefer</option>
                    <option value="Chute de Charge Manutention">Chute de Charge</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Degré de Gravité</label>
                  <select
                    value={formData.gravite}
                    onChange={e => setFormData({ ...formData, gravite: e.target.value as any })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  >
                    <option value="FAIBLE">Faible (Cosmétique)</option>
                    <option value="MOYENNE">Moyenne (Réparation Requise)</option>
                    <option value="CRITIQUE">Critique (Marchandise Menacée)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Lieu Exact sur le Port</label>
                  <input
                    type="text"
                    value={formData.lieu_exact}
                    onChange={e => setFormData({ ...formData, lieu_exact: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Dommage Estimé (XAF)</label>
                  <input
                    type="number"
                    value={formData.montant_dommage_estime_xaf}
                    onChange={e => setFormData({ ...formData, montant_dommage_estime_xaf: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Description des Circonstances</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
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
                  Émettre le Constat d'Avarie
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

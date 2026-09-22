'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Clock, Plus, Search, ArrowLeft, Ship, CheckCircle2,
  Calendar, MapPin, Anchor, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

interface BerthAllocation {
  id: number;
  poste_quai: string;
  port: string;
  longueur_disponible_m: number;
  navire_nom: string;
  armateur: string;
  date_accostage: string;
  date_appareillage: string;
  tirant_eau_m: number;
  statut: string;
}

export default function PortOperationsBerthPlanningPage() {
  const [berths, setBerths] = useState<BerthAllocation[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    poste_quai: 'Poste 14 (Quai Conteneurs)',
    port: 'Douala (PAD)',
    longueur_disponible_m: 280,
    navire_nom: '',
    armateur: 'CMA CGM',
    date_accostage: '',
    date_appareillage: '',
    tirant_eau_m: 10.5,
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error("L'allocation de poste à quai n'est pas encore raccordée à l'API.");
    setIsModalOpen(false);
    setFormData({
      poste_quai: 'Poste 14 (Quai Conteneurs)',
      port: 'Douala (PAD)',
      longueur_disponible_m: 280,
      navire_nom: '',
      armateur: 'CMA CGM',
      date_accostage: '',
      date_appareillage: '',
      tirant_eau_m: 10.5,
    });
  };

  const filtered = berths.filter(b =>
    b.navire_nom.toLowerCase().includes(search.toLowerCase()) ||
    b.poste_quai.toLowerCase().includes(search.toLowerCase()) ||
    b.port.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Opérations Portuaires
        </Link>
        <span>/</span>
        <span className="text-white">Planning d'Accostage & Attribution des Postes</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Planning d'Accostage des Postes à Quai
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono">
                KACC_PLN
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Affectation des postes d'accostage aux navires, tirants d'eau admissibles et fenêtres météo
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm shadow-lg shadow-cyan-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Attribuer un Poste à Quai
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
              placeholder="Rechercher par navire, poste ou port..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Ship className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucune attribution de poste active</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Tous les postes à quai de votre structure sont actuellement libres ou en attente de programmation. Attribuez un poste au premier navire attendu.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Programmer un accostage
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Poste / Quai</th>
                  <th className="py-3 px-4">Port</th>
                  <th className="py-3 px-4">Navire Affecté</th>
                  <th className="py-3 px-4">Armateur</th>
                  <th className="py-3 px-4">Fenêtre Accostage → Départ</th>
                  <th className="py-3 px-4">Tirant d'eau</th>
                  <th className="py-3 px-4 rounded-r-xl">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(b => (
                  <tr key={b.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {b.poste_quai}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {b.port}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-cyan-400">
                      {b.navire_nom}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {b.armateur}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-300">
                      {b.date_accostage ? new Date(b.date_accostage).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : 'ETA Inconnu'}
                      {' → '}
                      {b.date_appareillage ? new Date(b.date_appareillage).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : 'ETD Inconnu'}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs">
                      {b.tirant_eau_m} m
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {b.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Attribution */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Clock className="w-5 h-5 text-cyan-400" />
              Attribuer un Poste à Quai
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Réservation d'un linéaire de quai et validation du tirant d'eau
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Nom du Navire *</label>
                <input
                  type="text"
                  required
                  value={formData.navire_nom}
                  onChange={e => setFormData({ ...formData, navire_nom: e.target.value })}
                  placeholder="Ex: MSC SOPHIE, BOURBON LIBERTY"
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Port</label>
                  <select
                    value={formData.port}
                    onChange={e => setFormData({ ...formData, port: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="Douala (PAD)">Douala (PAD)</option>
                    <option value="Kribi (PAK)">Kribi (PAK Mboro)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Poste d'Accostage</label>
                  <input
                    type="text"
                    value={formData.poste_quai}
                    onChange={e => setFormData({ ...formData, poste_quai: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Accostage Prévu</label>
                  <input
                    type="datetime-local"
                    required
                    value={formData.date_accostage}
                    onChange={e => setFormData({ ...formData, date_accostage: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Appareillage Prévu</label>
                  <input
                    type="datetime-local"
                    required
                    value={formData.date_appareillage}
                    onChange={e => setFormData({ ...formData, date_appareillage: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Armateur</label>
                  <input
                    type="text"
                    value={formData.armateur}
                    onChange={e => setFormData({ ...formData, armateur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Tirant d'Eau Navire (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.tirant_eau_m}
                    onChange={e => setFormData({ ...formData, tirant_eau_m: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500"
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
                  className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Confirmer Attribution
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
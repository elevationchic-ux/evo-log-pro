'use client';

import React, { useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Fuel, Plus, Search, ArrowLeft, CheckCircle2,
  AlertTriangle, DollarSign, Gauge, Calendar, Truck
} from 'lucide-react';

interface TicketCarburant {
  id: number;
  numero_ticket: string;
  immatriculation: string;
  chauffeur: string;
  station: string;
  litres: number;
  prix_litre_xaf: number;
  montant_total_xaf: number;
  index_km: number;
  conso_calculee_l100: number;
  alerte_surconsommation: boolean;
  date_plein: string;
}

export default function SaisieTicketCarburantPage() {
  const [tickets, setTickets] = useState<TicketCarburant[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    numero_ticket: '',
    immatriculation: 'LT 912 AB (Actros 3340)',
    chauffeur: 'Pierre Martin (Chauffeur Lourd)',
    station: 'TotalEnergies Bonabéri (Douala)',
    litres: 350,
    prix_litre_xaf: 828, // Prix gazole officiel Cameroun
    index_km: 142500,
    index_precedent: 141700,
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setIsModalOpen(false);
    toast.error('La saisie carburant nécessite encore un endpoint backend persistant.');
  };

  const filtered = tickets.filter(t =>
    t.immatriculation.toLowerCase().includes(search.toLowerCase()) ||
    t.numero_ticket.toLowerCase().includes(search.toLowerCase()) ||
    t.chauffeur.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/transport-flotte" className="hover:text-amber-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Transport & Flotte
        </Link>
        <span>/</span>
        <span className="text-white">Saisie & Contrôle des Tickets Carburant</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Fuel className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Saisie des Tickets Carburant & Contrôle FuelGuard
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-mono">
                KTRN_FUL
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Enregistrement des prises de carburant en station, réconciliation des litrages et détection des anomalies
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-sm shadow-lg shadow-amber-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Saisir un Ticket Carburant
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
              placeholder="Rechercher ticket, camion, chauffeur..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Fuel className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun ticket carburant enregistré</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Votre structure n'a pas encore saisi de plein de carburant. Saisissez le premier ticket remis par vos conducteurs.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Saisir un premier ticket
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° Ticket</th>
                  <th className="py-3 px-4">Véhicule</th>
                  <th className="py-3 px-4">Chauffeur</th>
                  <th className="py-3 px-4">Station Service</th>
                  <th className="py-3 px-4">Litrages & Prix</th>
                  <th className="py-3 px-4">Total (XAF)</th>
                  <th className="py-3 px-4">Conso. Calculée</th>
                  <th className="py-3 px-4 rounded-r-xl">Contrôle FuelGuard</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-amber-400">
                      {t.numero_ticket}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {t.immatriculation}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {t.chauffeur}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {t.station}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs">
                      <span className="text-white font-bold">{t.litres} L</span>
                      <span className="text-slate-400 block">à {t.prix_litre_xaf} XAF/L</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-white font-bold">
                      {t.montant_total_xaf.toLocaleString()} XAF
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs font-bold text-slate-200">
                      {t.conso_calculee_l100} L/100km
                    </td>
                    <td className="py-3.5 px-4">
                      {t.alerte_surconsommation ? (
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20 flex items-center gap-1 w-fit">
                          <AlertTriangle className="w-3 h-3" />
                          Surconsommation
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                          <CheckCircle2 className="w-3 h-3" />
                          Conforme
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Saisie Ticket */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Fuel className="w-5 h-5 text-amber-400" />
              Saisir un Ticket de Carburant
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enregistrement de la prise de carburant et vérification du ratio kilométrique
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">N° du Reçu / Ticket *</label>
                  <input
                    type="text"
                    required
                    value={formData.numero_ticket}
                    onChange={e => setFormData({ ...formData, numero_ticket: e.target.value })}
                    placeholder="Ex: TCK-TOT-88412"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Véhicule Poids Lourd</label>
                  <input
                    type="text"
                    value={formData.immatriculation}
                    onChange={e => setFormData({ ...formData, immatriculation: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Chauffeur</label>
                  <input
                    type="text"
                    value={formData.chauffeur}
                    onChange={e => setFormData({ ...formData, chauffeur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Station Service</label>
                  <select
                    value={formData.station}
                    onChange={e => setFormData({ ...formData, station: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="TotalEnergies Bonabéri (Douala)">TotalEnergies Bonabéri</option>
                    <option value="Tradex Port Kribi">Tradex Port Kribi</option>
                    <option value="Tradex Bassa (Douala)">Tradex Bassa Douala</option>
                    <option value="Ola Energy Bafoussam">Ola Energy Bafoussam</option>
                    <option value="Cuve Interne Siège LPC SA">Cuve Interne Entreprise</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Litres Pris (L) *</label>
                  <input
                    type="number"
                    required
                    value={formData.litres}
                    onChange={e => setFormData({ ...formData, litres: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Prix au Litre (XAF)</label>
                  <input
                    type="number"
                    value={formData.prix_litre_xaf}
                    onChange={e => setFormData({ ...formData, prix_litre_xaf: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Index Compteur Précédent (km)</label>
                  <input
                    type="number"
                    value={formData.index_precedent}
                    onChange={e => setFormData({ ...formData, index_precedent: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Index Compteur Actuel (km) *</label>
                  <input
                    type="number"
                    required
                    value={formData.index_km}
                    onChange={e => setFormData({ ...formData, index_km: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
              </div>

              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs flex justify-between items-center">
                <span className="text-slate-400">Montant Total Plein :</span>
                <span className="font-mono text-amber-400 font-bold text-sm">
                  {(formData.litres * formData.prix_litre_xaf).toLocaleString()} XAF
                </span>
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
                  className="px-5 py-2 bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Enregistrer & Contrôler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

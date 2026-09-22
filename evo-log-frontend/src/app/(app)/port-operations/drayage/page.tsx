'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Truck, Plus, Search, ArrowLeft, CheckCircle2,
  Clock, MapPin, Box, ArrowRight
} from 'lucide-react';
import { toast } from 'sonner';

interface TransfertDrayage {
  id: number;
  numero_navette: string;
  numero_conteneur: string;
  provenance_quai: string;
  destination_mad: string;
  tracteur_parc: string;
  chauffeur_navette: string;
  heure_chargement: string;
  statut: string;
}

export default function PortOperationsDrayagePage() {
  const [transferts, setTransferts] = useState<TransfertDrayage[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    numero_conteneur: '',
    provenance_quai: 'Poste 14 (Terre-plein Sous-douane)',
    destination_mad: 'Entrepôt MAD Bonabéri (Douala)',
    tracteur_parc: 'Tracteur Kalmar TT-04',
    chauffeur_navette: 'Kotto Paul (Chauffeur Parc)',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error('Création indisponible : les transferts drayage doivent être enregistrés par une API portuaire persistante.');
    return;
  };

  const filtered = transferts.filter(t =>
    t.numero_conteneur.toLowerCase().includes(search.toLowerCase()) ||
    t.numero_navette.toLowerCase().includes(search.toLowerCase()) ||
    t.destination_mad.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Opérations Portuaires
        </Link>
        <span>/</span>
        <span className="text-white">Drayage & Transferts Terres-Pleins / MAD</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Truck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Drayage & Transferts Portuaires MAD
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-mono">
                KACC_DRY
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Évacuation des conteneurs du quai vers les magasins avancés sous-douane (MAD) et zones logistiques
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-sm shadow-lg shadow-amber-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Lancer un Transfert Navette
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
              placeholder="Rechercher conteneur, navette, destination MAD..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-amber-500 font-mono"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Truck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun transfert de drayage en cours</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Tous les conteneurs déchargés sont actuellement sur terre-plein ou déjà réceptionnés en magasin. Démarrez un transfert navette.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Lancer une première navette drayage
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° Navette</th>
                  <th className="py-3 px-4">N° Conteneur</th>
                  <th className="py-3 px-4">Provenance → Destination MAD</th>
                  <th className="py-3 px-4">Engin & Chauffeur</th>
                  <th className="py-3 px-4">Départ</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-amber-400">
                      {t.numero_navette}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-white font-bold">
                      {t.numero_conteneur}
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="text-slate-400">{t.provenance_quai}</span>
                      <ArrowRight className="w-3 h-3 inline mx-1 text-slate-500" />
                      <span className="text-white font-medium">{t.destination_mad}</span>
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="text-slate-300 block">{t.tracteur_parc}</span>
                      <span className="text-slate-400">{t.chauffeur_navette}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-400">
                      {t.heure_chargement}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        t.statut === 'LIVRE_MAD'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {t.statut}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {t.statut !== 'LIVRE_MAD' && (
                        <button
                          onClick={() => {
                            setTransferts(prev => prev.map(item => item.id === t.id ? { ...item, statut: 'LIVRE_MAD' } : item));
                          }}
                          className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs rounded border border-emerald-500/30 transition"
                        >
                          Confirmer MAD
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

      {/* Modal Lancement Drayage */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Truck className="w-5 h-5 text-amber-400" />
              Lancer un Transfert Drayage
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Ordre de transfert d'un conteneur vers un magasin avancé sous-douane (MAD)
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">N° Conteneur (ISO 6346) *</label>
                <input
                  type="text"
                  required
                  value={formData.numero_conteneur}
                  onChange={e => setFormData({ ...formData, numero_conteneur: e.target.value })}
                  placeholder="Ex: TGHU 850124-7"
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono uppercase"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Provenance Quai</label>
                  <input
                    type="text"
                    value={formData.provenance_quai}
                    onChange={e => setFormData({ ...formData, provenance_quai: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Destination MAD</label>
                  <select
                    value={formData.destination_mad}
                    onChange={e => setFormData({ ...formData, destination_mad: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="Entrepôt MAD Bonabéri (Douala)">Entrepôt MAD Bonabéri (Douala)</option>
                    <option value="Terre-plein Extérieur Bassa (Douala)">Terre-plein Extérieur Bassa</option>
                    <option value="Magasin Sous-Douane Mboro (Kribi)">Magasin Sous-Douane Mboro (Kribi)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Tracteur de Parc</label>
                  <input
                    type="text"
                    value={formData.tracteur_parc}
                    onChange={e => setFormData({ ...formData, tracteur_parc: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Chauffeur Navette</label>
                  <input
                    type="text"
                    value={formData.chauffeur_navette}
                    onChange={e => setFormData({ ...formData, chauffeur_navette: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
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
                  className="px-5 py-2 bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Valider le Bon de Navette
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

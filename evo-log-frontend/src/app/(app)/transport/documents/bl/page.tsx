'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  FileCheck, Plus, Search, ArrowLeft, Download, CheckCircle2,
  Printer, Truck, UserCheck, Calendar
} from 'lucide-react';

interface BonLivraison {
  id: number;
  numero_bl: string;
  mission_ref: string;
  client_destinataire: string;
  adresse_livraison: string;
  chauffeur: string;
  camion: string;
  date_livraison: string;
  heure_signature?: string;
  statut: 'LIVRE_SIGNE' | 'EN_COURS_LIVRAISON';
  nombre_colis: number;
}

export default function TransportBLPage() {
  const [blList, setBlList] = useState<BonLivraison[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    mission_ref: 'TRN-2026-0042',
    client_destinataire: 'Société Camerounaise de Distribution',
    adresse_livraison: 'Zone Industrielle de Bassa, Douala',
    chauffeur: 'Pierre Martin (Chauffeur Lourd)',
    camion: 'LT 912 AB',
    nombre_colis: 45,
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const id = Date.now();
    const newBL: BonLivraison = {
      id,
      numero_bl: `BL-2026-${String(blList.length + 1).padStart(4, '0')}`,
      mission_ref: formData.mission_ref,
      client_destinataire: formData.client_destinataire,
      adresse_livraison: formData.adresse_livraison,
      chauffeur: formData.chauffeur,
      camion: formData.camion,
      date_livraison: new Date().toLocaleDateString('fr-FR'),
      nombre_colis: formData.nombre_colis,
      statut: 'EN_COURS_LIVRAISON'
    };
    setBlList(prev => [newBL, ...prev]);
    setIsModalOpen(false);
  };

  const filtered = blList.filter(b =>
    b.numero_bl.toLowerCase().includes(search.toLowerCase()) ||
    b.client_destinataire.toLowerCase().includes(search.toLowerCase()) ||
    b.mission_ref.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/transport-flotte" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Transport & Flotte
        </Link>
        <span>/</span>
        <Link href="/transport/documents" className="hover:text-blue-400">
          Documents
        </Link>
        <span>/</span>
        <span className="text-white">Bons de Livraison (BL & e-POD)</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Registre des Bons de Livraison & e-POD
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                KTRN_BL
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Émission, suivi de remise et preuves électroniques de livraison (e-POD) signées sur smartphone chauffeur
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Émettre un Bon de Livraison
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
              placeholder="Rechercher par N° BL, client, mission..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <FileCheck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun bon de livraison enregistré</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Votre structure n'a pas encore émis de bon de livraison de transport.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Émettre un premier BL
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° Bon Livraison</th>
                  <th className="py-3 px-4">Mission Réf.</th>
                  <th className="py-3 px-4">Client & Destination</th>
                  <th className="py-3 px-4">Chauffeur & Camion</th>
                  <th className="py-3 px-4">Colis</th>
                  <th className="py-3 px-4">Statut Signature</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(b => (
                  <tr key={b.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-blue-400">
                      {b.numero_bl}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-300">
                      {b.mission_ref}
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="text-white font-medium block">{b.client_destinataire}</span>
                      <span className="text-slate-400">{b.adresse_livraison}</span>
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="text-slate-300 block">{b.chauffeur}</span>
                      <span className="text-slate-400 font-mono">{b.camion}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-white">
                      {b.nombre_colis} colis
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        b.statut === 'LIVRE_SIGNE'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {b.statut}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => alert(`Impression du Bon de Livraison officiel : ${b.numero_bl}`)}
                        className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition"
                        title="Imprimer BL"
                      >
                        <Printer className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Émission BL */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-blue-400" />
              Émettre un Bon de Livraison (BL)
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Création du document de décharge pour remise de marchandise
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Réf. Mission Transport *</label>
                <input
                  type="text"
                  required
                  value={formData.mission_ref}
                  onChange={e => setFormData({ ...formData, mission_ref: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Client Destinataire *</label>
                <input
                  type="text"
                  required
                  value={formData.client_destinataire}
                  onChange={e => setFormData({ ...formData, client_destinataire: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Adresse de Déchargement / Ville</label>
                <input
                  type="text"
                  value={formData.adresse_livraison}
                  onChange={e => setFormData({ ...formData, adresse_livraison: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Chauffeur Assigné</label>
                  <input
                    type="text"
                    value={formData.chauffeur}
                    onChange={e => setFormData({ ...formData, chauffeur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Nombre de Colis</label>
                  <input
                    type="number"
                    value={formData.nombre_colis}
                    onChange={e => setFormData({ ...formData, nombre_colis: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
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
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Générer Bon de Livraison
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

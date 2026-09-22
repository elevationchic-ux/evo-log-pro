'use client';

import React, { useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Scale, Plus, Search, ArrowLeft, Download, CheckCircle2,
  AlertTriangle, RefreshCw, Printer, FileCheck
} from 'lucide-react';

interface PeseeVGM {
  id: number;
  numero_ticket: string;
  numero_conteneur: string;
  type_conteneur: string;
  poids_brut: number;
  tare: number;
  masse_vgm: number;
  tolerance_conforme: boolean;
  camion_immatriculation: string;
  transporteur: string;
  date_pesee: string;
  operateur: string;
  certificat_solas: string;
}

export default function PortOperationsWeighbridgePage() {
  const [pesees, setPesees] = useState<PeseeVGM[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    numero_conteneur: '',
    type_conteneur: "40' High Cube",
    poids_brut: 28500,
    tare: 3800,
    camion_immatriculation: 'LT 842 BC',
    transporteur: 'Afric Heavy Logistics',
  });

  const handleCreatePesee = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error('Création indisponible : la pesée doit être enregistrée par une API portuaire persistante.');
    return;
  };

  const filtered = pesees.filter(p =>
    p.numero_conteneur.toLowerCase().includes(search.toLowerCase()) ||
    p.numero_ticket.toLowerCase().includes(search.toLowerCase()) ||
    p.camion_immatriculation.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Opérations Portuaires
        </Link>
        <span>/</span>
        <span className="text-white">Pont-Bascule & Pesage VGM (SOLAS)</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
            <Scale className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Pont-Bascule & Certification VGM SOLAS
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                KACC_VGM
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Contrôle pondéral réglementaire OMI SOLAS VI/2, calcul tare/net et émission des tickets certifiés VGM
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm shadow-lg shadow-emerald-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Effectuer une Pesée
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Pesées Réalisées</span>
          <p className="text-xl font-bold text-white mt-1">{pesees.length}</p>
        </div>
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Tonnage Certifié</span>
          <p className="text-xl font-bold text-emerald-400 mt-1">
            {(pesees.reduce((acc, p) => acc + p.masse_vgm, 0) / 1000).toFixed(1)} Tonnes
          </p>
        </div>
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Conformité SOLAS</span>
          <p className="text-xl font-bold text-blue-400 mt-1">
            {pesees.length > 0 ? '100%' : '0%'}
          </p>
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
              placeholder="Rechercher par N° conteneur, ticket, camion..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500 font-mono"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Scale className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun ticket de pesée enregistré</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Le pont-bascule n'a pas encore enregistré de passage de camion. Effectuez la première pesée d'un conteneur pour générer son certificat officiel VGM.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Enregistrer une première pesée
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° Ticket</th>
                  <th className="py-3 px-4">N° Conteneur</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Poids Brut / Tare</th>
                  <th className="py-3 px-4">Masse VGM</th>
                  <th className="py-3 px-4">Camion / Transport</th>
                  <th className="py-3 px-4">Certificat SOLAS</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-emerald-400">
                      {p.numero_ticket}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-white font-bold">
                      {p.numero_conteneur}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {p.type_conteneur}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono">
                      <span>{p.poids_brut.toLocaleString()} kg</span>
                      <span className="text-slate-400 block">Tare: {p.tare.toLocaleString()} kg</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-white font-bold">
                      {p.masse_vgm.toLocaleString()} kg
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="text-white block font-medium">{p.camion_immatriculation}</span>
                      <span className="text-slate-400">{p.transporteur}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                        <CheckCircle2 className="w-3 h-3" />
                        {p.certificat_solas}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => alert(`Impression du Certificat VGM Officiel pour le conteneur ${p.numero_conteneur} (Ticket ${p.numero_ticket})`)}
                        className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition"
                        title="Imprimer Certificat VGM"
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

      {/* Modal Pesée */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Scale className="w-5 h-5 text-emerald-400" />
              Nouvelle Pesée Pont-Bascule
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enregistrement officiel de la pesée et certification de la Masse Brute Vérifiée (VGM)
            </p>

            <form onSubmit={handleCreatePesee} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">N° Conteneur (ISO 6346) *</label>
                  <input
                    type="text"
                    required
                    value={formData.numero_conteneur}
                    onChange={e => setFormData({ ...formData, numero_conteneur: e.target.value })}
                    placeholder="Ex: MSKU 942851-2"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono uppercase"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Type Conteneur</label>
                  <select
                    value={formData.type_conteneur}
                    onChange={e => setFormData({ ...formData, type_conteneur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="20' Dry Standard">20' Dry Standard</option>
                    <option value="40' Dry Standard">40' Dry Standard</option>
                    <option value="40' High Cube">40' High Cube</option>
                    <option value="20' Reefer (Frigorifique)">20' Reefer (Frigo)</option>
                    <option value="40' Reefer (Frigorifique)">40' Reefer (Frigo)</option>
                    <option value="Tank (Citerne ISO)">Tank (Citerne ISO)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Poids Brut Mesuré (kg) *</label>
                  <input
                    type="number"
                    required
                    value={formData.poids_brut}
                    onChange={e => setFormData({ ...formData, poids_brut: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Tare du Conteneur (kg) *</label>
                  <input
                    type="number"
                    required
                    value={formData.tare}
                    onChange={e => setFormData({ ...formData, tare: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs">
                <div className="flex justify-between items-center text-slate-400">
                  <span>Masse Nette Calculée (VGM) :</span>
                  <span className="text-emerald-400 font-mono font-bold text-sm">
                    {Math.max(0, formData.poids_brut - formData.tare).toLocaleString()} kg
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Immatriculation Tracteur</label>
                  <input
                    type="text"
                    value={formData.camion_immatriculation}
                    onChange={e => setFormData({ ...formData, camion_immatriculation: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Société de Transport</label>
                  <input
                    type="text"
                    value={formData.transporteur}
                    onChange={e => setFormData({ ...formData, transporteur: e.target.value })}
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
                  Valider & Générer Certificat VGM
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

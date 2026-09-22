'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  FileText, Plus, Search, ArrowLeft, Download, CheckCircle2,
  Printer, Eye, Upload, Filter
} from 'lucide-react';
import { toast } from 'sonner';

interface DocumentTransport {
  id: number;
  reference: string;
  type_document: string;
  mission_numero: string;
  client: string;
  date_emission: string;
  statut: 'SIGNE_EPOD' | 'EMIS' | 'ARCHIVE';
  signataire?: string;
}

export default function TransportDocumentsPage() {
  const [documents, setDocuments] = useState<DocumentTransport[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    type_document: 'Lettre de Voiture Internationale CEMAC',
    mission_numero: 'TRN-2026-0418',
    client: 'Société Camerounaise de Métallurgie',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error("La création de documents de transport n'est pas encore raccordée à l'API.");
    setIsModalOpen(false);
  };

  const filtered = documents.filter(d =>
    d.reference.toLowerCase().includes(search.toLowerCase()) ||
    d.mission_numero.toLowerCase().includes(search.toLowerCase()) ||
    d.client.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/transport-flotte" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Transport & Flotte
        </Link>
        <span>/</span>
        <span className="text-white">GED Transport & Bons de Livraison</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              GED Transport & Documents de Bord
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                KTRN_DOC
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Lettres de voiture CEMAC, bons de livraison signés e-POD, ordres de mission et certificats d'empotage
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Émettre un Document de Transport
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
              placeholder="Rechercher document, mission, client..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucun document de transport enregistré</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              La base documentaire de transport est actuellement vierge. Émettez une lettre de voiture ou un bon de livraison pour votre premier ordre.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Émettre un premier document
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Réf. Document</th>
                  <th className="py-3 px-4">Type de Document</th>
                  <th className="py-3 px-4">N° Mission Transport</th>
                  <th className="py-3 px-4">Client Destinataire</th>
                  <th className="py-3 px-4">Date Émission</th>
                  <th className="py-3 px-4">Statut</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(d => (
                  <tr key={d.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-blue-400">
                      {d.reference}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {d.type_document}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-300">
                      {d.mission_numero}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-200">
                      {d.client}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400 font-mono">
                      {d.date_emission}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        d.statut === 'SIGNE_EPOD'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                      }`}>
                        {d.statut}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => alert(`Téléchargement de l'original électronique certifié : ${d.reference}`)}
                          className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition"
                          title="Télécharger"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => alert(`Impression du document officiel : ${d.reference}`)}
                          className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition"
                          title="Imprimer"
                        >
                          <Printer className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Émission Document */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-400" />
              Émettre un Document de Transport
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Génération du document officiel certifié conforme
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Type de Document *</label>
                <select
                  value={formData.type_document}
                  onChange={e => setFormData({ ...formData, type_document: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="Lettre de Voiture Internationale CEMAC">Lettre de Voiture Internationale CEMAC</option>
                  <option value="Bon de Livraison e-POD (Transport National)">Bon de Livraison e-POD</option>
                  <option value="Certificat d'Empotage / Plombage">Certificat d'Empotage / Plombage</option>
                  <option value="Feuille de Route Chauffeur">Feuille de Route Chauffeur</option>
                  <option value="Décharge Réception Marchandise">Décharge Réception Marchandise</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">N° Mission de Transport *</label>
                <input
                  type="text"
                  required
                  value={formData.mission_numero}
                  onChange={e => setFormData({ ...formData, mission_numero: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Client Donneur d'Ordre / Destinataire *</label>
                <input
                  type="text"
                  required
                  value={formData.client}
                  onChange={e => setFormData({ ...formData, client: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
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
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Générer le Document
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

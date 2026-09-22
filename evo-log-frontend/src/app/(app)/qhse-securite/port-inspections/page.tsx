'use client';

import React, { useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  ShieldCheck, Plus, Search, ArrowLeft, CheckCircle2,
  Calendar, MapPin, ClipboardList, AlertCircle
} from 'lucide-react';

interface InspectionISPS {
  id: number;
  reference: string;
  zone_portuaire: string;
  type_inspection: string;
  auditeur: string;
  date_inspection: string;
  score_conformite_pct: number;
  statut: 'CONFORME' | 'NON_CONFORME_MINEURE' | 'RESERVE_MAJEURE';
  remarques: string;
}

export default function QhsePortInspectionsPage() {
  const [inspections, setInspections] = useState<InspectionISPS[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    zone_portuaire: 'Zone Sous-Douane Quai 14 (Douala)',
    type_inspection: 'Contrôle Sûreté Code ISPS (Clôtures & Badges)',
    auditeur: 'Paul Nguessan (Auditeur Certifié ISPS)',
    score_conformite_pct: 96,
    statut: 'CONFORME' as 'CONFORME' | 'NON_CONFORME_MINEURE' | 'RESERVE_MAJEURE',
    remarques: 'Clôtures périmétriques intactes, contrôle des badges à la guérite 100% effectif',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    toast.error('Création indisponible : les inspections ISPS doivent être enregistrées par une API persistante.');
    return;
  };

  const filtered = inspections.filter(i =>
    i.zone_portuaire.toLowerCase().includes(search.toLowerCase()) ||
    i.reference.toLowerCase().includes(search.toLowerCase()) ||
    i.type_inspection.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Centre Sécurité QHSE
        </Link>
        <span>/</span>
        <span className="text-white">Inspections Portuaires & Code ISPS</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Inspections Portuaires & Conformité Code ISPS
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                KQHS_ISP
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Vérification des zones de restriction portuaire, barriérage, éclairage de quai et dispositifs anti-intrusion
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-lg shadow-blue-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Nouvelle Fiche d'Inspection
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
              placeholder="Rechercher zone portuaire, référence, type d'inspection..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">Aucune inspection portuaire enregistrée</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              Votre structure n'a pas encore consigné de rapport d'inspection Code ISPS pour ses installations.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl shadow transition"
            >
              <Plus className="w-4 h-4" />
              Consigner une première inspection
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Réf. Audit</th>
                  <th className="py-3 px-4">Zone Portuaire Inspectée</th>
                  <th className="py-3 px-4">Type de Contrôle</th>
                  <th className="py-3 px-4">Auditeur</th>
                  <th className="py-3 px-4">Score Conformité</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4 rounded-r-xl">Résultat</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(item => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-blue-400">
                      {item.reference}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {item.zone_portuaire}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {item.type_inspection}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {item.auditeur}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs font-bold text-emerald-400">
                      {item.score_conformite_pct}%
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400 font-mono">
                      {item.date_inspection}
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

      {/* Modal Inspection */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-blue-400" />
              Consigner une Inspection Portuaire
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Audit de conformité Code ISPS et sûreté des accès portuaires
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Zone Portuaire Inspectée *</label>
                <select
                  value={formData.zone_portuaire}
                  onChange={e => setFormData({ ...formData, zone_portuaire: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="Zone Sous-Douane Quai 14 (Douala)">Zone Sous-Douane Quai 14 (Douala)</option>
                  <option value="Terre-plein Conteneurs Amont (Douala)">Terre-plein Conteneurs Amont</option>
                  <option value="Poste Port en Eau Profonde Mboro (Kribi)">Poste Eau Profonde Mboro (Kribi)</option>
                  <option value="Entrepôt MAD Central Bonabéri">Entrepôt MAD Central Bonabéri</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Type d'Inspection</label>
                  <input
                    type="text"
                    value={formData.type_inspection}
                    onChange={e => setFormData({ ...formData, type_inspection: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Auditeur Responsable</label>
                  <input
                    type="text"
                    value={formData.auditeur}
                    onChange={e => setFormData({ ...formData, auditeur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Score Conformité (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.score_conformite_pct}
                    onChange={e => setFormData({ ...formData, score_conformite_pct: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Conclusion Audit</label>
                  <select
                    value={formData.statut}
                    onChange={e => setFormData({ ...formData, statut: e.target.value as any })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="CONFORME">Conforme (Sans réserve)</option>
                    <option value="NON_CONFORME_MINEURE">Non-conformité mineure</option>
                    <option value="RESERVE_MAJEURE">Réserve majeure (Blocage)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Observations & Constats</label>
                <textarea
                  rows={2}
                  value={formData.remarques}
                  onChange={e => setFormData({ ...formData, remarques: e.target.value })}
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
                  Enregistrer l'Inspection
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

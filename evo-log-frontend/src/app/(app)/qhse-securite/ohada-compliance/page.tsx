'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  FileCheck, Plus, Search, ArrowLeft, CheckCircle2,
  Calendar, Scale, AlertCircle, BookOpen
} from 'lucide-react';

interface ConformiteItem {
  id: number;
  article_reference: string;
  theme: string;
  exigence_legale: string;
  niveau_conformite: 'CONFORME' | 'ACTION_REQUISE';
  derniere_revue: string;
  actions_mises_en_oeuvre: string;
}

export default function QhseOhadaCompliancePage() {
  const [items, setItems] = useState<ConformiteItem[]>([
    {
      id: 1,
      article_reference: 'Loi n° 92/007 (Code du Travail CM)',
      theme: 'Comité d\'Hygiène et de Sécurité (CHSCT)',
      exigence_legale: 'Tenue des réunions trimestrielles obligatoires du CHSCT et PV affiché',
      niveau_conformite: 'CONFORME',
      derniere_revue: '2026-08-15',
      actions_mises_en_oeuvre: 'PV de réunion Q2 validé par l\'inspection du travail du Wouri'
    },
    {
      id: 2,
      article_reference: 'Décret n° 93/210/PM',
      theme: 'Médecine du Travail & Visites Périodiques',
      exigence_legale: 'Visite médicale d\'aptitude annuelle obligatoire pour l\'ensemble des salariés et chauffeurs',
      niveau_conformite: 'CONFORME',
      derniere_revue: '2026-07-20',
      actions_mises_en_oeuvre: 'Campagne annuelle effectuée avec le Centre Médical Interentreprises'
    },
    {
      id: 3,
      article_reference: 'Arrêté n° 039/MTPS/IMT',
      theme: 'Dotation des Équipements de Protection (EPI)',
      exigence_legale: 'Fourniture gratuite de chaussures de sécurité S3, gilets haute visibilité et casques',
      niveau_conformite: 'CONFORME',
      derniere_revue: '2026-09-01',
      actions_mises_en_oeuvre: 'Dotations semestrielles certifiées par le Chef du Personnel'
    }
  ]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    article_reference: '',
    theme: 'Contrôle Périodique des Appareils de Levage',
    exigence_legale: 'Contrôle technique semestriel obligatoire des grues, portiques et chariots élévateurs',
    actions_mises_en_oeuvre: 'Contrat d\'audit périodique avec Bureau Veritas Cameroun',
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const newItem: ConformiteItem = {
      id: Date.now(),
      article_reference: formData.article_reference,
      theme: formData.theme,
      exigence_legale: formData.exigence_legale,
      niveau_conformite: 'CONFORME',
      derniere_revue: new Date().toISOString().split('T')[0],
      actions_mises_en_oeuvre: formData.actions_mises_en_oeuvre
    };
    setItems(prev => [newItem, ...prev]);
    setIsModalOpen(false);
  };

  const filtered = items.filter(item =>
    item.article_reference.toLowerCase().includes(search.toLowerCase()) ||
    item.theme.toLowerCase().includes(search.toLowerCase()) ||
    item.exigence_legale.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/qhse-securite/dashboard" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Centre Sécurité QHSE
        </Link>
        <span>/</span>
        <span className="text-white">Conformité Légale & Hygiène du Travail</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Veille Réglementaire & Conformité Hygiène / Sécurité
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30 font-mono">
                KQHS_OHD
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Registre de conformité légale Code du Travail Camerounais, arrêtés MTPS et normes de prévention CEMAC
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-sm shadow-lg shadow-purple-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Ajouter une Exigence Légale
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
              placeholder="Rechercher article, texte de loi, exigence..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="py-3 px-4 rounded-l-xl">Référence Légale</th>
                <th className="py-3 px-4">Thématique</th>
                <th className="py-3 px-4">Exigence Réglementaire</th>
                <th className="py-3 px-4">Dernier Contrôle</th>
                <th className="py-3 px-4">Dispositions Prises</th>
                <th className="py-3 px-4 rounded-r-xl">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filtered.map(item => (
                <tr key={item.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 px-4 font-mono font-medium text-purple-400">
                    {item.article_reference}
                  </td>
                  <td className="py-3.5 px-4 font-semibold text-white">
                    {item.theme}
                  </td>
                  <td className="py-3.5 px-4 text-xs text-slate-300 max-w-xs">
                    {item.exigence_legale}
                  </td>
                  <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                    {item.derniere_revue}
                  </td>
                  <td className="py-3.5 px-4 text-xs text-emerald-400 max-w-xs">
                    {item.actions_mises_en_oeuvre}
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                      <CheckCircle2 className="w-3 h-3" />
                      {item.niveau_conformite}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Ajout Exigence */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-purple-400" />
              Ajouter une Exigence Légale de Sécurité
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enregistrement dans le registre de veille réglementaire de l'entreprise
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Texte de Référence / Article *</label>
                <input
                  type="text"
                  required
                  value={formData.article_reference}
                  onChange={e => setFormData({ ...formData, article_reference: e.target.value })}
                  placeholder="Ex: Arrêté n° 018/MTPS/SG/CJ"
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Thématique Couverte</label>
                <input
                  type="text"
                  value={formData.theme}
                  onChange={e => setFormData({ ...formData, theme: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Obligation Légale *</label>
                <textarea
                  rows={2}
                  required
                  value={formData.exigence_legale}
                  onChange={e => setFormData({ ...formData, exigence_legale: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Mesures Mises en Œuvre</label>
                <textarea
                  rows={2}
                  value={formData.actions_mises_en_oeuvre}
                  onChange={e => setFormData({ ...formData, actions_mises_en_oeuvre: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-purple-500"
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
                  className="px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  Enregistrer dans le Registre
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

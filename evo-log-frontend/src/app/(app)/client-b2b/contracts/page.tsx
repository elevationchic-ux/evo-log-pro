'use client';

import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Plus, 
  Search, 
  Filter, 
  Download, 
  CheckCircle2, 
  Clock, 
  Calendar, 
  DollarSign,
  Building2,
  ChevronRight,
  ShieldCheck
} from 'lucide-react';
import { toast } from 'sonner';
import { customerAPI } from '@/lib/api-client';

interface B2BContract {
  id: string;
  reference: string;
  clientNom: string;
  typeContrat: 'TRANSIT_CADRE' | 'MANUTENTION_DEDIEE' | 'TRANSPORT_CORRIDOR_ANNUEL' | 'MAGASINAGE_FRANCHISE';
  dateDebut: string;
  dateFin: string;
  conditionPaiement: string;
  franchiseSurestarieJours: number;
  statut: 'ACTIF' | 'EN_REVISION' | 'EXPIRE';
  valeurAnnuelleEstimee: number;
}

export default function ClientB2bContractsPage() {
  const [contracts, setContracts] = useState<B2BContract[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  const [form, setForm] = useState({
    reference: '',
    clientNom: '',
    typeContrat: 'TRANSIT_CADRE',
    dateDebut: new Date().toISOString().split('T')[0],
    dateFin: '',
    conditionPaiement: '30 jours fin de mois',
    franchiseSurestarieJours: 14,
    valeurAnnuelleEstimee: ''
  });

  const handleCreateContract = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.reference || !form.clientNom) {
      toast.error('Veuillez renseigner la référence du contrat et le client.');
      return;
    }

    try {
      await customerAPI.createContract({
        reference: form.reference.toUpperCase(),
        client_nom: form.clientNom,
        type_contrat: form.typeContrat,
        date_debut: form.dateDebut,
        date_fin: form.dateFin,
        conditions_paiement: form.conditionPaiement,
        franchise_surestarie_jours: Number(form.franchiseSurestarieJours),
        valeur_annuelle_estimee: Number(form.valeurAnnuelleEstimee) || 0,
      });
      setShowAddModal(false);
      toast.success(`Contrat-cadre ${form.reference.toUpperCase()} enregistré.`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Le contrat n’a pas pu être enregistré.');
    }
  };

  const filteredContracts = contracts.filter(c => 
    c.reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.clientNom.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Contrats Cadres & Conventions Tarifaires B2B</h1>
            <p className="text-sm text-on-surface-variant">
              Accords logistiques négociés, franchises de détention conteneurs et conditions de règlement
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          Nouveau Contrat B2B
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par référence contrat ou nom client..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline text-xs rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Table / Clean Slate State */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        {filteredContracts.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
            <h3 className="font-semibold text-on-surface text-base">Aucun contrat-cadre formalisé</h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
              Formalisez les grilles tarifaires accordées à vos clients stratégiques pour automatiser la facturation des débours, du transit et des surestaries.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95"
            >
              + Créer un Premier Contrat
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-surface-container-low border-b border-outline uppercase font-semibold text-on-surface-variant">
                  <th className="p-3 pl-5">Réf Contrat</th>
                  <th className="p-3">Client Chargeur</th>
                  <th className="p-3">Objet / Type</th>
                  <th className="p-3">Période de Validité</th>
                  <th className="p-3">Règlement</th>
                  <th className="p-3 text-center">Franchise</th>
                  <th className="p-3 text-right">Volume Annuel</th>
                  <th className="p-3 text-right pr-5">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline/40">
                {filteredContracts.map(c => (
                  <tr key={c.id} className="hover:bg-surface-container transition-colors">
                    <td className="p-3 pl-5 font-mono font-bold text-primary">{c.reference}</td>
                    <td className="p-3 font-semibold text-on-surface">{c.clientNom}</td>
                    <td className="p-3 text-on-surface-variant">{c.typeContrat.replace(/_/g, ' ')}</td>
                    <td className="p-3 font-mono text-on-surface">{c.dateDebut} au {c.dateFin}</td>
                    <td className="p-3 text-on-surface">{c.conditionPaiement}</td>
                    <td className="p-3 text-center font-mono font-bold text-emerald-600">{c.franchiseSurestarieJours} j</td>
                    <td className="p-3 text-right font-mono font-bold text-on-surface">
                      {c.valeurAnnuelleEstimee.toLocaleString('fr-FR')} FCFA
                    </td>
                    <td className="p-3 text-right pr-5">
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 font-bold text-[10px]">
                        {c.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <h3 className="font-bold text-on-surface text-base">Enregistrer un Contrat-Cadre B2B</h3>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleCreateContract} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Réf Contrat * :</label>
                  <input
                    type="text"
                    placeholder="Ex: CADC-CTR-2025-01"
                    value={form.reference}
                    onChange={(e) => setForm({ ...form, reference: e.target.value })}
                    required
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono uppercase focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Client * :</label>
                  <input
                    type="text"
                    placeholder="Ex: DANGOTE CEMENT"
                    value={form.clientNom}
                    onChange={(e) => setForm({ ...form, clientNom: e.target.value })}
                    required
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-semibold focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Type de Convention Logistique :</label>
                <select
                  value={form.typeContrat}
                  onChange={(e) => setForm({ ...form, typeContrat: e.target.value })}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="TRANSIT_CADRE">Transit & Dédouanement Global</option>
                  <option value="MANUTENTION_DEDIEE">Acconage & Manutention Dédiée Quai</option>
                  <option value="TRANSPORT_CORRIDOR_ANNUEL">Transport Corridors CEMAC Annuel</option>
                  <option value="MAGASINAGE_FRANCHISE">Stockage MAD avec Franchise Négociée</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Date Début :</label>
                  <input
                    type="date"
                    value={form.dateDebut}
                    onChange={(e) => setForm({ ...form, dateDebut: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Date Fin :</label>
                  <input
                    type="date"
                    value={form.dateFin}
                    onChange={(e) => setForm({ ...form, dateFin: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Franchise Surestarie (Jours) :</label>
                  <input
                    type="number"
                    value={form.franchiseSurestarieJours}
                    onChange={(e) => setForm({ ...form, franchiseSurestarieJours: Number(e.target.value) })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Volume Estimé (FCFA) :</label>
                  <input
                    type="number"
                    placeholder="Ex: 50000000"
                    value={form.valeurAnnuelleEstimee}
                    onChange={(e) => setForm({ ...form, valeurAnnuelleEstimee: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-outline rounded-xl text-on-surface hover:bg-surface-container font-semibold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90"
                >
                  Enregistrer l'Accord
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

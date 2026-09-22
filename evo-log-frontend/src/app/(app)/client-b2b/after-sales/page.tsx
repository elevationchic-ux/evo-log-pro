'use client';

import React, { useState, useEffect } from 'react';
import { 
  HeadphonesIcon, 
  Plus, 
  Search, 
  Filter, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  MessageSquare,
  FileSpreadsheet,
  Download,
  Building2,
  RefreshCw
} from 'lucide-react';
import { supportAPI } from '@/lib/api-client';
import { toast } from 'sonner';

interface B2BClaim {
  id: string;
  reference: string;
  clientNom: string;
  typeLitige: 'AVARIE_MARCHANDISE' | 'RETARD_LIVRAISON' | 'SURESTARIE_CONTESTEE' | 'ERREUR_FACTURATION_DEBOURS';
  priorite: 'BASSE' | 'MOYENNE' | 'HAUTE' | 'URGENTE';
  description: string;
  statut: 'OUVERT' | 'EN_INSTRUCTION' | 'RESOLU' | 'REJETE';
  dateDeclaration: string;
  montantReclame: number;
}

export default function ClientB2bAfterSalesPage() {
  const [claims, setClaims] = useState<B2BClaim[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [showAddModal, setShowAddModal] = useState(false);

  const [form, setForm] = useState({
    reference: '',
    clientNom: '',
    typeLitige: 'AVARIE_MARCHANDISE',
    priorite: 'HAUTE',
    description: '',
    montantReclame: ''
  });

  const loadClaims = async () => {
    setLoading(true);
    try {
      const res = await supportAPI.getIncidents({ limit: 50 });
      const raw = res.data?.items || res.data || [];
      if (Array.isArray(raw) && raw.length > 0) {
        setClaims(raw.map((i: any) => ({
          id: i.id?.toString() || '',
          reference: i.reference || `REC-${i.id || 101}`,
          clientNom: i.client_nom || i.auteur_nom || 'Client Partenaire',
          typeLitige: (i.type || 'AVARIE_MARCHANDISE') as any,
          priorite: (i.priorite || 'HAUTE') as any,
          description: i.description || i.titre || 'Réclamation client',
          statut: (i.statut || 'OUVERT') as any,
          dateDeclaration: i.dateCreation || new Date().toISOString().split('T')[0],
          montantReclame: Number(i.montant) || 0
        })));
      } else {
        setClaims([]);
      }
    } catch (err) {
      console.warn('Claims load handled:', err);
      setClaims([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClaims();
  }, []);

  const handleCreateClaim = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.clientNom || !form.description) {
      toast.error('Veuillez renseigner le client et la description de la réclamation.');
      return;
    }

    const created: B2BClaim = {
      id: Date.now().toString(),
      reference: form.reference || `REC-${Date.now().toString().slice(-4)}`,
      clientNom: form.clientNom,
      typeLitige: form.typeLitige as any,
      priorite: form.priorite as any,
      description: form.description,
      statut: 'OUVERT',
      dateDeclaration: new Date().toISOString().split('T')[0],
      montantReclame: Number(form.montantReclame) || 0
    };

    setClaims([created, ...claims]);
    setShowAddModal(false);
    setForm({
      reference: '',
      clientNom: '',
      typeLitige: 'AVARIE_MARCHANDISE',
      priorite: 'HAUTE',
      description: '',
      montantReclame: ''
    });
    toast.error("L'ouverture des dossiers de litige n'est pas encore raccordée à l'API.");
  };

  const filteredClaims = claims.filter(c => {
    const matchesSearch = 
      c.reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.clientNom.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || c.statut === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <HeadphonesIcon className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Service Après-Vente & Gestion des Litiges Logistiques</h1>
            <p className="text-sm text-on-surface-variant">
              Instruction des réclamations chargeurs, réserves de quai et constats d'avaries avec assureurs
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          Ouvrir un Dossier de Réclamation
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par référence, client ou motif..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline text-xs rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-surface-container-low border border-outline text-xs rounded-xl px-3 py-2 text-on-surface focus:outline-none focus:border-primary"
          >
            <option value="ALL">Tous les statuts de réclamation</option>
            <option value="OUVERT">Nouveaux Litiges Ouverts</option>
            <option value="EN_INSTRUCTION">En Instruction Expert / Assurance</option>
            <option value="RESOLU">Résolus / Indemnisés</option>
            <option value="REJETE">Rejetés</option>
          </select>

          <button
            onClick={loadClaims}
            className="p-2 border border-outline rounded-xl hover:bg-surface-container text-on-surface-variant hover:text-on-surface"
            title="Actualiser"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Table / Clean Slate State */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        {filteredClaims.length === 0 ? (
          <div className="p-12 text-center">
            <HeadphonesIcon className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
            <h3 className="font-semibold text-on-surface text-base">Aucune réclamation ou litige en cours</h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
              Le service après-vente est opérationnel. Toutes les contestations de facturation, réserves à l'enlèvement ou retards déclarés apparaîtront ici pour instruction juridique et financière.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95"
            >
              + Déclarer un Dossier de Litige
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-surface-container-low border-b border-outline uppercase font-semibold text-on-surface-variant">
                  <th className="p-3 pl-5">Réf Litige</th>
                  <th className="p-3">Client Chargeur</th>
                  <th className="p-3">Type de Réclamation</th>
                  <th className="p-3">Date</th>
                  <th className="p-3">Priorité</th>
                  <th className="p-3 text-right">Montant Réclamé</th>
                  <th className="p-3 text-right pr-5">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline/40">
                {filteredClaims.map(c => (
                  <tr key={c.id} className="hover:bg-surface-container transition-colors">
                    <td className="p-3 pl-5 font-mono font-bold text-primary">{c.reference}</td>
                    <td className="p-3 font-semibold text-on-surface">{c.clientNom}</td>
                    <td className="p-3 text-on-surface">{c.typeLitige.replace(/_/g, ' ')}</td>
                    <td className="p-3 text-on-surface-variant font-mono">{c.dateDeclaration}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        c.priorite === 'URGENTE' ? 'bg-red-500/10 text-red-600' :
                        c.priorite === 'HAUTE' ? 'bg-amber-500/10 text-amber-600' :
                        'bg-blue-500/10 text-blue-600'
                      }`}>
                        {c.priorite}
                      </span>
                    </td>
                    <td className="p-3 text-right font-mono font-bold text-on-surface">
                      {c.montantReclame > 0 ? `${c.montantReclame.toLocaleString('fr-FR')} FCFA` : 'N/D'}
                    </td>
                    <td className="p-3 text-right pr-5">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        c.statut === 'RESOLU' ? 'bg-emerald-500/10 text-emerald-600' :
                        c.statut === 'EN_INSTRUCTION' ? 'bg-amber-500/10 text-amber-600' :
                        'bg-blue-500/10 text-blue-600'
                      }`}>
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
              <h3 className="font-bold text-on-surface text-base">Déclarer un Dossier de Litige / SAV</h3>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleCreateClaim} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Réf Réclamation :</label>
                  <input
                    type="text"
                    placeholder="Ex: LIT-2025-089"
                    value={form.reference}
                    onChange={(e) => setForm({ ...form, reference: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono uppercase focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Client Chargeur * :</label>
                  <input
                    type="text"
                    placeholder="Ex: HEVECAM SA"
                    value={form.clientNom}
                    onChange={(e) => setForm({ ...form, clientNom: e.target.value })}
                    required
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-semibold focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Type de Réclamation :</label>
                  <select
                    value={form.typeLitige}
                    onChange={(e) => setForm({ ...form, typeLitige: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  >
                    <option value="AVARIE_MARCHANDISE">Avarie Constatée sur Marchandises</option>
                    <option value="RETARD_LIVRAISON">Retard Excessif de Livraison Corridor</option>
                    <option value="SURESTARIE_CONTESTEE">Surestaries / Stationnement Contesté</option>
                    <option value="ERREUR_FACTURATION_DEBOURS">Erreur Facturation Débours Douane</option>
                  </select>
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Priorité :</label>
                  <select
                    value={form.priorite}
                    onChange={(e) => setForm({ ...form, priorite: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  >
                    <option value="BASSE">Basse</option>
                    <option value="MOYENNE">Moyenne</option>
                    <option value="HAUTE">Haute</option>
                    <option value="URGENTE">Urgente</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Montant Réclamé / Préjudice (FCFA) :</label>
                <input
                  type="number"
                  placeholder="Ex: 4500000"
                  value={form.montantReclame}
                  onChange={(e) => setForm({ ...form, montantReclame: e.target.value })}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Exposé des Faits & Références BL/DUM * :</label>
                <textarea
                  rows={3}
                  placeholder="Circonstances, numéros de conteneur, nom du navire..."
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
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
                  Transmettre au Contentieux
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

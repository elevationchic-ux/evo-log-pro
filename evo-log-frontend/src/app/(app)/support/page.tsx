'use client';

import React, { useState, useEffect } from 'react';
import {
  LifeBuoy,
  Plus,
  Search,
  MessageSquare,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Send,
  RefreshCw,
  HelpCircle,
  PhoneCall,
  Mail
} from 'lucide-react';
import { supportAPI, incidentsAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function SupportPage() {
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [newTicket, setNewTicket] = useState({
    sujet: '',
    categorie: 'TECHNIQUE',
    priorite: 'NORMALE',
    description: '',
  });

  const loadTickets = async () => {
    setLoading(true);
    try {
      const res = await supportAPI.getTickets().catch(() => {
        return incidentsAPI.getIncidents();
      });
      const raw = res.data?.items || res.data || [];
      setTickets(Array.isArray(raw) ? raw : []);
    } catch (err) {
      console.error(err);
      setTickets([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await supportAPI.createTicket(newTicket).catch(() => {
        return incidentsAPI.createIncident({
          titre: newTicket.sujet,
          type: newTicket.categorie,
          priorite: newTicket.priorite,
          description: newTicket.description
        });
      });
      toast.success('Ticket d\'assistance créé et assigné à notre équipe support !');
      setIsModalOpen(false);
      setNewTicket({ sujet: '', categorie: 'TECHNIQUE', priorite: 'NORMALE', description: '' });
      loadTickets();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur lors de la création du ticket.');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredTickets = tickets.filter(t => {
    const matchStatus = statusFilter === 'ALL' || t.statut === statusFilter;
    const q = searchQuery.toLowerCase();
    const matchQuery = !q || (
      (t.sujet && t.sujet.toLowerCase().includes(q)) ||
      (t.titre && t.titre.toLowerCase().includes(q)) ||
      (t.description && t.description.toLowerCase().includes(q))
    );
    return matchStatus && matchQuery;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <LifeBuoy className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Support Technique & Assistance Client</h1>
            <p className="text-sm text-on-surface-variant">
              Guichet d'assistance applicative, déclaration d'incidents informatiques et suivi des tickets
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadTickets}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
          >
            <Plus className="w-4 h-4" /> Ouvrir un Ticket
          </button>
        </div>
      </div>

      {/* Contact Channels */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center gap-3">
          <div className="p-3 bg-primary/10 rounded-xl text-primary">
            <PhoneCall className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Hotline Support 24/7</p>
            <p className="text-sm font-bold text-on-surface mt-0.5">+237 233 42 88 90</p>
          </div>
        </div>
        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center gap-3">
          <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-600">
            <Mail className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Email Support Dédié</p>
            <p className="text-sm font-bold text-on-surface mt-0.5">support@evo-logistics.cm</p>
          </div>
        </div>
        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center gap-3">
          <div className="p-3 bg-blue-500/10 rounded-xl text-blue-600">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Délai Réponse SLA Moyen</p>
            <p className="text-sm font-bold text-on-surface mt-0.5">&lt; 30 minutes</p>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par sujet, description, n° ticket..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="sm:w-64 px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
        >
          <option value="ALL">Tous les statuts</option>
          <option value="OUVERT">Tickets Ouverts</option>
          <option value="EN_COURS">En cours de traitement</option>
          <option value="RESOLU">Résolus / Clôturés</option>
        </select>
      </div>

      {/* Tickets Table */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-on-surface">
            <thead className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline">
              <tr>
                <th className="px-5 py-3">Sujet du Ticket</th>
                <th className="px-5 py-3">Catégorie</th>
                <th className="px-5 py-3">Priorité</th>
                <th className="px-5 py-3">Date Création</th>
                <th className="px-5 py-3 text-right">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline/30">
              {loading ? (
                <tr>
                  <td colSpan={5} className="p-12 text-center text-on-surface-variant">
                    Chargement des tickets d'assistance...
                  </td>
                </tr>
              ) : filteredTickets.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-12 text-center">
                    <CheckCircle2 className="w-12 h-12 text-emerald-500/40 mx-auto mb-3" />
                    <h3 className="font-semibold text-on-surface text-base">Aucun incident ou ticket actif</h3>
                    <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
                      Tous les systèmes fonctionnent nominalement. Cliquez sur "Ouvrir un Ticket" si vous rencontrez une anomalie.
                    </p>
                  </td>
                </tr>
              ) : (
                filteredTickets.map((t, idx) => (
                  <tr key={t.id || idx} className="hover:bg-surface-container/50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="font-bold text-on-surface">{t.sujet || t.titre || `Ticket #${t.id}`}</div>
                      <div className="text-xs text-on-surface-variant line-clamp-1">{t.description || 'RAS'}</div>
                    </td>
                    <td className="px-5 py-3.5 text-xs">
                      <span className="px-2 py-0.5 rounded-lg bg-surface-container border border-outline/40">
                        {t.categorie || t.type || 'Technique'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-xs font-semibold">
                      <span className={`px-2 py-0.5 rounded-full text-[11px] ${
                        t.priorite === 'URGENTE' || t.priorite === 'CRITIQUE'
                          ? 'bg-rose-500/10 text-rose-600'
                          : 'bg-surface-container text-on-surface-variant'
                      }`}>
                        {t.priorite || 'Normale'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-xs text-on-surface-variant">
                      {t.created_at?.slice(0, 10) || 'Date courante'}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600">
                        {t.statut || 'EN COURS'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Creation */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-lg p-6 space-y-4 text-on-surface shadow-2xl">
            <div className="flex justify-between items-center pb-2 border-b border-outline">
              <h2 className="text-lg font-bold flex items-center gap-2">
                <LifeBuoy className="w-5 h-5 text-primary" /> Nouveau Ticket d'Assistance
              </h2>
              <button onClick={() => setIsModalOpen(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleCreateTicket} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold mb-1">Sujet du Ticket *</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: Erreur lors de l'édition du B/L sur le dossier TR-2026-0042"
                  value={newTicket.sujet}
                  onChange={e => setNewTicket({ ...newTicket, sujet: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold mb-1">Module Concerné</label>
                  <select
                    value={newTicket.categorie}
                    onChange={e => setNewTicket({ ...newTicket, categorie: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                  >
                    <option value="TRANSIT">Transit & Douane</option>
                    <option value="TRANSPORT">Transport & Flotte</option>
                    <option value="FACTURATION">Facturation & Finance</option>
                    <option value="MAGASIN">Magasin & Stocks</option>
                    <option value="ACCONAGE">Acconage Portuaire</option>
                    <option value="TECHNIQUE">Plateforme Générale / Accès</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold mb-1">Niveau d'Urgence</label>
                  <select
                    value={newTicket.priorite}
                    onChange={e => setNewTicket({ ...newTicket, priorite: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                  >
                    <option value="NORMALE">Normale (Sous 24h)</option>
                    <option value="URGENTE">Urgente (Sous 2h)</option>
                    <option value="CRITIQUE">Critique (Bloque l'exploitation)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold mb-1">Description Détaillée du Problème *</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Expliquez l'opération tentée, le message d'erreur et les dossiers concernés..."
                  value={newTicket.description}
                  onChange={e => setNewTicket({ ...newTicket, description: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-outline">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold border border-outline rounded-xl"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-xs font-semibold bg-primary text-on-primary rounded-xl"
                >
                  {submitting ? 'Envoi...' : 'Transmettre au Support'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

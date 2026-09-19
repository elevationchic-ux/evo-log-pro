'use client';

import React, { useEffect, useState } from 'react';
import {
  FileText,
  Calendar,
  CreditCard,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Search,
  Menu,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  PieChart
} from 'lucide-react';
import { financeAPI } from '@/lib/api-client';

export default function ClientInvoicesPage() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);
  const [filters, setFilters] = useState({
    statut: '',
    dateDebut: '',
    dateFin: '',
    search: '',
    minAmount: '',
    maxAmount: ''
  });
  const [sortBy, setSortBy] = useState<{ field: string; direction: 'asc' | 'desc' }>({
    field: 'dateCreation',
    direction: 'desc'
  });
  const [expandedInvoiceId, setExpandedInvoiceId] = useState<string | null>(null);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await financeAPI.getFactures({
        limit: 100,
        ...filters
      });
      setInvoices(res.data || res || []);
    } catch (err) {
      console.error('Failed to load invoices:', err);
      setError('Impossible de charger les factures. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const filteredInvoices = invoices.filter(invoice => {
    if (filters.statut && invoice.status !== filters.statut) return false;
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      return (
        invoice.id?.toString().toLowerCase().includes(searchTerm) ||
        (invoice.client_nom || '').toLowerCase().includes(searchTerm) ||
        (invoice.reference || '').toLowerCase().includes(searchTerm)
      );
    }
    if (filters.minAmount && invoice.amount < parseFloat(filters.minAmount)) return false;
    if (filters.maxAmount && invoice.amount > parseFloat(filters.maxAmount)) return false;
    if (filters.dateDebut) {
      const invoiceDate = new Date(invoice.dateCreation || invoice.date);
      const filterDate = new Date(filters.dateDebut);
      if (invoiceDate < filterDate) return false;
    }
    if (filters.dateFin) {
      const invoiceDate = new Date(invoice.dateCreation || invoice.date);
      const filterDate = new Date(filters.dateFin);
      if (invoiceDate > filterDate) return false;
    }
    return true;
  });

  const sortedInvoices = [...filteredInvoices].sort((a, b) => {
    const fieldA = a[sortBy.field];
    const fieldB = b[sortBy.field];

    if (fieldA === undefined || fieldA === null) return 1;
    if (fieldB === undefined || fieldB === null) return -1;

    if (sortBy.direction === 'asc') {
      return fieldA > fieldB ? 1 : -1;
    } else {
      return fieldA < fieldB ? 1 : -1;
    }
  });

  return (
    <div className="min-h-[80vh] py-12">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start sm:items-center sm:justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              Mes Factures
            </h1>
            <p className="text-slate-600">
              Gérez et suivez l'état de toutes vos factures
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSelectedInvoice(null)}
              className="btn btn-primary btn-sm flex items-center gap-2"
            >
              <FileText className="w-4 h-4" /> Nouvelle Facture
            </button>
            <button
              onClick={loadInvoices}
              className="btn btn-outline btn-sm flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" /> Actualiser
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
          <AlertTriangle className="w-4 h-4 text-red-600 mr-2" />
          <span>{error}</span>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Search className="w-5 h-5" /> Filtres
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Statut
              </label>
              <select
                value={filters.statut}
                onChange={(e) => setFilters(prev => ({ ...prev, statut: e.target.value }))}
                className="select select-bordered w-full"
              >
                <option value="">Tous les statuts</option>
                <option value="draft">Brouillon</option>
                <option value="sent">Envoyée</option>
                <option value="paid">Payée</option>
                <option value="overdue">En Retard</option>
                <option value="cancelled">Annulée</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Date de Début
              </label>
              <input
                type="date"
                value={filters.dateDebut}
                onChange={(e) => setFilters(prev => ({ ...prev, dateDebut: e.target.value }))}
                className="input input-bordered w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Date de Fin
              </label>
              <input
                type="date"
                value={filters.dateFin}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFin: e.target.value }))}
                className="input input-bordered w-full"
              />
            </div>
            <div className="flex items-end">
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Recherche
              </label>
              <input
                type="text"
                placeholder="Numéro, client, référence..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="input input-bordered w-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <FileText className="w-8 h-8 text-primary" />
            </div>
            <p className="text-sm font-medium text-slate-500">Total Factures</p>
            <p className="text-2xl font-bold text-slate-900">{invoices.length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <CheckCircle2 className="w-8 h-8 text-success" />
            </div>
            <p className="text-sm font-medium text-slate-500">Payées</p>
            <p className="text-2xl font-bold text-slate-900">
              {invoices.filter(i => i.status === 'paid').length}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <TrendingUp className="w-8 h-8 text-success" />
            </div>
            <p className="text-sm font-medium text-slate-500">Montant Total</p>
            <p className="text-2xl font-bold text-slate-900">
              FCFA {invoices.reduce((sum, inv) => sum + (inv.amount || 0), 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <PieChart className="w-8 h-8 text-info" />
            </div>
            <p className="text-sm font-medium text-slate-500">En Attente</p>
            <p className="text-2xl font-bold text-slate-900">
              {invoices.filter(i => ['sent', 'draft'].includes(i.status)).length}
            </p>
          </div>
        </div>
      </div>

      {/* anys List */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <h3 className="text-lg font-bold text-slate-800">
            Liste des Factures ({filteredInvoices.length} résultat{(filteredInvoices.length !== 1) ? 's' : ''})
          </h3>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <span>Trier par :</span>
            <select
              value={sortBy.field}
              onChange={(e) => setSortBy(prev => ({ ...prev, field: e.target.value }))}
              className="select select-sm select-bordered"
            >
              <option value="dateCreation">Date (récent)</option>
              <option value="dateCreation:asc">Date (ancien)</option>
              <option value="id">Numéro</option>
              <option value="amount">Montant</option>
              <option value="status">Statut</option>
            </select>
          </div>
        </div>

        {loading && !invoices.length && (
          <div className="p-12 text-center">
            <RefreshCw className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
            <p className="text-slate-600">Chargement des factures...</p>
          </div>
        )}

        {!loading && invoices.length === 0 && !error && (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-500">Aucune facture trouvée</p>
            <p className="text-slate-400 text-sm mt-2">
              Aucune facture ne correspond aux filtres appliqués
            </p>
          </div>
        )}

        {!loading && invoices.length > 0 && (
          <div className="divide-y divide-slate-100">
            {sortedInvoices.map((invoice) => (
              <div key={invoice.id} className="cursor-pointer hover:bg-slate-50 transition-colors">
                {/* any Header */}
                <div className="flex justify-between items-start px-6 py-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full">
                        {invoice.status === 'paid' && (
                          <CheckCircle2 className="w-4 h-4 text-success" />
                        )}
                        {invoice.status === 'overdue' && (
                          <div className="w-3 h-3 border-2 border-destructive" />
                        )}
                        {invoice.status === 'sent' && (
                          <div className="w-3 h-3 border-2 border-warning" />
                        )}
                        {invoice.status === 'draft' && (
                          <div className="w-3 h-3 border-2 border-slate-400" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">Facture #{invoice.id}</p>
                        <p className="text-sm text-slate-500 truncate">
                          {invoice.reference || 'Facture standard'}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <p className={
                      invoice.status === 'paid' ? 'text-success font-medium' :
                      invoice.status === 'overdue' ? 'text-destructive font-medium' :
                      invoice.status === 'sent' ? 'text-warning font-medium' :
                      'text-slate-500'
                    }>
                      {invoice.status === 'paid' && 'Payée'}
                      {invoice.status === 'overdue' && 'En Retard'}
                      {invoice.status === 'sent' && 'Envoyée'}
                      {invoice.status === 'draft' && 'Brouillon'}
                    </p>
                    <p className="text-slate-500 text-right">
                      FCFA {(invoice.amount || 0).toLocaleString()}
                    </p>
                    <button
                      onClick={() => setExpandedInvoiceId(invoice.id.toString())}
                      className="btn btn-ghost btn-sm p-1"
                      aria-label="Développer/Réduire les détails"
                    >
                      {expandedInvoiceId === invoice.id.toString() ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* any Details (expandable) */}
                {expandedInvoiceId === invoice.id.toString() && (
                  <div className="px-6 py-4 bg-slate-50 border-t border-slate-100">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Date de Facturation</p>
                        <p className="text-slate-500">
                          {invoice.dateCreation ? new Date(invoice.dateCreation).toLocaleDateString('fr-FR') : 'Non définie'}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Date d'Échéance</p>
                        <p className="text-slate-500">
                          {invoice.dueDate ? new Date(invoice.dueDate).toLocaleDateString('fr-FR') : 'Non définie'}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Client</p>
                        <p className="text-slate-500">{invoice.client_nom || 'Non spécifié'}</p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Référence</p>
                        <p className="text-slate-500 font-mono">{invoice.reference || 'N/A'}</p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Mode de Paiement</p>
                        <p className="text-slate-500">{invoice.mode_paiement || 'Non spécifié'}</p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Bon de Commande Associé</p>
                        <p className="text-slate-500">
                          {invoice.bon_commande_ref || 'Aucun'}
                        </p>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-4 pt-3 border-t border-slate-200 flex flex-col sm:flex-row gap-3">
                      {invoice.status !== 'paid' && (
                        <button
                          onClick={() => {
                            // In a real app, this would open a payment modal
                            alert(`Traitement du paiement pour la facture #${invoice.id}`);
                          }}
                          className="btn btn-sm btn-outline btn-success flex-1"
                        >
                          Effectuer Paiement
                        </button>
                      )}
                      {invoice.status === 'paid' || invoice.status === 'sent' ? (
                        <button
                          onClick={() => {
                            // In a real app, this would open a print/download modal
                            alert(`Téléchargement de la facture #${invoice.id}`);
                          }}
                          className="btn btn-sm btn-outline btn-info flex-1"
                        >
                          Télécharger PDF
                        </button>
                      ) : null}
                      {invoice.status === 'draft' ? (
                        <>
                          <button
                            onClick={() => {
                              // In a real app, this would send the invoice
                              alert(`Envoi de la facture #${invoice.id} au client`);
                            }}
                            className="btn btn-sm btn-outline btn-warning flex-1"
                          >
                            Envoyer au Client
                          </button>
                          <button
                            onClick={() => {
                              // In a real app, this would delete the draft
                              alert(`Suppression de la facture brouillon #${invoice.id}`);
                            }}
                            className="btn btn-sm btn-outline btn-destructive flex-1"
                          >
                            Supprimer
                          </button>
                        </>
                      ) : null}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected any Detail View */}
      {selectedInvoice && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl mx-4 p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">
                  Facture #{selectedInvoice.id}
                </h2>
                <p className="text-slate-600">
                  Détails complets de la facture
                </p>
              </div>
              <button
                onClick={() => setSelectedInvoice(null)}
                className="btn btn-ghost btn-sm"
                aria-label="Fermer"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 011.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              {/* any Info */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Informations Générales</h3>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Numéro de Facture</p>
                    <p className="font-mono text-slate-900">#{selectedInvoice.id}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Référence</p>
                    <p className="text-slate-500">{selectedInvoice.reference || 'N/A'}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Date de Facturation</p>
                    <p className="text-slate-500">
                      {selectedInvoice.dateCreation ? new Date(selectedInvoice.dateCreation).toLocaleDateString('fr-FR') : 'Non définie'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Date d'Échéance</p>
                    <p className="text-slate-500">
                      {selectedInvoice.dueDate ? new Date(selectedInvoice.dueDate).toLocaleDateString('fr-FR') : 'Non définie'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Statut</p>
                    <span className={
                      selectedInvoice.status === 'paid' ? 'badge badge-success' :
                      selectedInvoice.status === 'overdue' ? 'badge badge-destructive' :
                      selectedInvoice.status === 'sent' ? 'badge badge-warning' :
                      'badge badge-secondary'
                    }>
                      {selectedInvoice.status === 'paid' && 'Payée'}
                      {selectedInvoice.status === 'overdue' && 'En Retard'}
                      {selectedInvoice.status === 'sent' && 'Envoyée'}
                      {selectedInvoice.status === 'draft' && 'Brouillon'}
                    </span>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Montants</h3>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Montant HT</p>
                    <p className="text-slate-500 font-mono">
                      FCFA {(selectedInvoice.amount_ht || selectedInvoice.amount || 0).toLocaleString()}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">TVA (19.25%)</p>
                    <p className="text-slate-500 font-mono">
                      FCFA {((selectedInvoice.amount_ht || selectedInvoice.amount || 0) * 0.1925).toLocaleString()}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Montant TTC</p>
                    <p className="text-2xl font-bold text-slate-900">
                      FCFA {((selectedInvoice.amount_ttc || (selectedInvoice.amount || 0) * 1.1925) || 0).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Informations Client</h3>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Nom du Client</p>
                    <p className="text-slate-500">{selectedInvoice.client_nom || 'Non spécifié'}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Adresse de Facturation</p>
                    <p className="text-slate-500 break-all">
                      {selectedInvoice.client_adresse || 'Non spécifiée'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Contact</p>
                    <p className="text-slate-500">
                      {selectedInvoice.client_contact || 'Non spécifié'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Line Items */}
              <div className="lg:col-span-3">
                <h3 className="text-lg font-semibold text-slate-800">Détails des Lignes</h3>
                {selectedInvoice.lignes && selectedInvoice.lignes.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead className="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase">
                        <tr>
                          <th className="px-6 py-3">Description</th>
                          <th className="px-6 py-3 text-center">Quantité</th>
                          <th className="px-6 py-3 text-center">Prix Unitaire</th>
                          <th className="px-6 py-3 text-right">Montant</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {selectedInvoice.lignes.map((ligne: any, index: number) => (
                          <tr key={index} className="hover:bg-slate-50 transition-colors">
                            <td className="px-6 py-3">
                              <p className="font-medium text-slate-800">{ligne.description}</p>
                              {ligne.details && (
                                <p className="text-sm text-slate-500">{ligne.details}</p>
                              )}
                            </td>
                            <td className="px-6 py-3 text-center">
                              <p className="text-slate-500">{ligne.quantite}</p>
                            </td>
                            <td className="px-6 py-3 text-center">
                              <p className="text-slate-500 font-mono">
                                FCFA {ligne.prix_unitaire?.toLocaleString() || '0'}
                              </p>
                            </td>
                            <td className="px-6 py-3 text-right">
                              <p className="text-slate-500 font-mono">
                                FCFA {(ligne.quantite * ligne.prix_unitaire || 0).toLocaleString()}
                              </p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-8 text-center text-slate-500">
                    Aucun détail de ligne disponible pour cette facture
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
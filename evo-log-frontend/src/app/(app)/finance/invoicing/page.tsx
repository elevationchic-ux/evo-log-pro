'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  FileText,
  Plus,
  Search,
  Download,
  Filter,
  RefreshCw,
  CheckCircle2,
  Clock,
  AlertCircle,
  Eye,
  Printer,
  X
} from 'lucide-react';
import { financeAPI } from '@/lib/api-client';
import { toast } from 'sonner';
import { CompanyDocumentHeader, CompanyDocumentFooter } from '@/components/documents/CompanyDocumentHeader';

export default function InvoicingPage() {
  const router = useRouter();
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedInvoice, setSelectedInvoice] = useState<any | null>(null);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const res = await financeAPI.getFactures();
      const raw = res.data?.items || res.data || [];
      setInvoices(Array.isArray(raw) ? raw : []);
    } catch (err) {
      console.error('Failed to load invoices', err);
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const filteredInvoices = invoices.filter((inv) => {
    const matchStatus = statusFilter === 'ALL' || inv.statut === statusFilter;
    const q = searchQuery.toLowerCase();
    const matchSearch = !q || (
      (inv.numero_facture && inv.numero_facture.toLowerCase().includes(q)) ||
      (inv.client_nom && inv.client_nom.toLowerCase().includes(q)) ||
      (inv.reference && inv.reference.toLowerCase().includes(q))
    );
    return matchStatus && matchSearch;
  });

  const totalFacture = invoices.reduce((sum, inv) => sum + Number(inv.montant_ttc || inv.montant || 0), 0);
  const totalPaye = invoices.filter(i => i.statut === 'PAYEE').reduce((sum, inv) => sum + Number(inv.montant_ttc || inv.montant || 0), 0);
  const totalEnAttente = totalFacture - totalPaye;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Facturation & Décomptes Clients</h1>
            <p className="text-sm text-on-surface-variant">
              Émission de factures OHADA avec entête officiel d'entreprise, suivi des encaissements et relances
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchInvoices()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => toast.error("L'export du journal des ventes n'est pas encore raccordé à l'API.")}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container text-on-surface"
          >
            <Download className="w-4 h-4" /> Exporter
          </button>
          <Link
            href="/finance/invoicing/create"
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" /> Nouvelle Facture
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-surface rounded-2xl border border-outline/70">
          <p className="text-xs font-medium text-on-surface-variant uppercase tracking-wider">Total Facturé</p>
          <p className="text-2xl font-bold text-on-surface mt-1">{totalFacture.toLocaleString('fr-FR')} FCFA</p>
          <p className="text-xs text-on-surface-variant mt-1">{invoices.length} factures générées</p>
        </div>
        <div className="p-4 bg-surface rounded-2xl border border-outline/70">
          <p className="text-xs font-medium text-emerald-600 uppercase tracking-wider">Total Encaissé</p>
          <p className="text-2xl font-bold text-emerald-600 mt-1">{totalPaye.toLocaleString('fr-FR')} FCFA</p>
          <p className="text-xs text-on-surface-variant mt-1">Recouvrement actif</p>
        </div>
        <div className="p-4 bg-surface rounded-2xl border border-outline/70">
          <p className="text-xs font-medium text-amber-600 uppercase tracking-wider">Créances En Attente</p>
          <p className="text-2xl font-bold text-amber-600 mt-1">{totalEnAttente.toLocaleString('fr-FR')} FCFA</p>
          <p className="text-xs text-on-surface-variant mt-1">À recouvrer sous 30j</p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par n° de facture, client ou référence..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-surface border border-outline rounded-xl text-sm text-on-surface placeholder:text-on-surface-variant/50 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>
        <div className="flex gap-2">
          {['ALL', 'PAYEE', 'EN_ATTENTE', 'BROUILLON'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-2 rounded-xl text-xs font-semibold transition-colors ${
                statusFilter === st
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface border border-outline text-on-surface-variant hover:bg-surface-container'
              }`}
            >
              {st === 'ALL' ? 'Toutes' : st.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface rounded-2xl border border-outline overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-outline bg-surface-container/30 text-xs font-semibold text-on-surface-variant">
                <th className="px-5 py-3.5">N° Facture</th>
                <th className="px-5 py-3.5">Client / Tiers</th>
                <th className="px-5 py-3.5">Date Émission</th>
                <th className="px-5 py-3.5 text-right">Montant HT</th>
                <th className="px-5 py-3.5 text-right">Total TTC</th>
                <th className="px-5 py-3.5 text-center">Statut</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-on-surface-variant">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-primary" />
                    Chargement des factures...
                  </td>
                </tr>
              ) : filteredInvoices.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center">
                    <FileText className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
                    <h3 className="font-semibold text-on-surface text-base">Aucune facture émise</h3>
                    <p className="text-xs text-on-surface-variant mt-1">Cliquez sur "Nouvelle Facture" pour commencer.</p>
                  </td>
                </tr>
              ) : (
                filteredInvoices.map((inv, idx) => (
                  <tr key={inv.id || idx} className="hover:bg-surface-container/50 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-on-surface">
                      {inv.numero_facture || `FAC-2026-${String(inv.id).padStart(4, '0')}`}
                    </td>
                    <td className="px-5 py-3.5 font-medium">{inv.client_nom || inv.tiers_nom || 'Client Général'}</td>
                    <td className="px-5 py-3.5 text-on-surface-variant">{inv.date_emission || inv.created_at?.slice(0, 10)}</td>
                    <td className="px-5 py-3.5 text-right">{Number(inv.montant_ht || inv.montant || 0).toLocaleString('fr-FR')} FCFA</td>
                    <td className="px-5 py-3.5 text-right font-bold text-primary">{Number(inv.montant_ttc || inv.montant || 0).toLocaleString('fr-FR')} FCFA</td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        inv.statut === 'PAYEE' ? 'bg-emerald-500/10 text-emerald-600' : 'bg-amber-500/10 text-amber-600'
                      }`}>
                        {inv.statut || 'VALIDÉE'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right font-sans">
                      <div className="flex justify-end gap-1.5">
                        <button
                          onClick={() => setSelectedInvoice(inv)}
                          className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg border border-outline hover:bg-surface-container text-primary"
                          title="Aperçu et Impression"
                        >
                          <Eye className="w-3.5 h-3.5" /> Aperçu
                        </button>
                        <button
                          onClick={() => {
                            setSelectedInvoice(inv);
                            setTimeout(() => window.print(), 300);
                          }}
                          className="p-1.5 rounded-lg border border-outline hover:bg-surface-container text-on-surface-variant"
                          title="Imprimer Directement"
                        >
                          <Printer className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Printable Invoice Modal with Company Document Header */}
      {selectedInvoice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
          <div className="bg-surface rounded-2xl border border-outline max-w-3xl w-full p-6 sm:p-8 space-y-6 my-8 shadow-2xl relative">
            <div className="flex items-center justify-between no-print border-b border-outline pb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-primary">Aperçu Facture OHADA</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => window.print()}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-primary text-on-primary"
                >
                  <Printer className="w-4 h-4" /> Imprimer / PDF
                </button>
                <button
                  onClick={() => setSelectedInvoice(null)}
                  className="p-1.5 rounded-xl border border-outline hover:bg-surface-container text-on-surface-variant"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <CompanyDocumentHeader
              documentTitle="FACTURE PROFORMA / DÉFINITIVE"
              documentNumber={selectedInvoice.numero_facture || `FAC-2026-${String(selectedInvoice.id).padStart(4, '0')}`}
              documentDate={selectedInvoice.date_emission || new Date().toISOString().slice(0, 10)}
              documentReference={selectedInvoice.reference}
            />

            <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-surface-container/30 border border-outline text-xs">
              <div>
                <p className="font-semibold text-on-surface uppercase tracking-wider text-[11px]">Facturé à (Client) :</p>
                <p className="font-bold text-sm text-on-surface mt-1">{selectedInvoice.client_nom || 'Client Externe'}</p>
                <p className="text-on-surface-variant">Réf Dossier : {selectedInvoice.reference || 'REF-GEN-2026'}</p>
                <p className="text-on-surface-variant">Conditions : Règlement 30 jours fin de mois</p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-on-surface uppercase tracking-wider text-[11px]">Détails Document :</p>
                <p className="text-on-surface-variant mt-1">Devise : <span className="font-semibold text-on-surface">FCFA (XAF)</span></p>
                <p className="text-on-surface-variant">Mode de règlement : <span className="font-semibold text-on-surface">Virement Bancaire</span></p>
                <p className="text-on-surface-variant">Statut : <span className="font-bold text-emerald-600">{selectedInvoice.statut || 'VALIDÉE'}</span></p>
              </div>
            </div>

            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-outline bg-surface-container/50 font-bold text-on-surface">
                  <th className="p-2.5">Désignation des Prestations</th>
                  <th className="p-2.5 text-center">Qté</th>
                  <th className="p-2.5 text-right">Prix Unitaire</th>
                  <th className="p-2.5 text-right">Total HT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline">
                <tr>
                  <td className="p-2.5 font-medium text-on-surface">
                    {selectedInvoice.description || 'Prestations logistiques, manutention portuaire et transport multimodal'}
                  </td>
                  <td className="p-2.5 text-center">1</td>
                  <td className="p-2.5 text-right">{Number(selectedInvoice.montant_ht || selectedInvoice.montant || 0).toLocaleString('fr-FR')} FCFA</td>
                  <td className="p-2.5 text-right font-bold text-on-surface">{Number(selectedInvoice.montant_ht || selectedInvoice.montant || 0).toLocaleString('fr-FR')} FCFA</td>
                </tr>
              </tbody>
            </table>

            <div className="flex justify-end">
              <div className="w-64 space-y-1.5 text-xs p-3 rounded-xl bg-surface-container/20 border border-outline">
                <div className="flex justify-between text-on-surface-variant">
                  <span>Sous-total HT :</span>
                  <span>{Number(selectedInvoice.montant_ht || selectedInvoice.montant || 0).toLocaleString('fr-FR')} FCFA</span>
                </div>
                <div className="flex justify-between text-on-surface-variant">
                  <span>TVA (19.25%) :</span>
                  <span>{Math.round(Number(selectedInvoice.montant_ht || selectedInvoice.montant || 0) * 0.1925).toLocaleString('fr-FR')} FCFA</span>
                </div>
                <div className="flex justify-between text-sm font-bold text-primary border-t border-outline pt-1.5">
                  <span>Net à Payer TTC :</span>
                  <span>{Number(selectedInvoice.montant_ttc || selectedInvoice.montant || 0).toLocaleString('fr-FR')} FCFA</span>
                </div>
              </div>
            </div>

            <CompanyDocumentFooter />
          </div>
        </div>
      )}
    </div>
  );
}

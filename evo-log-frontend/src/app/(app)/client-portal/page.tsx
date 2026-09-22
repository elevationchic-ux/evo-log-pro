'use client';

import React, { useEffect, useState } from 'react';
import { Package, Search, TrendingUp, Calendar, ArrowRight, FileText, CheckCircle, Clock, ShieldCheck, Plus, X } from 'lucide-react';
import { transportAPI, financeAPI, magasinAPI, b2bPortalAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function ClientPortalHome() {
  const [loading, setLoading] = useState(true);
  const [missions, setMissions] = useState<any[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [declarations, setDeclarations] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isQuoteModalOpen, setIsQuoteModalOpen] = useState(false);

  // Form quote request state
  const [quoteOrigin, setQuoteOrigin] = useState('');
  const [quoteDestination, setQuoteDestination] = useState('');
  const [quoteCargo, setQuoteCargo] = useState('');

  type TabType = 'transport' | 'finance' | 'douane';
  const [activeTab, setActiveTab] = useState<TabType>('transport');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await transportAPI.getMissions({ limit: 15 });
      const rawMissions = res.data?.items || res.data || (Array.isArray(res) ? res : []);
      setMissions(rawMissions);

      const invRes = await financeAPI.getFactures();
      const rawInvoices = invRes.data?.items || invRes.data || (Array.isArray(invRes) ? invRes : []);
      setInvoices(rawInvoices);

      const decRes = await magasinAPI.getDeclarations();
      const rawDeclarations = decRes.data?.items || decRes.data || (Array.isArray(decRes) ? decRes : []);
      setDeclarations(rawDeclarations);
    } catch (error) {
      console.error('Failed to load portal data', error);
      toast.error('Erreur de chargement des données en direct du serveur.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quoteOrigin || !quoteDestination) {
      toast.error('Veuillez remplir l\'origine et la destination');
      return;
    }
    try {
      await b2bPortalAPI.createQuote({
        type_fret: 'TERRESTRE',
        origine: quoteOrigin,
        destination: quoteDestination,
        nature_marchandise: quoteCargo || 'Cargaison Marchandises Diverses',
        poids_estime_kg: 1000.0,
        volume_cbm: 5.0,
        incoterm: 'CIF',
        notes: 'Demande soumise en direct via le portail B2B client'
      });
      toast.success('Demande de cotation transmise avec succès aux équipes EVO-LOG !');
      setIsQuoteModalOpen(false);
      setQuoteOrigin('');
      setQuoteDestination('');
      setQuoteCargo('');
      loadData();
    } catch (err) {
      toast.error('Erreur lors de la création de la cotation.');
    }
  };

  // Filter items
  const filteredMissions = missions.filter((m) =>
    (m.reference + ' ' + (m.origine || '') + ' ' + (m.destination || '') + ' ' + (m.nature_fret || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  const filteredInvoices = invoices.filter((i) =>
    (i.numero_facture || String(i.id || '')).toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredDeclarations = declarations.filter((d) =>
    (String(d.numero_declaration || d.id || '') + ' ' + (d.marchandise || '')).toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-500 max-w-7xl mx-auto px-2 sm:px-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl text-white shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-semibold mb-2 border border-blue-500/20">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
            Portail Client B2B • CFAO LOGISTICS
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Espace Suivi de Fret</h1>
          <p className="text-slate-400 text-sm mt-1">Supervision temps réel de vos expéditions, conteneurs et facturation.</p>
        </div>

        <button
          onClick={() => setIsQuoteModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-indigo-600/30 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          Demander une Cotation
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="bg-slate-900/60 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-sm backdrop-blur-md">
          <div className="w-12 h-12 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-xl flex items-center justify-center mb-3">
            <TrendingUp className="w-6 h-6" />
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Missions En Route</p>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-100">
            {missions.filter((m) => m.statut === 'EN_ROUTE' || m.statut === 'EN_CHARGEMENT').length}
          </h2>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-sm backdrop-blur-md">
          <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-xl flex items-center justify-center mb-3">
            <Package className="w-6 h-6" />
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Expéditions Livrées</p>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-100">
            {missions.filter((m) => m.statut === 'LIVRE' || m.statut === 'LIVREE' || m.statut === 'TERMINEE').length}
          </h2>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-sm backdrop-blur-md sm:col-span-2 lg:col-span-1">
          <div className="w-12 h-12 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-xl flex items-center justify-center mb-3">
            <FileText className="w-6 h-6" />
          </div>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Factures En Attente</p>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-100">
            {invoices.filter((i) => i.statut === 'VALIDEE_NON_PAYEE' || i.statut === 'EN_ATTENTE').length}
          </h2>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex overflow-x-auto gap-2 bg-slate-900/80 p-1.5 border border-slate-800 rounded-xl max-w-full">
        <button
          onClick={() => setActiveTab('transport')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold whitespace-nowrap transition-all ${
            activeTab === 'transport'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Package className="w-4 h-4" /> Expéditions ({missions.length})
        </button>

        <button
          onClick={() => setActiveTab('finance')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold whitespace-nowrap transition-all ${
            activeTab === 'finance'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <FileText className="w-4 h-4" /> Facturation ({invoices.length})
        </button>

        <button
          onClick={() => setActiveTab('douane')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold whitespace-nowrap transition-all ${
            activeTab === 'douane'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <ShieldCheck className="w-4 h-4" /> Douane & Magasin ({declarations.length})
        </button>
      </div>

      {/* Main Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            {activeTab === 'transport'
              ? 'Expéditions et Ordres de Transport Récents'
              : activeTab === 'finance'
              ? 'Relevé des Factures Client'
              : 'Déclarations en Douane & Transit'}
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par référence..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              {activeTab === 'transport' && (
                <tr>
                  <th className="px-6 py-4">Référence OT</th>
                  <th className="px-6 py-4">Trajet (Origine → Destination)</th>
                  <th className="px-6 py-4">Nature Fret</th>
                  <th className="px-6 py-4 text-right">Statut</th>
                </tr>
              )}
              {activeTab === 'finance' && (
                <tr>
                  <th className="px-6 py-4">N° Facture</th>
                  <th className="px-6 py-4">Échéance</th>
                  <th className="px-6 py-4 text-right">Montant TTC</th>
                  <th className="px-6 py-4 text-right">Statut</th>
                </tr>
              )}
              {activeTab === 'douane' && (
                <tr>
                  <th className="px-6 py-4">N° Déclaration</th>
                  <th className="px-6 py-4">Marchandise</th>
                  <th className="px-6 py-4 text-right">Statut</th>
                </tr>
              )}
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={4} className="p-12 text-center text-slate-400">
                    <div className="inline-block animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full mr-2" />
                    Chargement des données en direct du serveur...
                  </td>
                </tr>
              ) : activeTab === 'transport' ? (
                filteredMissions.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-slate-500">
                      Aucune expédition trouvée.
                    </td>
                  </tr>
                ) : (
                  filteredMissions.map((m) => (
                    <tr key={m.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-100">
                        {m.reference}
                        <div className="text-xs font-normal text-slate-400 flex items-center gap-1 mt-0.5">
                          <Calendar className="w-3 h-3 text-slate-500" />
                          {m.date_chargement_prevue ? new Date(m.date_chargement_prevue).toLocaleDateString() : 'Aujourd\'hui'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-200">{m.origine || m.lieu_depart || 'Douala Port'}</div>
                        <div className="text-xs text-slate-400 flex items-center gap-1">
                          <ArrowRight className="w-3 h-3 text-indigo-400" /> {m.destination || m.lieu_arrivee || 'Bassa'}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-300 font-medium">{m.nature_fret || 'Marchandises diverses'}</td>
                      <td className="px-6 py-4 text-right">
                        {(m.statut === 'EN_ROUTE' || m.statut === 'EN_CHARGEMENT') && (
                          <span className="inline-flex px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                            EN ROUTE
                          </span>
                        )}
                        {(m.statut === 'LIVRE' || m.statut === 'LIVREE' || m.statut === 'TERMINEE') && (
                          <span className="inline-flex px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            LIVRÉ
                          </span>
                        )}
                        {(m.statut === 'BROUILLON' || m.statut === 'PLANIFIE') && (
                          <span className="inline-flex px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                            PROGRAMMÉ
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )
              ) : activeTab === 'finance' ? (
                filteredInvoices.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-slate-500">
                      Aucune facture enregistrée.
                    </td>
                  </tr>
                ) : (
                  filteredInvoices.map((inv: any) => (
                    <tr key={inv.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-100">{inv.numero_facture || `FAC-${inv.id}`}</td>
                      <td className="px-6 py-4 text-slate-300">
                        {inv.date_echeance ? new Date(inv.date_echeance).toLocaleDateString() : '30 jours'}
                      </td>
                      <td className="px-6 py-4 text-right font-mono font-bold text-emerald-400">
                        {Number(inv.montant_ttc_xaf || inv.montant_ttc || 0).toLocaleString()} XAF
                      </td>
                      <td className="px-6 py-4 text-right">
                        {(inv.statut === 'PAYEE' || inv.statut === 'PAYE_TOTAL') && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            <CheckCircle className="w-3 h-3" /> PAYÉE
                          </span>
                        )}
                        {(inv.statut === 'VALIDEE_NON_PAYEE' || inv.statut === 'EMISE') && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                            <Clock className="w-3 h-3" /> EN ATTENTE
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )
              ) : (
                filteredDeclarations.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-slate-500">
                      Aucune déclaration enregistrée.
                    </td>
                  </tr>
                ) : (
                  filteredDeclarations.map((dec: any) => (
                    <tr key={dec.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-100">{dec.numero_declaration || `DEC-${dec.id}`}</td>
                      <td className="px-6 py-4 text-slate-300">{dec.marchandise || 'Importation Fret'}</td>
                      <td className="px-6 py-4 text-right">
                        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                          <ShieldCheck className="w-3 h-3" /> CONFORME
                        </span>
                      </td>
                    </tr>
                  ))
                )
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Demande de Cotation */}
      {isQuoteModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold">Nouvelle Demande de Cotation</h3>
              <button onClick={() => setIsQuoteModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateQuote} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Lieu de Chargement (Origine)</label>
                <input
                  type="text"
                  required
                  value={quoteOrigin}
                  onChange={(e) => setQuoteOrigin(e.target.value)}
                  placeholder="ex: Port Autonome de Douala"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Lieu de Livraison (Destination)</label>
                <input
                  type="text"
                  required
                  value={quoteDestination}
                  onChange={(e) => setQuoteDestination(e.target.value)}
                  placeholder="ex: Entrepôt CFAO Bassa"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Description Fret & Conteneurs</label>
                <textarea
                  value={quoteCargo}
                  onChange={(e) => setQuoteCargo(e.target.value)}
                  placeholder="ex: 2 conteneurs 40ft pièces détachées (35T)"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 h-24"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsQuoteModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30"
                >
                  Envoyer la Demande
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

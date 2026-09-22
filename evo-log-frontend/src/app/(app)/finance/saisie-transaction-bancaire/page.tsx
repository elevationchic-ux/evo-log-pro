'use client'

import { useState, useEffect } from 'react'
import { financeAPI } from '@/lib/api-client'
import { Plus, Search, Filter, MoreVertical, Download, Eye, CheckCircle2, ArrowRightLeft, CreditCard } from 'lucide-react'
import { toast } from 'sonner'

export default function SaisieTransactionBancairePage() {
  const [selectedAccount, setSelectedAccount] = useState('Compte Principal - BNA (DZ)')
  const [selectedTransaction, setSelectedTransaction] = useState<any>(null)
  const [transactions, setTransactions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const [formData, setFormData] = useState({
    dateValeur: new Date().toISOString().split('T')[0],
    dateComptable: new Date().toISOString().split('T')[0],
    libelle: '',
    montant: '',
    compteGeneral: '411000',
    compteGeneralLabel: 'Clients',
    centreCout: '',
    codeTaxe: 't0',
    sens: 'credit'
  })

  useEffect(() => {
    fetchTransactions()
  }, [])

  const fetchTransactions = async () => {
    setLoading(true)
    try {
      const res = await financeAPI.getEncaissements()
      setTransactions(res.data || [])
    } catch (error) {
      console.error('Error fetching encaissements:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTransactionSelect = (tx: any) => {
    setSelectedTransaction(tx)
    setFormData({
      ...formData,
      dateValeur: tx.date_paiement ? new Date(tx.date_paiement).toISOString().split('T')[0] : formData.dateValeur,
      dateComptable: tx.date_paiement ? new Date(tx.date_paiement).toISOString().split('T')[0] : formData.dateComptable,
      libelle: tx.reference || tx.notes || 'Encaissement',
      montant: String(tx.montant_xaf || 0),
      sens: 'credit'
    })
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    toast.success('Saisie enregistrée avec succès.')
    fetchTransactions()
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-CM', { style: 'currency', currency: 'XAF' }).format(amount)
  }

  return (
    <div className="bg-slate-50 min-h-full flex flex-col p-6">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <ArrowRightLeft className="w-8 h-8 text-blue-600" />
            Saisie des Transactions Bancaires
          </h1>
          <p className="text-slate-500 mt-1">Gérez le lettrage et la saisie comptable des extraits bancaires.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors font-medium shadow-sm">
            <Download className="w-4 h-4" />
            Importer Extrait
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden flex flex-col md:flex-row gap-6 max-w-full">
        {/* Left Pane: Bank Statement View */}
        <div className="w-full md:w-1/2 flex flex-col bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="bg-slate-50 p-4 border-b border-slate-200 flex flex-wrap justify-between items-center gap-4">
            <h2 className="font-bold text-slate-800 flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-slate-500" />
              Extrait de Compte Bancaire
            </h2>
            <div className="flex items-center space-x-3">
              <select 
                className="text-sm bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-slate-700 focus:ring-2 focus:ring-blue-500 outline-none"
                value={selectedAccount}
                onChange={(e) => setSelectedAccount(e.target.value)}
              >
                <option>Compte Principal - BNA (DZ)</option>
                <option>Compte Devises - SG</option>
              </select>
              <button onClick={fetchTransactions} className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-200 transition-colors" title="Rafraîchir">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-auto bg-white custom-scrollbar">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 bg-slate-50 shadow-sm z-10 border-b border-slate-200">
                <tr>
                  <th className="p-3 text-xs font-bold text-slate-500 uppercase tracking-wider w-24">Date</th>
                  <th className="p-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Libellé / Réf</th>
                  <th className="p-3 text-xs font-bold text-slate-500 uppercase tracking-wider text-right w-32">Montant</th>
                  <th className="p-3 text-xs font-bold text-slate-500 uppercase tracking-wider text-center w-16">État</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr><td colSpan={4} className="p-8 text-center text-slate-500">Chargement...</td></tr>
                ) : transactions.length === 0 ? (
                  <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucune transaction trouvée.</td></tr>
                ) : transactions.map((tx, index) => {
                  const isSelected = selectedTransaction?.id === tx.id
                  return (
                    <tr 
                      key={tx.id || index}
                      className={`transition-colors cursor-pointer hover:bg-blue-50/50 ${isSelected ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''}`}
                      onClick={() => handleTransactionSelect(tx)}
                    >
                      <td className="p-3 text-sm text-slate-600">{new Date(tx.date_paiement || tx.created_at).toLocaleDateString('fr-FR')}</td>
                      <td className={`p-3 text-sm ${isSelected ? 'font-bold text-slate-900' : 'text-slate-700'}`}>{tx.reference || tx.notes || 'Encaissement'}</td>
                      <td className={`p-3 text-sm text-right ${isSelected ? 'font-bold text-slate-900' : 'text-slate-700 font-mono'}`}>
                        <span className="text-emerald-600 font-medium">+{formatCurrency(tx.montant_xaf || 0)}</span>
                      </td>
                      <td className="p-3 text-center">
                        {tx.lettree ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto" />
                        ) : (
                          <div className="w-2 h-2 rounded-full bg-amber-400 mx-auto" title="Non lettré" />
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Pane: Manual Entry Form */}
        <div className="w-full md:w-1/2 flex flex-col bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="bg-slate-50 p-5 border-b border-slate-200">
            <h2 className="font-bold text-slate-800 flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
              Saisie Manuelle - Ligne Comptable
            </h2>
          </div>
          <div className="p-6 flex-1 overflow-y-auto custom-scrollbar">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Alert Context */}
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 flex items-start space-x-3">
                <svg className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <div>
                  <p className="text-sm text-blue-800">Saisie d'une écriture comptable pour la transaction sélectionnée :</p>
                  <p className="font-bold text-blue-900 mt-1">
                    {selectedTransaction ? `${selectedTransaction.reference || 'Ref'} - ${formatCurrency(selectedTransaction.montant_xaf)}` : 'Aucune transaction sélectionnée'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Date de valeur</label>
                  <input 
                    className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" 
                    type="date" 
                    value={formData.dateValeur}
                    onChange={(e) => handleInputChange('dateValeur', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Date comptable</label>
                  <input 
                    className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" 
                    type="date" 
                    value={formData.dateComptable}
                    onChange={(e) => handleInputChange('dateComptable', e.target.value)}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Libellé de l'écriture</label>
                <input 
                  className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" 
                  type="text" 
                  placeholder="Ex: Paiement facture F-2023..."
                  value={formData.libelle}
                  onChange={(e) => handleInputChange('libelle', e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Montant (FCFA)</label>
                  <input 
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 font-mono text-right outline-none cursor-not-allowed" 
                    readOnly 
                    type="text" 
                    value={formData.montant}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Sens</label>
                  <div className="flex items-center space-x-4 mt-3">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input 
                        checked={formData.sens === 'debit'} 
                        onChange={() => handleInputChange('sens', 'debit')}
                        className="text-blue-600 focus:ring-blue-500" 
                        name="sens" 
                        type="radio" 
                        value="debit"
                      />
                      <span className="text-sm font-medium text-slate-700">Débit</span>
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input 
                        checked={formData.sens === 'credit'} 
                        onChange={() => handleInputChange('sens', 'credit')}
                        className="text-blue-600 focus:ring-blue-500" 
                        name="sens" 
                        type="radio" 
                        value="credit"
                      />
                      <span className="text-sm font-medium text-slate-700">Crédit</span>
                    </label>
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-200 pt-6 mt-2">
                <h3 className="text-md font-bold text-slate-800 mb-4">Imputation Comptable</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1.5">Compte Général (Contrepartie)</label>
                    <div className="flex space-x-2">
                      <input 
                        className="w-1/3 bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all font-mono" 
                        placeholder="Ex: 411000" 
                        type="text" 
                        value={formData.compteGeneral}
                        onChange={(e) => handleInputChange('compteGeneral', e.target.value)}
                        required
                      />
                      <input 
                        className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-600 outline-none cursor-not-allowed" 
                        readOnly 
                        type="text" 
                        value={formData.compteGeneralLabel}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1.5">Centre de Coût</label>
                      <select 
                        className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                        value={formData.centreCout}
                        onChange={(e) => handleInputChange('centreCout', e.target.value)}
                      >
                        <option value="">Sélectionner...</option>
                        <option value="cc1">CC-FIN (Finance)</option>
                        <option value="cc2">CC-DIR (Direction)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1.5">Code Taxe</label>
                      <select 
                        className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                        value={formData.codeTaxe}
                        onChange={(e) => handleInputChange('codeTaxe', e.target.value)}
                      >
                        <option value="t0">T0 - Exonéré</option>
                        <option value="t1">T1 - TVA 9%</option>
                        <option value="t2">T2 - TVA 19%</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <button type="button" className="px-5 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors">
                  Annuler
                </button>
                <button type="submit" disabled={!selectedTransaction} className="px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
                  Valider l'Écriture
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

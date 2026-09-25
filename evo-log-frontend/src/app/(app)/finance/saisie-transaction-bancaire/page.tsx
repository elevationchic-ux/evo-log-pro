'use client'

import { useState, useEffect, useCallback } from 'react'
import { ArrowRightLeft, CreditCard, CheckCircle2 } from 'lucide-react'
import { financeAPI, transactionsAPI } from '@/lib/api-client'
import { toast } from 'sonner'

interface TxRow {
  id: number
  facture_id: number | null
  facture_numero: string | null
  montant: number
  date_paiement: string | null
  mode_paiement: string | null
  reference: string | null
  statut: string
  notes: string | null
}

const MODES_PAIEMENT = [
  { value: 'virement', label: 'Virement bancaire' },
  { value: 'cheque', label: 'Chèque' },
  { value: 'espece', label: 'Espèces' },
  { value: 'mobile_money', label: 'Mobile Money' },
  { value: 'orange_money', label: 'Orange Money' },
  { value: 'mtn_momo', label: 'MTN MoMo' },
]

export default function SaisieTransactionBancairePage() {
  const [transactions, setTransactions] = useState<TxRow[]>([])
  const [factures, setFactures] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [selectedTransaction, setSelectedTransaction] = useState<TxRow | null>(null)

  const [formData, setFormData] = useState({
    facture_id: '',
    montant: '',
    mode_paiement: 'virement',
    reference: '',
    date_paiement: new Date().toISOString().split('T')[0],
    notes: '',
  })

  const fetchTransactions = useCallback(async () => {
    setLoading(true)
    try {
      const res = await transactionsAPI.getAll({ limit: 200 })
      const items = Array.isArray(res.data) ? res.data : (res.data?.items ?? [])
      setTransactions(items)
    } catch (error) {
      console.error('Error fetching transactions:', error)
      toast.error('Erreur lors du chargement des transactions')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTransactions()
    // Factures reelles du tenant (source de la selection reglement)
    financeAPI.getFactures()
      .then(res => {
        const items = Array.isArray(res.data) ? res.data : (res.data?.items ?? [])
        setFactures(items)
      })
      .catch(console.error)
  }, [fetchTransactions])

  const handleTransactionSelect = (tx: TxRow) => {
    setSelectedTransaction(tx)
    setFormData(prev => ({
      ...prev,
      facture_id: tx.facture_id != null ? String(tx.facture_id) : prev.facture_id,
      montant: String(tx.montant ?? ''),
      mode_paiement: tx.mode_paiement || prev.mode_paiement,
      reference: tx.reference || prev.reference,
      notes: tx.notes || prev.notes,
    }))
  }

  const handleFactureChange = (factureId: string) => {
    const f = factures.find((x: any) => String(x.id) === factureId)
    setFormData(prev => ({
      ...prev,
      facture_id: factureId,
      montant: f ? String(f.montant_ttc) : prev.montant,
    }))
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.facture_id) {
      toast.error('Sélectionnez une facture à régler.')
      return
    }
    const montant = parseFloat(formData.montant)
    if (!Number.isFinite(montant) || montant <= 0) {
      toast.error('Montant invalide.')
      return
    }
    setSaving(true)
    try {
      await transactionsAPI.create({
        facture_id: parseInt(formData.facture_id),
        montant,
        mode_paiement: formData.mode_paiement,
        reference: formData.reference || null,
        date_paiement: formData.date_paiement || null,
        notes: formData.notes || null,
      })
      toast.success('Règlement enregistré.')
      setSelectedTransaction(null)
      fetchTransactions()
    } catch (err: any) {
      toast.error(`Erreur: ${err.response?.data?.detail || 'Enregistrement impossible'}`)
    } finally {
      setSaving(false)
    }
  }

  const handleReconcile = async (tx: TxRow) => {
    try {
      await transactionsAPI.reconcile(tx.id)
      toast.success('Transaction rapprochée, écriture comptable générée.')
      fetchTransactions()
    } catch (err: any) {
      toast.error(`Erreur: ${err.response?.data?.detail || 'Rapprochement impossible'}`)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-CM', { style: 'currency', currency: 'XAF' }).format(amount || 0)
  }

  return (
    <div className="bg-slate-800 min-h-full flex flex-col p-4 sm:p-6">

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-200 flex items-center gap-3">
            <ArrowRightLeft className="w-8 h-8 text-blue-600" />
            Saisie des Transactions Bancaires
          </h1>
          <p className="text-slate-500 mt-1">Enregistrez les règlements reçus et lettez-les avec les écritures comptables.</p>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden flex flex-col md:flex-row gap-6 max-w-full">
        {/* Left Pane: Transactions list */}
        <div className="w-full md:w-1/2 flex flex-col bg-slate-900 border border-slate-700 rounded-2xl shadow-sm overflow-hidden">
          <div className="bg-slate-800 p-4 border-b border-slate-700 flex flex-wrap justify-between items-center gap-4">
            <h2 className="font-bold text-slate-200 flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-slate-500" />
              Règlements enregistrés
            </h2>
            <button onClick={fetchTransactions} className="p-1.5 text-slate-500 hover:text-slate-200 rounded-lg hover:bg-slate-700 transition-colors" title="Rafraîchir">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            </button>
          </div>
          <div className="flex-1 overflow-auto custom-scrollbar">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 bg-slate-800 shadow-sm z-10 border-b border-slate-700">
                <tr>
                  <th className="p-3 text-xs font-bold text-slate-500 uppercase tracking-wider w-24">Date</th>
                  <th className="p-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Réf / Facture</th>
                  <th className="p-3 text-xs font-bold text-slate-500 uppercase tracking-wider text-right w-32">Montant</th>
                  <th className="p-3 text-xs font-bold text-slate-500 uppercase tracking-wider text-center w-24">État</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {loading ? (
                  <tr><td colSpan={4} className="p-8 text-center text-slate-500">Chargement...</td></tr>
                ) : transactions.length === 0 ? (
                  <tr><td colSpan={4} className="p-8 text-center text-slate-500">Aucune transaction enregistrée.</td></tr>
                ) : transactions.map((tx) => {
                  const isSelected = selectedTransaction?.id === tx.id
                  return (
                    <tr
                      key={tx.id}
                      className={`transition-colors cursor-pointer hover:bg-blue-500/5 ${isSelected ? 'bg-blue-500/10 border-l-4 border-l-blue-600' : ''}`}
                      onClick={() => handleTransactionSelect(tx)}
                    >
                      <td className="p-3 text-sm text-slate-400">{tx.date_paiement ? new Date(tx.date_paiement).toLocaleDateString('fr-FR') : ''}</td>
                      <td className={`p-3 text-sm ${isSelected ? 'font-bold text-slate-200' : 'text-slate-300'}`}>
                        {tx.reference || tx.notes || 'Règlement'}
                        {tx.facture_numero && <span className="block text-xs text-slate-500">{tx.facture_numero}</span>}
                      </td>
                      <td className="p-3 text-sm text-right font-mono text-emerald-600 font-medium">
                        +{formatCurrency(tx.montant)}
                      </td>
                      <td className="p-3 text-center">
                        {tx.statut === 'valide' ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto" aria-hidden />
                        ) : (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleReconcile(tx) }}
                            className="text-xs font-bold px-2 py-1 rounded-lg bg-amber-500/15 text-amber-300 hover:bg-amber-500/25 transition-colors"
                            title="Générer l'écriture comptable de rapprochement"
                          >
                            Lettrer
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Pane: New payment form */}
        <div className="w-full md:w-1/2 flex flex-col bg-slate-900 border border-slate-700 rounded-2xl shadow-sm">
          <div className="bg-slate-800 p-5 border-b border-slate-700">
            <h2 className="font-bold text-slate-200 flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
              Nouveau Règlement
            </h2>
          </div>
          <div className="p-6 flex-1 overflow-y-auto custom-scrollbar">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-1.5">Facture réglée *</label>
                <select
                  className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  value={formData.facture_id}
                  onChange={(e) => handleFactureChange(e.target.value)}
                  required
                >
                  <option value="">Sélectionner une facture...</option>
                  {factures.map((f: any) => (
                    <option key={f.id} value={f.id}>
                      {f.numero_facture}{f.client_nom ? `  ${f.client_nom}` : ''}  {formatCurrency(f.montant_ttc)}
                    </option>
                  ))}
                </select>
                {factures.length === 0 && (
                  <p className="text-xs text-slate-500 mt-1">Aucune facture enregistrée pour le moment.</p>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">Montant (FCFA) *</label>
                  <input
                    className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-2.5 text-sm text-slate-200 font-mono text-right focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    type="number" step="0.01" min="0"
                    value={formData.montant}
                    onChange={(e) => handleInputChange('montant', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">Date de paiement</label>
                  <input
                    className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    type="date"
                    value={formData.date_paiement}
                    onChange={(e) => handleInputChange('date_paiement', e.target.value)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">Mode de paiement *</label>
                  <select
                    className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    value={formData.mode_paiement}
                    onChange={(e) => handleInputChange('mode_paiement', e.target.value)}
                    required
                  >
                    {MODES_PAIEMENT.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">Référence bancaire</label>
                  <input
                    className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all font-mono"
                    type="text"
                    placeholder="Ex: VIR-2026-00451"
                    value={formData.reference}
                    onChange={(e) => handleInputChange('reference', e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-1.5">Notes</label>
                <textarea
                  className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  rows={3}
                  placeholder="Informations complémentaires..."
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                />
              </div>

              <div className="pt-4 flex justify-end">
                <button type="submit" disabled={saving} className="px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
                  {saving ? 'Enregistrement...' : 'Enregistrer le règlement'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

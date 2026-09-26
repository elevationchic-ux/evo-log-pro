'use client'

import { useState, useEffect } from 'react'
import { Search, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/Card'
import { magasinAPI } from '@/lib/api-client'

// Contrat reel de /api/magasin/transactions : alias metier de /history,
// qui renvoie un MovementListResponse (journal des mouvements de stock),
// PAS un annuaire de « transactions » avec interface de navigation.
interface Transaction {
  id: number
  reference: string
  type_mouvement: string
  quantite: number
  code_article?: string | null
  designation?: string | null
  raison?: string | null
  date_mouvement?: string | null
}

export function TransactionSearch() {
  const [searchTerm, setSearchTerm] = useState('')
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>([])
  const [showResults, setShowResults] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadTransactions = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await magasinAPI.getTransactions()
        // L'enveloppe reelle est MovementListResponse : { items, total, entrees, sorties }
        const data = res.data?.items || []
        setTransactions(data)
      } catch (err) {
        console.error('Failed to load transactions', err)
        setError('Failed to load transactions')
        setTransactions([])
      } finally {
        setLoading(false)
      }
    }

    loadTransactions()
  }, [])

  const handleSearch = (value: string) => {
    setSearchTerm(value)
    if (value.length >= 2) {
      const needle = value.toLowerCase()
      const filtered = transactions.filter(
        (t) =>
          (t.reference ?? '').toLowerCase().includes(needle) ||
          (t.code_article ?? '').toLowerCase().includes(needle) ||
          (t.designation ?? '').toLowerCase().includes(needle)
      )
      setFilteredTransactions(filtered)
      setShowResults(true)
    } else {
      setShowResults(false)
    }
  }

  const handleSelect = (transaction: Transaction) => {
    // Pas de page de detail par mouvement : on ouvre le journal filtre sur la reference.
    window.location.href = `/magasin/transactions?q=${encodeURIComponent(transaction.reference)}`
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const exactMatch = transactions.find(
      (t) =>
        (t.reference ?? '').toLowerCase() === searchTerm.toLowerCase() ||
        (t.code_article ?? '').toLowerCase() === searchTerm.toLowerCase()
    )
    if (exactMatch) {
      handleSelect(exactMatch)
    }
  }

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              type="text"
              placeholder="Rechercher un mouvement (ref, article, designation...)"
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button type="submit" size="icon">
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>

        {loading && (
          <div className="text-center py-4">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-500"></div>
            <span className="ml-2">Chargement des transactions...</span>
          </div>
        )}

        {!loading && error && (
          <div className="text-center py-4 text-red-500">
            {error}
          </div>
        )}

        {!loading && !error && showResults && filteredTransactions.length > 0 && (
          <div className="border rounded-lg overflow-hidden">
            {filteredTransactions.map((transaction) => (
              <button
                key={transaction.id}
                type="button"
                onClick={() => handleSelect(transaction)}
                className="w-full px-4 py-3 text-left hover:bg-slate-800 border-b last:border-b-0 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-slate-100">
                      {transaction.reference} - {transaction.designation || transaction.code_article || 'Mouvement de stock'}
                    </div>
                    <div className="text-sm text-slate-400">
                      {transaction.type_mouvement} &middot; {transaction.quantite}
                      {transaction.raison ? ` - ${transaction.raison}` : ''}
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-gray-400" />
                </div>
              </button>
            ))}
          </div>
        )}

        {!loading && !error && showResults && filteredTransactions.length === 0 && (
          <div className="text-center py-4 text-slate-400">
            Aucune transaction trouvée pour "{searchTerm}"
          </div>
        )}

        {!loading && !error && !showResults && transactions.length === 0 && (
          <div className="text-center py-4 text-slate-400">
            Aucune transaction disponible
          </div>
        )}
      </form>
    </Card>
  )
}

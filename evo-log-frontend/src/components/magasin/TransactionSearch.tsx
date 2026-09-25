'use client'

import { useState, useEffect } from 'react'
import { Search, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/Card'
import { magasinAPI } from '@/lib/api-client'

interface Transaction {
  code_transaction: string
  nom: string
  description: string
  interface: string
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
        // Assuming the API returns { data: Transaction[] } or directly Transaction[]
        const data = res.data || []
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
      const filtered = transactions.filter(
        (t) =>
          t.code_transaction.toLowerCase().includes(value.toLowerCase()) ||
          t.nom.toLowerCase().includes(value.toLowerCase())
      )
      setFilteredTransactions(filtered)
      setShowResults(true)
    } else {
      setShowResults(false)
    }
  }

  const handleSelect = (transaction: Transaction) => {
    window.location.href = transaction.interface
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const exactMatch = transactions.find(
      (t) => t.code_transaction.toLowerCase() === searchTerm.toLowerCase()
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
              placeholder="Tapez une transaction (ex: KM24, KT10...)"
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
                key={transaction.code_transaction}
                type="button"
                onClick={() => handleSelect(transaction)}
                className="w-full px-4 py-3 text-left hover:bg-slate-800 border-b last:border-b-0 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-slate-100">
                      {transaction.code_transaction} - {transaction.nom}
                    </div>
                    <div className="text-sm text-slate-400">{transaction.description}</div>
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

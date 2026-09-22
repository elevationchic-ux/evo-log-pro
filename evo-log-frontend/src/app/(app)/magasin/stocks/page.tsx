'use client'

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Search, Filter, Warehouse, Package, Calendar, User } from 'lucide-react'
import { DataTable } from '@/components/shared/DataTable'
import { Stock, StockFilter } from '@/types/magasin'
import { PortIllustration } from '@/components/illustrations/PortIllustration'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { magasinAPI } from '@/lib/api-client'
import { toast } from 'sonner'

export default function StocksPage() {
  const [showFilters, setShowFilters] = useState(false)
  
  const [filters, setFilters] = useState<StockFilter>({
    code_article: '',
    magasin_ids: [],
    client_id: undefined,
    date_debut: '',
    date_fin: ''
  })
  
  const [activeFilters, setActiveFilters] = useState<any>(undefined)

  const { data: stocks = [], isLoading, refetch: loadStocks } = useQuery({
    queryKey: ['stocks', activeFilters],
    queryFn: async () => {
      const response = await magasinAPI.getStocks(activeFilters)
      return response.data || []
    }
  })

  const columns = [
    {
      key: 'article',
      header: 'Article',
      cell: (row: Stock) => (
        <div>
          <div className="font-mono font-medium text-blue-600">{row.article?.code_article}</div>
          <div className="font-medium">{row.article?.nom}</div>
        </div>
      )
    },
    {
      key: 'magasin',
      header: 'Magasin',
      cell: (row: Stock) => (
        <div className="flex items-center gap-2">
          <Warehouse className="h-4 w-4 text-gray-400" />
          <span>{row.magasin?.nom}</span>
        </div>
      )
    },
    {
      key: 'quantite_disponible',
      header: 'Quantité disponible',
      cell: (row: Stock) => (
        <div className="font-medium">
          {(row.quantite_disponible || 0).toLocaleString()} {row.article?.unite_mesure}
        </div>
      )
    },
    {
      key: 'quantite_udb',
      header: 'Quantité UDB',
      cell: (row: Stock) => (
        <div className="text-gray-600">
          {(row.quantite_udb || 0).toLocaleString()} UDB
        </div>
      )
    },
    {
      key: 'derniere_maj',
      header: 'Dernière mise à jour',
      cell: (row: Stock) => (
        row.derniere_maj ? new Date(row.derniere_maj).toLocaleDateString('fr-FR') : '-'
      )
    }
  ]

  const handleFilter = () => {
    const newActiveFilters: any = {}
    if (filters.code_article) newActiveFilters.code_article = filters.code_article
    if (filters.magasin_ids && filters.magasin_ids.length > 0) newActiveFilters.magasin_id = filters.magasin_ids[0]
    
    setActiveFilters(newActiveFilters)
  }

  const handleReset = () => {
    setFilters({
      code_article: '',
      magasin_ids: [],
      client_id: undefined,
      date_debut: '',
      date_fin: ''
    })
    setActiveFilters(undefined)
  }

  return (
    <ModuleLayout module="magasin">
      <div className="container mx-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Stocks</h1>
            <p className="text-gray-600 mt-1">Vérification et gestion des stocks avec filtres avancés</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-32 h-20">
              <PortIllustration className="w-full h-full" />
            </div>
            <Button onClick={() => setShowFilters(!showFilters)}>
              <Filter className="mr-2 h-4 w-4" />
              Filtres
            </Button>
          </div>
        </div>

        {showFilters && (
          <div className="mb-6 rounded-lg bg-gray-50 p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="mb-1 flex items-center gap-2 text-sm font-medium">
                  <Package className="h-4 w-4" />
                  Code article
                </label>
                <Input
                  placeholder="Ex: 1000001"
                  value={filters.code_article}
                  onChange={(e) => setFilters({ ...filters, code_article: e.target.value })}
                />
              </div>
              <div>
                <label className="mb-1 flex items-center gap-2 text-sm font-medium">
                  <Warehouse className="h-4 w-4" />
                  Magasin
                </label>
                {/* Magasin dropdown will be implemented similarly to StockFilter component */}
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Tous les magasins" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tous les magasins</SelectItem>
                    {/* These will be populated dynamically - placeholder for now */}
                    <SelectItem value="1">Loading...</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="mb-1 flex items-center gap-2 text-sm font-medium">
                  <User className="h-4 w-4" />
                  Client
                </label>
                {/* Client dropdown will be implemented similarly to StockFilter component */}
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Tous les clients" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tous les clients</SelectItem>
                    {/* These will be populated dynamically - placeholder for now */}
                    <SelectItem value="1">Loading...</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="mb-1 flex items-center gap-2 text-sm font-medium">
                  <Calendar className="h-4 w-4" />
                  Date début
                </label>
                <Input
                  type="date"
                  value={filters.date_debut}
                  onChange={(e) => setFilters({ ...filters, date_debut: e.target.value })}
                />
              </div>
              <div>
                <label className="mb-1 flex items-center gap-2 text-sm font-medium">
                  <Calendar className="h-4 w-4" />
                  Date fin
                </label>
                <Input
                  type="date"
                  value={filters.date_fin}
                  onChange={(e) => setFilters({ ...filters, date_fin: e.target.value })}
                />
              </div>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <Button variant="outline" onClick={handleReset}>
                Réinitialiser
              </Button>
              <Button onClick={handleFilter}>
                <Search className="mr-2 h-4 w-4" />
                Filtrer
              </Button>
            </div>
          </div>
        )}

        <DataTable
          columns={columns}
          data={stocks}
          isLoading={isLoading}
        />
      </div>
    </ModuleLayout>
  )
}

'use client'

import { useState } from 'react'
import { StockFilter } from '@/components/magasin/StockFilter'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { Card } from '@/components/ui/Card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'

interface StockResult {
  id: number
  code_article: string
  nom_article: string
  magasin: string
  quantite_disponible: number
  quantite_udb: number
  statut: string
  categorie: string
}

export default function StockSearchPage() {
  const [results, setResults] = useState<StockResult[]>([])
  const [loading, setLoading] = useState(false)

  const handleFilter = async (filters: any) => {
    setLoading(true)
    try {
      const response = await fetch('/api/magasin/stocks/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters),
      })
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Erreur lors de la recherche:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatutColor = (statut: string) => {
    switch (statut) {
      case 'NORMAL':
        return 'bg-green-500/15 text-green-300'
      case 'DECHIRE':
        return 'bg-red-500/15 text-red-300'
      case 'MOUILLE':
        return 'bg-blue-500/15 text-blue-300'
      case 'ENDOMMAGE':
        return 'bg-orange-500/15 text-orange-300'
      case 'PERIME':
        return 'bg-purple-500/15 text-purple-300'
      case 'EN_ATTENTE':
        return 'bg-yellow-500/15 text-yellow-300'
      case 'RESERVE':
        return 'bg-slate-800 text-slate-100'
      default:
        return 'bg-slate-800 text-slate-100'
    }
  }

  return (
    <ModuleLayout module="magasin">
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Recherche Avancée de Stock</h1>
          <p className="text-slate-400">Recherchez des stocks avec des filtres avancés</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <StockFilter onFilter={handleFilter} />
          </div>

          <div className="lg:col-span-2">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Résultats</h2>
              
              {loading ? (
                <div className="text-center py-8 text-slate-400">
                  Chargement...
                </div>
              ) : results.length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                  Aucun résultat trouvé
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Code Article</TableHead>
                      <TableHead>Nom</TableHead>
                      <TableHead>Magasin</TableHead>
                      <TableHead>Quantité</TableHead>
                      <TableHead>Statut</TableHead>
                      <TableHead>Catégorie</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {results.map((stock) => (
                      <TableRow key={stock.id}>
                        <TableCell className="font-mono">{stock.code_article}</TableCell>
                        <TableCell>{stock.nom_article}</TableCell>
                        <TableCell>{stock.magasin}</TableCell>
                        <TableCell>
                          {stock.quantite_disponible} UDB
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatutColor(stock.statut)}>
                            {stock.statut}
                          </Badge>
                        </TableCell>
                        <TableCell>{stock.categorie}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </Card>
          </div>
        </div>
      </div>
    </ModuleLayout>
  )
}

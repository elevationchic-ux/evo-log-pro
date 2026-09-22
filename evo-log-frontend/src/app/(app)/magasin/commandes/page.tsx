'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Plus, Search, Edit, Trash2, ShoppingCart, Lock, Unlock, CheckCircle, Clock, Truck, Calendar, User } from 'lucide-react'
import { DataTable } from '@/components/shared/DataTable'
import { Commande, CommandeCreate, LigneCommandeCreate, StatutCommande, UniteMesure } from '@/types/magasin'
import { PortIllustration } from '@/components/illustrations/PortIllustration'
import { ModuleLayout } from '@/components/layout/ModuleLayout'

export default function CommandesPage() {
  const [commandes, setCommandes] = useState<Commande[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedCommande, setSelectedCommande] = useState<Commande | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const columns = [
    {
      key: 'numero_commande',
      header: 'N° Commande',
      cell: (row: Commande) => <span className="font-mono font-medium text-blue-600">{row.numero_commande}</span>
    },
    {
      key: 'client',
      header: 'Client',
      cell: (row: Commande) => (
        <div>
          <div className="font-medium">{row.client?.nom} {row.client?.prenom}</div>
          {row.client?.raison_sociale && <div className="text-sm text-gray-500">{row.client.raison_sociale}</div>}
        </div>
      )
    },
    {
      key: 'date_commande',
      header: 'Date commande',
      cell: (row: Commande) => (
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-gray-400" />
          <span>{new Date(row.date_commande).toLocaleDateString('fr-FR')}</span>
        </div>
      )
    },
    {
      key: 'statut',
      header: 'Statut',
      cell: (row: Commande) => {
        const statusConfig = {
          [StatutCommande.BROUILLON]: { color: 'bg-gray-100 text-gray-800', icon: Clock },
          [StatutCommande.EN_COURS]: { color: 'bg-blue-100 text-blue-800', icon: Clock },
          [StatutCommande.EN_ATTENTE]: { color: 'bg-gray-100 text-gray-800', icon: Clock },
          [StatutCommande.VERROUILLEE]: { color: 'bg-yellow-100 text-yellow-800', icon: Lock },
          [StatutCommande.PAYEE]: { color: 'bg-blue-100 text-blue-800', icon: CheckCircle },
          [StatutCommande.EN_PREPARATION]: { color: 'bg-purple-100 text-purple-800', icon: ShoppingCart },
          [StatutCommande.PRETE]: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
          [StatutCommande.LIVREE]: { color: 'bg-teal-100 text-teal-800', icon: Truck },
          [StatutCommande.ANNULEE]: { color: 'bg-red-100 text-red-800', icon: Trash2 }
        }
        const config = statusConfig[row.statut]
        const Icon = config.icon
        return (
          <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${config.color}`}>
            <Icon className="h-3 w-3" />
            {row.statut}
          </span>
        )
      }
    },
    {
      key: 'verrou',
      header: 'Verrou',
      cell: (row: Commande) => (
        row.est_verrouille ? (
          <Lock className="h-5 w-5 text-yellow-500" />
        ) : (
          <Unlock className="h-5 w-5 text-green-500" />
        )
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      cell: (row: Commande) => (
        <div className="flex gap-2">
          {row.est_verrouille && row.statut !== StatutCommande.ANNULEE && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleValidatePayment(row.id)}
              title="Valider le paiement"
            >
              <CheckCircle className="h-4 w-4 text-green-500" />
            </Button>
          )}
          {!row.est_verrouille && row.statut === StatutCommande.PAYEE && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handlePrepare(row.id)}
              title="Mettre en préparation"
            >
              <ShoppingCart className="h-4 w-4 text-purple-500" />
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleEdit(row)}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
          >
            <Trash2 className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      )
    }
  ]

  const handleEdit = (commande: Commande) => {
    setSelectedCommande(commande)
    setShowEditModal(true)
  }

  const handleValidatePayment = async (commandeId: number) => {
    setIsLoading(true)
    try {
      // API call to validate payment
      // await apiClient.post(`/api/magasin/commandes/${commandeId}/valider-paiement`, {}, { params: { valide_par: 'user' } })
      setCommandes(commandes.map(c => 
        c.id === commandeId ? { ...c, est_verrouille: false, paiement_valide: true, statut: StatutCommande.PAYEE } : c
      ))
    } catch (error) {
      console.error('Error validating payment:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handlePrepare = async (commandeId: number) => {
    setIsLoading(true)
    try {
      // API call to put in preparation
      // await apiClient.post(`/api/magasin/commandes/${commandeId}/preparer`)
      setCommandes(commandes.map(c => 
        c.id === commandeId ? { ...c, statut: StatutCommande.EN_PREPARATION } : c
      ))
    } catch (error) {
      console.error('Error preparing order:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (commandeId: number) => {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette commande ?')) {
      setIsLoading(true)
      try {
        // API call to delete order
        // await apiClient.post(`/api/magasin/commandes/${commandeId}/annuler`)
        setCommandes(commandes.filter(c => c.id !== commandeId))
      } catch (error) {
        console.error('Error deleting order:', error)
      } finally {
        setIsLoading(false)
      }
    }
  }

  const filteredCommandes = commandes.filter(commande =>
    commande.numero_commande.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (commande.client?.nom && commande.client.nom.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <ModuleLayout module="magasin">
      <div className="container mx-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Commandes Clients</h1>
            <p className="text-gray-600 mt-1">Gestion des commandes avec système de verrouillage</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-32 h-20">
              <PortIllustration className="w-full h-full" />
            </div>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Nouvelle Commande
            </Button>
          </div>
        </div>

        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="Rechercher par N° commande ou client..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <DataTable
          columns={columns}
          data={filteredCommandes}
          isLoading={isLoading}
        />

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="w-full max-w-4xl rounded-lg bg-white p-6">
              <h2 className="mb-4 text-xl font-bold">Nouvelle Commande</h2>
              <CommandeForm
                onSubmit={async (data) => {
                  setIsLoading(true)
                  try {
                    // API call to create order
                    // const response = await apiClient.post('/api/magasin/commandes', data, { params: { cree_par: 'user' } })
                    // setCommandes([...commandes, response.data])
                    setShowCreateModal(false)
                  } catch (error) {
                    console.error('Error creating order:', error)
                  } finally {
                    setIsLoading(false)
                  }
                }}
                onCancel={() => setShowCreateModal(false)}
              />
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && selectedCommande && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="w-full max-w-4xl rounded-lg bg-white p-6">
              <h2 className="mb-4 text-xl font-bold">Modifier Commande</h2>
              <CommandeForm
                initialData={selectedCommande}
                onSubmit={async (data) => {
                  setIsLoading(true)
                  try {
                    // API call to update order
                    // const response = await apiClient.put(`/api/magasin/commandes/${selectedCommande.id}`, data)
                    // setCommandes(commandes.map(c => c.id === selectedCommande.id ? response.data : c))
                    setShowEditModal(false)
                    setSelectedCommande(null)
                  } catch (error) {
                    console.error('Error updating order:', error)
                  } finally {
                    setIsLoading(false)
                  }
                }}
                onCancel={() => {
                  setShowEditModal(false)
                  setSelectedCommande(null)
                }}
              />
            </div>
          </div>
        )}
      </div>
    </ModuleLayout>
  )
}

function CommandeForm({
  initialData,
  onSubmit,
  onCancel
}: {
  initialData?: Commande
  onSubmit: (data: CommandeCreate) => void
  onCancel: () => void
}) {
  const [formData, setFormData] = useState<CommandeCreate>({
    numero_commande: initialData?.numero_commande || '',
    date_commande: initialData?.date_commande ? new Date(initialData.date_commande).toISOString().split('T')[0] : '',
    client_id: initialData?.client_id || 0,
    date_livraison_souhaitee: initialData?.date_livraison_souhaitee ? new Date(initialData.date_livraison_souhaitee).toISOString().split('T')[0] : '',
    statut: initialData?.statut || StatutCommande.EN_ATTENTE,
    est_verrouille: initialData?.est_verrouille ?? true,
    paiement_valide: initialData?.paiement_valide ?? false,
    notes: initialData?.notes || '',
    lignes: initialData?.lignes?.map(l => ({
      article_id: l.article_id,
      quantite_demandee: l.quantite_demandee,
      quantite_livree: l.quantite_livree || 0,
      unite_mesure: l.unite_mesure || UniteMesure.UDB,
      prix_unitaire: l.prix_unitaire
    })) || []
  })

  const [newLigne, setNewLigne] = useState<LigneCommandeCreate>({
    article_id: 0,
    quantite_demandee: 0,
    quantite_livree: 0,
    unite_mesure: UniteMesure.UDB,
    prix_unitaire: 0
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const addLigne = () => {
    if (newLigne.article_id && (newLigne.quantite_demandee || 0) > 0) {
      setFormData({
        ...formData,
        lignes: [...(formData.lignes || []), { ...newLigne }]
      })
      setNewLigne({
        article_id: 0,
        quantite_demandee: 0,
        quantite_livree: 0,
        unite_mesure: UniteMesure.UDB,
        prix_unitaire: 0
      })
    }
  }

  const removeLigne = (index: number) => {
    setFormData({
      ...formData,
      lignes: (formData.lignes || []).filter((_, i) => i !== index)
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 flex items-center gap-2 text-sm font-medium">
            <User className="h-4 w-4" />
            Client *
          </label>
          <Select
            value={(formData.client_id || 0).toString()}
            onValueChange={(value) => setFormData({ ...formData, client_id: parseInt(value) })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Sélectionner un client" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Client 1</SelectItem>
              <SelectItem value="2">Client 2</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <label className="mb-1 flex items-center gap-2 text-sm font-medium">
            <Calendar className="h-4 w-4" />
            Date livraison souhaitée
          </label>
          <Input
            type="date"
            value={formData.date_livraison_souhaitee}
            onChange={(e) => setFormData({ ...formData, date_livraison_souhaitee: e.target.value })}
          />
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Notes</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="w-full rounded-md border border-gray-300 p-2"
          rows={2}
        />
      </div>

      <div className="flex items-center gap-4 rounded-lg bg-yellow-50 p-3">
        <Lock className="h-5 w-5 text-yellow-600" />
        <div className="flex-1">
          <p className="text-sm font-medium text-yellow-800">Commande verrouillée</p>
          <p className="text-xs text-yellow-600">La commande sera verrouillée jusqu'à validation du paiement</p>
        </div>
        <input
          type="checkbox"
          id="est_verrouille"
          checked={formData.est_verrouille}
          onChange={(e) => setFormData({ ...formData, est_verrouille: e.target.checked })}
          className="h-4 w-4"
        />
      </div>

      <div className="border-t pt-4">
        <h3 className="mb-3 font-semibold">Lignes de commande</h3>
        
        <div className="mb-4 rounded-lg bg-gray-50 p-4">
          <div className="grid grid-cols-5 gap-2">
            <div>
              <label className="mb-1 block text-xs font-medium">Article</label>
              <Select
                value={newLigne.article_id.toString()}
                onValueChange={(value) => setNewLigne({ ...newLigne, article_id: parseInt(value) })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Article" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Riz Bellaluna 25kg</SelectItem>
                  <SelectItem value="2">Riz Bellaluna 50kg</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium">Quantité</label>
              <Input
                type="number"
                step="0.001"
                value={newLigne.quantite_demandee}
                onChange={(e) => setNewLigne({ ...newLigne, quantite_demandee: parseFloat(e.target.value) })}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium">Unité</label>
              <Select
                value={newLigne.unite_mesure}
                onValueChange={(value) => setNewLigne({ ...newLigne, unite_mesure: value as UniteMesure })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={UniteMesure.UDB}>UDB</SelectItem>
                  <SelectItem value={UniteMesure.KG}>KG</SelectItem>
                  <SelectItem value={UniteMesure.TONNE}>Tonne</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium">Prix unitaire</label>
              <Input
                type="number"
                step="0.01"
                value={newLigne.prix_unitaire || ''}
                onChange={(e) => setNewLigne({ ...newLigne, prix_unitaire: e.target.value ? parseFloat(e.target.value) : 0 })}
              />
            </div>
            <div className="flex items-end">
              <Button type="button" onClick={addLigne} className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Ajouter
              </Button>
            </div>
          </div>
        </div>

        {(formData.lignes || []).length > 0 && (
          <div className="space-y-2">
            {(formData.lignes || []).map((ligne, index) => (
              <div key={index} className="flex items-center justify-between rounded border bg-white p-2">
                <div className="text-sm">
                  <span className="font-medium">Article #{ligne.article_id}</span>
                  <span className="mx-2 text-gray-500">|</span>
                  <span>{ligne.quantite_demandee} {ligne.unite_mesure}</span>
                  {ligne.prix_unitaire && (
                    <>
                      <span className="mx-2 text-gray-500">|</span>
                      <span className="text-green-600">{ligne.prix_unitaire.toLocaleString()} FCFA</span>
                    </>
                  )}
                </div>
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  onClick={() => removeLigne(index)}
                >
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Annuler
        </Button>
        <Button type="submit" disabled={(formData.lignes || []).length === 0}>
          Enregistrer
        </Button>
      </div>
    </form>
  )
}

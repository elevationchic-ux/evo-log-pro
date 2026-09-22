'use client'

import React, { useState, useEffect } from 'react'
import { EmptyStates } from '@/components/design-system'
import { Card, CardBody } from '@/components/design-system/Card'
import { Button } from '@/components/design-system'

export default function AnnuairePrestatairesPage() {
  const [prestataires, setPrestataires] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch from API - NO mock fallback
    fetch('/api/v1/prestataires')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success' && data.prestataires) {
          setPrestataires(data.prestataires)
        }
      })
      .catch(err => console.error('Error fetching prestataires:', err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (prestataires.length === 0) {
    return (
      <div className="p-6">
        <Card>
          <CardBody>
            <EmptyStates.NoData
              action={{
                label: 'Ajouter un prestataire',
                onClick: () => {/* Navigate to create page */}
              }}
            />
          </CardBody>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Annuaire des Prestataires</h1>
        <p className="text-gray-600">Gérez vos prestataires et partenaires logistiques</p>
      </div>

      <div className="grid gap-4">
        {prestataires.map((prestataire) => (
          <Card key={prestataire.id} hoverable>
            <CardBody>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-gray-900">{prestataire.nom}</h3>
                  <p className="text-sm text-gray-600">{prestataire.specialite}</p>
                </div>
                <Button variant="secondary" size="sm">Voir détails</Button>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  )
}

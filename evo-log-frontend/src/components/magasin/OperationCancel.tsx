'use client'

import { useState } from 'react'
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/Card'
import { Alert, AlertDescription } from '@/components/ui/alert'

export function OperationCancel() {
  const [numeroOt, setNumeroOt] = useState('')
  const [annulePar, setAnnulePar] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<'success' | 'error' | null>(null)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setMessage('')

    try {
      const response = await fetch('/api/transactions/operations/cancel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          numero_ot: numeroOt,
          annule_par: annulePar,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setResult('success')
        setMessage(`Opération ${numeroOt} annulée avec succès`)
        setNumeroOt('')
      } else {
        setResult('error')
        setMessage(data.detail || 'Erreur lors de l\'annulation')
      }
    } catch (error) {
      setResult('error')
      setMessage('Erreur de connexion au serveur')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Annulation d'Opération</h2>
        <p className="text-gray-600">
          Annulez une opération en saisissant son numéro d'OT (Opération Trace)
        </p>
      </div>

      {result === 'success' && (
        <Alert className="mb-4 bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{message}</AlertDescription>
        </Alert>
      )}

      {result === 'error' && (
        <Alert className="mb-4 bg-red-50 border-red-200">
          <XCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{message}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="numeroOt" className="block text-sm font-medium text-gray-700 mb-2">
            Numéro d'OT
          </label>
          <Input
            id="numeroOt"
            type="text"
            placeholder="Ex: 780494878"
            value={numeroOt}
            onChange={(e) => setNumeroOt(e.target.value)}
            required
            pattern="[0-9]{9}"
            title="Le numéro d'OT doit contenir 9 chiffres"
          />
          <p className="text-xs text-gray-500 mt-1">
            Numéro unique de 9 chiffres généré lors de l'opération
          </p>
        </div>

        <div>
          <label htmlFor="annulePar" className="block text-sm font-medium text-gray-700 mb-2">
            Annulé par
          </label>
          <Input
            id="annulePar"
            type="text"
            placeholder="Votre nom ou identifiant"
            value={annulePar}
            onChange={(e) => setAnnulePar(e.target.value)}
            required
          />
        </div>

        <div className="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-yellow-800">
            <p className="font-semibold mb-1">Attention</p>
            <p>
              L'annulation d'une opération est irréversible. Assurez-vous d'avoir le bon numéro d'OT avant de confirmer.
            </p>
          </div>
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? 'Annulation en cours...' : 'Annuler l\'opération'}
        </Button>
      </form>
    </Card>
  )
}

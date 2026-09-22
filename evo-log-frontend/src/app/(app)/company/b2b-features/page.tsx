'use client'

import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { FileText, Plus, Send, MessageCircle, RefreshCw, CheckCircle } from 'lucide-react'
import apiClient from '../../../../lib/api-client'
import { useAuth } from '../../../../components/layout/AuthProvider'

export default function B2BFeaturesPage() {
  const [mounted, setMounted] = useState(false)
  const [activeTab, setActiveTab] = useState('quotes')
  const [isQuoteModalOpen, setIsQuoteModalOpen] = useState(false)
  const [chatMessage, setChatMessage] = useState('')
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const companyId = user?.companyId ?? null

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: quotes } = useQuery({
    queryKey: ['b2b-quotes', companyId],
    queryFn: async () => {
      if (companyId === null) throw new Error('Aucune société active')
      const res = await apiClient.get(`/api/v1/b2b/portal/${companyId}/quotes`)
      return res.data
    },
    enabled: mounted && activeTab === 'quotes' && companyId !== null,
  })

  const { data: chatMessages } = useQuery({
    queryKey: ['b2b-chat', companyId],
    queryFn: async () => {
      if (companyId === null) throw new Error('Aucune société active')
      const res = await apiClient.get(`/api/v1/b2b/portal/${companyId}/chat`)
      return res.data
    },
    enabled: mounted && activeTab === 'chat' && companyId !== null,
  })

  const createQuoteMutation = useMutation({
    mutationFn: async (data: any) => {
      if (companyId === null) throw new Error('Aucune société active')
      const res = await apiClient.post(`/api/v1/b2b/portal/${companyId}/quotes`, data)
      return res.data
    },
    onSuccess: () => {
      console.log('Devis créé avec succès')
      queryClient.invalidateQueries({ queryKey: ['b2b-quotes', companyId] })
      setIsQuoteModalOpen(false)
    },
    onError: () => {
      console.log('Erreur lors de la création du devis')
    },
  })

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (companyId === null) throw new Error('Aucune société active')
      const res = await apiClient.post(`/api/v1/b2b/portal/${companyId}/chat`, { content: message })
      return res.data
    },
    onSuccess: () => {
      setChatMessage('')
      queryClient.invalidateQueries({ queryKey: ['b2b-chat', companyId] })
    },
  })

  const handleCreateQuote = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const payload = {
      reference: formData.get('reference'),
      client_nom: formData.get('client_nom'),
      origine: formData.get('origine'),
      destination: formData.get('destination'),
      nature_fret: formData.get('nature_fret'),
      montant_estime_xaf: parseFloat(formData.get('montant_estime_xaf') as string),
    }
    createQuoteMutation.mutate(payload)
  }

  const handleSendMessage = () => {
    if (chatMessage.trim()) {
      sendMessageMutation.mutate(chatMessage)
    }
  }

  if (!mounted) return null

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Fonctionnalités B2B</h1>
          <p className="text-gray-600 mt-1">Devis, chat support et API</p>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab('quotes')}
          className={`px-4 py-2 rounded-lg ${activeTab === 'quotes' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          <FileText className="w-4 h-4 inline mr-2" />
          Devis
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`px-4 py-2 rounded-lg ${activeTab === 'chat' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          <MessageCircle className="w-4 h-4 inline mr-2" />
          Chat Support
        </button>
      </div>

      {activeTab === 'quotes' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Devis</h2>
            <button
              onClick={() => setIsQuoteModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              Nouveau Devis
            </button>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 divide-y divide-gray-200">
            {quotes?.map((quote: any) => (
              <div key={quote.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{quote.reference}</h3>
                    <p className="text-sm text-gray-600">{quote.client_nom}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{Number(quote.montant_estime_xaf).toLocaleString('fr-FR')} FCFA</p>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      quote.statut === 'accepte' ? 'bg-green-100 text-green-700' :
                      quote.statut === 'refuse' ? 'bg-red-100 text-red-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {quote.statut}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'chat' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Chat Support</h2>
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
              <RefreshCw className="w-4 h-4" />
              Actualiser
            </button>
          </div>
          <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
            {chatMessages?.map((msg: any) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-md p-3 rounded-lg ${
                    msg.sender_id === user?.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                  <p className="text-xs mt-1 opacity-70">{new Date(msg.created_at).toLocaleString('fr-FR')}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Écrivez votre message..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSendMessage}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {isQuoteModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Nouveau Devis</h2>
              <button onClick={() => setIsQuoteModalOpen(false)} className="text-gray-400 hover:text-gray-600">
                <CheckCircle className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={handleCreateQuote} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Numéro</label>
                <input
                  name="reference"
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="DEV-2026-004"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client</label>
                <input
                  name="client_nom"
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Nom du client"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Origine</label>
                <input
                  name="origine"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Douala"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Destination</label>
                <input
                  name="destination"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Yaoundé"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nature du fret</label>
                <input
                  name="nature_fret"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Conteneur"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Montant estimé (FCFA)</label>
                <input
                  name="montant_estime_xaf"
                  type="number"
                  min="0"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="1500000"
                />
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setIsQuoteModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Créer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

'use client'

import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { FileText, Plus, Send, MessageCircle, RefreshCw, CheckCircle } from 'lucide-react'

const b2bAPI = {
  getQuotes: async (companyId: number) => {
    return {
      data: [
        { id: 1, numero: 'DEV-2026-001', client: 'Société Alpha', montant: 2500000, statut: 'en_attente', date_validite: '2026-02-28' },
        { id: 2, numero: 'DEV-2026-002', client: 'Beta Logistics', montant: 1800000, statut: 'accepte', date_validite: '2026-02-15' },
        { id: 3, numero: 'DEV-2026-003', client: 'Gamma SA', montant: 5200000, statut: 'refuse', date_validite: '2026-03-01' }
      ]
    }
  },
  createQuote: async (companyId: number, data: any) => {
    return { data: { ...data, id: Date.now() } }
  },
  getChatMessages: async (companyId: number) => {
    return {
      data: [
        { id: 1, message: 'Bonjour, je voudrais des informations sur le transport Douala-Yaoundé', expediteur: 'client', date: '2026-01-18 10:30' },
        { id: 2, message: 'Bonjour, le prix est de 150000 FCFA pour le trajet standard', expediteur: 'support', date: '2026-01-18 10:35' },
        { id: 3, message: 'Est-ce que le camion est disponible demain ?', expediteur: 'client', date: '2026-01-18 10:40' }
      ]
    }
  },
  sendMessage: async (companyId: number, message: string) => {
    return { data: { success: true } }
  }
}

export default function B2BFeaturesPage() {
  const [mounted, setMounted] = useState(false)
  const [activeTab, setActiveTab] = useState('quotes')
  const [isQuoteModalOpen, setIsQuoteModalOpen] = useState(false)
  const [chatMessage, setChatMessage] = useState('')
  const queryClient = useQueryClient()

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: quotes } = useQuery({
    queryKey: ['b2b-quotes', 1],
    queryFn: async () => {
      const res = await b2bAPI.getQuotes(1)
      return res.data || []
    },
    enabled: mounted && activeTab === 'quotes',
  })

  const { data: chatMessages } = useQuery({
    queryKey: ['b2b-chat', 1],
    queryFn: async () => {
      const res = await b2bAPI.getChatMessages(1)
      return res.data || []
    },
    enabled: mounted && activeTab === 'chat',
  })

  const createQuoteMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await b2bAPI.createQuote(1, data)
      return res.data
    },
    onSuccess: () => {
      console.log('Devis créé avec succès')
      queryClient.invalidateQueries({ queryKey: ['b2b-quotes'] })
      setIsQuoteModalOpen(false)
    },
    onError: () => {
      console.log('Erreur lors de la création du devis')
    },
  })

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      const res = await b2bAPI.sendMessage(1, message)
      return res.data
    },
    onSuccess: () => {
      setChatMessage('')
      queryClient.invalidateQueries({ queryKey: ['b2b-chat'] })
    },
  })

  const handleCreateQuote = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const payload = {
      numero: formData.get('numero'),
      client: formData.get('client'),
      montant: parseFloat(formData.get('montant') as string),
      date_validite: formData.get('date_validite')
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
                    <h3 className="font-semibold text-gray-900">{quote.numero}</h3>
                    <p className="text-sm text-gray-600">{quote.client}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{quote.montant.toLocaleString('fr-FR')} FCFA</p>
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
                className={`flex ${msg.expediteur === 'client' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-md p-3 rounded-lg ${
                    msg.expediteur === 'client' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{msg.message}</p>
                  <p className="text-xs mt-1 opacity-70">{msg.date}</p>
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
                  name="numero"
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="DEV-2026-004"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client</label>
                <input
                  name="client"
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Nom du client"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Montant (FCFA)</label>
                <input
                  name="montant"
                  type="number"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="1500000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date de Validité</label>
                <input
                  name="date_validite"
                  type="date"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
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

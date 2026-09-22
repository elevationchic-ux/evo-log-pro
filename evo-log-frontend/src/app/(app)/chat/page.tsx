'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardBody, CardHeader } from '@/components/design-system/Card'
import { Button } from '@/components/design-system'
import { Input } from '@/components/design-system/Input'
import { EmptyStates } from '@/components/design-system'

interface Message {
  id: string
  user_id: string
  user_nom: string
  message: string
  type: string
  timestamp: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [isConnected, setIsConnected] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Fetch message history from API
    fetch('/api/v1/collaboration/rooms/general/messages')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success' && data.messages) {
          setMessages(data.messages)
        }
        setIsConnected(true)
      })
      .catch(err => {
        console.error('Error fetching messages:', err)
        setIsConnected(false)
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return

    try {
      const response = await fetch('/api/v1/collaboration/rooms/general/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_id: 'general',
          user_id: 'current_user',
          user_nom: 'Utilisateur',
          message: newMessage,
          type: 'TEXT'
        })
      })

      if (response.ok) {
        setNewMessage('')
      }
    } catch (err) {
      console.error('Error sending message:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isConnected) {
    return (
      <div className="p-6">
        <Card>
          <CardBody>
            <EmptyStates.NoConnection />
          </CardBody>
        </Card>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      <Card className="flex-1 flex flex-col m-4">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold">Chat Collaboration</h2>
              <p className="text-sm text-gray-600">Communication en temps réel avec votre équipe</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Connecté
              </span>
            </div>
          </div>
        </CardHeader>

        <CardBody className="flex-1 flex flex-col overflow-hidden">
          {/* Messages List */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 ? (
              <EmptyStates.NoData
                description="Soyez le premier à envoyer un message dans cette conversation."
              />
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.user_id === 'current_user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.user_id === 'current_user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="text-xs font-medium mb-1">{msg.user_nom}</div>
                    <div className="text-sm">{msg.message}</div>
                    <div className="text-xs opacity-70 mt-1">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="flex gap-2">
            <Input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Tapez votre message..."
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <Button onClick={handleSendMessage}>Envoyer</Button>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

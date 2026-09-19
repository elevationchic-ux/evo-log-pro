'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { MessageSquare, Bot, User, Send, Smartphone, RefreshCw, CarFront, PackageCheck, Fuel } from 'lucide-react';
import { toast } from 'sonner';

export default function ChatOpsDashboard() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [testMessage, setTestMessage] = useState('');
  const [testSender, setTestSender] = useState('+237690000000');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/webhooks/chatops/logs`);
      const data = await res.json();
      setLogs(data.logs || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 3000); // Polling every 3s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [logs]);

  const sendTestMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testMessage.trim()) return;
    
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/webhooks/whatsapp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: testMessage, sender: testSender })
      });
      setTestMessage('');
      toast.success("Message envoyé à K-Bot !");
      setTimeout(fetchLogs, 500); // Quick refresh after sending
    } catch (err) {
      toast.error("Erreur lors de l'envoi");
    }
  };

  const ActionIcon = ({ action }: { action: string }) => {
    switch(action) {
      case 'SIGNALEMENT_PANNE': return <CarFront className="w-4 h-4 text-rose-500" />;
      case 'VALIDATION_LIVRAISON': return <PackageCheck className="w-4 h-4 text-emerald-500" />;
      case 'DEMANDE_CARBURANT': return <Fuel className="w-4 h-4 text-amber-500" />;
      default: return null;
    }
  };

  return (
    <ModuleLayout module="transport">
      <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-6 gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-slate-100 flex items-center gap-3">
              <MessageSquare className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              ChatOps & K-Bot Live
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">Supervisez en temps réel les interactions WhatsApp entre les chauffeurs et l'IA K-Bot.</p>
          </div>
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40 px-4 py-2 rounded-xl">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            K-Bot Actif & Connecté
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[650px] min-h-[600px]">
          
          {/* Chat Simulator Panel */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col">
            <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
              <Smartphone className="w-5 h-5 text-blue-500" />
              Simulateur Chauffeur
            </h2>
            
            <form onSubmit={sendTestMessage} className="flex flex-col gap-4 flex-1">
              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1 uppercase">Numéro (Sender)</label>
                <input 
                  type="text" 
                  value={testSender}
                  onChange={e => setTestSender(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm text-slate-900 dark:text-slate-100 outline-none focus:border-blue-500"
                />
              </div>
              
              <div className="flex-1 flex flex-col">
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1 uppercase">Message WhatsApp</label>
                <textarea 
                  value={testMessage}
                  onChange={e => setTestMessage(e.target.value)}
                  placeholder="Ex: Je suis en panne avec le camion LT-1234..."
                  className="w-full flex-1 px-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm text-slate-900 dark:text-slate-100 outline-none focus:border-blue-500 resize-none"
                />
              </div>

              <div className="pt-2">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">Exemples supportés par le bot :</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  <button type="button" onClick={() => setTestMessage("Mission TRN-001 bien livrée à destination")} className="text-[10px] bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-slate-700 dark:text-slate-300 hover:bg-slate-200">Livraison</button>
                  <button type="button" onClick={() => setTestMessage("Grosse panne moteur sur le LT-9999")} className="text-[10px] bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-slate-700 dark:text-slate-300 hover:bg-slate-200">Panne</button>
                  <button type="button" onClick={() => setTestMessage("Besoin de carburant pour le trajet")} className="text-[10px] bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-slate-700 dark:text-slate-300 hover:bg-slate-200">Carburant</button>
                </div>
                <button type="submit" disabled={!testMessage} className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold py-3 rounded-xl flex justify-center items-center gap-2 transition-all shadow-md cursor-pointer">
                  <Send className="w-4 h-4" /> Envoyer à K-Bot
                </button>
              </div>
            </form>
          </div>

          {/* Chat Logs Panel */}
          <div className="lg:col-span-2 bg-slate-900 rounded-3xl p-3 shadow-xl border border-slate-800 flex flex-col relative overflow-hidden h-full">
            {/* Top Bar */}
            <div className="bg-slate-800/80 backdrop-blur-md rounded-2xl p-4 flex justify-between items-center mb-2 z-10 border border-slate-700">
              <div className="flex items-center gap-3 text-white">
                <Bot className="w-6 h-6 text-blue-400" />
                <div>
                  <h3 className="font-bold text-sm">Monitoring WhatsApp Global</h3>
                  <p className="text-[10px] text-slate-400">Canal: Tous les chauffeurs</p>
                </div>
              </div>
              <button onClick={fetchLogs} className="text-slate-400 hover:text-white transition-colors cursor-pointer">
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {/* Messages Area */}
            <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 z-10">
              {logs.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4">
                  <MessageSquare className="w-12 h-12 opacity-20" />
                  <p className="text-sm">En attente de messages entrants...</p>
                </div>
              ) : (
                logs.map((log) => (
                  <div key={log.id} className={`flex w-full ${log.is_bot ? 'justify-start' : 'justify-end'}`}>
                    <div className={`max-w-[75%] rounded-2xl p-4 shadow-sm ${
                      log.is_bot ? 'bg-slate-800 border border-slate-700 text-slate-100 rounded-tl-none' 
                                 : 'bg-blue-600 text-white rounded-tr-none'
                    }`}>
                      <div className="flex justify-between items-center mb-2 gap-4">
                        <span className="text-xs font-black opacity-60 flex items-center gap-1">
                          {log.is_bot ? <Bot className="w-3 h-3" /> : <User className="w-3 h-3" />}
                          {log.sender}
                        </span>
                        <span className="text-[10px] opacity-40">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{log.message}</p>
                      
                      {log.action_detected && log.action_detected !== 'INCONNU' && (
                        <div className="mt-3 pt-2 border-t border-white/10 flex items-center gap-2 text-xs font-bold">
                          <ActionIcon action={log.action_detected} />
                          <span className="opacity-80">Action déclenchée : {log.action_detected.replace('_', ' ')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      </div>
    </ModuleLayout>
  );
}

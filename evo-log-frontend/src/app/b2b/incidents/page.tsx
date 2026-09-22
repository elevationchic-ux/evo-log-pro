'use client';

import React, { useState } from 'react';
import {
  AlertTriangle, Camera, CheckCircle2, Clock, ChevronDown,
  FileText, ImagePlus, Send, MessageSquare, Shield, Phone
} from 'lucide-react';
import { toast } from 'sonner';
import { supportAPI } from '@/lib/api-client';

export default function B2BIncidentsPage() {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    type: 'AVARIE', operationRef: '', description: '', photos: []
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const incidents: Array<{
    id: string; type: string; ref: string; subject: string; date: string;
    status: string; statusColor: string; priority: string; priorityColor: string;
    timeline: Array<{ date: string; label: string; done: boolean }>;
    messages: Array<{ from: string; time: string; body: string }>;
  }> = [];

  const incidentTypes = [
    { value: 'AVARIE', label: 'Avarie / Dommage Marchandise' },
    { value: 'RETARD', label: 'Retard de Livraison Constaté' },
    { value: 'MANQUANT', label: 'Manquant / Colis Non Livré' },
    { value: 'VOL', label: 'Vol ou Disparition Partielle' },
    { value: 'ERREUR_DOC', label: 'Erreur Documentaire (DUM, B/L)' },
    { value: 'LITIGE_TAXI', label: 'Litige Tarification / Débours Contesté' },
    { value: 'AUTRE', label: 'Autre Incident' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await supportAPI.createTicket({
        category: form.type,
        subject: form.operationRef,
        description: form.description,
      });
      setIsSubmitting(false);
      setShowForm(false);
      toast.success('Déclaration d’incident enregistrée.');
    } catch {
      toast.error('Impossible d’enregistrer l’incident auprès du service support.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <Shield className="w-6 h-6 text-amber-400" /> Incidents & Réclamations
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Déclarez un incident (avarie, retard, manquant), suivez votre dossier en temps réel et échangez avec votre gestionnaire
            </p>
          </div>
          {incidents.length === 0 && (
            <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-5 text-sm text-amber-200">
              Aucun incident persisté n’est disponible pour cette société. Les exemples de démonstration ont été supprimés.
            </div>
          )}
          <button
            onClick={() => setShowForm(true)}
            className="px-5 py-3 bg-gradient-to-r from-red-600 to-rose-500 text-white font-black text-sm rounded-xl flex items-center gap-2 shadow-lg shadow-red-500/20 transition-all hover:from-red-500 hover:to-rose-400"
          >
            <AlertTriangle className="w-4 h-4" /> Déclarer un Incident
          </button>
        </div>

        {/* Emergency hotline */}
        <div className="mt-4 p-3 bg-blue-500/5 border border-blue-500/20 rounded-xl flex items-center gap-3">
          <Phone className="w-4 h-4 text-blue-400 shrink-0" />
          <div className="text-xs text-slate-300">
            <strong className="text-blue-400">Urgence 24h/24 :</strong> +237 699 000 000 (Hotline CADC Logistique)  Pour les avaries majeures, contactez-nous immédiatement
          </div>
        </div>
      </div>

      {/* Incident Declaration Form Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200">
            <h2 className="text-xl font-black text-white mb-1">Déclaration d'Incident Logistique</h2>
            <p className="text-xs text-slate-400 mb-5">Renseignez les informations ci-dessous. Notre équipe sera notifiée immédiatement.</p>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Type d'Incident</label>
                <select
                  value={form.type}
                  onChange={e => setForm(f => ({ ...f, type: e.target.value }))}
                  className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                >
                  {incidentTypes.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Référence Opération / Conteneur / Facture</label>
                <input
                  type="text"
                  value={form.operationRef}
                  onChange={e => setForm(f => ({ ...f, operationRef: e.target.value }))}
                  placeholder="Référence de l’opération concernée"
                  className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Description Précise de l'Incident</label>
                <textarea
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  placeholder="Décrivez précisément les faits constatés : date, lieu, nature des dommages, quantités affectées, circonstances..."
                  rows={5}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 resize-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Photos / Preuves Visuelles</label>
                <div
                  className="border-2 border-dashed border-slate-700 rounded-2xl p-8 text-center cursor-pointer hover:border-amber-500/50 transition-colors"
                  onClick={() => toast.info('Sélection de fichiers photos disponible en version mobile (appareil photo direct)')}
                >
                  <ImagePlus className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                  <p className="text-xs text-slate-400">Cliquez pour ajouter des photos (JPG, PNG, max 10 Mo/fichier)</p>
                  <p className="text-[11px] text-slate-500 mt-1">Recommandé: photos du conteneur, des colis, du dommage visible, de la plaque de réserves</p>
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="flex-1 py-3 bg-slate-800 text-slate-300 font-bold text-sm rounded-xl border border-slate-700">
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 py-3 bg-gradient-to-r from-red-600 to-rose-500 text-white font-black text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg disabled:opacity-60"
                >
                  <Send className="w-4 h-4" /> {isSubmitting ? 'Envoi en cours...' : 'Soumettre la Déclaration'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Existing Incidents */}
      {incidents.map(inc => (
        <div key={inc.id} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-lg space-y-5">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="font-mono font-black text-sm text-white">{inc.id}</span>
                <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${inc.statusColor}`}>
                  {inc.status.replace('_', ' ')}
                </span>
                <span className={`text-[11px] font-bold ${inc.priorityColor}`}>● Priorité {inc.priority}</span>
              </div>
              <div className="text-sm font-bold text-white">{inc.subject}</div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">{inc.ref} • Déclaré le {inc.date}</div>
            </div>
          </div>

          {/* Timeline */}
          <div>
            <div className="text-xs font-bold text-slate-300 uppercase mb-3">Suivi d'Instruction du Dossier</div>
            <div className="space-y-2">
              {inc.timeline.map((step, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 text-[10px] ${step.done ? 'bg-emerald-500 text-white' : 'bg-slate-800 border border-slate-700 text-slate-500'}`}>
                    {step.done ? '✓' : (i + 1)}
                  </div>
                  <div className="flex-1">
                    <span className="text-xs text-slate-300 font-medium">{step.label}</span>
                    <span className="text-[11px] text-slate-500 ml-2 font-mono">{step.date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Messages */}
          <div>
            <div className="text-xs font-bold text-slate-300 uppercase mb-3 flex items-center gap-2">
              <MessageSquare className="w-3.5 h-3.5" /> Échanges avec votre Gestionnaire
            </div>
            {inc.messages.map((msg, i) => (
              <div key={i} className="bg-slate-950 border border-slate-800 rounded-2xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 rounded-full bg-amber-500/20 flex items-center justify-center text-[10px] text-amber-400 font-bold">CA</div>
                  <span className="text-xs font-bold text-slate-300">{msg.from}</span>
                  <span className="text-[10px] text-slate-500 font-mono ml-auto">{msg.time}</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{msg.body}</p>
              </div>
            ))}

            <div className="mt-3 flex gap-2">
              <input
                type="text"
                placeholder="Répondre à votre gestionnaire de compte..."
                className="flex-1 h-10 px-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
              <button
                onClick={() => toast.success('Message envoyé à votre gestionnaire')}
                className="px-4 py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-xl border border-amber-500/30 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ))}

      {incidents.length === 0 && (
        <div className="text-center py-20 text-slate-500">
          <Shield className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="text-sm">Aucun incident déclaré  Vos opérations se déroulent normalement</p>
        </div>
      )}
    </div>
  );
}

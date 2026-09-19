'use client';

import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { trackingAPI } from '@/lib/api-client';
import { FileCheck, ArrowLeft, Send, DollarSign, CheckCircle2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import Link from 'next/link';

export default function EPodCapturePage() {
  const queryClient = useQueryClient();
  const [missionRef, setMissionRef] = useState('');
  const [destinataire, setDestinataire] = useState('');
  const [clientNom, setClientNom] = useState('');
  const [montantFret, setMontantFret] = useState('');
  const [invoiceResult, setInvoiceResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setInvoiceResult(null);

    try {
      const response = await trackingAPI.createEpod({
        reference_mission: missionRef,
        nom_destinataire: destinataire,
      });
      const data = response.data;
      setInvoiceResult(data.facture_generee);
      toast.success('e-POD enregistré.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Impossible d’enregistrer l’e-POD.');
      return;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8 px-4 text-foreground animate-in fade-in duration-500">
      <Link href="/tracking" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="w-4 h-4" /> Retour au tracking
      </Link>

      <div className="bg-card border border-border rounded-3xl p-8 shadow-2xl">
        <div className="flex items-center gap-3 pb-6 border-b border-border mb-6">
          <div className="w-12 h-12 bg-cyan-500/10 text-cyan-400 rounded-2xl flex items-center justify-center border border-cyan-500/20">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-foreground">Numérisation e-POD & Facturation Auto</h1>
            <p className="text-sm text-muted-foreground">Signature chauffeur & création automatique du projet de facture K-Finance.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-muted-foreground uppercase mb-2">N° Ordre de Transport (OT / Mission)</label>
            <input
              type="text"
              value={missionRef}
              onChange={(e) => setMissionRef(e.target.value)}
              className="w-full bg-background border border-border rounded-2xl p-4 text-sm text-foreground focus:ring-2 focus:ring-cyan-500 font-mono font-bold"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-muted-foreground uppercase mb-2">Client Facturé</label>
              <input
                type="text"
                value={clientNom}
                onChange={(e) => setClientNom(e.target.value)}
                className="w-full bg-background border border-border rounded-2xl p-4 text-sm text-foreground focus:ring-2 focus:ring-cyan-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-muted-foreground uppercase mb-2">Montant Fret HT (XAF)</label>
              <input
                type="number"
                value={montantFret}
                onChange={(e) => setMontantFret(e.target.value)}
                className="w-full bg-background border border-border rounded-2xl p-4 text-sm text-foreground focus:ring-2 focus:ring-cyan-500 font-bold"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-muted-foreground uppercase mb-2">Nom du Réceptionnaire / Destinataire</label>
            <input
              type="text"
              value={destinataire}
              onChange={(e) => setDestinataire(e.target.value)}
              className="w-full bg-background border border-border rounded-2xl p-4 text-sm text-foreground focus:ring-2 focus:ring-cyan-500"
              required
            />
          </div>

          {/* Canvas de Signature Numérique */}
          <div>
            <label className="block text-xs font-bold text-muted-foreground uppercase mb-2">Signature Électronique du Destinataire</label>
            <div className="border border-dashed border-cyan-500/40 rounded-2xl p-6 bg-cyan-500/5 text-center cursor-pointer hover:bg-cyan-500/10 transition-all">
              <p className="text-xs text-cyan-400 font-mono font-bold">✓ Zone de signature tactile / stylet active</p>
              <p className="text-xs text-muted-foreground mt-1">La signature et la géolocalisation doivent être fournies par le dispositif de capture.</p>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 rounded-2xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold transition-all shadow-lg shadow-cyan-600/20 flex items-center justify-center gap-2 mt-4"
          >
            {loading ? <span className="animate-spin">⏳</span> : <Send className="w-5 h-5" />}
            Valider e-POD & Générer Facture K-Finance
          </button>
        </form>

        {/* Alerte Facture Générée */}
        {invoiceResult && (
          <div className="mt-6 p-5 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 space-y-2 animate-in slide-in-from-bottom duration-300">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
              <CheckCircle2 size={18} />
              Automation Active : Facture Créée dans K-Finance
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-foreground font-mono mt-2">
              <div>Facture N° : <span className="font-bold text-emerald-400">{invoiceResult.numero_facture}</span></div>
              <div>Montant HT : {new Intl.NumberFormat('fr-FR').format(invoiceResult.montant_ht_xaf)} XAF</div>
              <div>TVA (19.25%) : {new Intl.NumberFormat('fr-FR').format(invoiceResult.tva_xaf)} XAF</div>
              <div>Montant TTC : <span className="font-bold text-emerald-400">{new Intl.NumberFormat('fr-FR').format(invoiceResult.montant_ttc_xaf)} XAF</span></div>
            </div>
            <div className="pt-2">
              <Link href="/finance/factures" className="text-xs text-emerald-400 hover:underline flex items-center gap-1">
                <DollarSign size={12} /> Voir dans K-Finance →
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

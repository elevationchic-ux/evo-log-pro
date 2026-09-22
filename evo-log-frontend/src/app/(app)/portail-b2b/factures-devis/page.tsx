'use client';

import React, { useEffect, useState } from 'react';
import { FileText, Download, CheckCircle2, Clock, CreditCard, Smartphone, ShieldCheck, X, ArrowRight } from 'lucide-react';
import { b2bPortalAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function PortailB2BFacturesPage() {
  const [loading, setLoading] = useState(true);
  const [factures, setFactures] = useState<any[]>([]);
  const [selectedFacture, setSelectedFacture] = useState<any | null>(null);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [paymentMode, setPaymentMode] = useState<'MOMO_MTN' | 'MOMO_ORANGE' | 'CB_VISA' | 'CB_MASTERCARD'>('MOMO_MTN');
  const [telephone, setTelephone] = useState('+237 6 70 00 12 34');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    loadFactures();
  }, []);

  const loadFactures = async () => {
    setLoading(true);
    try {
      const res = await b2bPortalAPI.getFactures(1);
      const data = res.data || (Array.isArray(res) ? res : []);
      setFactures(data);
    } catch (err) {
      console.error('Erreur chargement factures', err);
      toast.error('Erreur de chargement des factures');
    } finally {
      setLoading(false);
    }
  };

  const totalTTC = factures.reduce((s, f) => s + (f.montant_ttc || 0), 0);
  const enAttente = factures.filter(f => f.statut === 'EN_ATTENTE').reduce((s, f) => s + (f.montant_ttc || 0), 0);
  const totalTVA = factures.reduce((s, f) => s + (f.tva_19_25_pct || f.tva || 0), 0);

  const handleOpenPayment = (facture: any) => {
    setSelectedFacture(facture);
    setPaymentModalOpen(true);
  };

  const handlePayCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFacture) return;
    setIsProcessing(true);
    try {
      const res = await b2bPortalAPI.processPayment({
        facture_id: selectedFacture.id,
        mode_paiement: paymentMode,
        montant_xaf: selectedFacture.montant_ttc,
        telephone: telephone
      });
      const data = res.data || res;
      toast.success(data.message || 'Paiement en ligne validé avec succès ! Bon de Sortie débloqué.');
      setPaymentModalOpen(false);

      // Local state update
      setFactures(prev => prev.map(f => f.id === selectedFacture.id ? { ...f, statut: 'PAYEE', reference_paiement: data.transaction_id } : f));
    } catch (err) {
      toast.error('Erreur lors du traitement du paiement en ligne.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
            Portail Client • Facturation & Règlements
          </span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
            T-Code : KB2B_FCT
          </span>
        </div>
        <h1 className="text-2xl font-black text-slate-100 flex items-center gap-3">
          <FileText className="w-7 h-7 text-violet-400" /> Factures & Règlements en Ligne
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Réglez directement vos débours et factures de transit via MTN MoMo, Orange Money ou Carte Bancaire pour libérer instantanément vos bons de sortie.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'Total Facturé TTC (2026)', value: `${(totalTTC / 1000000).toFixed(2)} M XAF`, color: 'text-violet-400' },
          { label: 'En attente de règlement', value: `${(enAttente / 1000000).toFixed(2)} M XAF`, color: 'text-amber-400' },
          { label: 'TVA 19.25% Déductible', value: `${(totalTVA / 1000000).toFixed(2)} M XAF`, color: 'text-blue-400' },
        ].map((k, i) => (
          <div key={i} className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">{k.label}</div>
            <div className={`text-xl font-black font-mono ${k.color}`}>{k.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">N° Facture</th>
                <th className="py-3.5 px-4">Prestation</th>
                <th className="py-3.5 px-4 text-right">HT (XAF)</th>
                <th className="py-3.5 px-4 text-right">TVA 19.25%</th>
                <th className="py-3.5 px-4 text-right">TTC (XAF)</th>
                <th className="py-3.5 px-4">Échéance</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-center">Paiement / PDF</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-500 font-sans">
                    Chargement des factures en direct...
                  </td>
                </tr>
              ) : factures.map((f) => (
                <tr key={f.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-violet-400">{f.id}</div>
                    <div className="text-[11px] text-slate-500">{f.dossier}</div>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300 max-w-[200px]">{f.desc}</td>
                  <td className="py-3.5 px-4 text-right">{f.montant_ht.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right text-blue-400">{(f.tva_19_25_pct || f.tva || 0).toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-slate-100">{f.montant_ttc.toLocaleString()}</td>
                  <td className="py-3.5 px-4 text-slate-400">{f.echeance}</td>
                  <td className="py-3.5 px-4 text-center">
                    {f.statut === 'PAYEE' ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit mx-auto">
                        <CheckCircle2 className="w-3 h-3" /> PAYÉE
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1 w-fit mx-auto animate-pulse">
                        <Clock className="w-3 h-3" /> EN ATTENTE
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <div className="flex items-center justify-center gap-2">
                      {f.statut === 'EN_ATTENTE' ? (
                        <button
                          onClick={() => handleOpenPayment(f)}
                          className="px-2.5 py-1 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-[11px] font-sans font-bold flex items-center gap-1.5 shadow-md shadow-violet-600/20 transition-all cursor-pointer"
                        >
                          <CreditCard className="w-3.5 h-3.5" /> Payer
                        </button>
                      ) : (
                        <button
                          onClick={() => toast.error("Le téléchargement des quittances n'est pas encore raccordé à l'API.")}
                          className="p-1.5 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                          title="Télécharger la facture"
                        >
                          <Download className="w-4 h-4 text-slate-400 hover:text-violet-400" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Paiement Sécurisé */}
      {paymentModalOpen && selectedFacture && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-violet-500/40 rounded-3xl w-full max-w-md p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold">Paiement Sécurisé en Ligne</h3>
              </div>
              <button onClick={() => setPaymentModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4 space-y-3">
              <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800">
                <div className="text-xs text-slate-400">Facture à régler :</div>
                <div className="font-mono text-sm font-bold text-violet-400">{selectedFacture.id} ({selectedFacture.desc})</div>
                <div className="text-2xl font-black font-mono text-emerald-400 mt-1">
                  {selectedFacture.montant_ttc.toLocaleString()} XAF
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-2">Choisir le mode de paiement :</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'MOMO_MTN', label: 'MTN Mobile Money', icon: Smartphone, bg: 'hover:border-yellow-400/50' },
                    { id: 'MOMO_ORANGE', label: 'Orange Money CM', icon: Smartphone, bg: 'hover:border-orange-400/50' },
                    { id: 'CB_VISA', label: 'Carte Visa', icon: CreditCard, bg: 'hover:border-blue-400/50' },
                    { id: 'CB_MASTERCARD', label: 'Mastercard', icon: CreditCard, bg: 'hover:border-red-400/50' },
                  ].map((mode) => (
                    <button
                      key={mode.id}
                      type="button"
                      onClick={() => setPaymentMode(mode.id as any)}
                      className={`p-3 rounded-xl border text-left flex items-center gap-2.5 text-xs font-bold transition-all ${
                        paymentMode === mode.id
                          ? 'border-violet-500 bg-violet-500/20 text-white'
                          : `border-slate-800 bg-slate-950/60 text-slate-400 ${mode.bg}`
                      }`}
                    >
                      <mode.icon className="w-4 h-4 text-violet-400" />
                      <span>{mode.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {paymentMode.startsWith('MOMO') && (
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Numéro Téléphone Cameroun :</label>
                  <input
                    type="text"
                    value={telephone}
                    onChange={(e) => setTelephone(e.target.value)}
                    placeholder="+237 6 XX XX XX XX"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm font-mono text-slate-100 focus:outline-none focus:border-violet-500"
                  />
                  <p className="text-[11px] text-slate-500 mt-1">Un prompt USSD de confirmation sera envoyé sur votre téléphone.</p>
                </div>
              )}

              {paymentMode.startsWith('CB') && (
                <div className="space-y-2">
                  <input
                    type="text"
                    placeholder="Numéro de carte (16 chiffres)"
                    defaultValue="4500 •••• •••• 9842"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm font-mono text-slate-100 focus:outline-none focus:border-violet-500"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="MM/AA"
                      defaultValue="08/28"
                      className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm font-mono text-slate-100 focus:outline-none focus:border-violet-500"
                    />
                    <input
                      type="password"
                      placeholder="CVV"
                      defaultValue="•••"
                      className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm font-mono text-slate-100 focus:outline-none focus:border-violet-500"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setPaymentModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 cursor-pointer"
              >
                Annuler
              </button>
              <button
                type="button"
                onClick={handlePayCheckout}
                disabled={isProcessing}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-600/30 flex items-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {isProcessing ? 'Validation...' : 'Valider & Débloquer Bon de Sortie'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

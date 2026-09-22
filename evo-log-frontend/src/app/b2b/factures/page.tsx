'use client';

import React, { useState } from 'react';
import {
  CreditCard, Download, CheckCircle2, Clock, AlertTriangle,
  Smartphone, Building2, ArrowRight, Receipt, ChevronRight, Info, DollarSign
} from 'lucide-react';
import { toast } from 'sonner';
import { b2bPortalAPI } from '@/lib/api-client';

interface InvoiceEntry {
  id: string;
  description: string;
  date: string;
  dueDate: string;
  amount: number;
  currency: string;
  status: string;
  items: Array<{ label: string; amount: number }>;
}

export default function B2BFacturesPage() {
  const [paymentModal, setPaymentModal] = useState<InvoiceEntry | null>(null);
  const [paymentMethod, setPaymentMethod] = useState('MTN_MOMO');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isPaying, setIsPaying] = useState(false);

  const invoices: InvoiceEntry[] = [];

  const paymentMethods = [
    { id: 'MTN_MOMO', label: 'MTN Mobile Money', icon: '📱', color: 'text-yellow-400', desc: 'Paiement instantané via votre compte MTN MOMO Cameroun' },
    { id: 'ORANGE_MONEY', label: 'Orange Money', icon: '🟠', color: 'text-orange-400', desc: 'Paiement sécurisé via votre compte Orange Money' },
    { id: 'VIREMENT_SGBC', label: 'Virement Bancaire (SGBC / SCB / BICEC)', icon: '🏦', color: 'text-blue-400', desc: 'Virement SEPA ou local vers notre compte domicilié' },
  ];

  const totalDue = invoices.filter(i => i.status === 'EN_ATTENTE').reduce((s, i) => s + i.amount, 0);

  const handlePay = async () => {
    if (!paymentModal) return;
    setIsPaying(true);
    try {
      await b2bPortalAPI.processPayment({ invoice_id: paymentModal.id, method: paymentMethod, phone: phoneNumber });
      setPaymentModal(null);
      toast.success('Paiement transmis au fournisseur configuré.');
    } catch {
      toast.error('Paiement indisponible : aucun fournisseur réel n’est configuré.');
    } finally {
      setIsPaying(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <CreditCard className="w-6 h-6 text-amber-400" /> Factures & Paiements
            </h1>
            <p className="text-xs text-slate-400 mt-1">Règlement sécurisé via Mobile Money ou Virement Bancaire CEMAC</p>
          </div>
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 text-right">
            <div className="text-xs font-mono text-slate-400">Total en attente de paiement</div>
            <div className="text-2xl font-black text-amber-300 font-mono">{totalDue.toLocaleString()} FCFA</div>
            <div className="text-[11px] text-slate-500">{invoices.filter(i => i.status === 'EN_ATTENTE').length} factures à régler</div>
          </div>
        </div>
      </div>

      {/* Invoice List */}
      <div className="space-y-4">
        {invoices.length === 0 && (
          <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-5 text-sm text-amber-200">
            Aucune facture persistée n’est disponible pour cette société. Les données de démonstration ont été supprimées.
          </div>
        )}
        {invoices.map(inv => (
          <div key={inv.id} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
            <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
              <div className="space-y-2 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-sm font-black text-amber-300">{inv.id}</span>
                  <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                    inv.status === 'PAYEE'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  }`}>
                    {inv.status === 'PAYEE' ? '✓ Payée' : '⏱ En Attente'}
                  </span>
                </div>
                <div className="text-sm font-bold text-white">{inv.description}</div>
                <div className="text-xs text-slate-400 font-mono">
                  Émise le {inv.date} • {inv.dueDate}
                </div>

                {/* Line items */}
                <div className="mt-3 space-y-1 pt-3 border-t border-slate-800/80">
                  {inv.items.map((item, i) => (
                    <div key={i} className="flex justify-between text-xs text-slate-400">
                      <span>{item.label}</span>
                      <span className="font-mono text-slate-300">{item.amount.toLocaleString()} XAF</span>
                    </div>
                  ))}
                  <div className="flex justify-between text-sm font-black text-white pt-2 border-t border-slate-800 mt-2">
                    <span>Total</span>
                    <span className="font-mono text-amber-300">{inv.amount.toLocaleString()} XAF</span>
                  </div>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex flex-col gap-2 shrink-0 min-w-[160px]">
                <button
                  onClick={() => toast.success(`Téléchargement de la facture ${inv.id}`)}
                  className="px-4 py-2 bg-slate-800 border border-slate-700 text-slate-200 text-xs font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-slate-700 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Télécharger PDF
                </button>
                {inv.status === 'EN_ATTENTE' && (
                  <button
                    onClick={() => setPaymentModal(inv)}
                    className="px-4 py-2 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition-all hover:from-amber-400 hover:to-yellow-300"
                  >
                    <CreditCard className="w-3.5 h-3.5" /> Payer Maintenant
                  </button>
                )}
                {inv.status === 'PAYEE' && (
                  <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold rounded-xl flex items-center justify-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Quittance Disponible
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Payment Modal */}
      {paymentModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-5 animate-in zoom-in-95 duration-200">
            <div>
              <h2 className="text-xl font-black text-white">Paiement Sécurisé</h2>
              <p className="text-xs text-slate-400 mt-0.5">Facture {paymentModal.id} • Montant : <strong className="text-amber-300 font-mono">{paymentModal.amount.toLocaleString()} XAF</strong></p>
            </div>

            {/* Payment Method Selector */}
            <div className="space-y-2">
              {paymentMethods.map(pm => (
                <label key={pm.id} className={`flex items-center gap-3 p-4 rounded-2xl border cursor-pointer transition-all ${paymentMethod === pm.id ? 'bg-amber-500/10 border-amber-500/30' : 'bg-slate-950 border-slate-800 hover:border-slate-700'}`}>
                  <input type="radio" name="paymethod" value={pm.id} checked={paymentMethod === pm.id} onChange={() => setPaymentMethod(pm.id)} className="text-amber-500" />
                  <span className="text-xl">{pm.icon}</span>
                  <div>
                    <div className={`text-xs font-bold ${pm.color}`}>{pm.label}</div>
                    <div className="text-[11px] text-slate-400">{pm.desc}</div>
                  </div>
                </label>
              ))}
            </div>

            {(paymentMethod === 'MTN_MOMO' || paymentMethod === 'ORANGE_MONEY') && (
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Numéro Mobile Money (Cameroun +237)</label>
                <div className="relative">
                  <Smartphone className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={e => setPhoneNumber(e.target.value)}
                    placeholder="Ex: 677 123 456"
                    className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button onClick={() => setPaymentModal(null)} className="flex-1 py-3 bg-slate-800 text-slate-300 font-bold text-sm rounded-xl border border-slate-700">
                Annuler
              </button>
              <button
                onClick={handlePay}
                disabled={isPaying || ((paymentMethod === 'MTN_MOMO' || paymentMethod === 'ORANGE_MONEY') && !phoneNumber)}
                className="flex-1 py-3 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg disabled:opacity-60"
              >
                {isPaying ? 'Traitement...' : `Confirmer ${paymentModal.amount.toLocaleString()} XAF`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

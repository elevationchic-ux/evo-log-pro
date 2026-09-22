'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  CreditCard,
  BarChart3,
  FileText,
  Banknote,
  RefreshCw,
  Plus,
  ArrowUpRight,
  ShieldCheck,
  Building2,
  Users
} from 'lucide-react';
import { financeAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function FinanceDashboardPage() {
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [encaissements, setEncaissements] = useState<any[]>([]);

  const loadFinanceData = async () => {
    setLoading(true);
    try {
      const [invRes, encRes] = await Promise.allSettled([
        financeAPI.getFactures({ limit: 10 }),
        financeAPI.getEncaissements({ limit: 10 })
      ]);

      if (invRes.status === 'fulfilled') {
        const raw = invRes.value.data?.items || invRes.value.data || [];
        setInvoices(Array.isArray(raw) ? raw : []);
      }
      if (encRes.status === 'fulfilled') {
        const raw = encRes.value.data?.items || encRes.value.data || [];
        setEncaissements(Array.isArray(raw) ? raw : []);
      }
    } catch (err) {
      console.error('Error loading finance dashboard', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFinanceData();
  }, []);

  const totalFacture = invoices.reduce((sum, i) => sum + Number(i.montant_ttc || i.montant || 0), 0);
  const totalEncaisse = encaissements.reduce((sum, e) => sum + Number(e.montant || 0), 0);
  const soldeDu = totalFacture - totalEncaisse;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <DollarSign className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Direction Financière & Comptabilité OHADA</h1>
            <p className="text-sm text-on-surface-variant">
              Supervision des flux de trésorerie, facturation d'exploitation, encaissements et balance âgée
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadFinanceData}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Link
            href="/finance/invoicing/create"
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
          >
            <Plus className="w-4 h-4" /> Émettre Facture
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Chiffre d'Affaires Facturé</p>
            <p className="text-xl font-bold font-mono text-on-surface mt-1">
              {totalFacture.toLocaleString('fr-FR')} FCFA
            </p>
          </div>
          <div className="p-3 bg-primary/10 rounded-xl text-primary">
            <FileText className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Règlements Encaissés</p>
            <p className="text-xl font-bold font-mono text-emerald-600 mt-1">
              {totalEncaisse.toLocaleString('fr-FR')} FCFA
            </p>
          </div>
          <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-600">
            <Banknote className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Créances Clients en Attente</p>
            <p className="text-xl font-bold font-mono text-amber-600 mt-1">
              {soldeDu.toLocaleString('fr-FR')} FCFA
            </p>
          </div>
          <div className="p-3 bg-amber-500/10 rounded-xl text-amber-600">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Norme Comptable</p>
            <p className="text-lg font-bold text-on-surface mt-1">
              SYSCOHADA
            </p>
          </div>
          <div className="p-3 bg-blue-500/10 rounded-xl text-blue-600">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Financial Modules Directory */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { title: 'Facturation Clients', desc: 'Émission et suivi des décomptes', link: '/finance/invoicing', icon: FileText, color: 'primary' },
          { title: 'Encaissements & Rapprochement', desc: 'Saisie règlements et lettrage bancaire', link: '/finance/encaissements', icon: Banknote, color: 'emerald-600' },
          { title: 'Grilles Tarifaires', desc: 'Tarifs transit, acconage et fret km', link: '/finance/tarifs', icon: BarChart3, color: 'blue-600' },
          { title: 'Paie des Chauffeurs', desc: 'Primes de trajet, vacations et avances', link: '/finance/payroll', icon: Users, color: 'purple-600' },
        ].map((mod, idx) => (
          <Link
            key={idx}
            href={mod.link}
            className="bg-surface border border-outline rounded-2xl p-5 hover:border-primary/50 hover:bg-surface-container/40 transition-all group shadow-sm block"
          >
            <div className="flex items-center justify-between mb-3">
              <div className={`p-2.5 rounded-xl bg-${mod.color}/10 text-${mod.color}`}>
                <mod.icon className="w-5 h-5" />
              </div>
              <ArrowUpRight className="w-4 h-4 text-on-surface-variant group-hover:text-primary transition-colors" />
            </div>
            <h3 className="font-bold text-sm text-on-surface">{mod.title}</h3>
            <p className="text-xs text-on-surface-variant mt-1">{mod.desc}</p>
          </Link>
        ))}
      </div>

      {/* Recent Activity Table */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        <div className="px-5 py-4 border-b border-outline bg-surface-container-low flex justify-between items-center">
          <h2 className="font-bold text-sm text-on-surface">Dernières Factures Émises</h2>
          <Link href="/finance/invoicing" className="text-xs text-primary font-semibold hover:underline">
            Voir toutes les factures →
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-on-surface">
            <thead className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline">
              <tr>
                <th className="px-5 py-3">N° Facture</th>
                <th className="px-5 py-3">Client</th>
                <th className="px-5 py-3">Date</th>
                <th className="px-5 py-3 text-right">Montant TTC</th>
                <th className="px-5 py-3 text-right">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline/30 font-mono">
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center font-sans text-on-surface-variant">
                    Aucune facture enregistrée pour le moment.
                  </td>
                </tr>
              ) : (
                invoices.slice(0, 5).map((inv, i) => (
                  <tr key={inv.id || i} className="hover:bg-surface-container/50 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-on-surface">
                      {inv.numero_facture || `FAC-${inv.id}`}
                    </td>
                    <td className="px-5 py-3.5 font-sans font-medium text-on-surface">
                      {inv.client_nom || inv.tiers_nom || 'Client Externe'}
                    </td>
                    <td className="px-5 py-3.5 text-xs text-on-surface-variant">
                      {inv.date_emission || '2026-08-30'}
                    </td>
                    <td className="px-5 py-3.5 text-right font-bold text-primary">
                      {Number(inv.montant_ttc || inv.montant || 0).toLocaleString('fr-FR')} FCFA
                    </td>
                    <td className="px-5 py-3.5 text-right font-sans">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600">
                        {inv.statut || 'VALIDÉE'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

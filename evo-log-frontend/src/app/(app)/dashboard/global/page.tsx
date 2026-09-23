'use client'

import React, { useState, useEffect, useCallback } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer
} from 'recharts'
import {
  TrendingUp,
  Package,
  AlertTriangle,
  CreditCard,
  Truck,
  Terminal,
  Building,
  Warehouse,
  ArrowRight,
  Loader2,
  Radio,
  ShoppingCart,
  Landmark,
  BarChart3,
  RefreshCw,
  Sparkles,
  ShieldCheck,
  Zap,
  Clock,
  ShieldAlert,
  Fuel,
  Globe,
  Activity
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getRouteFromTCode } from '@/utils/tcodeLookup'
import { financeAPI, transportAPI, magasinAPI } from '@/lib/api-client'

type Num = number | null

interface DashboardData {
  chiffreAffaires: Num
  missionsEnCours: Num
  vehiculesActifs: Num
  vehiculesTotal: Num
  camionsDispos: Num
  valeurStock: Num
  alertesStock: Num
  mouvementsJour: Num
  nbEntrepots: Num
}

interface RevenuePoint {
  month: string
  revenue: number
}

interface ZoneOccupation {
  entrepot_id: number
  zone: string
  nb_articles: number
  valeur_stockee: number
  occupancy: number | null
}

interface ActivityItem {
  id: string
  type: string
  text: string
  date: string
}

const EMPTY: DashboardData = {
  chiffreAffaires: null,
  missionsEnCours: null,
  vehiculesActifs: null,
  vehiculesTotal: null,
  camionsDispos: null,
  valeurStock: null,
  alertesStock: null,
  mouvementsJour: null,
  nbEntrepots: null
}

const fmtM = (v: Num, unit = 'M') =>
  v === null ? '—' : `${(v / 1_000_000).toFixed(1)}${unit}`

const fmtInt = (v: Num) => (v === null ? '—' : v.toLocaleString('fr-FR'))

export default function GlobalDashboard() {
  const router = useRouter()
  const [tcodeFocused, setTcodeFocused] = useState(false)
  const [tcode, setTcode] = useState('')
  const [loading, setLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)
  const [lastSync, setLastSync] = useState<string>('—')
  const [loadError, setLoadError] = useState(false)

  const [data, setData] = useState<DashboardData>(EMPTY)
  const [revenueMonths, setRevenueMonths] = useState<RevenuePoint[]>([])
  const [zones, setZones] = useState<ZoneOccupation[]>([])
  const [activity, setActivity] = useState<ActivityItem[]>([])

  const load = useCallback(async () => {
    const [finRes, transRes, magRes, chartRes, facturesRes, encaisRes, zonesRes] =
      await Promise.allSettled([
        financeAPI.getKpis(),
        transportAPI.getKpis(),
        magasinAPI.getKpis(),
        financeAPI.getAnalyticsChartData(),
        financeAPI.getFactures(),
        financeAPI.getEncaissements(),
        magasinAPI.getEntrepotsOccupation()
      ])

    let ok = false
    const next: DashboardData = { ...EMPTY }

    if (finRes.status === 'fulfilled' && finRes.value?.data) {
      ok = true
      next.chiffreAffaires = Number(finRes.value.data.chiffre_affaires ?? 0)
    }
    if (transRes.status === 'fulfilled' && transRes.value?.data) {
      ok = true
      next.missionsEnCours = Number(transRes.value.data.missions_en_cours ?? 0)
      next.vehiculesActifs = Number(transRes.value.data.vehicules_actifs ?? 0)
      next.vehiculesTotal = Number(transRes.value.data.vehicules_total ?? 0)
      next.camionsDispos = Number(transRes.value.data.camions_disponibles ?? 0)
    }
    if (magRes.status === 'fulfilled' && magRes.value?.data) {
      ok = true
      next.valeurStock = Number(magRes.value.data.valeur_stock ?? 0)
      next.alertesStock = Number(magRes.value.data.nb_alertes_min ?? 0)
      next.mouvementsJour = Number(magRes.value.data.mouvements_jour ?? 0)
      next.nbEntrepots = Number(magRes.value.data.nb_entrepots ?? 0)
    }
    setData(next)

    if (chartRes.status === 'fulfilled' && Array.isArray(chartRes.value?.data?.months)) {
      setRevenueMonths(
        chartRes.value.data.months.map((m: { month: string; revenue: number }) => ({
          month: m.month,
          revenue: Number(m.revenue)
        }))
      )
    } else {
      setRevenueMonths([])
    }

    if (zonesRes.status === 'fulfilled' && Array.isArray(zonesRes.value?.data?.zones)) {
      setZones(zonesRes.value.data.zones)
    } else {
      setZones([])
    }

    // Flux d'activité : fusions réelles factures + encaissements, tri chronologique
    const items: ActivityItem[] = []
    if (facturesRes.status === 'fulfilled' && Array.isArray(facturesRes.value?.data)) {
      for (const f of facturesRes.value.data.slice(0, 20)) {
        items.push({
          id: `F-${f.id}`,
          type: 'FACTURE',
          text: `Facture ${f.numero || `#${f.id}`} — ${f.client_nom || 'client inconnu'} (${fmtM(Number(f.montant_ttc), ' M FCFA')})`,
          date: f.date_emission || f.created_at || ''
        })
      }
    }
    if (encaisRes.status === 'fulfilled' && Array.isArray(encaisRes.value?.data)) {
      for (const p of encaisRes.value.data.slice(0, 20)) {
        items.push({
          id: `E-${p.id}`,
          type: 'ENCAISSEMENT',
          text: `Encaissement #${p.id} de ${fmtM(Number(p.montant), ' FCFA')} (${p.mode_paiement || 'mode non précisé'})`,
          date: p.date_paiement || ''
        })
      }
    }
    items.sort((a, b) => (b.date || '').localeCompare(a.date || ''))
    setActivity(items.slice(0, 8))

    setLoadError(!ok)
    if (ok) setLastSync(new Date().toLocaleTimeString('fr-FR'))
    return ok
  }, [])

  useEffect(() => {
    const run = async () => {
      setLoading(true)
      await load()
      setLoading(false)
    }
    run()
  }, [load])

  const handleSync = async () => {
    setIsSyncing(true)
    await load()
    setTimeout(() => setIsSyncing(false), 400)
  }

  const handleTCodeSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (tcode.trim()) {
      router.push(getRouteFromTCode(tcode.trim()))
    }
  }

  const kpiCards: { label: string; value: string; icon: typeof Truck; color: string; bg: string; border: string }[] = [
    { label: "Chiffre d'Affaires (FCFA)", value: fmtM(data.chiffreAffaires), icon: TrendingUp, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30' },
    { label: 'Missions en Cours', value: fmtInt(data.missionsEnCours), icon: Truck, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30' },
    { label: 'Véhicules Actifs', value: data.vehiculesActifs === null ? '—' : `${data.vehiculesActifs} / ${data.vehiculesTotal ?? 0}`, icon: Radio, color: 'text-indigo-400', bg: 'bg-indigo-500/10', border: 'border-indigo-500/30' },
    { label: 'Valeur Stock (FCFA)', value: fmtM(data.valeurStock), icon: Package, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30' },
    { label: 'Stock sous Minimum', value: fmtInt(data.alertesStock), icon: AlertTriangle, color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/30' },
    { label: 'Mouvements du Jour', value: fmtInt(data.mouvementsJour), icon: Activity, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/30' }
  ]

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12">
      {/* 👑 Top Executive Enterprise Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-2xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" /> Écosystème Logistique Global • Port de Douala & Kribi Deep Sea
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Vue d'Ensemble Entreprise EVO-LOG
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Supervision stratégique agrégée en temps réel depuis la base de votre organisation (finance, transport, magasin).
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* T-Code Quick Search */}
          <form onSubmit={handleTCodeSubmit} className="relative">
            <Terminal className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-amber-400" />
            <input
              type="text"
              value={tcode}
              onChange={(e) => setTcode(e.target.value.toUpperCase())}
              onFocus={() => setTcodeFocused(true)}
              onBlur={() => setTcodeFocused(false)}
              placeholder="Saisir T-Code (ex: EVO-TR01)"
              className="h-10 pl-9 pr-3 bg-slate-950 border border-amber-500/30 rounded-xl text-xs text-amber-300 font-mono placeholder-slate-500 focus:outline-none focus:border-amber-400 w-44"
            />
          </form>

          {/* Sync Button */}
          <button
            onClick={handleSync}
            disabled={isSyncing || loading}
            className="h-10 px-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-bold rounded-xl flex items-center gap-2 transition cursor-pointer text-slate-200"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-amber-400 ${isSyncing || loading ? 'animate-spin' : ''}`} />
            {isSyncing || loading ? 'Chargement...' : `Actualisé (${lastSync})`}
          </button>

          <Link
            href="/admin"
            className="h-10 px-4 bg-gradient-to-r from-amber-500 via-yellow-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-black text-xs rounded-xl flex items-center gap-1.5 shadow-lg shadow-amber-500/20 transition cursor-pointer"
          >
            <ShieldCheck className="w-4 h-4" />
            Admin ERP
          </Link>
        </div>
      </div>

      {loadError && (
        <div className="flex items-center gap-3 bg-amber-500/10 border border-amber-500/40 rounded-2xl px-4 py-3 text-xs text-amber-300">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          Backend injoignable ou non authentifié : les indicateurs ci-dessous ne peuvent pas être calculés. Aucune valeur n&apos;est simulée.
        </div>
      )}

      {/* 💎 Enterprise KPI Cards (100% réels) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpiCards.map((kpi, idx) => {
          const IconComponent = kpi.icon
          return (
            <div key={idx} className={`${kpi.bg} ${kpi.border} border p-4 rounded-2xl flex flex-col items-center justify-center gap-2 shadow-lg`}>
              <IconComponent className={`w-5 h-5 ${kpi.color}`} />
              <span className="text-xs font-bold text-slate-400 text-center">{kpi.label}</span>
              <span className="text-lg font-black text-white">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : kpi.value}</span>
            </div>
          )
        })}
      </div>

      {/* 📊 Enterprise Charts & Ops */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart — données réelles 12 mois */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" /> Revenus (12 derniers mois)
            </h2>
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Source : factures • M FCFA</span>
          </div>

          {revenueMonths.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={revenueMonths}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <RechartsTooltip
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }}
                  itemStyle={{ color: '#f1f5f9' }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorRevenue)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex flex-col items-center justify-center text-center gap-2 border border-dashed border-slate-800 rounded-2xl">
              <BarChart3 className="w-8 h-8 text-slate-600" />
              <p className="text-sm font-bold text-slate-300">Aucune facture enregistrée</p>
              <p className="text-xs text-slate-500 max-w-xs">Le graphique se construit à partir des émissions de factures réelles de votre organisation.</p>
            </div>
          )}
        </div>

        {/* Fleet & Warehouse — agrégats réels */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Radio className="w-5 h-5 text-indigo-400" /> Flotte & Entrepôts
          </h2>

          <div className="space-y-3">
            <div className="text-xs text-slate-400 font-bold uppercase tracking-wider">Parc roulant (base réelle) :</div>
            <div className="space-y-2">
              {[
                { name: 'Véhicules actifs (en mission)', count: data.vehiculesActifs, color: '#10b981' },
                { name: 'Véhicules disponibles', count: data.camionsDispos, color: '#6366f1' },
                { name: 'Parc total immatriculé', count: data.vehiculesTotal, color: '#f59e0b' }
              ].map((item, idx) => (
                <div key={idx} className="bg-slate-950 p-4 rounded-2xl border border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-3.5 h-3.5 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-xs font-bold text-slate-200">{item.name}</span>
                  </div>
                  <span className="text-sm font-black text-white">{fmtInt(item.count)} Camions</span>
                </div>
              ))}
            </div>

            <div className="pt-2 border-t border-slate-800">
              <div className="text-xs text-slate-400 mb-2 font-bold uppercase tracking-wider">Entrepôts (valeur stockée réelle) :</div>
              {zones.length > 0 ? (
                <div className="space-y-2">
                  {zones.slice(0, 5).map((z) => (
                    <div key={z.entrepot_id} className="space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-300 font-semibold">{z.zone} • {z.nb_articles} art.</span>
                        <strong className="text-amber-400 font-bold">
                          {z.occupancy !== null ? `${z.occupancy}%` : 'capacité non renseignée'}
                        </strong>
                      </div>
                      <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                        <div
                          className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full"
                          style={{ width: `${z.occupancy ?? 0}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl p-3">
                  Aucun entrepot enregistre — la carte se remplit des entrepots et stocks reels de votre organisation.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 🚀 All ERP Modules Quick Access Grid */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2 pb-3 border-b border-slate-800">
          <Zap className="w-5 h-5 text-amber-400" /> Navigation Rapide aux Modules ERP
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {[
            { label: 'Admin ERP', href: '/admin', icon: ShieldCheck, color: 'text-amber-400' },
            { label: 'Transport', href: '/transport/control', icon: Truck, color: 'text-emerald-400' },
            { label: 'Magasin', href: '/magasin/dashboard', icon: Package, color: 'text-indigo-400' },
            { label: 'Finance', href: '/finance/overview', icon: CreditCard, color: 'text-cyan-400' },
            { label: 'Acconage Quai', href: '/acconage', icon: Building, color: 'text-purple-400' },
            { label: 'QHSE Sécurité', href: '/qhse', icon: ShieldAlert, color: 'text-red-400' },
            { label: 'Transit Douane', href: '/transit', icon: Globe, color: 'text-yellow-400' },
            { label: 'Maintenance', href: '/maintenance', icon: RefreshCw, color: 'text-blue-400' },
            { label: 'e-POD & GPS', href: '/tracking', icon: Radio, color: 'text-emerald-400' },
            { label: 'FuelGuard', href: '/fuel-guard', icon: Fuel, color: 'text-orange-400' },
            { label: 'Procurement', href: '/procurement', icon: ShoppingCart, color: 'text-pink-400' },
            { label: 'Analytics BI', href: '/bi', icon: BarChart3, color: 'text-amber-400' },
          ].map((m, idx) => {
            const IconComponent = m.icon
            return (
              <Link
                key={idx}
                href={m.href}
                className="bg-slate-950 hover:bg-slate-800/80 border border-slate-800 p-3.5 rounded-2xl flex flex-col items-center text-center gap-2 transition hover:scale-105 active:scale-95 group shadow-md"
              >
                <div className={`p-2.5 rounded-xl bg-slate-900 border border-slate-800 ${m.color} group-hover:scale-110 transition`}>
                  <IconComponent className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-slate-200 group-hover:text-amber-400 transition">{m.label}</span>
              </Link>
            )
          })}
        </div>
      </div>

      {/* 📡 Last document activity — issu des écritures réelles */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2 pb-3 border-b border-slate-800">
          <Clock className="w-5 h-5 text-emerald-400" /> Derniers Documents Financiers (factures & encaissements)
        </h2>

        {activity.length > 0 ? (
          <div className="divide-y divide-slate-800/70">
            {activity.map((log) => (
              <div key={log.id} className="py-3 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-amber-300 font-mono text-[10px] font-bold shrink-0">
                    {log.type}
                  </span>
                  <span className="text-xs text-slate-200 font-semibold truncate">{log.text}</span>
                </div>
                <span className="text-xs text-slate-400 font-mono shrink-0">
                  {log.date ? new Date(log.date).toLocaleDateString('fr-FR') : 'date inconnue'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-8 flex flex-col items-center justify-center text-center gap-2 border border-dashed border-slate-800 rounded-2xl">
            <Warehouse className="w-8 h-8 text-slate-600" />
            <p className="text-sm font-bold text-slate-300">Aucun document financier enregistré</p>
            <p className="text-xs text-slate-500 max-w-md">
              Ce flux affiche les dernières factures émises et encaissements enregistrés dans la base.{' '}
              <Link href="/finance/overview" className="text-amber-400 font-bold inline-flex items-center gap-1 hover:underline">
                Ouvrir la console Finance <ArrowRight className="w-3 h-3" />
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

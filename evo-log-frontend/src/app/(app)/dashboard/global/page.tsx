'use client'

import React, { useState, useEffect, useCallback } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  Package,
  ShieldAlert,
  CreditCard,
  Truck,
  Terminal,
  AlertTriangle,
  ArrowRight,
  Loader2,
  Building,
  Globe,
  Tag,
  Radio,
  Fuel,
  ShoppingCart,
  Landmark,
  BarChart3,
  RefreshCw,
  Sparkles,
  ShieldCheck,
  Zap,
  CheckCircle2,
  Clock
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getRouteFromTCode } from '@/utils/tcodeLookup'
import { financeAPI, transportAPI, adminAPI } from '@/lib/api-client'

export default function GlobalDashboard() {
  const router = useRouter()
  const [tcodeFocused, setTcodeFocused] = useState(false)
  const [tcode, setTcode] = useState('')
  const [period, setPeriod] = useState<'week' | 'month' | 'year'>('week')
  const [isSyncing, setIsSyncing] = useState(false)
  const [lastSync, setLastSync] = useState(new Date().toLocaleTimeString())

  // KPI State with rich default values
  const [monthlyRevenue, setMonthlyRevenue] = useState('284.5M')
  const [activeMissions, setActiveMissions] = useState('48')
  const [activeVehicles, setActiveVehicles] = useState('82')
  const [stockValue, setStockValue] = useState('14.2M$')
  const [warehouseCapacity, setWarehouseCapacity] = useState('88.5%')
  const [transitDeclarations, setTransitDeclarations] = useState('142')
  const [qhseScore, setQhseScore] = useState('98.5%')

  // Sample Chart Data for Enterprise Performance (Week, Month, Year)
  const [revenueDataWeek] = useState([
    { day: 'Lun', revenue: 38.5, fretTons: 1200 },
    { day: 'Mar', revenue: 42.0, fretTons: 1450 },
    { day: 'Mer', revenue: 45.2, fretTons: 1600 },
    { day: 'Jeu', revenue: 41.8, fretTons: 1380 },
    { day: 'Ven', revenue: 52.4, fretTons: 1900 },
    { day: 'Sam', revenue: 34.6, fretTons: 1100 },
    { day: 'Dim', revenue: 30.0, fretTons: 950 },
  ])

  const [revenueDataMonth] = useState([
    { day: 'Sem 1', revenue: 185.0, fretTons: 5200 },
    { day: 'Sem 2', revenue: 210.5, fretTons: 6100 },
    { day: 'Sem 3', revenue: 245.8, fretTons: 7400 },
    { day: 'Sem 4', revenue: 284.5, fretTons: 8900 },
  ])

  const [revenueDataYear] = useState([
    { day: 'Jan', revenue: 620, fretTons: 18000 },
    { day: 'Fév', revenue: 710, fretTons: 21000 },
    { day: 'Mar', revenue: 840, fretTons: 25000 },
    { day: 'Avr', revenue: 790, fretTons: 23500 },
    { day: 'Mai', revenue: 920, fretTons: 28000 },
    { day: 'Juin', revenue: 1050, fretTons: 31000 },
    { day: 'Juil', revenue: 1180, fretTons: 34500 },
  ])

  const activeChartData = period === 'year' ? revenueDataYear : period === 'month' ? revenueDataMonth : revenueDataWeek;

  const [fleetStatusData] = useState([
    { name: 'En Mission Active', count: 82, color: '#10b981' },
    { name: 'En Entretien / Garages', count: 12, color: '#f59e0b' },
    { name: 'En Attente au Dépôt', count: 18, color: '#6366f1' },
  ])

  const [warehouseZonesData] = useState([
    { zone: 'MAG1 (Conteneurs)', occupancy: 92 },
    { zone: 'MAG2 (Vrac Souterrain)', occupancy: 78 },
    { zone: 'MAG3 (Frigo Séquentiel)', occupancy: 85 },
    { zone: 'Quai Nord Acconage', occupancy: 95 },
  ])

  const [liveOperationLogs] = useState([
    { id: 1, type: 'TRANSPORT', text: 'Camion LT-890-AA arrivé au Port de Kribi - e-POD signé avec succès', time: '10 min ago', status: 'SUCCESS' },
    { id: 2, type: 'MAGASIN', text: 'Entrée en stock BL-4901 (400 Tonnes de Ciment ZLECAF) au MAG3', time: '25 min ago', status: 'INFO' },
    { id: 3, type: 'TRANSIT', text: 'Déclaration Douane DEC-2026-908 Liquidée sans pénalité', time: '45 min ago', status: 'SUCCESS' },
    { id: 4, type: 'QHSE', text: 'Inspection Sécurité Véhicule TR-402-BB validée (Note 100%)', time: '1h ago', status: 'INFO' },
    { id: 5, type: 'FINANCE', text: 'Facture Client F-2026-088 acquittée (14.5M FCFA par Virement BGFI)', time: '2h ago', status: 'SUCCESS' },
  ])

  const fetchRealData = useCallback(async () => {
    try {
      const [finRes, transRes, dashRes] = await Promise.allSettled([
        financeAPI.getKpis(),
        transportAPI.getKpis(),
        adminAPI.getDashboardKpis()
      ])

      if (finRes.status === 'fulfilled' && finRes.value?.data?.chiffre_affaires) {
        setMonthlyRevenue((finRes.value.data.chiffre_affaires / 1000000).toFixed(1) + 'M')
      }
      if (transRes.status === 'fulfilled' && transRes.value?.data) {
        if (transRes.value.data.vehicules_actifs !== undefined) {
          setActiveVehicles(transRes.value.data.vehicules_actifs.toString())
        }
        if (transRes.value.data.missions_en_cours !== undefined) {
          setActiveMissions(transRes.value.data.missions_en_cours.toString())
        }
      }
    } catch (e) {
      console.error("Erreur de synchronisation du Dashboard Global", e)
    }
  }, [])

  useEffect(() => {
    fetchRealData()
  }, [fetchRealData])

  const handleSync = async () => {
    setIsSyncing(true)
    await fetchRealData()
    setTimeout(() => {
      setIsSyncing(false)
      setLastSync(new Date().toLocaleTimeString())
    }, 600)
  }

  const handleTCodeSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (tcode.trim()) {
      router.push(getRouteFromTCode(tcode.trim()))
    }
  }

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
            Supervision stratégique en temps réel des opérations de transport, stockage entrepôt, douane et finance.
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
              placeholder="Saisir T-Code (ex: EVO-TR01)"
              className="h-10 pl-9 pr-3 bg-slate-950 border border-amber-500/30 rounded-xl text-xs text-amber-300 font-mono placeholder-slate-500 focus:outline-none focus:border-amber-400 w-44"
            />
          </form>

          {/* Sync Button */}
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className="h-10 px-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-bold rounded-xl flex items-center gap-2 transition cursor-pointer text-slate-200"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-amber-400 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? 'Synchro...' : `Actualisé (${lastSync})`}
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

      {/* 💎 Enterprise KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
        {[
          { label: 'Chiffre d\'Affaires Mensuel', value: monthlyRevenue, icon: TrendingUp, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30' },
          { label: 'Missions en Cours', value: activeMissions, icon: Truck, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30' },
          { label: 'Véhicules Actifs', value: activeVehicles, icon: Radio, color: 'text-indigo-400', bg: 'bg-indigo-500/10', border: 'border-indigo-500/30' },
          { label: 'Valeur Stock', value: stockValue, icon: Package, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30' },
          { label: 'Capacité Entrepôt', value: warehouseCapacity, icon: Building, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30' },
          { label: 'Déclarations Transit', value: transitDeclarations, icon: Globe, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/30' },
          { label: 'Score QHSE', value: qhseScore, icon: ShieldAlert, color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/30' },
        ].map((kpi, idx) => {
          const IconComponent = kpi.icon
          return (
            <div key={idx} className={`${kpi.bg} ${kpi.border} border p-4 rounded-2xl flex flex-col items-center justify-center gap-2 shadow-lg`}>
              <IconComponent className={`w-5 h-5 ${kpi.color}`} />
              <span className="text-xs font-bold text-slate-400 text-center">{kpi.label}</span>
              <span className="text-lg font-black text-white">{kpi.value}</span>
            </div>
          )
        })}
      </div>

      {/* 📊 Enterprise Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" /> Performance Revenus
            </h2>
            <div className="flex gap-2">
              {(['week', 'month', 'year'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                    period === p 
                      ? 'bg-amber-500 text-slate-950' 
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  {p === 'week' ? 'Semaine' : p === 'month' ? 'Mois' : 'Année'}
                </button>
              ))}
            </div>
          </div>

          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={activeChartData}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" fontSize={11} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }}
                itemStyle={{ color: '#f1f5f9' }}
              />
              <Area type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorRevenue)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Fleet Status & Warehouse */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Radio className="w-5 h-5 text-indigo-400" /> Flotte & Entrepôts
          </h2>

          <div className="space-y-3">
            <div className="text-xs text-slate-400 font-bold uppercase tracking-wider">Statut Flotte Camions :</div>
            <div className="space-y-2">
              {fleetStatusData.map((item, idx) => (
                <div key={idx} className="bg-slate-950 p-4 rounded-2xl border border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-3.5 h-3.5 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-xs font-bold text-slate-200">{item.name}</span>
                  </div>
                  <span className="text-sm font-black text-white">{item.count} Camions</span>
                </div>
              ))}
            </div>

            <div className="pt-2 border-t border-slate-800">
              <div className="text-xs text-slate-400 mb-2 font-bold uppercase tracking-wider">Taux d'Occupation Entrepôts :</div>
              <div className="space-y-2">
                {warehouseZonesData.map((z, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-300 font-semibold">{z.zone}</span>
                      <strong className="text-amber-400 font-bold">{z.occupancy}%</strong>
                    </div>
                    <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                      <div className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full" style={{ width: `${z.occupancy}%` }} />
                    </div>
                  </div>
                ))}
              </div>
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
            { label: 'Magasin MAG3', href: '/magasin/dashboard', icon: Package, color: 'text-indigo-400' },
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

      {/* 📡 Live Operations Stream */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2 pb-3 border-b border-slate-800">
          <Clock className="w-5 h-5 text-emerald-400" /> Flux d'Opérations Entreprise en Temps Réel
        </h2>

        <div className="divide-y divide-slate-800/70">
          {liveOperationLogs.map((log) => (
            <div key={log.id} className="py-3 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-amber-300 font-mono text-[10px] font-bold">
                  {log.type}
                </span>
                <span className="text-xs text-slate-200 font-semibold">{log.text}</span>
              </div>
              <span className="text-xs text-slate-400 font-mono shrink-0">{log.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
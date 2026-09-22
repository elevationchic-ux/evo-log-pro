'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { getModuleIcon, getModuleName } from '../../config/moduleColors'
import { ModuleType } from './ModuleSidebar'
import { useModuleTheme } from '../../hooks/useModuleTheme'
import { getRouteFromTCode, canAccessTCode, TCODE_MAP } from '@/utils/tcodeLookup'
import { useAuth } from './AuthProvider'
import { useSettings, ThemePreference } from './SettingsProvider'
import { useI18n } from '@/hooks/useI18n'
import { toast } from 'sonner'
import { useTheme } from 'next-themes'
import { HelpAndShortcutsModal } from '@/components/shared/HelpAndShortcutsModal'
import { AppBreadcrumb } from '@/components/shared/AppBreadcrumb'
import { RecentWorkingTabs } from '@/components/shared/RecentWorkingTabs'
import dynamic from 'next/dynamic'

const OfflineSyncIndicator = dynamic(
  () => import('@/components/shared/OfflineSyncIndicator'),
  { ssr: false }
)

const NOTIFICATIONS_STORAGE_KEY = 'evolog_erp_notifications'

type ERPNotification = {
  id: string
  message: string
  severity: 'CRITICAL' | 'WARNING' | 'INFO'
  timestamp: string
  read: boolean
}

type ModuleHeaderProps = {
  currentModule: ModuleType
  onMenuClick?: () => void
}

export function ModuleHeader({ currentModule, onMenuClick }: ModuleHeaderProps) {
  const { theme } = useModuleTheme()
  const router = useRouter()
  const t = useI18n()

  const [searchValue, setSearchValue] = useState('')
  const [showSuggestion, setShowSuggestion] = useState(false)
  const [notifications, setNotifications] = useState<ERPNotification[]>([])
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false)
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false)

  const moduleIcon = getModuleIcon(currentModule)
  const moduleName = getModuleName(currentModule)
  // themeClasses now uses CSS-variable-based dark-aware utility
  const themeClasses = theme.headerClasses || 'module-badge-admin'

  const { user, logout, sessionExpiresAt, renewSession, sessionExpired } = useAuth()
  const suggestionRef = useRef<HTMLDivElement>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const soundEnabledRef = useRef(true)
  const notificationIdRef = useRef(0)

  const { soundEnabled, toggleSound, showSoundBadge, triggerSoundBadge, language, setLanguage } = useSettings()
  const { theme: uiTheme, setTheme } = useTheme()

  const [isModuleMenuOpen, setIsModuleMenuOpen] = useState(false)
  const [selectedAgency, setSelectedAgency] = useState('Douala, CMR')
  const [isAgencyMenuOpen, setIsAgencyMenuOpen] = useState(false)
  const [minutesLeft, setMinutesLeft] = useState<number | null>(null)
  const [showSessionExpiredModal, setShowSessionExpiredModal] = useState(false)

  const AGENCIES = [
    { id: 'DLA', name: 'Douala, CMR', icon: 'domain' },
    { id: 'ABJ', name: 'Abidjan, CIV', icon: 'domain' },
    { id: 'DKR', name: 'Dakar, SEN', icon: 'domain' },
  ]

  const MODULES_LIST: { id: ModuleType; label: string; icon: string; path: string }[] = [
    { id: 'transport', label: 'K-Transport / Flotte', icon: 'local_shipping', path: '/transport/control' },
    { id: 'finance', label: 'K-Finance / Comptabilité', icon: 'account_balance', path: '/finance/overview' },
    { id: 'magasin', label: 'K-Magasin / Entrepôt', icon: 'warehouse', path: '/magasin/dashboard' },
    { id: 'parc', label: 'K-Parc / Yard', icon: 'directions_car', path: '/parc/zones' },
    { id: 'acconage', label: 'K-Acconage / Quai', icon: 'anchor', path: '/acconage' },
    { id: 'qhse', label: 'K-QHSE / Sécurité', icon: 'shield', path: '/qhse' },
    { id: 'transit', label: 'K-Transit / Douane', icon: 'public', path: '/transit' },
    { id: 'maintenance', label: 'K-Maintenance / Atelier', icon: 'build', path: '/maintenance' },
    { id: 'cotations', label: 'K-Cotation / Devis', icon: 'local_offer', path: '/cotations' },
    { id: 'tracking', label: 'K-Tracking / e-POD', icon: 'sensors', path: '/tracking' },
    { id: 'fuel-guard', label: 'K-FuelGuard / Télémétrie', icon: 'local_gas_station', path: '/fuel-guard' },
    { id: 'procurement', label: 'K-Procurement / Achats', icon: 'shopping_cart', path: '/procurement' },
    { id: 'compliance', label: 'K-Compliance / Douane', icon: 'gavel', path: '/compliance' },
    { id: 'bi', label: 'K-Analytics BI Executive', icon: 'analytics', path: '/bi' },
    { id: 'master-data', label: 'Données Maîtres', icon: 'hub', path: '/master-data/tiers' },
    { id: 'rh', label: 'Ressources Humaines', icon: 'groups', path: '/rh/dashboard' },
    { id: 'client-portal', label: 'Portail Client B2B', icon: 'language', path: '/client-portal' },
    { id: 'admin', label: 'Administration', icon: 'admin_panel_settings', path: '/admin/user-management/listing' },
  ]



  useEffect(() => { soundEnabledRef.current = soundEnabled }, [soundEnabled])

  useEffect(() => {
    const handleHelpKey = (e: KeyboardEvent) => {
      if ((e.key === '?' || e.key === 'F1') && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        e.preventDefault()
        setIsHelpModalOpen((prev) => !prev)
      }
    }
    window.addEventListener('keydown', handleHelpKey)
    return () => window.removeEventListener('keydown', handleHelpKey)
  }, [])

  useEffect(() => {
    if (!sessionExpiresAt) return
    const checkSession = () => {
      const diffMins = Math.floor((sessionExpiresAt.getTime() - Date.now()) / 60000)
      setMinutesLeft(diffMins > 0 ? diffMins : 0)
      if (diffMins <= 0 && sessionExpired) setShowSessionExpiredModal(true)
    }
    checkSession()
    const timer = setInterval(checkSession, 1000)
    return () => clearInterval(timer)
  }, [sessionExpiresAt, sessionExpired])

  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const socketRef = useRef<WebSocket | null>(null)

  const cycleTheme = () => {
    const themes = ['light', 'dark', 'system']
    setTheme(themes[(themes.indexOf(uiTheme || 'system') + 1) % themes.length])
  }

  const connect = useCallback(() => {
    let wsUrl = process.env.NEXT_PUBLIC_WS_URL
    if (!wsUrl) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL
      if (apiUrl) {
        const wsProto = apiUrl.startsWith('https') ? 'wss://' : 'ws://'
        const cleanHost = apiUrl.replace(/^https?:\/\//, '').replace(/\/$/, '')
        wsUrl = `${wsProto}${cleanHost}/api/v1/ws/events`
      } else if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
        const wsProto = window.location.protocol === 'https:' ? 'wss://' : 'ws://'
        wsUrl = `${wsProto}${window.location.hostname}/api/v1/ws/events`
      } else {
        wsUrl = 'ws://localhost:8000/api/v1/ws/events'
      }
    }
    if (!user?.accessToken || !user.companyId || !user.id) return
    const socket = new WebSocket(`${wsUrl}?token=${encodeURIComponent(user.accessToken)}&company_id=${user.companyId}&user_id=${encodeURIComponent(user.id)}`)
    socketRef.current = socket
    setWsStatus('connecting')

    socket.onopen = () => { reconnectAttemptsRef.current = 0; setWsStatus('connected') }
    socket.onmessage = (event) => {
      const alert = JSON.parse(event.data)
      window.dispatchEvent(new CustomEvent('evo-log:event', { detail: alert }))
      const newNotif: ERPNotification = { ...alert, id: alert.id || `notif-${notificationIdRef.current++}`, read: false, timestamp: alert.timestamp || new Date().toISOString() }
      setNotifications((prev) => [newNotif, ...prev])
      if (alert.severity === 'CRITICAL' && soundEnabledRef.current) {
        const audio = new Audio('/assets/sounds/critical-alert.mp3')
        triggerSoundBadge(); audio.volume = 0.5
        audio.play().catch((e) => console.warn('Audio playback failed:', e))
      }
      toast(alert.message, { icon: alert.severity === 'CRITICAL' ? '🚨' : '⚠️', duration: 6000, style: { background: '#0f172a', color: '#fff', borderLeft: alert.severity === 'CRITICAL' ? '4px solid #ba1a1a' : '4px solid #f59e0b' } })
    }
    socket.onclose = (e) => {
      if (e.wasClean) return
      setWsStatus('disconnected')
      if (reconnectAttemptsRef.current < 3) {
        reconnectAttemptsRef.current++
        const delay = Math.min(2000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
        reconnectTimeoutRef.current = setTimeout(() => { connect() }, delay)
      } else {
        console.info('[WebSocket] Statut silencieux: reconnexion mise en pause.')
      }
    }
    socket.onerror = () => {
      try { socket.close() } catch {}
    }
  }, [user, triggerSoundBadge])

  useEffect(() => {
    setMounted(true)
    if (!user) return
    const savedNotifs = localStorage.getItem(NOTIFICATIONS_STORAGE_KEY)
    if (savedNotifs) { try { setNotifications(JSON.parse(savedNotifs)) } catch { } }
    connect()
    return () => { if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current); socketRef.current?.close() }
  }, [user, connect])

  const markAsRead = (id: string) => setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n))
  const markAllAsRead = () => setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
  const clearReadNotifications = () => { setNotifications((prev) => prev.filter((n) => !n.read)); toast.success(language === 'fr' ? 'Notifications lues effacées' : 'Read notifications cleared') }

  useEffect(() => {
    if (notifications.length > 0 || localStorage.getItem(NOTIFICATIONS_STORAGE_KEY)) {
      localStorage.setItem(NOTIFICATIONS_STORAGE_KEY, JSON.stringify(notifications))
    }
  }, [notifications])

  const tcodeKey = searchValue.toUpperCase()
  const matchedSuggestion = TCODE_MAP[tcodeKey]
  useEffect(() => { setShowSuggestion(!!matchedSuggestion) }, [searchValue, matchedSuggestion])

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); searchInputRef.current?.focus() }
      if (e.key === 'Escape') { setShowSuggestion(false); searchInputRef.current?.blur() }
    }
    window.addEventListener('keydown', handleGlobalKeyDown)
    return () => window.removeEventListener('keydown', handleGlobalKeyDown)
  }, [])

  const navigateToTCode = (code: string) => {
    const hasAccess = user?.roles?.some((r) => canAccessTCode(r, code)) ?? false
    if (!hasAccess) { toast.error(`Accès Interdit : Votre profil (${user?.roles?.join(', ') || 'INVITÉ'}) ne dispose pas des droits pour ${code}.`, { id: 'forbidden-tcode', icon: 'lock' }); return }
    const targetRoute = getRouteFromTCode(code)
    if (targetRoute) { router.push(targetRoute); setSearchValue(''); setShowSuggestion(false) }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') { navigateToTCode(searchValue.toUpperCase()); (e.target as HTMLInputElement).blur() }
  }

  const unreadCount = notifications.filter((n) => !n.read).length

  return (
    <>
      {/* ════════════════════════════════════════════
          HEADER  sticky, 64px tall, 3 zones
          Zone 1: Hamburger + Logo + Module switcher
          Zone 2: T-Code search bar
          Zone 3: Actions (agency, theme, lang, sound, notifs, profile, logout)
          ════════════════════════════════════════════ */}
      <header className="sticky top-0 z-40 h-16 border-b border-outline bg-surface/95 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-surface/85">
        <div className="flex h-full items-center gap-2 px-3 sm:px-4 lg:px-5">

          {/* ── Zone 1: Identity ── */}
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            {/* Hamburger / Sidebar Toggle */}
            <button
              onClick={onMenuClick}
              className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-outline bg-surface-container-low text-on-surface-variant transition-colors hover:bg-surface-container hover:text-on-surface"
              aria-label="Rétracter/Ouvrir le menu"
              title="Activer/Rétracter la Sidebar"
            >
              <span className="material-symbols-outlined text-[20px]">menu</span>
            </button>

            {/* Logo */}
            <div className="hidden items-center gap-1.5 sm:flex">
              <span className="text-[18px] font-black tracking-tight text-EVO-LOG-primary">EVO-LOG</span>
              <span className="hidden text-[11px] font-medium text-on-surface-variant md:block">EM-ERP</span>
            </div>

            {/* Divider */}
            <div className="hidden h-5 w-px bg-outline sm:block" />

            {/* Module switcher */}
            <div className="relative">
              <button
                onClick={() => setIsModuleMenuOpen(!isModuleMenuOpen)}
                className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[12px] font-bold uppercase tracking-wide transition-all hover:opacity-90 ${themeClasses}`}
                aria-haspopup="listbox"
                aria-expanded={isModuleMenuOpen}
              >
                <span className="material-symbols-outlined text-[16px]">{moduleIcon}</span>
                <span className="hidden max-w-[120px] truncate sm:block">{moduleName}</span>
                <span className="material-symbols-outlined text-[14px] opacity-70">expand_more</span>
              </button>

              {isModuleMenuOpen && (
                <>
                  <div className="fixed inset-0 z-[45]" onClick={() => setIsModuleMenuOpen(false)} />
                  <div className="absolute top-full left-0 z-50 mt-1.5 w-64 overflow-hidden rounded-xl border border-outline bg-surface shadow-2xl animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="border-b border-outline bg-surface-container-low px-4 py-2.5">
                      <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Changer de module</span>
                    </div>
                    <div className="py-1">
                      {MODULES_LIST.map((m) => (
                        <button
                          key={m.id}
                          role="option"
                          aria-selected={currentModule === m.id}
                          onClick={() => { setIsModuleMenuOpen(false); router.push(m.path) }}
                          className={`w-full flex items-center gap-3 border-l-[3px] px-4 py-2.5 text-left text-sm transition-colors hover:bg-surface-container-low ${currentModule === m.id ? 'border-primary bg-surface-container-low font-semibold text-primary' : 'border-transparent text-on-surface'}`}
                        >
                          <span className={`material-symbols-outlined text-[18px] ${currentModule === m.id ? 'text-primary' : 'text-on-surface-variant'}`}>{m.icon}</span>
                          {m.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* ── Zone 2: T-Code Search (flex-1 center) ── */}
          <div className="min-w-0 flex-1 px-2 sm:px-4 lg:max-w-xl" role="search">
            <div className="relative group">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-on-surface-variant transition-colors group-focus-within:text-primary">
                <span className="material-symbols-outlined text-[18px]">manage_search</span>
              </div>
              <input
                type="text"
                ref={searchInputRef}
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`T-Code (ex: KM24)…`}
                aria-label="Recherche par T-Code"
                className="block w-full rounded-lg border border-outline bg-surface-container-low py-2 pl-9 pr-14 text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:border-primary focus:bg-surface focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
              />
              {/* Keyboard shortcut hint  hidden on very small screens */}
              <div className="pointer-events-none absolute inset-y-0 right-0 hidden items-center pr-2.5 sm:flex">
                <kbd className="rounded border border-outline px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-tighter text-on-surface-variant bg-surface-container">⌘K</kbd>
              </div>

              {/* T-Code suggestion dropdown */}
              {showSuggestion && matchedSuggestion && (
                <div
                  ref={suggestionRef}
                  className="absolute left-0 right-0 top-full z-50 mt-1 overflow-hidden rounded-xl border border-outline bg-surface shadow-2xl animate-in fade-in slide-in-from-top-2 duration-200"
                >
                  <button
                    onClick={() => navigateToTCode(tcodeKey)}
                    className="w-full text-left transition-colors hover:bg-surface-container-low"
                  >
                    <div className="flex items-center justify-between gap-3 px-4 py-3">
                      <div className="flex min-w-0 items-center gap-3">
                        <span className="flex-shrink-0 rounded border border-primary/30 bg-primary/10 px-2 py-0.5 font-mono text-sm font-bold text-primary">{tcodeKey}</span>
                        <span className="truncate text-sm text-on-surface">→ {matchedSuggestion.split('/').pop()?.replace(/-/g, ' ')}</span>
                      </div>
                      <kbd className="flex-shrink-0 rounded border border-outline px-1.5 py-0.5 text-[10px] font-bold uppercase text-on-surface-variant">↵</kbd>
                    </div>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* ── Zone 3: Actions ── */}
          <div className="flex shrink-0 items-center gap-1 sm:gap-1.5">

            {/* WS status  desktop only */}
            {wsStatus !== 'connected' && (
              <div className="hidden items-center gap-1.5 rounded-lg bg-surface-container px-2.5 py-1.5 md:flex">
                <span className={`h-1.5 w-1.5 rounded-full ${wsStatus === 'connecting' ? 'bg-amber-500 animate-pulse' : 'bg-red-500'}`} />
                <span className="text-[10px] font-bold uppercase text-on-surface-variant">
                  {wsStatus === 'connecting' ? 'Sync…' : 'Off'}
                </span>
                {wsStatus === 'disconnected' && (
                  <button
                    onClick={() => { if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current); socketRef.current?.close(); connect() }}
                    className="text-[10px] font-bold text-primary hover:underline"
                  >
                    Retry
                  </button>
                )}
              </div>
            )}

            {/* Session expiry warning  xl only */}
            {minutesLeft !== null && minutesLeft <= 5 && minutesLeft > 0 && (
              <div className="hidden animate-pulse items-center gap-1 rounded-lg border border-red-300/50 bg-red-500/10 px-2.5 py-1.5 xl:flex">
                <span className="text-[10px] font-bold text-red-500">SESSION {minutesLeft}m</span>
                <button onClick={renewSession} className="text-[10px] font-black text-primary hover:underline">↺</button>
              </div>
            )}

            {/* Agency selector  hidden on mobile */}
            <div className="relative hidden md:block">
              <button
                onClick={() => setIsAgencyMenuOpen(!isAgencyMenuOpen)}
                className="flex items-center gap-1 rounded-lg border border-outline bg-surface-container-low px-2.5 py-1.5 text-[11px] font-semibold text-on-surface shadow-sm transition-colors hover:bg-surface-container"
                aria-haspopup="listbox"
                aria-expanded={isAgencyMenuOpen}
              >
                <span className="material-symbols-outlined text-[15px] text-primary">domain</span>
                <span className="hidden max-w-[7rem] truncate lg:block">{selectedAgency}</span>
                <span className="material-symbols-outlined text-[14px] text-on-surface-variant">arrow_drop_down</span>
              </button>

              {isAgencyMenuOpen && (
                <>
                  <div className="fixed inset-0 z-[45]" onClick={() => setIsAgencyMenuOpen(false)} />
                  <div className="absolute right-0 top-full z-50 mt-1.5 w-52 overflow-hidden rounded-xl border border-outline bg-surface shadow-2xl animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="flex items-center justify-between border-b border-outline bg-surface-container-low px-4 py-2.5">
                      <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Agence</span>
                      <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[9px] font-bold uppercase text-primary">Global</span>
                    </div>
                    <div className="py-1">
                      {AGENCIES.map((agency) => (
                        <button
                          key={agency.id}
                          role="option"
                          aria-selected={selectedAgency === agency.name}
                          onClick={() => { setSelectedAgency(agency.name); setIsAgencyMenuOpen(false); toast.success(`Agence → ${agency.name}`, { icon: '🏢' }) }}
                          className={`w-full flex items-center gap-3 border-l-2 px-4 py-2.5 text-left text-sm transition-colors hover:bg-surface-container-low ${selectedAgency === agency.name ? 'border-primary bg-surface-container-low font-semibold text-primary' : 'border-transparent text-on-surface'}`}
                        >
                          <span className={`material-symbols-outlined text-[16px] ${selectedAgency === agency.name ? 'text-primary' : 'text-on-surface-variant'}`}>{agency.icon}</span>
                          <span>{agency.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Help & shortcuts modal button */}
            <button
              onClick={() => setIsHelpModalOpen(true)}
              className="inline-flex h-9 w-9 items-center justify-center rounded-xl text-on-surface-variant transition-colors hover:bg-primary/10 hover:text-primary"
              title="Centre d'aide, glossaire et raccourcis clavier (Touche ? ou F1)"
              aria-label="Centre d'aide et raccourcis"
            >
              <span className="material-symbols-outlined text-[20px]">help</span>
            </button>

            {/* Offline Sync Indicator — visible for field agents on transit corridors */}
            <OfflineSyncIndicator baseUrl={typeof window !== 'undefined' ? window.location.origin : ''} />

            {/* Notifications bell */}
            <button
              onClick={() => setIsDrawerOpen(true)}
              className="relative inline-flex h-9 w-9 items-center justify-center rounded-xl text-on-surface-variant transition-colors hover:bg-surface-container hover:text-on-surface"
              aria-label={`Notifications (${unreadCount} non lues)`}
            >
              <span className="material-symbols-outlined text-[20px]">notifications</span>
              {unreadCount > 0 && (
                <span className="absolute right-0.5 top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full border-2 border-surface bg-red-500 px-0.5 text-[9px] font-black text-white">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </button>

            <div className="h-5 w-px bg-outline mx-1 hidden sm:block" />

            {/* UNIFIED USER PROFILE & PREFERENCES DROPDOWN */}
            <div className="relative">
              <button
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                className="flex items-center gap-2 p-1 pl-2 rounded-xl hover:bg-surface-container transition-all text-left"
                aria-haspopup="true"
                aria-expanded={isProfileMenuOpen}
              >
                <div className="hidden flex-col items-end text-right lg:flex">
                  <p className="text-[13px] font-semibold leading-tight text-on-surface">{user?.fullName || 'Utilisateur'}</p>
                  <p className="text-[10px] text-on-surface-variant font-medium">{selectedAgency.split(',')[0]}</p>
                </div>
                <div className="relative h-8 w-8 rounded-xl bg-primary flex items-center justify-center text-on-primary text-xs font-black shadow-sm ring-2 ring-primary/20">
                  {user?.fullName?.charAt(0) || 'U'}
                  <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-surface bg-emerald-500" />
                </div>
                <span className="material-symbols-outlined text-[16px] text-on-surface-variant hidden sm:block">
                  expand_more
                </span>
              </button>

              {isProfileMenuOpen && (
                <>
                  <div className="fixed inset-0 z-[45]" onClick={() => setIsProfileMenuOpen(false)} />
                  <div className="absolute right-0 top-full mt-2 w-72 overflow-hidden rounded-2xl border border-outline bg-surface shadow-2xl z-50 animate-in fade-in slide-in-from-top-2 duration-150 divide-y divide-outline/60 text-xs">
                    
                    {/* User Header */}
                    <div className="p-4 bg-surface-container-low/80">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-primary flex items-center justify-center text-on-primary text-base font-black shadow-sm">
                          {user?.fullName?.charAt(0) || 'U'}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="font-bold text-sm text-on-surface truncate">{user?.fullName || 'Utilisateur'}</p>
                          <p className="text-[11px] text-on-surface-variant truncate">{user?.email}</p>
                          <span className="inline-flex items-center px-1.5 py-0.2 mt-1 rounded bg-primary/10 text-primary font-mono text-[9px] font-bold">
                            {user?.roles?.[0] || 'COLLABORATEUR'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Agency Switcher */}
                    <div className="p-3 space-y-1.5">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant px-1">
                        Agence d'exploitation
                      </span>
                      <div className="grid grid-cols-3 gap-1">
                        {AGENCIES.map((ag) => (
                          <button
                            key={ag.id}
                            onClick={() => {
                              setSelectedAgency(ag.name);
                              toast.success(`Agence active : ${ag.name}`, { icon: '🏢' });
                            }}
                            className={`px-2 py-1.5 rounded-lg text-center font-bold text-[11px] transition-colors ${
                              selectedAgency === ag.name
                                ? 'bg-primary text-on-primary'
                                : 'bg-surface-container hover:bg-surface-container-high text-on-surface'
                            }`}
                          >
                            {ag.id}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Preferences: Theme, Language, Sound */}
                    <div className="p-3 space-y-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant px-1">
                        Préférences de travail
                      </span>
                      
                      {/* Theme */}
                      <div className="flex items-center justify-between px-1">
                        <span className="text-on-surface text-xs font-medium">Thème :</span>
                        <div className="inline-flex rounded-lg border border-outline bg-surface-container p-0.5">
                          <button
                            onClick={() => setTheme('light')}
                            className={`p-1 rounded ${uiTheme === 'light' ? 'bg-surface text-primary shadow-xs' : 'text-on-surface-variant'}`}
                            title="Clair"
                          >
                            <span className="material-symbols-outlined text-[15px]">light_mode</span>
                          </button>
                          <button
                            onClick={() => setTheme('dark')}
                            className={`p-1 rounded ${uiTheme === 'dark' ? 'bg-surface text-primary shadow-xs' : 'text-on-surface-variant'}`}
                            title="Sombre"
                          >
                            <span className="material-symbols-outlined text-[15px]">dark_mode</span>
                          </button>
                          <button
                            onClick={() => setTheme('system')}
                            className={`p-1 rounded ${uiTheme === 'system' ? 'bg-surface text-primary shadow-xs' : 'text-on-surface-variant'}`}
                            title="Système"
                          >
                            <span className="material-symbols-outlined text-[15px]">settings_brightness</span>
                          </button>
                        </div>
                      </div>

                      {/* Language */}
                      <div className="flex items-center justify-between px-1">
                        <span className="text-on-surface text-xs font-medium">Langue :</span>
                        <button
                          onClick={() => setLanguage(language === 'fr' ? 'en' : 'fr')}
                          className="px-2 py-1 rounded-lg border border-outline bg-surface-container font-bold text-[11px] hover:bg-surface-container-high"
                        >
                          {language === 'fr' ? '🇫🇷 Français' : '🇬🇧 English'}
                        </button>
                      </div>

                      {/* Sound */}
                      <div className="flex items-center justify-between px-1">
                        <span className="text-on-surface text-xs font-medium">Alertes sonores :</span>
                        <button
                          onClick={toggleSound}
                          className={`flex items-center gap-1 px-2 py-1 rounded-lg border border-outline text-[11px] font-bold ${
                            soundEnabled ? 'bg-primary/10 text-primary' : 'bg-surface-container text-on-surface-variant'
                          }`}
                        >
                          <span className="material-symbols-outlined text-[14px]">
                            {soundEnabled ? 'volume_up' : 'volume_off'}
                          </span>
                          {soundEnabled ? 'Activé' : 'Coupé'}
                        </button>
                      </div>
                    </div>

                    {/* Quick navigation links */}
                    <div className="p-2 space-y-0.5">
                      <button
                        onClick={() => { setIsProfileMenuOpen(false); router.push('/portail-employe'); }}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-on-surface hover:bg-surface-container text-left"
                      >
                        <span className="material-symbols-outlined text-[17px] text-primary">badge</span>
                        <span>Mon Espace Collaborateur</span>
                      </button>
                      <button
                        onClick={() => { setIsProfileMenuOpen(false); router.push('/security'); }}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-on-surface hover:bg-surface-container text-left"
                      >
                        <span className="material-symbols-outlined text-[17px] text-primary">shield</span>
                        <span>Sécurité du Compte & 2FA</span>
                      </button>
                    </div>

                    {/* Logout */}
                    <div className="p-2">
                      <button
                        onClick={() => { setIsProfileMenuOpen(false); router.push('/logout'); }}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-error hover:bg-error/10 text-left font-bold transition-colors"
                      >
                        <span className="material-symbols-outlined text-[17px]">logout</span>
                        <span>Se déconnecter</span>
                      </button>
                    </div>

                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Sub-bar: Dynamic Breadcrumb & Recent Working Tabs */}
        <div className="hidden sm:flex items-center px-4 py-1 border-t border-outline/30 bg-surface-container-lowest/50">
          <AppBreadcrumb />
        </div>
        <RecentWorkingTabs />
      </header>

      {/* Universal Help & Shortcuts Modal */}
      <HelpAndShortcutsModal
        isOpen={isHelpModalOpen}
        onClose={() => setIsHelpModalOpen(false)}
      />

      {/* ════════════════════════════════════════════
          NOTIFICATION DRAWER
          ════════════════════════════════════════════ */}
      {isDrawerOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[55]"
            onClick={() => setIsDrawerOpen(false)}
          />
          <div className="fixed inset-y-0 right-0 z-[60] flex w-[90vw] max-w-sm flex-col bg-surface border-l border-outline shadow-2xl animate-in slide-in-from-right duration-300">
            {/* Drawer header */}
            <div className="flex items-center justify-between border-b border-outline bg-surface-container-low px-4 py-3.5 shrink-0">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[20px] text-on-surface-variant">notifications</span>
                <h2 className="text-sm font-bold uppercase tracking-wider text-on-surface">{t.auth.notifTitle}</h2>
                {unreadCount > 0 && (
                  <span className="rounded-full bg-red-500 px-2 py-0.5 text-[10px] font-black text-white">{unreadCount}</span>
                )}
              </div>
              <button
                onClick={() => setIsDrawerOpen(false)}
                className="rounded-lg p-1 text-on-surface-variant transition-colors hover:bg-surface-container hover:text-on-surface"
                aria-label="Fermer les notifications"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            {/* Notification list */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-surface-container-low/30">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 text-on-surface-variant gap-2">
                  <span className="material-symbols-outlined text-5xl opacity-40">notifications_off</span>
                  <p className="text-sm">{t.auth.notifEmpty}</p>
                </div>
              ) : (
                notifications.map((notif) => (
                  <div
                    key={notif.id}
                    className={`group relative rounded-xl border border-outline bg-surface p-3.5 shadow-sm transition-all
                      ${notif.severity === 'CRITICAL' ? 'border-l-4 border-l-red-500' : notif.severity === 'WARNING' ? 'border-l-4 border-l-amber-400' : 'border-l-4 border-l-blue-400'}
                      ${notif.read ? 'opacity-50' : ''}
                    `}
                  >
                    <div className="mb-1.5 flex items-center justify-between">
                      <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide
                        ${notif.severity === 'CRITICAL' ? 'bg-error-container text-on-error-container' : notif.severity === 'WARNING' ? 'bg-tertiary-container text-on-tertiary-container' : 'bg-primary-container text-on-primary-container'}
                      `}>
                        {notif.severity}
                      </span>
                      <span className="font-mono text-[10px] text-on-surface-variant">
                        {mounted ? new Date(notif.timestamp).toLocaleTimeString() : '--:--'}
                      </span>
                    </div>
                    <p className={`text-xs leading-relaxed ${notif.read ? 'text-on-surface-variant' : 'text-on-surface font-medium'}`}>
                      {notif.message}
                    </p>
                    {!notif.read && (
                      <button
                        onClick={() => markAsRead(notif.id)}
                        className="absolute bottom-2 right-2 rounded p-1 text-on-surface-variant opacity-0 transition-opacity hover:text-primary group-hover:opacity-100"
                        aria-label="Marquer comme lu"
                      >
                        <span className="material-symbols-outlined text-[16px]">done</span>
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Drawer footer */}
            <div className="grid grid-cols-2 gap-2 border-t border-outline bg-surface p-3 shrink-0">
              <button
                onClick={markAllAsRead}
                className="rounded-lg border border-outline py-2 text-[11px] font-bold uppercase tracking-wide text-on-surface transition-colors hover:bg-surface-container"
              >
                {t.auth.notifMarkAll}
              </button>
              <button
                onClick={clearReadNotifications}
                disabled={!notifications.some((n) => n.read)}
                className="rounded-lg border border-error/30 py-2 text-[11px] font-bold uppercase tracking-wide text-error transition-colors hover:bg-error-container/20 disabled:cursor-not-allowed disabled:opacity-30"
              >
                {t.auth.notifClearRead}
              </button>
            </div>
          </div>
        </>
      )}

      {/* ════════════════════════════════════════════
          SESSION EXPIRED MODAL
          ════════════════════════════════════════════ */}
      {showSessionExpiredModal && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm rounded-2xl border border-outline bg-surface p-8 text-center shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            <span
              className="material-symbols-outlined text-error text-6xl mb-4"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              lock_clock
            </span>
            <h3 className="mb-2 text-xl font-bold text-on-surface">{t.auth.sessionModalTitle}</h3>
            <p className="mb-6 text-sm text-on-surface-variant">{t.auth.sessionModalBody}</p>
            <button
              onClick={() => router.push('/logout')}
              className="w-full rounded-xl bg-primary py-3 px-4 font-bold text-on-primary transition-opacity hover:opacity-90"
            >
              {t.auth.sessionModalCta}
            </button>
          </div>
        </div>
      )}
    </>
  )
}

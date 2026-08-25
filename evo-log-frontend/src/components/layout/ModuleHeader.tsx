'use client';
'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useSession, signOut } from 'next-auth/react';
import { useModuleTheme } from '@/hooks/useModuleTheme';
import { useSettings, type ThemePreference } from '@/components/layout/SettingsProvider';
import { useI18n } from '@/hooks/useI18n';
import { getModuleName } from '@/config/moduleColors';
import { toast } from 'sonner';

// ─── Types ────────────────────────────────────────────────────────────────────

type ERPNotification = {
  id: string;
  message: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  timestamp: string;
  read: boolean;
};

const NOTIFICATIONS_KEY = 'evolog_erp_notifications';

// ═══════════════════════════════════════════════════════════════════════════════
// T-CODE MAP - Navigation Rapide ERP Logistique Portuaire COMPLET
// Architecture: 12 Modules × 5+ Sous-modules = 72+ Routes Business
// Process End-to-End: Navire → Client avec Comptabilité OHADA & CEMAC
// ═══════════════════════════════════════════════════════════════════════════════

const TCODE_MAP: Record<string, string> = {
  // ─── DASHBOARD & VUE GLOBALE ───
  'KM00': '/dashboard/global',
  'KM01': '/dashboard/process-flow',
  'KM02': '/dashboard/alerts', 
  'KM03': '/dashboard/cross-kpis',
  'KM04': '/dashboard/real-time-activity',

  // ─── 1. PORT OPERATIONS (🚢) - Phase 1: Arrivée Navire ───
  'PO00': '/port-operations/dashboard',
  'PO01': '/port-operations/manifests',
  'PO02': '/port-operations/quai-operations', 
  'PO03': '/port-operations/berth-planning',
  'PO04': '/port-operations/maritime-stats',
  'PO05': '/port-operations/port-integration',

  // ─── 2. TRANSIT & DOUANE (🛃) - Phase 2: Dédouanement ───
  'TD00': '/transit-douane/dashboard',
  'TD01': '/transit-douane/dossiers-cemac',
  'TD02': '/transit-douane/declarations',
  'TD03': '/transit-douane/taxation-cameroun',
  'TD04': '/transit-douane/compliance',
  'TD05': '/transit-douane/bae',

  // ─── 3. TRANSPORT & FLOTTE (🚛) - Phase 3: Transport Client ───
  'TR00': '/transport-flotte/control-tower',
  'TR01': '/transport-flotte/fleet-management',
  'TR02': '/transport-flotte/missions-dispatch',
  'TR03': '/transport-flotte/tracking-epod',
  'TR04': '/transport-flotte/drivers',
  'TR05': '/transport-flotte/fuel-telematics',

  // ─── 4. MAGASIN & STOCK WMS (📦) - Phase 4: Stock & Préparation ───
  'WM00': '/magasin-stock/dashboard',
  'WM01': '/magasin-stock/reception',
  'WM02': '/magasin-stock/locations',
  'WM03': '/magasin-stock/movements',
  'WM04': '/magasin-stock/inventory',
  'WM05': '/magasin-stock/picking',

  // ─── 5. FINANCE OHADA (💰) - Phase 5: Facturation & Encaissement ───
  'FI00': '/finance-ohada/dashboard',
  'FI01': '/finance-ohada/invoicing',
  'FI02': '/finance-ohada/collections',
  'FI03': '/finance-ohada/suppliers',
  'FI04': '/finance-ohada/treasury',
  'FI05': '/finance-ohada/taxes-cemac',

  // ─── 6. COMPTABILITÉ OHADA (📚) - Phase 6: États Financiers ───
  'CO00': '/comptabilite-ohada/dashboard',
  'CO01': '/comptabilite-ohada/journal',
  'CO02': '/comptabilite-ohada/chart-accounts',
  'CO03': '/comptabilite-ohada/general-ledger',
  'CO04': '/comptabilite-ohada/monthly-closing',
  'CO05': '/comptabilite-ohada/financial-statements',
  'CO06': '/comptabilite-ohada/tax-package-cemac',

  // ─── 7. PARC & VÉHICULES (🚗) - Support: Équipements ───
  'VE00': '/parc-vehicules/dashboard',
  'VE01': '/parc-vehicules/fleet-complete',
  'VE02': '/parc-vehicules/preventive-maintenance',
  'VE03': '/parc-vehicules/documents',
  'VE04': '/parc-vehicules/costs-consumption',
  'VE05': '/parc-vehicules/license-plates',

  // ─── 8. QHSE & SÉCURITÉ (🛡️) - Support: Conformité ───
  'QH00': '/qhse-securite/dashboard',
  'QH01': '/qhse-securite/port-inspections',
  'QH02': '/qhse-securite/incident-management',
  'QH03': '/qhse-securite/safety-training',
  'QH04': '/qhse-securite/ohada-compliance',
  'QH05': '/qhse-securite/environment',

  // ─── 9. RH & PERSONNEL (👥) - Support: Capital Humain ───
  'RH00': '/rh-personnel/dashboard',
  'RH01': '/rh-personnel/employees',
  'RH02': '/rh-personnel/payroll-ohada',
  'RH03': '/rh-personnel/time-attendance',
  'RH04': '/rh-personnel/training-skills',
  'RH05': '/rh-personnel/social-declarations',

  // ─── 10. CLIENT & B2B (🤝) - Support: Relation Client ───
  'CL00': '/client-b2b/dashboard',
  'CL01': '/client-b2b/crm',
  'CL02': '/client-b2b/portal',
  'CL03': '/client-b2b/contracts',
  'CL04': '/client-b2b/after-sales',
  'CL05': '/client-b2b/loyalty',
  'CL06': '/client-b2b/analytics',

  // ─── 11. ADMIN & TENANT (⚙️) - Support: Gouvernance ───
  'AD00': '/admin-tenant/dashboard',
  'AD01': '/admin-tenant/system-admin',
  'AD02': '/admin-tenant/multi-tenant',
  'AD03': '/admin-tenant/users-rbac',
  'AD04': '/admin-tenant/audit-logs',
  'AD05': '/admin-tenant/integrations',
  'AD06': '/admin-tenant/global-settings',

  // ─── 12. REPORTS & BI (📊) - Support: Pilotage ───
  'BI00': '/reports-bi/executive-dashboard',
  'BI01': '/reports-bi/operational-analytics', 
  'BI02': '/reports-bi/financial-reports-ohada',
  'BI03': '/reports-bi/compliance-audit',
  'BI04': '/reports-bi/report-generator',
  'BI05': '/reports-bi/data-export',

  // ─── LEGACY T-CODES (Compatibilité Ancienne Version) ───
  // Anciens raccourcis maintenus pour transition
  'TR01': '/transport-flotte/control-tower',
  'MG01': '/magasin-stock/dashboard',
  'FI01': '/finance-ohada/dashboard',
  'AC01': '/port-operations/dashboard',
  'TS01': '/transit-douane/dashboard',
  'ST01': '/admin-tenant/global-settings',
};

// ─── Material Symbol icon per module (for header badge) ──────────────────────
const MODULE_SYMBOL: Record<string, string> = {
  // Modules principaux (correspondant à navigationRegistry)
  dashboard:              'dashboard',
  'port-operations':      'anchor',
  'transit-douane':       'gavel',
  'transport-flotte':     'local_shipping',
  'magasin-stock':        'warehouse',
  'finance-ohada':        'account_balance',
  'comptabilite-ohada':   'menu_book',
  'parc-vehicules':       'directions_car',
  'qhse-securite':        'shield',
  'rh-personnel':         'groups',
  'client-b2b':           'handshake',
  'admin-tenant':         'admin_panel_settings',
  'reports-bi':           'analytics',

  // Legacy keys (compatibilité)
  admin:                  'admin_panel_settings',
  settings:               'settings',
  transport:              'local_shipping',
  tracking:               'sensors',
  'fuel-guard':           'local_gas_station',
  parc:                   'directions_car',
  magasin:                'warehouse',
  finance:                'account_balance',
  cotations:              'local_offer',
  'paiement-local':       'payments',
  'fiscalite-cameroun':   'receipt_long',
  transit:                'public',
  acconage:               'anchor',
  compliance:             'gavel',
  qhse:                   'shield',
  security:               'security',
  maintenance:            'build',
  rh:                     'groups',
  chauffeur:              'drive_eta',
  procurement:            'shopping_cart',
  purchase:               'receipt_long',
  suppliers:              'store',
  fournisseurs:           'store',
  'master-data':          'hub',
  tiers:                  'diversity_3',
  documents:              'folder',
  reports:                'assessment',
  bi:                     'analytics',
  integration:            'api',
  'integration-cameroun': 'flag',
  'client-portal':        'language',
  support:                'help',
};

// ═══════════════════════════════════════════════════════════════════════════════
// MODULE SWITCHER LIST - Architecture ERP Portuaire Complète
// 12 Modules Principaux × 5+ Sous-modules = 72+ Routes Business Process
// Processus End-to-End: Navire → Déchargement → Dédouanement → Transport → Client
// ═══════════════════════════════════════════════════════════════════════════════

const MODULES_LIST = [
  // ─── VUE GLOBALE ERP ───
  { 
    key: 'dashboard', 
    label: '🎯 Vue Globale ERP', 
    icon: 'dashboard', 
    path: '/dashboard/global',
    category: 'Supervision'
  },

  // ─── PROCESSUS PHASE 1: ARRIVÉE NAVIRE ───
  { 
    key: 'port-operations', 
    label: '🚢 Opérations Portuaires', 
    icon: 'anchor', 
    path: '/port-operations/dashboard',
    category: 'Phase 1 - Arrivée Navire'
  },

  // ─── PROCESSUS PHASE 2: DÉDOUANEMENT ───
  { 
    key: 'transit-douane', 
    label: '🛃 Transit & Douane', 
    icon: 'gavel', 
    path: '/transit-douane/dashboard',
    category: 'Phase 2 - Dédouanement'
  },

  // ─── PROCESSUS PHASE 3: TRANSPORT CLIENT ───
  { 
    key: 'transport-flotte', 
    label: '🚛 Transport & Flotte', 
    icon: 'local_shipping', 
    path: '/transport-flotte/control-tower',
    category: 'Phase 3 - Transport'
  },

  // ─── PROCESSUS PHASE 4: STOCK & PRÉPARATION ───
  { 
    key: 'magasin-stock', 
    label: '📦 Magasin & Stock WMS', 
    icon: 'warehouse', 
    path: '/magasin-stock/dashboard',
    category: 'Phase 4 - Stock & Préparation'
  },

  // ─── PROCESSUS PHASE 5: FACTURATION ───
  { 
    key: 'finance-ohada', 
    label: '💰 Finance OHADA', 
    icon: 'account_balance', 
    path: '/finance-ohada/dashboard',
    category: 'Phase 5 - Facturation'
  },

  // ─── PROCESSUS PHASE 6: COMPTABILITÉ ───
  { 
    key: 'comptabilite-ohada', 
    label: '📚 Comptabilité OHADA', 
    icon: 'menu_book', 
    path: '/comptabilite-ohada/dashboard',
    category: 'Phase 6 - Comptabilité'
  },

  // ─── MODULES SUPPORT TRANSVERSES ───
  { 
    key: 'parc-vehicules', 
    label: '🚗 Parc & Véhicules', 
    icon: 'directions_car', 
    path: '/parc-vehicules/dashboard',
    category: 'Support - Équipements'
  },
  { 
    key: 'qhse-securite', 
    label: '🛡️ QHSE & Sécurité', 
    icon: 'shield', 
    path: '/qhse-securite/dashboard',
    category: 'Support - Conformité'
  },
  { 
    key: 'rh-personnel', 
    label: '👥 RH & Personnel', 
    icon: 'groups', 
    path: '/rh-personnel/dashboard',
    category: 'Support - Capital Humain'
  },
  { 
    key: 'client-b2b', 
    label: '🤝 Client & B2B', 
    icon: 'handshake', 
    path: '/client-b2b/dashboard',
    category: 'Support - Relation Client'
  },
  { 
    key: 'reports-bi', 
    label: '📊 Reports & BI', 
    icon: 'analytics', 
    path: '/reports-bi/executive-dashboard',
    category: 'Support - Pilotage'
  },

  // ─── ADMINISTRATION ───
  { 
    key: 'admin-tenant', 
    label: '⚙️ Admin & Tenant', 
    icon: 'admin_panel_settings', 
    path: '/admin-tenant/dashboard',
    category: 'Administration'
  },

  // ─── MODULES LEGACY (Compatibilité Transition) ───
  { 
    key: 'admin', 
    label: 'Administration ERP (Legacy)', 
    icon: 'admin_panel_settings', 
    path: '/admin/user-management/listing',
    category: 'Legacy - Transition',
    hidden: true
  },
  { 
    key: 'settings', 
    label: 'Paramètres & Profil', 
    icon: 'settings', 
    path: '/settings',
    category: 'Personnel'
  }
] as const;

const AGENCIES = [
  { id: 'DLA', name: 'Douala, CMR',   icon: 'domain' },
  { id: 'ABJ', name: 'Abidjan, CIV', icon: 'domain' },
  { id: 'DKR', name: 'Dakar, SEN',   icon: 'domain' },
  { id: 'LBV', name: 'Libreville, GAB', icon: 'domain' },
  { id: 'YDE', name: 'Yaoundé, CMR', icon: 'domain' },
];

// ─── Props ────────────────────────────────────────────────────────────────────

interface ModuleHeaderProps {
  currentModule?: string;
  onMenuClick?: () => void;
}

// ─── Component ────────────────────────────────────────────────────────────────

export function ModuleHeader({ currentModule: moduleProp, onMenuClick }: ModuleHeaderProps) {
  const router = useRouter();
  const { data: session } = useSession();
  const { currentModule, theme } = useModuleTheme();
  const { soundEnabled, toggleSound, showSoundBadge, triggerSoundBadge, language, setLanguage, theme: uiTheme, setTheme: setUiTheme } = useSettings();
  const t = useI18n();

  const activeModule = moduleProp || currentModule;
  const moduleSymbol = MODULE_SYMBOL[activeModule] || 'apps';
  const moduleName   = getModuleName(activeModule);
  const themeClasses = theme.headerClasses || 'module-badge-admin';

  // ── Session user ──
  const user       = session?.user as any;
  const userName   = user?.name || user?.fullName || user?.email?.split('@')[0] || '…';
  const userEmail  = user?.email || '';
  const userRoles: string[] = user?.roles || [];
  const userInitial = userName.charAt(0).toUpperCase();

  // ── UI state ──
  const [searchValue, setSearchValue]         = useState('');
  const [showSuggestion, setShowSuggestion]   = useState(false);
  const [isModuleMenuOpen, setIsModuleMenuOpen] = useState(false);
  const [isAgencyMenuOpen, setIsAgencyMenuOpen] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen]       = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen]   = useState(false);
  const [selectedAgency, setSelectedAgency]   = useState('Douala, CMR');
  const [mounted, setMounted]                 = useState(false);

  // ── Session expiry ──
  const [minutesLeft, setMinutesLeft]                   = useState<number | null>(null);
  const [showSessionExpiredModal, setShowSessionExpiredModal] = useState(false);

  // ── Notifications ──
  const [notifications, setNotifications] = useState<ERPNotification[]>([]);
  const [wsStatus, setWsStatus]           = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const unreadCount = notifications.filter(n => !n.read).length;

  // ── Refs ──
  const searchInputRef        = useRef<HTMLInputElement>(null);
  const soundEnabledRef       = useRef(soundEnabled);
  const socketRef             = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef  = useRef(0);
  const reconnectTimeoutRef   = useRef<ReturnType<typeof setTimeout> | null>(null);
  const notificationIdRef     = useRef(0);

  useEffect(() => { soundEnabledRef.current = soundEnabled; }, [soundEnabled]);
  useEffect(() => { setMounted(true); }, []);

  // ── T-Code suggestion ──
  const tcodeKey         = searchValue.toUpperCase().trim();
  const matchedRoute     = TCODE_MAP[tcodeKey];
  const matchedLabel     = matchedRoute
    ? matchedRoute.split('/').filter(Boolean).join(' › ')
    : null;

  useEffect(() => {
    setShowSuggestion(!!matchedRoute && searchValue.length > 0);
  }, [searchValue, matchedRoute]);

  // ── Global keyboard shortcuts ──
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      if (e.key === 'Escape') {
        setShowSuggestion(false);
        searchInputRef.current?.blur();
        setIsModuleMenuOpen(false);
        setIsAgencyMenuOpen(false);
        setIsUserMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // ── Session expiry countdown ──
  useEffect(() => {
    // In a real app this would use a session expiry timestamp from the JWT.
    // Here we just keep the UI wired up without a hard deadline.
    const timer = setInterval(() => {
      // placeholder  extend with real expiresAt from session if available
      const expiresAt = (session as any)?.expires
        ? new Date((session as any).expires).getTime()
        : null;
      if (!expiresAt) return;
      const diff = Math.floor((expiresAt - Date.now()) / 60000);
      setMinutesLeft(diff > 0 ? diff : 0);
      if (diff <= 0) setShowSessionExpiredModal(true);
    }, 30000);
    return () => clearInterval(timer);
  }, [session]);

  // ── WebSocket connection ──
  const connect = useCallback(() => {
    if (!user) return;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    let wsUrl = process.env.NEXT_PUBLIC_WS_URL;
    if (!wsUrl && apiUrl) {
      const proto = apiUrl.startsWith('https') ? 'wss://' : 'ws://';
      const host  = apiUrl.replace(/^https?:\/\//, '').replace(/\/$/, '');
      wsUrl = `${proto}${host}/api/v1/ws/events`;
    } else if (!wsUrl) {
      wsUrl = 'ws://localhost:8000/api/v1/ws/events';
    }

    try {
      const socket = new WebSocket(`${wsUrl}?token=${user.id || 'guest'}`);
      socketRef.current = socket;
      setWsStatus('connecting');

      socket.onopen  = () => { reconnectAttemptsRef.current = 0; setWsStatus('connected'); };
      socket.onmessage = (event) => {
        try {
          const alert = JSON.parse(event.data);
          const notif: ERPNotification = {
            id:        alert.id || `n-${notificationIdRef.current++}`,
            message:   alert.message || 'Nouvelle notification',
            severity:  alert.severity || 'INFO',
            timestamp: alert.timestamp || new Date().toISOString(),
            read:      false,
          };
          setNotifications(prev => [notif, ...prev.slice(0, 99)]);
          if (notif.severity === 'CRITICAL' && soundEnabledRef.current) {
            const audio = new Audio('/assets/sounds/critical-alert.mp3');
            audio.volume = 0.5;
            audio.play().catch(() => {});
            triggerSoundBadge();
          }
          toast(notif.message, {
            icon:     notif.severity === 'CRITICAL' ? '🚨' : notif.severity === 'WARNING' ? '⚠️' : 'ℹ️',
            duration: 6000,
            style:    { background: '#0f172a', color: '#fff', borderLeft: notif.severity === 'CRITICAL' ? '4px solid #ef4444' : notif.severity === 'WARNING' ? '4px solid #f59e0b' : '4px solid #6366f1' },
          });
        } catch {}
      };
      socket.onclose = (e) => {
        if (e.wasClean) return;
        setWsStatus('disconnected');
        if (reconnectAttemptsRef.current < 3) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(2000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        }
      };
      socket.onerror = () => { try { socket.close(); } catch {} };
    } catch {}
  }, [user, triggerSoundBadge]);

  useEffect(() => {
    // Restore persisted notifications
    try {
      const saved = localStorage.getItem(NOTIFICATIONS_KEY);
      if (saved) setNotifications(JSON.parse(saved));
    } catch {}
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      socketRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Persist notifications to localStorage
  useEffect(() => {
    try { localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify(notifications.slice(0, 100))); } catch {}
  }, [notifications]);

  // ── Notification actions ──
  const markAsRead      = (id: string) => setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  const markAllAsRead   = () => setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  const clearRead       = () => {
    setNotifications(prev => prev.filter(n => !n.read));
    toast.success(language === 'fr' ? 'Notifications lues effacées' : 'Read notifications cleared');
  };

  // ── T-Code navigation ──
  const navigateToTCode = (code: string) => {
    const route = TCODE_MAP[code.toUpperCase().trim()];
    if (route) {
      router.push(route);
      setSearchValue('');
      setShowSuggestion(false);
    } else {
      toast.error(`T-Code inconnu : ${code}`);
    }
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      navigateToTCode(searchValue);
      (e.target as HTMLInputElement).blur();
    }
  };

  // ── Theme cycle ──
  const cycleTheme = () => {
    const order: ThemePreference[] = ['light', 'dark', 'system'];
    const next = order[(order.indexOf(uiTheme) + 1) % order.length];
    setUiTheme(next);
  };

  const themeIcon  = uiTheme === 'light' ? 'light_mode' : uiTheme === 'dark' ? 'dark_mode' : 'settings_brightness';

  // ─────────────────────────────────────────────────────────────────────────────

  return (
    <>
      {/* ════════════════════════════════════════════════════════════════
          STICKY HEADER  64 px, 3 zones
          Zone 1 : Hamburger · Logo · Module switcher
          Zone 2 : T-Code search bar (flex-1 centre)
          Zone 3 : Actions (agency · theme · lang · sound · notifs · user · logout)
          ════════════════════════════════════════════════════════════════ */}
      <header className="sticky top-0 z-40 h-16 border-b border-outline bg-surface/95 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-surface/85">
        <div className="flex h-full items-center gap-2 px-3 sm:px-4 lg:px-5">

          {/* ── Zone 1: Identity ── */}
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">

            {/* Hamburger */}
            <button
              onClick={onMenuClick}
              className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-outline bg-surface-container-low text-on-surface-variant transition-colors hover:bg-surface-container hover:text-on-surface"
              aria-label="Ouvrir / Fermer le menu"
            >
              <span className="material-symbols-outlined text-[20px]">menu</span>
            </button>

            {/* Logo */}
            <div className="hidden items-center gap-1.5 sm:flex">
              <span className="text-[18px] font-black tracking-tight text-EVO-LOG-primary">EVO-LOG</span>
              <span className="hidden text-[11px] font-medium text-on-surface-variant md:block">SaaS ERP</span>
            </div>

            {/* Divider */}
            <div className="hidden h-5 w-px bg-outline sm:block" />

            {/* Module switcher button */}
            <div className="relative">
              <button
                onClick={() => setIsModuleMenuOpen(v => !v)}
                className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[12px] font-bold uppercase tracking-wide transition-all hover:opacity-90 ${themeClasses}`}
                aria-haspopup="listbox"
                aria-expanded={isModuleMenuOpen}
              >
                <span className="material-symbols-outlined text-[16px]">{moduleSymbol}</span>
                <span className="hidden max-w-[130px] truncate sm:block">{moduleName}</span>
                <span className="material-symbols-outlined text-[14px] opacity-70">expand_more</span>
              </button>

              {isModuleMenuOpen && (
                <>
                  <div className="fixed inset-0 z-[45]" onClick={() => setIsModuleMenuOpen(false)} />
                  <div className="absolute top-full left-0 z-50 mt-1.5 w-68 overflow-hidden rounded-xl border border-outline bg-surface shadow-2xl animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="border-b border-outline bg-surface-container-low px-4 py-2.5">
                      <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                        Changer de module
                      </span>
                    </div>
                    <div className="max-h-[60vh] overflow-y-auto py-1 scrollbar-sidebar">
                      {/* Groupe les modules par catégorie */}
                      {[
                        { category: 'Supervision', title: '🎯 Vue Globale' },
                        { category: 'Phase 1 - Arrivée Navire', title: '🚢 Processus Maritime' },
                        { category: 'Phase 2 - Dédouanement', title: '🛃 Dédouanement CEMAC' },
                        { category: 'Phase 3 - Transport', title: '🚛 Logistique Transport' },
                        { category: 'Phase 4 - Stock & Préparation', title: '📦 WMS & Stock' },
                        { category: 'Phase 5 - Facturation', title: '💰 Finance OHADA' },
                        { category: 'Phase 6 - Comptabilité', title: '📚 Comptabilité OHADA' },
                        { category: 'Support - Équipements', title: '🚗 Parc & Véhicules' },
                        { category: 'Support - Conformité', title: '🛡️ QHSE & Sécurité' },
                        { category: 'Support - Capital Humain', title: '👥 Ressources Humaines' },
                        { category: 'Support - Relation Client', title: '🤝 CRM & B2B' },
                        { category: 'Support - Pilotage', title: '📊 Business Intelligence' },
                        { category: 'Administration', title: '⚙️ Administration' },
                        { category: 'Personnel', title: '👤 Personnel' }
                      ].map(group => {
                        const categoryModules = MODULES_LIST.filter(m => 
                          m.category === group.category && !m.hidden
                        );
                        if (categoryModules.length === 0) return null;
                        
                        return (
                          <div key={group.category}>
                            <div className="px-4 py-1.5 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant border-t border-outline/50 first:border-t-0 bg-surface-container-low/50">
                              {group.title}
                            </div>
                            {categoryModules.map(m => (
                              <button
                                key={m.key}
                                role="option"
                                aria-selected={activeModule === m.key}
                                onClick={() => { setIsModuleMenuOpen(false); router.push(m.path); }}
                                className={`w-full flex items-center gap-3 border-l-[3px] px-4 py-2.5 text-left text-sm transition-colors hover:bg-surface-container-low ${
                                  activeModule === m.key
                                    ? 'border-primary bg-surface-container-low font-semibold text-primary'
                                    : 'border-transparent text-on-surface'
                                }`}
                              >
                                <span className={`material-symbols-outlined text-[18px] ${activeModule === m.key ? 'text-primary' : 'text-on-surface-variant'}`}>
                                  {m.icon}
                                </span>
                                <div className="flex-1">
                                  <div className={`${activeModule === m.key ? 'text-primary font-semibold' : 'text-on-surface'}`}>
                                    {m.label}
                                  </div>
                                </div>
                              </button>
                            ))}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* ── Zone 2: T-Code search (flex-1 centre) ── */}
          <div className="min-w-0 flex-1 px-2 sm:px-4 lg:max-w-lg" role="search">
            <div className="relative group">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-on-surface-variant transition-colors group-focus-within:text-primary">
                <span className="material-symbols-outlined text-[18px]">manage_search</span>
              </div>
              <input
                ref={searchInputRef}
                type="text"
                value={searchValue}
                onChange={e => setSearchValue(e.target.value)}
                onKeyDown={handleSearchKeyDown}
                placeholder="T-Code (ex: PO01, TD02, TR03, WM04, FI05, CO06…)"
                aria-label="Recherche par T-Code"
                className="block w-full rounded-lg border border-outline bg-surface-container-low py-2 pl-9 pr-14 text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:border-primary focus:bg-surface focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
              />
              <div className="pointer-events-none absolute inset-y-0 right-0 hidden items-center pr-2.5 sm:flex">
                <kbd className="rounded border border-outline px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-tighter text-on-surface-variant bg-surface-container">
                  ⌘K
                </kbd>
              </div>

              {/* T-Code suggestion */}
              {showSuggestion && matchedLabel && (
                <div className="absolute left-0 right-0 top-full z-50 mt-1 overflow-hidden rounded-xl border border-outline bg-surface shadow-2xl animate-in fade-in slide-in-from-top-2 duration-200">
                  <button
                    onClick={() => navigateToTCode(tcodeKey)}
                    className="w-full text-left transition-colors hover:bg-surface-container-low"
                  >
                    <div className="flex items-center justify-between gap-3 px-4 py-3">
                      <div className="flex min-w-0 items-center gap-3">
                        <span className="flex-shrink-0 rounded border border-primary/30 bg-primary/10 px-2 py-0.5 font-mono text-sm font-bold text-primary">
                          {tcodeKey}
                        </span>
                        <span className="truncate text-sm text-on-surface">→ {matchedLabel}</span>
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

            {/* WS status (desktop only, shown when not connected) */}
            {wsStatus !== 'connected' && (
              <div className="hidden items-center gap-1.5 rounded-lg bg-surface-container px-2.5 py-1.5 md:flex">
                <span className={`h-1.5 w-1.5 rounded-full ${wsStatus === 'connecting' ? 'bg-amber-500 animate-pulse' : 'bg-red-500'}`} />
                <span className="text-[10px] font-bold uppercase text-on-surface-variant">
                  {wsStatus === 'connecting' ? 'Sync…' : 'Hors ligne'}
                </span>
                {wsStatus === 'disconnected' && (
                  <button
                    onClick={() => { if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current); socketRef.current?.close(); connect(); }}
                    className="text-[10px] font-bold text-primary hover:underline"
                  >
                    Retry
                  </button>
                )}
              </div>
            )}

            {/* Session expiry warning (≤ 5 min, xl only) */}
            {minutesLeft !== null && minutesLeft <= 5 && minutesLeft > 0 && (
              <div className="hidden animate-pulse items-center gap-1 rounded-lg border border-red-300/50 bg-red-500/10 px-2.5 py-1.5 xl:flex">
                <span className="text-[10px] font-bold text-red-500">SESSION {minutesLeft}m</span>
              </div>
            )}

            {/* Agency selector (hidden on mobile) */}
            <div className="relative hidden md:block">
              <button
                onClick={() => setIsAgencyMenuOpen(v => !v)}
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
                      {AGENCIES.map(agency => (
                        <button
                          key={agency.id}
                          role="option"
                          aria-selected={selectedAgency === agency.name}
                          onClick={() => { setSelectedAgency(agency.name); setIsAgencyMenuOpen(false); toast.success(`Agence → ${agency.name}`, { icon: '🏢' }); }}
                          className={`w-full flex items-center gap-3 border-l-2 px-4 py-2.5 text-left text-sm transition-colors hover:bg-surface-container-low ${
                            selectedAgency === agency.name
                              ? 'border-primary bg-surface-container-low font-semibold text-primary'
                              : 'border-transparent text-on-surface'
                          }`}
                        >
                          <span className={`material-symbols-outlined text-[16px] ${selectedAgency === agency.name ? 'text-primary' : 'text-on-surface-variant'}`}>
                            {agency.icon}
                          </span>
                          {agency.name}
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Theme toggle */}
            <button
              onClick={cycleTheme}
              className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-on-surface-variant transition-colors hover:bg-surface-container hover:text-on-surface"
              title={`Thème : ${uiTheme}`}
              aria-label="Changer le thème"
            >
              <span className="material-symbols-outlined text-[20px]">{themeIcon}</span>
            </button>

            {/* Language toggle */}
            <button
              onClick={() => setLanguage(language === 'fr' ? 'en' : 'fr')}
              className="hidden items-center gap-0.5 rounded-lg border border-outline px-2 py-1.5 text-[11px] font-bold uppercase text-on-surface-variant transition-colors hover:bg-surface-container hover:text-on-surface sm:flex"
              aria-label="Changer la langue"
            >
              <span className="material-symbols-outlined text-[15px]">translate</span>
              {language}
            </button>

            {/* Sound toggle */}
            <button
              onClick={toggleSound}
              className={`relative inline-flex h-8 w-8 items-center justify-center rounded-lg transition-colors hover:bg-surface-container ${soundEnabled ? 'text-primary' : 'text-on-surface-variant'}`}
              aria-label={soundEnabled ? 'Couper le son' : 'Activer le son'}
            >
              {showSoundBadge && (
                <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
              )}
              <span className="material-symbols-outlined text-[20px]">
                {soundEnabled ? 'volume_up' : 'volume_off'}
              </span>
            </button>

            {/* Notification bell */}
            <button
              onClick={() => setIsDrawerOpen(true)}
              className="relative inline-flex h-8 w-8 items-center justify-center rounded-lg text-on-surface-variant transition-colors hover:bg-surface-container hover:text-on-surface"
              aria-label={`Notifications (${unreadCount} non lues)`}
            >
              <span className="material-symbols-outlined text-[20px]">notifications</span>
              {unreadCount > 0 && (
                <span className="absolute right-0.5 top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full border-2 border-surface bg-red-500 px-0.5 text-[9px] font-black text-white">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </button>

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(v => !v)}
                className="flex items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-surface-container transition-colors"
                aria-haspopup="menu"
                aria-expanded={isUserMenuOpen}
              >
                <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center text-on-primary text-sm font-black shadow-sm ring-2 ring-primary/20">
                  {userInitial}
                </div>
                <div className="hidden flex-col items-start lg:flex">
                  <p className="text-[13px] font-semibold leading-tight text-on-surface">{userName}</p>
                  <p className="text-[11px] text-on-surface-variant truncate max-w-[120px]">{userRoles[0] || 'Utilisateur'}</p>
                </div>
                <span className="material-symbols-outlined hidden text-[16px] text-on-surface-variant sm:block">expand_more</span>
              </button>

              {isUserMenuOpen && (
                <>
                  <div className="fixed inset-0 z-[45]" onClick={() => setIsUserMenuOpen(false)} />
                  <div className="absolute right-0 top-full mt-2 w-56 overflow-hidden rounded-2xl border border-outline bg-surface shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-150">
                    <div className="px-4 py-3 border-b border-outline bg-surface-container-low">
                      <p className="text-xs font-bold text-on-surface">{userName}</p>
                      <p className="text-[10px] text-on-surface-variant font-mono truncate">{userEmail}</p>
                      {userRoles[0] && (
                        <span className="mt-1 inline-block rounded-full bg-primary/10 px-2 py-0.5 text-[9px] font-black uppercase tracking-widest text-primary">
                          {userRoles[0]}
                        </span>
                      )}
                    </div>
                    <div className="p-1.5 space-y-0.5">
                      <button
                        onClick={() => { setIsUserMenuOpen(false); router.push('/settings'); }}
                        className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-on-surface hover:text-on-surface hover:bg-surface-container rounded-xl transition-colors font-medium"
                      >
                        <span className="material-symbols-outlined text-[16px] text-on-surface-variant">manage_accounts</span>
                        Mon Profil & Paramètres
                      </button>
                      {userRoles.some(r => r.toUpperCase() === 'ADMIN') && (
                        <button
                          onClick={() => { setIsUserMenuOpen(false); router.push('/admin/user-management/listing'); }}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-on-surface hover:bg-surface-container rounded-xl transition-colors font-medium"
                        >
                          <span className="material-symbols-outlined text-[16px] text-on-surface-variant">group</span>
                          Gestion Utilisateurs
                        </button>
                      )}
                      <div className="border-t border-outline my-1" />
                      <button
                        onClick={() => signOut({ callbackUrl: '/login' })}
                        className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-error hover:text-error hover:bg-error-container/20 rounded-xl transition-colors font-medium"
                      >
                        <span className="material-symbols-outlined text-[16px]">logout</span>
                        Déconnexion
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* ════════════════════════════════════════════════════════════════
          NOTIFICATION DRAWER
          ════════════════════════════════════════════════════════════════ */}
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
            <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-surface-container-low/30 scrollbar-sidebar">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 text-on-surface-variant gap-2">
                  <span className="material-symbols-outlined text-5xl opacity-40">notifications_off</span>
                  <p className="text-sm">{t.auth.notifEmpty}</p>
                </div>
              ) : (
                notifications.map(notif => (
                  <div
                    key={notif.id}
                    className={`group relative rounded-xl border border-outline bg-surface p-3.5 shadow-sm transition-all
                      ${notif.severity === 'CRITICAL' ? 'border-l-4 border-l-red-500' : notif.severity === 'WARNING' ? 'border-l-4 border-l-amber-400' : 'border-l-4 border-l-primary'}
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
                onClick={clearRead}
                disabled={!notifications.some(n => n.read)}
                className="rounded-lg border border-error/30 py-2 text-[11px] font-bold uppercase tracking-wide text-error transition-colors hover:bg-error-container/20 disabled:cursor-not-allowed disabled:opacity-30"
              >
                {t.auth.notifClearRead}
              </button>
            </div>
          </div>
        </>
      )}

      {/* ════════════════════════════════════════════════════════════════
          SESSION EXPIRED MODAL
          ════════════════════════════════════════════════════════════════ */}
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
              onClick={() => signOut({ callbackUrl: '/login' })}
              className="w-full rounded-xl bg-primary py-3 px-4 font-bold text-on-primary transition-opacity hover:opacity-90"
            >
              {t.auth.sessionModalCta}
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default ModuleHeader;

'use client';

import React, { useEffect, useState, useMemo } from 'react';
import {
  Compass, ShieldCheck, Anchor, Ship, Truck,
  Boxes, BarChart3, Users, ShieldAlert, Wrench,
  Landmark, KeyRound, MessageSquare, BookOpen, Layers,
  Fuel, AlertTriangle, Scale, Award,
  Clock, ShoppingCart, FileCheck, QrCode, Building,
  Warehouse, UserCheck, Receipt, FileText, CheckCircle2
} from 'lucide-react';
import {
  resolveDomainLoadingConfig,
  DomainLoadingConfig
} from '@/config/domainLoadingConfig';
import { useSettings } from '@/components/layout/SettingsProvider';

interface DomainLoadingExperienceProps {
  /**
   * Route cible (ex: '/comptabilite-ohada', '/chat', '/port-operations', etc.)
   * ou clé de domaine directe
   */
  targetDomain?: string;
  /**
   * Pourcentage optionnel si contrôlé par le parent (0 à 100)
   */
  progress?: number;
  /**
   * Durée totale de la progression interne en ms si auto-gérée (défaut: 1800ms)
   */
  durationMs?: number;
  /**
   * Callback déclenché à 100%
   */
  onComplete?: () => void;
  /**
   * Titre personnalisé optionnel
   */
  customTitle?: string;
  /**
   * Sous-titre personnalisé optionnel
   */
  customSubtitle?: string;
  /**
   * Mode plein écran fixe (true) ou conteneur intégré (false)
   */
  fullScreen?: boolean;
}

/**
 * Associe une icône emblématique officielle à chaque département ou type d'animation.
 * Grandes icônes nettes, parlantes et immédiatement reconnaissables.
 */
function getDomainIcon(config: DomainLoadingConfig) {
  const { key, animationType } = config;

  switch (animationType) {
    case 'syscohada-ledger':
      return BookOpen;
    case 'treasury-flux':
      return Landmark;
    case 'radar-maritime':
      return Ship;
    case 'crane-sts':
      return Anchor;
    case 'customs-laser':
      return FileCheck;
    case 'dum-customs-stamp':
      return ShieldCheck;
    case 'telematics-satellite':
    case 'truck-dashboard':
      return Truck;
    case 'wms-lidar':
      return Warehouse;
    case 'rf-scan-gun':
      return QrCode;
    case 'container-3d-lifecycle':
      return Boxes;
    case 'gmao-gears':
    case 'workshop-wrench':
      return Wrench;
    case 'fuel-gauge':
      return Fuel;
    case 'isps-shield':
      return ShieldAlert;
    case 'incident-beacon':
      return AlertTriangle;
    case 'biometric-ring':
      return Users;
    case 'employee-badge':
      return UserCheck;
    case 'shift-clock':
      return Clock;
    case 'expense-voucher':
      return Receipt;
    case 'synergy-constellation':
      return MessageSquare;
    case 'collaborator-hub':
      return Layers;
    case 'b2b-gateway':
      return Building;
    case 'pricing-scale':
      return Scale;
    case 'procurement-cart':
      return ShoppingCart;
    case 'tax-dgi':
      return Landmark;
    case 'bi-prism':
      return BarChart3;
    case 'rbac-matrix':
      return KeyRound;
    case 'strategic-compass':
    default:
      if (key.includes('compta')) return BookOpen;
      if (key.includes('finance') || key.includes('tresor')) return Landmark;
      if (key.includes('port') || key.includes('navire')) return Ship;
      if (key.includes('acconage')) return Anchor;
      if (key.includes('transit') || key.includes('douane')) return FileCheck;
      if (key.includes('transport') || key.includes('camion') || key.includes('chauffeur')) return Truck;
      if (key.includes('stock') || key.includes('magasin')) return Warehouse;
      if (key.includes('parc') || key.includes('maintenance')) return Wrench;
      if (key.includes('qhse') || key.includes('securite')) return ShieldAlert;
      if (key.includes('rh') || key.includes('personnel')) return Users;
      if (key.includes('chat') || key.includes('message')) return MessageSquare;
      if (key.includes('client') || key.includes('b2b')) return Building;
      if (key.includes('bi') || key.includes('stat') || key.includes('report')) return BarChart3;
      if (key.includes('admin')) return KeyRound;
      return Compass;
  }
}

/**
 * Assombrit une couleur hex (ex. #3b82f6) d'un facteur donné (0..1).
 * Les teintes signature des modules sont écrites pour le fond SOMBRE (vives /
 * claires) : posées telles quelles sur un fond CLAIR, les textes/icônes d'accent
 * (pourcentage, libellés, médaillon, badge) deviennent illisibles. On les fonce
 * pour garantir un contraste suffisant en thème clair, tout en gardant l'identité.
 */
function darkenHex(hex: string, amount: number): string {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex.trim());
  if (!m) return hex;
  const f = 1 - Math.max(0, Math.min(1, amount));
  const r = Math.round(parseInt(m[1], 16) * f);
  const g = Math.round(parseInt(m[2], 16) * f);
  const b = Math.round(parseInt(m[3], 16) * f);
  return `#${[r, g, b].map((v) => v.toString(16).padStart(2, '0')).join('')}`;
}

/**
 * Nettoie les messages d'étapes des préfixes techniques (▶, ✓)
 * pour un affichage limpide et naturel.
 */
function cleanStepMessage(message: string): string {
  if (!message) return 'Chargement des données en cours...';
  return message
    .replace(/^[▶✓•\s-]+/, '')
    .trim();
}

/**
 * COMPOSANT DE CHARGEMENT SOBRE, ÉLÉGANT & ACCESSIBLE
 * Conçu spécialement pour une lecture facile et immédiate (ergonomie seniors & direction).
 * - Identité fidèle aux couleurs officielles de chaque module
 * - Absence totale de gadgets cyberpunk agressifs ou de particules perturbantes
 * - Typographie contrastée, grande taille et mise en page aérée
 */
export default function DomainLoadingExperience({
  targetDomain = 'dashboard',
  progress: externalProgress,
  durationMs = 1800,
  onComplete,
  customTitle,
  customSubtitle,
  fullScreen = true,
}: DomainLoadingExperienceProps) {
  const { theme } = useSettings();
  const isLight =
    theme === 'light' ||
    (theme === 'system' &&
      typeof window !== 'undefined' &&
      typeof window.matchMedia === 'function' &&
      window.matchMedia('(prefers-color-scheme: light)').matches);

  const config = useMemo(() => resolveDomainLoadingConfig(targetDomain), [targetDomain]);
  const [internalProgress, setInternalProgress] = useState(0);

  useEffect(() => {
    if (typeof externalProgress === 'number') return;
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const pct = Math.min(100, Math.round((elapsed / durationMs) * 100));
      setInternalProgress(pct);
      if (pct >= 100) {
        clearInterval(interval);
        if (onComplete) {
          const timer = setTimeout(onComplete, 250);
          return () => clearTimeout(timer);
        }
      }
    }, 25);
    return () => clearInterval(interval);
  }, [externalProgress, durationMs, onComplete]);

  const activeProgress = typeof externalProgress === 'number' ? externalProgress : internalProgress;

  const currentStepMessage = useMemo(() => {
    const steps = config.steps;
    let raw = steps[0];
    if (activeProgress >= 88) raw = steps[3] ?? steps[2];
    else if (activeProgress >= 58) raw = steps[2] ?? steps[1];
    else if (activeProgress >= 28) raw = steps[1] ?? steps[0];
    return cleanStepMessage(raw);
  }, [activeProgress, config.steps]);

  const IconComponent = useMemo(() => getDomainIcon(config), [config]);

  // Palette adaptée au thème : le fond et les accents sont en styles inline
  // (dégradés/lueur), donc le filet CSS .light ne peut pas les inverser ici.
  const surfaceBase = isLight ? '#eef1f5' : '#030712';
  const radialBg = isLight
    ? `radial-gradient(circle at 50% 42%, ${config.primaryColor}14 0%, rgba(255, 255, 255, 0.85) 55%, ${surfaceBase} 100%)`
    : `radial-gradient(circle at 50% 42%, ${config.primaryColor}18 0%, rgba(3, 7, 18, 0.95) 60%, #030712 100%)`;
  const medaillonBg = isLight ? 'rgba(255, 255, 255, 0.82)' : 'rgba(15, 23, 42, 0.85)';
  // En clair, la teinte "accent" (pastel, écrite pour le sombre) devient
  // illisible : on bascule les textes/icônes d'accent sur la couleur primaire.
  const accentInk = isLight ? darkenHex(config.primaryColor, 0.42) : config.accentColor;

  const inkClass = isLight ? 'text-slate-800' : 'text-white';
  const containerClasses = fullScreen
    ? `fixed inset-0 z-[120] flex flex-col justify-between items-center p-6 sm:p-10 md:p-14 overflow-hidden select-none ${inkClass}`
    : `relative w-full min-h-[580px] flex flex-col justify-between items-center p-6 sm:p-10 overflow-hidden select-none ${inkClass} rounded-3xl border border-slate-800/80 shadow-2xl`;

  return (
    <div
      className={containerClasses}
      style={{
        backgroundColor: surfaceBase,
        backgroundImage: radialBg,
      }}
    >
      {/* ── LUEUR D'AMBIANCE APAISANTE (Douce et feutrée, sans clignotement) ── */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[520px] h-[520px] rounded-full blur-[140px] pointer-events-none opacity-20"
        style={{ backgroundColor: config.primaryColor }}
      />

      {/* ── EN-TÊTE SOBRE & ÉPURÉ ── */}
      <header className="relative z-10 w-full max-w-4xl flex items-center justify-between border-b border-slate-800/80 pb-4">
        {/* Identité de marque EVO-LOG */}
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center font-black text-sm text-white shadow-md border"
            style={{
              backgroundColor: `${config.primaryColor}22`,
              borderColor: `${config.primaryColor}66`,
              color: accentInk,
            }}
          >
            EV
          </div>
          <div>
            <span className="block text-sm font-bold tracking-wider text-white">EVO-LOG ERP</span>
            <span className="block text-xs text-slate-400 font-medium">Système Portuaire & Logistique</span>
          </div>
        </div>

        {/* Repère de département officiel */}
        <div className="flex items-center gap-2">
          {config.departmentNumber > 0 ? (
            <span
              className="px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase border shadow-sm"
              style={{
                backgroundColor: `${config.primaryColor}15`,
                borderColor: `${config.primaryColor}55`,
                color: accentInk,
              }}
            >
              Département N° {config.departmentNumber.toString().padStart(2, '0')}
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase border border-slate-700 bg-slate-800/60 text-slate-300">
              Supervision Générale
            </span>
          )}
        </div>
      </header>

      {/* ── CORPS CENTRAL : MÉDAILLON, NOM DU DÉPARTEMENT & DESCRIPTION PARLANTE ── */}
      <main className="relative z-10 flex flex-col items-center text-center my-auto max-w-2xl px-4 w-full">
        {/* Médaillon officiel du département : grand, noble, rassurant */}
        <div className="relative mb-6">
          <div
            className="w-24 h-24 sm:w-28 sm:h-28 rounded-3xl flex items-center justify-center border-2 backdrop-blur-md transition-transform duration-700"
            style={{
              backgroundColor: medaillonBg,
              borderColor: `${config.primaryColor}88`,
              boxShadow: `0 14px 40px ${config.primaryColor}25`,
              animation: 'domainIconBreathe 3.5s ease-in-out infinite',
            }}
          >
            <IconComponent
              className="w-12 h-12 sm:w-14 sm:h-14 transition-all duration-300 drop-shadow"
              style={{ color: accentInk }}
              strokeWidth={1.8}
            />
          </div>
        </div>

        {/* Indication d'accès */}
        <span
          className="text-xs sm:text-sm font-bold tracking-[0.25em] uppercase mb-2"
          style={{ color: accentInk }}
        >
          Ouverture de l&apos;espace
        </span>

        {/* Grand Nom du Département / Module (parfaitement lisible, fort contraste) */}
        <h1 className="text-2xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight uppercase leading-tight mb-3">
          {customTitle || config.domainName}
        </h1>

        {/* Sous-titre parlant et explicite */}
        <p className="text-sm sm:text-base md:text-lg text-slate-300 font-normal leading-relaxed max-w-xl mb-4">
          {customSubtitle || config.subTitle}
        </p>

        {/* Badge de contexte institutionnel / localisation */}
        {config.locationTag && (
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-medium text-slate-300 bg-slate-900/80 border border-slate-800 mb-6">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: config.primaryColor }}
            />
            <span>{config.locationTag}</span>
          </div>
        )}

        {/* ── ZONE DE CHARGEMENT SOBRE & ÉLÉGANTE ── */}
        <div className="w-full max-w-lg bg-slate-900/80 border border-slate-800/90 p-5 sm:p-6 rounded-2xl shadow-xl backdrop-blur-md">
          {/* Ligne pourcentage et état */}
          <div className="flex items-center justify-between text-sm mb-3">
            <span className="font-semibold text-slate-300 flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full animate-pulse"
                style={{ backgroundColor: config.primaryColor }}
              />
              Chargement en cours...
            </span>
            <span
              className="text-lg font-bold tabular-nums"
              style={{ color: accentInk }}
            >
              {activeProgress}%
            </span>
          </div>

          {/* Barre de progression épurée */}
          <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-800 p-0.5">
            <div
              className="h-full rounded-full transition-all duration-150"
              style={{
                width: `${activeProgress}%`,
                background: `linear-gradient(90deg, ${config.primaryColor} 0%, ${accentInk} 100%)`,
                boxShadow: `0 0 14px ${config.primaryColor}66`,
              }}
            />
          </div>

          {/* Message d'étape clair et informatif */}
          <div className="mt-3.5 min-h-[24px] flex items-center justify-center text-xs sm:text-sm text-slate-300 font-medium transition-all duration-300">
            {activeProgress === 100 ? (
              <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                <CheckCircle2 className="w-4 h-4" />
                Département prêt, ouverture imminente...
              </span>
            ) : (
              <span>{currentStepMessage}</span>
            )}
          </div>
        </div>
      </main>

      {/* ── PIED DE PAGE DISCRET & INSTITUTIONNEL ── */}
      <footer className="relative z-10 w-full max-w-4xl flex items-center justify-between text-xs text-slate-500 border-t border-slate-800/80 pt-3">
        <span>EVO-LOG Enterprise • Plateforme Portuaire & Douanière</span>
        <span className="hidden sm:inline font-medium text-slate-400">
          Système Sécurisé CEMAC & OHADA
        </span>
        <span>Version 2.0</span>
      </footer>

      {/* ── ANIMATION DE RESPIRATION DOUCE (Sans aucune saccade ni fatigue visuelle) ── */}
      <style>{`
        @keyframes domainIconBreathe {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.04);
          }
        }
      `}</style>
    </div>
  );
}

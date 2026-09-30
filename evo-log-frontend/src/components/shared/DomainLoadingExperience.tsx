'use client';

import React, { useEffect, useState, useMemo } from 'react';
import {
  Compass, Radio, Sparkles, ShieldCheck, Anchor, Ship, Truck,
  Boxes, Calculator, BarChart3, Users, ShieldAlert, Wrench,
  Globe, Landmark, KeyRound, MessageSquare, BookOpen, Layers,
  CheckCircle2, ArrowRight, Fuel, AlertOctagon, Scale, Award,
  Clock, Tag, ShoppingCart, FileCheck, QrCode, FileText
} from 'lucide-react';
import {
  resolveDomainLoadingConfig,
  DomainLoadingConfig,
  DomainAnimationType
} from '@/config/domainLoadingConfig';

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
   * Durée totale de la progression interne en ms si auto-gérée (défaut: 2400ms)
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
 * MOTEUR D'ANIMATION SIGNATURE DES 28 DÉPARTEMENTS
 */
function DomainSignatureVisual({
  config,
  progress
}: {
  config: DomainLoadingConfig;
  progress: number;
}) {
  const { animationType, primaryColor, accentColor } = config;

  switch (animationType) {
    // ═════════════════════════════════════════════════════════════════════════
    // 1. COMPTABILITÉ OHADA : Balance bilatérale Débit/Crédit & Grand Livre
    // ═════════════════════════════════════════════════════════════════════════
    case 'syscohada-ledger':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-0 rounded-3xl opacity-20 border"
            style={{
              borderColor: `${primaryColor}40`,
              backgroundImage: `linear-gradient(${primaryColor}33 1px, transparent 1px), linear-gradient(90deg, ${primaryColor}33 1px, transparent 1px)`,
              backgroundSize: '24px 24px',
              animation: 'ledgerGridPulse 4s ease-in-out infinite',
            }}
          />
          <div
            className="absolute inset-x-8 h-1 blur-sm rounded-full"
            style={{
              background: `linear-gradient(90deg, transparent, ${primaryColor}, ${accentColor}, transparent)`,
              animation: 'scanSweep 2.8s ease-in-out infinite',
            }}
          />
          <div
            className="absolute inset-2 rounded-full border-2 border-dashed"
            style={{ borderColor: `${primaryColor}66`, animation: 'spinSlow 14s linear infinite' }}
          />
          <div
            className="absolute inset-8 rounded-full border"
            style={{ borderColor: `${accentColor}55`, animation: 'spinSlow 8s linear infinite reverse' }}
          />
          <div
            className="absolute inset-0 flex items-center justify-center pointer-events-none"
            style={{ animation: 'spinSlow 18s linear infinite' }}
          >
            <div className="absolute -top-3 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-violet-950 border border-violet-400 text-violet-300 shadow-lg">
              DÉBIT (+)
            </div>
            <div className="absolute -bottom-3 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-950 border border-amber-400 text-amber-300 shadow-lg">
              CRÉDIT (−)
            </div>
          </div>
          {['601', '701', '521', '411', '101', '401'].map((code, i) => (
            <span
              key={code}
              className="absolute font-mono text-[11px] font-black pointer-events-none transition-all duration-700"
              style={{
                color: i % 2 === 0 ? primaryColor : accentColor,
                top: `${50 + 38 * Math.sin((i * 60 * Math.PI) / 180 + progress * 0.05)}%`,
                left: `${50 + 38 * Math.cos((i * 60 * Math.PI) / 180 + progress * 0.05)}%`,
                transform: 'translate(-50%, -50%)',
                textShadow: `0 0 10px ${primaryColor}88`,
              }}
            >
              Cpte {code}
            </span>
          ))}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor}dd 0%, #4c1d95 60%, #1e1b4b 100%)`,
              borderColor: `${accentColor}88`,
              boxShadow: `0 0 35px ${primaryColor}66`,
            }}
          >
            <BookOpen className="w-9 h-9 text-amber-300 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-white tracking-widest mt-0.5">SYSCOHADA</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 2. FINANCE & TRÉSORERIE : Flux de capitaux & Ondes bancaires
    // ═════════════════════════════════════════════════════════════════════════
    case 'treasury-flux':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {[120, 180, 240, 290].map((size, i) => (
            <div
              key={size}
              className="absolute rounded-full border"
              style={{
                width: `${size}px`,
                height: `${size}px`,
                borderColor: `${primaryColor}${i === 0 ? '66' : i === 1 ? '44' : '22'}`,
                animation: `pulseWave ${3 + i}s ease-in-out infinite`,
                animationDelay: `${i * 0.4}s`,
              }}
            />
          ))}
          {['XAF', 'EUR', 'USD', 'FCFA'].map((curr, idx) => (
            <div
              key={curr}
              className="absolute font-mono font-bold text-xs px-2 py-0.5 rounded-lg border shadow-lg"
              style={{
                borderColor: `${accentColor}88`,
                backgroundColor: '#022c22',
                color: accentColor,
                top: `${50 + 36 * Math.sin(((idx * 90 + progress * 2) * Math.PI) / 180)}%`,
                left: `${50 + 36 * Math.cos(((idx * 90 + progress * 2) * Math.PI) / 180)}%`,
                transform: 'translate(-50%, -50%)',
                boxShadow: `0 0 14px ${primaryColor}66`,
              }}
            >
              {curr}
            </div>
          ))}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #064e3b 100%)`,
              borderColor: `${primaryColor}aa`,
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Landmark className="w-10 h-10 text-emerald-100" />
            <span className="text-[9px] font-mono font-black text-emerald-200 tracking-wider">TRÉSORERIE</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 3. PORT OPERATIONS : Radar Maritime Douala / Kribi
    // ═════════════════════════════════════════════════════════════════════════
    case 'radar-maritime':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: `conic-gradient(from 0deg, ${primaryColor}55 0deg, ${primaryColor}0d 60deg, transparent 90deg)`,
              animation: 'radarSweep 3.5s linear infinite',
            }}
          />
          {[120, 180, 240, 300].map((size, i) => (
            <div
              key={size}
              className="absolute rounded-full border"
              style={{ width: `${size}px`, height: `${size}px`, borderColor: `${primaryColor}${i === 3 ? '22' : '33'}` }}
            />
          ))}
          <div className="absolute inset-x-0 h-px bg-sky-500/20" />
          <div className="absolute inset-y-0 w-px bg-sky-500/20" />
          <div className="absolute top-[28%] left-[68%] flex items-center gap-1 text-[10px] font-mono text-sky-300 font-bold animate-pulse">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400 shadow-md shadow-sky-400" />
            <span>CARGO DOUALA #42</span>
          </div>
          <div className="absolute bottom-[30%] left-[24%] flex items-center gap-1 text-[10px] font-mono text-amber-300 font-bold animate-pulse">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-md shadow-amber-400" />
            <span>REMORQUEUR PAD</span>
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #0369a1 60%, #082f49 100%)`,
              borderColor: `${accentColor}88`,
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Ship className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-sky-100 tracking-wider">RADAR 360°</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 4. ACCONAGE & MANUTENTION : Grue Portique STS & Levage de Conteneurs
    // ═════════════════════════════════════════════════════════════════════════
    case 'crane-sts':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Lignes du portique STS géant */}
          <svg className="absolute inset-0 w-full h-full opacity-60" viewBox="0 0 300 300">
            <line x1="60" y1="260" x2="120" y2="40" stroke={primaryColor} strokeWidth="3" />
            <line x1="240" y1="260" x2="180" y2="40" stroke={primaryColor} strokeWidth="3" />
            <line x1="100" y1="40" x2="200" y2="40" stroke={primaryColor} strokeWidth="4" />
            <line x1="80" y1="160" x2="220" y2="160" stroke={primaryColor} strokeWidth="2" strokeDasharray="4 4" />
            {/* Câbles de levage motorisés */}
            <line x1="150" y1="40" x2="150" y2="130" stroke="#f59e0b" strokeWidth="2.5" />
          </svg>
          {/* Conteneur suspendu au portique */}
          <div
            className="absolute w-32 h-14 rounded-lg border-2 shadow-2xl flex items-center justify-center"
            style={{
              top: '125px',
              backgroundColor: '#0f2942',
              borderColor: '#f59e0b',
              boxShadow: '0 0 25px rgba(245, 158, 11, 0.5)',
              animation: 'floatDot 2.5s ease-in-out infinite',
            }}
          >
            <div className="flex flex-col items-center">
              <span className="text-[10px] font-mono font-black text-amber-400">CADC-EVP 40&apos;</span>
              <span className="text-[8px] font-mono text-slate-300">LEVAGE QUAI STS #2</span>
            </div>
          </div>
          <div
            className="relative z-10 w-16 h-16 rounded-2xl flex items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #1e3a8a 100%)`,
              borderColor: '#60a5fa',
              boxShadow: `0 0 30px ${primaryColor}88`,
            }}
          >
            <Anchor className="w-8 h-8 text-amber-300" />
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 5. TRANSIT & GUICHET GUCE : Scan laser de manifestes & Sydonia++
    // ═════════════════════════════════════════════════════════════════════════
    case 'customs-laser':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-x-4 h-1.5 rounded-full blur-[2px]"
            style={{
              background: `linear-gradient(90deg, transparent, ${primaryColor}, #60a5fa, transparent)`,
              animation: 'scanSweep 2.5s ease-in-out infinite',
            }}
          />
          <div className="absolute inset-4 rounded-full border-2 border-dashed border-blue-500/40" style={{ animation: 'spinSlow 10s linear infinite' }} />
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-blue-950 border border-blue-400 text-blue-200">
            GUCE CAMEROUN • SYDONIA++
          </div>
          <div className="absolute bottom-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-blue-950 border border-blue-400 text-blue-200">
            CONNAISSEMENT B/L CERTIFIÉ
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #1e40af 100%)`,
              borderColor: '#93c5fd',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <FileCheck className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-blue-200 tracking-wider">GUCE TRANSIT</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 6. DÉDOUANEMENT RÉEL & DUM : Tampon officiel et liquidation
    // ═════════════════════════════════════════════════════════════════════════
    case 'dum-customs-stamp':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute w-56 h-56 rounded-full border-4 border-dashed"
            style={{ borderColor: `${primaryColor}66`, animation: 'spinSlow 12s linear infinite' }}
          />
          <div
            className="absolute w-44 h-44 rounded-2xl border-2 flex items-center justify-center bg-sky-950/40"
            style={{ borderColor: accentColor, transform: 'rotate(-12deg)' }}
          >
            <div className="text-center">
              <span className="block text-[11px] font-mono font-black text-amber-400 tracking-widest uppercase">
                DOUANE CAMEROUN
              </span>
              <span className="block text-sm font-black text-white uppercase tracking-wider my-0.5">
                BAE ACCORDÉ
              </span>
              <span className="block text-[9px] font-mono text-sky-300">
                DUM LIQUIDÉE • TAXES OK
              </span>
            </div>
          </div>
          <div
            className="relative z-10 w-16 h-16 rounded-2xl flex items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #0369a1 100%)`,
              borderColor: '#38bdf8',
              boxShadow: `0 0 30px ${primaryColor}88`,
            }}
          >
            <ShieldCheck className="w-9 h-9 text-amber-300" />
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 7. TRANSPORT & FLOTTE : Visée satellitaire GPS & Corridors CEMAC
    // ═════════════════════════════════════════════════════════════════════════
    case 'telematics-satellite':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div className="absolute inset-4 rounded-full border border-cyan-500/30" style={{ animation: 'spinSlow 16s linear infinite' }} />
          <div className="absolute inset-10 rounded-full border border-dashed border-cyan-400/40" style={{ animation: 'spinSlow 10s linear infinite reverse' }} />
          <div className="absolute inset-x-0 h-px bg-cyan-500/30" />
          <div className="absolute inset-y-0 w-px bg-cyan-500/30" />
          {[
            { label: 'YAOUNDÉ', angle: 45 },
            { label: 'N\'DJAMENA', angle: 135 },
            { label: 'BANGUI', angle: 225 },
            { label: 'DOUALA (HUB)', angle: 315 },
          ].map((pt) => (
            <div
              key={pt.label}
              className="absolute font-mono text-[9px] font-bold px-2 py-0.5 rounded bg-cyan-950 border border-cyan-400 text-cyan-200"
              style={{
                top: `${50 + 38 * Math.sin((pt.angle * Math.PI) / 180)}%`,
                left: `${50 + 38 * Math.cos((pt.angle * Math.PI) / 180)}%`,
                transform: 'translate(-50%, -50%)',
                boxShadow: '0 0 10px rgba(6,182,212,0.5)',
              }}
            >
              {pt.label}
            </div>
          ))}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #0e7490 100%)`,
              borderColor: '#67e8f9',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Truck className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-cyan-100 tracking-wider">TÉLÉMATIQUE</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 8. PORTAIL CHAUFFEUR : Tableau de bord camion & Tachygraphe
    // ═════════════════════════════════════════════════════════════════════════
    case 'truck-dashboard':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Cadran compteur de vitesse analogique */}
          <div
            className="absolute w-60 h-60 rounded-full border-4 border-slate-800 bg-slate-950 flex items-center justify-center"
            style={{ boxShadow: `0 0 35px ${primaryColor}44, inset 0 0 20px rgba(0,0,0,0.8)` }}
          >
            {/* Graduations compteur */}
            <div className="absolute inset-3 rounded-full border-2 border-dashed border-rose-500/40" />
            {/* Aiguille compteur animée */}
            <div
              className="absolute w-1 h-24 bg-gradient-to-t from-transparent to-rose-400 rounded-full origin-bottom"
              style={{
                top: '24px',
                transform: `rotate(${Math.sin(progress * 0.1) * 35 + 20}deg)`,
                boxShadow: '0 0 12px #f43f5e',
                transition: 'transform 0.1s linear',
              }}
            />
          </div>
          <div className="absolute top-8 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-rose-950 border border-rose-500 text-rose-200">
            TACHYGRAPHE NUMÉRIQUE ACTIF
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #be123c 100%)`,
              borderColor: '#fda4af',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Truck className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-rose-100 tracking-wider">CHAUFFEUR</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 9. MAGASIN & STOCK WMS : Racks 3D & Lidar Scanner
    // ═════════════════════════════════════════════════════════════════════════
    case 'wms-lidar':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-4 rounded-2xl border border-amber-500/30 opacity-40"
            style={{
              backgroundImage: 'linear-gradient(#f59e0b22 1px, transparent 1px), linear-gradient(90deg, #f59e0b22 1px, transparent 1px)',
              backgroundSize: '20px 20px',
            }}
          />
          <div
            className="absolute inset-x-8 h-1 rounded-full blur-[1px]"
            style={{
              background: 'linear-gradient(90deg, transparent, #ef4444, #f59e0b, transparent)',
              animation: 'scanSweep 2.2s ease-in-out infinite',
            }}
          />
          {['RACK-A1', 'RACK-B4', 'COLIS-99', 'ZONE-CALE'].map((tag, idx) => (
            <div
              key={tag}
              className="absolute font-mono text-[9px] font-bold px-2 py-0.5 rounded bg-amber-950 border border-amber-500 text-amber-200"
              style={{
                top: `${50 + 36 * Math.sin(((idx * 90 + 30) * Math.PI) / 180)}%`,
                left: `${50 + 36 * Math.cos(((idx * 90 + 30) * Math.PI) / 180)}%`,
                transform: 'translate(-50%, -50%)',
              }}
            >
              {tag}
            </div>
          ))}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #b45309 100%)`,
              borderColor: '#fde68a',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Boxes className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-slate-950 tracking-wider">STOCK WMS</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 10. PORTAIL MAGASINIER : Douchette RF & Scan-Gun
    // ═════════════════════════════════════════════════════════════════════════
    case 'rf-scan-gun':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute w-52 h-36 rounded-2xl border-2 border-zinc-600 bg-zinc-950/80 p-3 flex flex-col justify-between"
            style={{ boxShadow: '0 0 25px rgba(245, 158, 11, 0.3)' }}
          >
            <div className="flex items-center justify-between text-[10px] font-mono text-zinc-400 border-b border-zinc-800 pb-1">
              <span>RF TERMINAL</span>
              <span className="text-amber-400 font-bold">READY</span>
            </div>
            {/* Lignes de code-barres simulées */}
            <div className="flex items-center justify-center gap-1 h-12 bg-white/10 rounded p-1">
              {[4, 2, 6, 3, 5, 2, 4, 3, 6, 2, 5, 3, 4, 2, 5, 3].map((w, idx) => (
                <div key={idx} className="bg-amber-400 h-full" style={{ width: `${w}px` }} />
              ))}
            </div>
            <div className="text-[9px] font-mono text-center text-zinc-400">GS1-128 / CODE 39 SCAN</div>
          </div>
          <div
            className="relative z-10 w-16 h-16 rounded-2xl flex items-center justify-center shadow-2xl border mt-32"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #3f3f46 100%)`,
              borderColor: '#f59e0b',
              boxShadow: '0 0 25px rgba(245,158,11,0.5)',
            }}
          >
            <QrCode className="w-8 h-8 text-amber-300" />
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 11. CYCLE DE VIE CONTENEURS : Conteneur ISO 3D & IoT Tracker
    // ═════════════════════════════════════════════════════════════════════════
    case 'container-3d-lifecycle':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Orbite de cycle */}
          <div
            className="absolute inset-6 rounded-full border-2 border-dashed border-purple-500/40"
            style={{ animation: 'spinSlow 14s linear infinite' }}
          />
          {/* Conteneur 3D isométrique */}
          <div
            className="absolute w-40 h-20 rounded-xl border-2 flex items-center justify-between px-3"
            style={{
              backgroundColor: '#1a0b2e',
              borderColor: '#06b6d4',
              boxShadow: '0 0 30px rgba(6, 182, 212, 0.4)',
              transform: 'perspective(400px) rotateX(15deg) rotateY(-10deg)',
            }}
          >
            <div className="flex flex-col">
              <span className="text-[10px] font-mono font-black text-cyan-400">MSKU 942851-2</span>
              <span className="text-[9px] font-mono text-purple-300">40&apos; HIGH CUBE</span>
            </div>
            <span className="w-3 h-3 rounded-full bg-emerald-400 animate-ping shadow-md shadow-emerald-400" />
          </div>
          <div
            className="relative z-10 w-16 h-16 rounded-2xl flex items-center justify-center shadow-2xl border mt-28"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #4c1d95 100%)`,
              borderColor: '#c084fc',
              boxShadow: `0 0 30px ${primaryColor}88`,
            }}
          >
            <Boxes className="w-8 h-8 text-cyan-300" />
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 12. PARC VÉHICULES : Double engrenages & Télémétrie moteur
    // ═════════════════════════════════════════════════════════════════════════
    case 'gmao-gears':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute top-8 left-8 w-28 h-28 rounded-full border-4 border-dashed border-orange-500/40"
            style={{ animation: 'spinSlow 6s linear infinite' }}
          />
          <div
            className="absolute bottom-8 right-8 w-36 h-36 rounded-full border-4 border-dashed border-orange-400/40"
            style={{ animation: 'spinSlow 8s linear infinite reverse' }}
          />
          <div className="absolute top-2 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-orange-950 border border-orange-500 text-orange-200">
            DIAGNOSTIC TÉLÉMÉTRIQUE GMAO
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #c2410c 100%)`,
              borderColor: '#fed7aa',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Wrench className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-slate-950 tracking-wider">ENGINS</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 13. MAINTENANCE GMAO ATELIER : Clé & Banc d'essai
    // ═════════════════════════════════════════════════════════════════════════
    case 'workshop-wrench':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute w-56 h-56 rounded-full border-2 border-dashed border-orange-500/40"
            style={{ animation: 'spinSlow 10s linear infinite' }}
          />
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-stone-900 border border-orange-500 text-orange-200">
            BANC DE DIAGNOSTIC ATELIER
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #7c2d12 100%)`,
              borderColor: '#fdba74',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Wrench className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-orange-200 tracking-wider">GMAO</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 14. FUEL GUARD : Jauge cuve & Débitmètre
    // ═════════════════════════════════════════════════════════════════════════
    case 'fuel-gauge':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Cuve de carburant stylisée */}
          <div
            className="absolute w-44 h-48 rounded-3xl border-2 border-amber-500/50 bg-slate-950 p-3 flex flex-col justify-end overflow-hidden"
            style={{ boxShadow: '0 0 30px rgba(245, 158, 11, 0.3)' }}
          >
            {/* Niveau de gazole animé */}
            <div
              className="w-full rounded-2xl transition-all duration-300"
              style={{
                height: `${progress}%`,
                background: 'linear-gradient(180deg, #f59e0b 0%, #b45309 100%)',
                boxShadow: '0 0 15px rgba(245, 158, 11, 0.6)',
              }}
            />
          </div>
          <div className="absolute top-2 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-amber-950 border border-amber-500 text-amber-200">
            JAUGE ÉLECTRONIQUE • SÉCURITÉ CUVES
          </div>
          <div
            className="relative z-10 w-16 h-16 rounded-2xl flex items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #92400e 100%)`,
              borderColor: '#fde68a',
              boxShadow: `0 0 30px ${primaryColor}88`,
            }}
          >
            <Fuel className="w-8 h-8 text-white" />
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 15. QHSE SÉCURITÉ : Bouclier hexagonal ISPS
    // ═════════════════════════════════════════════════════════════════════════
    case 'isps-shield':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {[140, 200, 260].map((size, i) => (
            <div
              key={size}
              className="absolute rounded-full border border-red-500/30"
              style={{
                width: `${size}px`,
                height: `${size}px`,
                animation: `pulseWave ${2.5 + i}s ease-in-out infinite`,
                animationDelay: `${i * 0.3}s`,
              }}
            />
          ))}
          <div className="absolute top-3 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-red-950 border border-red-500 text-red-200">
            CODE ISPS • SÉCURITÉ PORTUAIRE
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #991b1b 100%)`,
              borderColor: '#fca5a5',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <ShieldAlert className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-red-100 tracking-wider">ISPS</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 16. PORTAIL QHSE TERRAIN & INCIDENTS : Gyrophare & Alerte
    // ═════════════════════════════════════════════════════════════════════════
    case 'incident-beacon':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: `conic-gradient(from 0deg, rgba(239,68,68,0.4) 0deg, transparent 90deg)`,
              animation: 'radarSweep 1.8s linear infinite',
            }}
          />
          <div className="absolute top-3 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-rose-950 border border-rose-500 text-rose-200">
            CANAL ALERTE IMMÉDIATE QUAI
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #881337 100%)`,
              borderColor: '#f43f5e',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <AlertOctagon className="w-10 h-10 text-white animate-pulse" />
            <span className="text-[9px] font-mono font-black text-rose-100 tracking-wider">URGENCE</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 17. RH & CAPITAL HUMAIN : Anneau Biométrique & Équipes
    // ═════════════════════════════════════════════════════════════════════════
    case 'biometric-ring':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {[120, 180, 240].map((size, i) => (
            <div
              key={size}
              className="absolute rounded-full border border-dashed"
              style={{
                width: `${size}px`,
                height: `${size}px`,
                borderColor: `${primaryColor}${i === 0 ? '66' : '33'}`,
                animation: `spinSlow ${12 + i * 4}s linear infinite ${i % 2 === 0 ? '' : 'reverse'}`,
              }}
            />
          ))}
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-pink-950 border border-pink-500 text-pink-200">
            POINTAGE BIOMÉTRIQUE CONVENTIONNÉ
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #9d174d 100%)`,
              borderColor: '#f472b6',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Users className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-pink-100 tracking-wider">RH SOCIAL</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 18. PORTAIL EMPLOYÉ : Badge RFID lumineux
    // ═════════════════════════════════════════════════════════════════════════
    case 'employee-badge':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute w-44 h-56 rounded-2xl border-2 border-lime-500/60 bg-lime-950/40 p-4 flex flex-col items-center justify-between"
            style={{ boxShadow: '0 0 30px rgba(132, 204, 22, 0.4)' }}
          >
            <div className="w-12 h-12 rounded-full bg-lime-500/20 border border-lime-400 flex items-center justify-center">
              <Users className="w-6 h-6 text-lime-400" />
            </div>
            <div className="text-center">
              <span className="block text-[11px] font-bold text-white uppercase">AGENT CERTIFIÉ</span>
              <span className="block text-[9px] font-mono text-lime-300">ID: CADC-EMP-2026</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[8px] font-mono bg-lime-500 text-slate-950 font-black">
              RFID ACCRÉDITÉ
            </span>
          </div>
          <div
            className="relative z-10 w-14 h-14 rounded-2xl flex items-center justify-center shadow-2xl border mt-36"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #3f6212 100%)`,
              borderColor: '#bef264',
              boxShadow: `0 0 25px ${primaryColor}88`,
            }}
          >
            <Award className="w-7 h-7 text-white" />
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 19. CHEF DE PERSONNEL : Horloge de quart 3x8 & Roster
    // ═════════════════════════════════════════════════════════════════════════
    case 'shift-clock':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute w-60 h-60 rounded-full border-4 border-slate-800 bg-slate-950 flex items-center justify-center"
            style={{ boxShadow: '0 0 30px rgba(244, 63, 94, 0.4)' }}
          >
            {/* 3 secteurs des quarts (3x8) */}
            <div className="absolute top-4 text-[9px] font-mono font-bold text-amber-400">QUART MATIN</div>
            <div className="absolute bottom-4 text-[9px] font-mono font-bold text-cyan-400">QUART SOIR</div>
            <div className="absolute right-4 text-[9px] font-mono font-bold text-rose-400">QUART NUIT</div>
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #881337 100%)`,
              borderColor: '#fda4af',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Clock className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-rose-100 tracking-wider">SHIFTS 3X8</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 20. PORTAIL FRAIS : Reçu dématérialisé & Sceau
    // ═════════════════════════════════════════════════════════════════════════
    case 'expense-voucher':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute w-44 h-56 rounded-2xl border-2 border-teal-500/60 bg-teal-950/40 p-4 flex flex-col justify-between"
            style={{ boxShadow: '0 0 30px rgba(13, 148, 136, 0.4)' }}
          >
            <div className="flex items-center justify-between text-[10px] font-mono text-teal-300 border-b border-teal-800 pb-1">
              <span>BORDEREAU FRAIS</span>
              <span className="text-emerald-400 font-bold">VISE</span>
            </div>
            <div className="text-center py-2">
              <span className="block text-xs font-mono font-bold text-white">INDEMNITÉ CORRIDOR</span>
              <span className="block text-sm font-black text-teal-300 font-mono">XAF VALIDE</span>
            </div>
            <div className="text-[8px] font-mono text-center text-teal-400">SCELLÉ COMPTABLE</div>
          </div>
          <div
            className="relative z-10 w-14 h-14 rounded-2xl flex items-center justify-center shadow-2xl border mt-36"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #115e59 100%)`,
              borderColor: '#5eead4',
              boxShadow: `0 0 25px ${primaryColor}88`,
            }}
          >
            <FileText className="w-7 h-7 text-white" />
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 21. HUB COLLABORATIF & MESSAGERIE : Constellation
    // ═════════════════════════════════════════════════════════════════════════
    case 'synergy-constellation':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {[130, 190, 250].map((size, i) => (
            <div
              key={size}
              className="absolute rounded-full border border-dashed"
              style={{
                width: `${size}px`,
                height: `${size}px`,
                borderColor: `${primaryColor}${i === 0 ? '55' : '25'}`,
                animation: `spinSlow ${10 + i * 4}s linear infinite`,
              }}
            />
          ))}
          {[
            { label: 'QUAI', top: '22%', left: '22%' },
            { label: 'DISPATCH', top: '22%', left: '78%' },
            { label: 'COMPTA', top: '72%', left: '80%' },
            { label: 'FLOTTE', top: '72%', left: '20%' },
          ].map((node, i) => (
            <div
              key={node.label}
              className="absolute px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5 shadow-lg border"
              style={{
                top: node.top,
                left: node.left,
                transform: 'translate(-50%, -50%)',
                backgroundColor: '#052010',
                borderColor: `${primaryColor}88`,
                color: '#86efac',
                animation: `floatDot ${3 + i * 0.5}s ease-in-out infinite`,
              }}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>{node.label}</span>
            </div>
          ))}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #15803d 100%)`,
              borderColor: `${accentColor}88`,
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <MessageSquare className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-amber-200 tracking-wider">COLLAB</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 22. PORTAIL COLLABORATEUR CENTRAL : Carrefour des missions
    // ═════════════════════════════════════════════════════════════════════════
    case 'collaborator-hub':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-4 rounded-full border-2 border-dashed border-yellow-500/40"
            style={{ animation: 'spinSlow 12s linear infinite' }}
          />
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-yellow-950 border border-yellow-500 text-yellow-200">
            AIGUILLAGE OPÉRATIONNEL DES MISSIONS
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #a16207 100%)`,
              borderColor: '#fef08a',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Layers className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-white tracking-wider">HUB AGENT</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 23. CLIENT & PARTENAIRES B2B : Passerelle EDI
    // ═════════════════════════════════════════════════════════════════════════
    case 'b2b-gateway':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-4 rounded-full border border-teal-500/30"
            style={{ animation: 'spinSlow 10s linear infinite' }}
          />
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-teal-950 border border-teal-500 text-teal-200">
            PASSERELLE CRYPTÉE EDI 256-BIT
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #0f766e 100%)`,
              borderColor: '#2dd4bf',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Globe className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-teal-100 tracking-wider">B2B EDI</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 24. COTATIONS & COMMERCIAL : Balance tarifaire
    // ═════════════════════════════════════════════════════════════════════════
    case 'pricing-scale':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-yellow-950 border border-yellow-500 text-yellow-200">
            TARIFICATION FRET & SIMULATEUR DE MARGE
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #ca8a04 100%)`,
              borderColor: '#fde047',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Tag className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-slate-950 tracking-wider">COTATIONS</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 25. ACHATS & FOURNISSEURS : Chariot d'approvisionnement
    // ═════════════════════════════════════════════════════════════════════════
    case 'procurement-cart':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-950 border border-emerald-500 text-emerald-200">
            CENTRALE D&apos;ACHATS & VISA BUDGÉTAIRE
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #047857 100%)`,
              borderColor: '#6ee7b7',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <ShoppingCart className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-emerald-100 tracking-wider">ACHATS</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 26. FISCALITÉ CAMEROUN : Sceau DGI & TVA
    // ═════════════════════════════════════════════════════════════════════════
    case 'tax-dgi':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute w-52 h-52 rounded-full border-4 border-dashed border-violet-500/40"
            style={{ animation: 'spinSlow 14s linear infinite' }}
          />
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-violet-950 border border-violet-500 text-violet-200">
            DGI CAMEROUN • CGI TVA 19.25%
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #4c1d95 100%)`,
              borderColor: '#a78bfa',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Landmark className="w-10 h-10 text-amber-300 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-white tracking-wider">FISCALITÉ</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 27. DÉCISIONNEL & BI : Prisme holographique 3D
    // ═════════════════════════════════════════════════════════════════════════
    case 'bi-prism':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-4 rounded-2xl border border-purple-500/40"
            style={{ animation: 'spinSlow 10s linear infinite' }}
          />
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-purple-950 border border-purple-500 text-purple-200">
            CUBES OLAP & PRÉVISIONS LOGISTIQUES
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #6b21a8 100%)`,
              borderColor: '#c084fc',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <BarChart3 className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-purple-100 tracking-wider">DATA BI</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 28. GOUVERNANCE & ADMIN SAAS : Cylindre cryptographique RBAC
    // ═════════════════════════════════════════════════════════════════════════
    case 'rbac-matrix':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-4 rounded-full border-2 border-dashed border-slate-500/40"
            style={{ animation: 'spinSlow 12s linear infinite' }}
          />
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-slate-900 border border-slate-600 text-slate-200">
            MATRICE RBAC & SOUVERAINETÉ TENANT
          </div>
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #1e293b 100%)`,
              borderColor: '#94a3b8',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <KeyRound className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-slate-200 tracking-wider">SÉCURITÉ</span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // TRANSVERSAL : COCKPIT STRATÉGIQUE GLOBAL
    // ═════════════════════════════════════════════════════════════════════════
    default:
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div className="absolute inset-2 rounded-full border-2 border-dashed border-indigo-500/40" style={{ animation: 'spinSlow 12s linear infinite' }} />
          <div className="absolute inset-8 rounded-full border border-indigo-400/30" style={{ animation: 'spinSlow 7s linear infinite reverse' }} />
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #312e81 100%)`,
              borderColor: `${accentColor}aa`,
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Compass className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-amber-200 tracking-wider">COCKPIT</span>
          </div>
        </div>
      );
  }
}

/**
 * COMPOSANT DE CHARGEMENT HAUTE FIDÉLITÉ DES 28 DÉPARTEMENTS
 */
export default function DomainLoadingExperience({
  targetDomain = 'dashboard',
  progress: externalProgress,
  durationMs = 2400,
  onComplete,
  customTitle,
  customSubtitle,
  fullScreen = true,
}: DomainLoadingExperienceProps) {
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
        if (onComplete) setTimeout(onComplete, 350);
      }
    }, 25);
    return () => clearInterval(interval);
  }, [externalProgress, durationMs, onComplete]);

  const activeProgress = typeof externalProgress === 'number' ? externalProgress : internalProgress;

  const currentStepMessage = useMemo(() => {
    const steps = config.steps;
    if (activeProgress < 28) return steps[0];
    if (activeProgress < 58) return steps[1];
    if (activeProgress < 88) return steps[2];
    return steps[3];
  }, [activeProgress, config.steps]);

  const containerClasses = fullScreen
    ? 'fixed inset-0 z-[120] flex flex-col items-center justify-between p-4 sm:p-8 md:p-12 overflow-hidden select-none text-white'
    : 'relative w-full min-h-[620px] flex flex-col items-center justify-between p-6 sm:p-10 overflow-hidden select-none text-white rounded-3xl border border-slate-800';

  return (
    <div
      className={containerClasses}
      style={{
        background: `radial-gradient(circle at center, ${config.primaryColor}24 0%, #030816 65%, #01040a 100%)`,
        backgroundColor: '#020611',
      }}
    >
      {/* ── FOND PARTICULES & LUEURS DU DÉPARTEMENT ── */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute inset-0 opacity-[0.06]"
          style={{
            backgroundImage: `linear-gradient(${config.primaryColor} 1px, transparent 1px), linear-gradient(90deg, ${config.primaryColor} 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] rounded-full blur-[130px] opacity-25 pointer-events-none"
          style={{ backgroundColor: config.primaryColor }}
        />
        {[6, 4, 7, 3, 5, 8, 4, 6, 3, 7, 5, 4].map((size, i) => (
          <span
            key={i}
            className="absolute rounded-full"
            style={{
              width: `${size}px`,
              height: `${size}px`,
              backgroundColor: i % 2 === 0 ? config.primaryColor : config.accentColor,
              top: `${(i * 19 + 11) % 92}%`,
              left: `${(i * 27 + 13) % 94}%`,
              boxShadow: `0 0 12px ${config.primaryColor}`,
              opacity: 0.4 + (i % 3) * 0.2,
              animation: `floatDot ${3.5 + (i % 3)}s ease-in-out ${(i % 4) * 0.3}s infinite`,
            }}
          />
        ))}
      </div>

      {/* ── BANNIÈRE TÉLÉMÉTRIE SUPÉRIEURE AVEC NUMÉRO DE DÉPARTEMENT ── */}
      <header className="relative z-10 w-full max-w-5xl flex items-center justify-between text-[11px] font-mono border-b pb-2 pt-1 border-slate-800">
        <div className="flex items-center gap-2" style={{ color: `${config.accentColor}cc` }}>
          <Compass className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '10s' }} />
          <span className="hidden sm:inline font-bold tracking-wider">{config.locationTag}</span>
        </div>

        <div className="flex items-center gap-2">
          {config.departmentNumber > 0 && (
            <span
              className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-black uppercase tracking-widest border"
              style={{
                backgroundColor: `${config.primaryColor}22`,
                borderColor: `${config.primaryColor}88`,
                color: config.accentColor,
              }}
            >
              DÉPARTEMENT N° {config.departmentNumber.toString().padStart(2, '0')}
            </span>
          )}

          <div
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase backdrop-blur-md shadow-lg border"
            style={{
              backgroundColor: '#0a101f',
              borderColor: `${config.primaryColor}66`,
              color: config.accentColor,
              boxShadow: `0 0 16px ${config.primaryColor}33`,
            }}
          >
            <Sparkles className="w-3.5 h-3.5 animate-spin" />
            <span>{config.badgeCode}</span>
          </div>
        </div>

        <div className="hidden md:flex items-center gap-2">
          <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span className="text-emerald-400 font-bold">SYSTÈME OPÉRATIONNEL</span>
        </div>
      </header>

      {/* ── CORPS CENTRAL : BRANDING EVO-LOG & VISUEL DU DÉPARTEMENT ── */}
      <main className="relative z-10 flex flex-col items-center text-center my-auto max-w-3xl px-4 w-full">
        {/* Animation visuelle signature unique */}
        <div className="mb-4">
          <DomainSignatureVisual config={config} progress={activeProgress} />
        </div>

        {/* Titre EVO-LOG et identification du domaine */}
        <div className="mb-1">
          <span
            className="text-xs sm:text-sm font-black tracking-[0.35em] uppercase px-3.5 py-1 rounded-full border inline-block mb-2 shadow-lg"
            style={{
              backgroundColor: `${config.primaryColor}1a`,
              borderColor: `${config.primaryColor}55`,
              color: config.accentColor,
            }}
          >
            TRANSITION DE DÉPARTEMENT EN COURS
          </span>
          <h1
            className="text-5xl sm:text-7xl font-black tracking-tight select-none"
            style={{
              background: `linear-gradient(180deg, #ffffff 0%, ${config.accentColor} 45%, ${config.primaryColor} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              filter: `drop-shadow(0 0 25px ${config.primaryColor}66)`,
            }}
          >
            EVO-LOG
          </h1>
        </div>

        {/* Intitulé solennel du département */}
        <div className="mb-6">
          <h2
            className="text-xl sm:text-3xl font-extrabold tracking-wide uppercase drop-shadow-md"
            style={{ color: '#ffffff' }}
          >
            {customTitle || config.domainName}
          </h2>
          <p
            className="text-xs sm:text-sm font-mono tracking-wider mt-1 max-w-xl mx-auto"
            style={{ color: `${config.accentColor}dd` }}
          >
            {customSubtitle || config.subTitle}
          </p>
        </div>

        {/* ── BARRE DE PROGRESSION HIGH-TECH ── */}
        <div className="w-full max-w-lg bg-slate-900/90 border border-slate-700/80 p-4 sm:p-5 rounded-2xl shadow-2xl backdrop-blur-xl">
          <div className="flex items-center justify-between text-xs font-mono px-1 mb-2 text-slate-300">
            <span className="font-bold flex items-center gap-1.5" style={{ color: config.accentColor }}>
              <span className="w-2 h-2 rounded-full animate-ping" style={{ backgroundColor: config.primaryColor }} />
              Initialisation des services...
            </span>
            <span
              className="font-black tabular-nums text-sm px-2 py-0.5 rounded-md"
              style={{
                backgroundColor: `${config.primaryColor}22`,
                color: config.accentColor,
                border: `1px solid ${config.primaryColor}55`,
              }}
            >
              {activeProgress}%
            </span>
          </div>

          <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800 p-0.5">
            <div
              className="h-full rounded-full transition-all duration-100"
              style={{
                width: `${activeProgress}%`,
                background: `linear-gradient(90deg, ${config.primaryColor} 0%, ${config.accentColor} 100%)`,
                boxShadow: `0 0 16px ${config.primaryColor}, 0 0 30px ${config.accentColor}66`,
              }}
            />
          </div>

          <div className="flex items-center justify-center gap-1.5 mt-3 h-4">
            {[10, 16, 24, 14, 20, 28, 16, 22, 18, 26, 12, 18, 24, 15, 20].map((height, idx) => (
              <div
                key={idx}
                className="w-1 rounded-full transition-all duration-150"
                style={{
                  height: `${Math.max(4, (height * ((activeProgress + idx * 7) % 100)) / 70)}px`,
                  backgroundColor: config.primaryColor,
                  opacity: activeProgress > 10 ? 0.9 : 0.2,
                  boxShadow: `0 0 6px ${config.primaryColor}88`,
                }}
              />
            ))}
          </div>

          <div
            className="mt-3 px-2 text-xs font-mono text-center min-h-[22px] flex items-center justify-center transition-all duration-200"
            style={{ color: `${config.accentColor}ee` }}
          >
            {currentStepMessage}
          </div>
        </div>
      </main>

      {/* ── PIED DE PAGE SÉCURITÉ & CADC ── */}
      <footer className="relative z-10 w-full max-w-5xl flex items-center justify-between text-[11px] text-slate-500 font-mono pt-2 border-t border-slate-800/80">
        <span>© 2026 Code Axis Digital Cameroun (CADC)</span>
        <span
          className="hidden sm:inline font-semibold"
          style={{ color: `${config.primaryColor}aa` }}
        >
          SSL 256-BIT • ARCHITECTURE ZERO MOCK • 28 DÉPARTEMENTS INTÉGRÉS
        </span>
        <span>v2.0.0 EM-ERP</span>
      </footer>

      {/* ── STYLES D'ANIMATION ── */}
      <style>{`
        @keyframes radarSweep { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes spinSlow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes floatDot { 0%, 100% { transform: translateY(0) scale(1); opacity: 0.35; } 50% { transform: translateY(-16px) scale(1.3); opacity: 0.9; } }
        @keyframes pulseWave { 0% { transform: scale(0.85); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 0.3; } 100% { transform: scale(1.15); opacity: 0; } }
        @keyframes ledgerGridPulse { 0%, 100% { opacity: 0.15; } 50% { opacity: 0.35; } }
        @keyframes scanSweep { 0% { transform: translateY(-110px); opacity: 0; } 30% { opacity: 1; } 70% { opacity: 1; } 100% { transform: translateY(110px); opacity: 0; } }
      `}</style>
    </div>
  );
}

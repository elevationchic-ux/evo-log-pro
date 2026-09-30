'use client';

import React, { useEffect, useState, useMemo } from 'react';
import {
  Compass, Radio, Sparkles, ShieldCheck, Anchor, Ship, Truck,
  Boxes, Calculator, BarChart3, Users, ShieldAlert, Wrench,
  Globe, Landmark, KeyRound, MessageSquare, BookOpen, Layers,
  CheckCircle2, ArrowRight
} from 'lucide-react';
import {
  resolveDomainLoadingConfig,
  DomainLoadingConfig,
  DomainAnimationType
} from '@/config/domainLoadingConfig';

interface DomainLoadingExperienceProps {
  /**
   * Route cible (ex: '/comptabilite-ohada', '/chat', '/port-operations')
   * ou clé de domaine directe (ex: 'comptabilite-ohada', 'transport-flotte')
   */
  targetDomain?: string;
  /**
   * Pourcentage optionnel si contrôlé par le parent (0 à 100).
   * Si non fourni, le composant exécute sa propre progression fluide.
   */
  progress?: number;
  /**
   * Durée totale de la progression interne en millisecondes si auto-gérée (défaut: 2200ms)
   */
  durationMs?: number;
  /**
   * Callback déclenché lorsque la progression atteint 100%
   */
  onComplete?: () => void;
  /**
   * Titre personnalisé optionnel (écrase le nom par défaut du domaine)
   */
  customTitle?: string;
  /**
   * Sous-titre personnalisé optionnel
   */
  customSubtitle?: string;
  /**
   * Mode plein écran fixe (true par défaut) ou mode conteneur intégré (false)
   */
  fullScreen?: boolean;
}

/**
 * Composant d'animation signature unique selon le métier du domaine
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
          {/* Grille holographique du journal comptable */}
          <div
            className="absolute inset-0 rounded-3xl opacity-20 border border-violet-500/30"
            style={{
              backgroundImage: `linear-gradient(${primaryColor}33 1px, transparent 1px), linear-gradient(90deg, ${primaryColor}33 1px, transparent 1px)`,
              backgroundSize: '24px 24px',
              animation: 'ledgerGridPulse 4s ease-in-out infinite',
            }}
          />

          {/* Faisceau laser vertical de balance Débit / Crédit */}
          <div
            className="absolute inset-x-8 h-1 blur-sm rounded-full"
            style={{
              background: `linear-gradient(90deg, transparent, ${primaryColor}, ${accentColor}, transparent)`,
              animation: 'ledgerScanSweep 2.8s ease-in-out infinite',
            }}
          />

          {/* Anneau gyroscopique externe : Débit / Crédit SYSCOHADA */}
          <div
            className="absolute inset-2 rounded-full border-2 border-dashed"
            style={{
              borderColor: `${primaryColor}66`,
              animation: 'spinSlow 14s linear infinite',
            }}
          />
          <div
            className="absolute inset-8 rounded-full border border-violet-400/40"
            style={{
              animation: 'spinSlow 8s linear infinite reverse',
            }}
          />

          {/* Balance équilibrée en orbite (Symboles Débit et Crédit) */}
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
            <div className="absolute -left-3 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-slate-900 border border-violet-500/40 text-violet-200">
              SYSCOHADA
            </div>
            <div className="absolute -right-3 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-slate-900 border border-amber-500/40 text-amber-200">
              XAF • CEMAC
            </div>
          </div>

          {/* Nombres comptables flottants en orbite */}
          {['601', '701', '521', '411', '101', '401'].map((code, i) => (
            <span
              key={code}
              className="absolute font-mono text-[11px] font-black pointer-events-none transition-all duration-700"
              style={{
                color: i % 2 === 0 ? primaryColor : accentColor,
                top: `${50 + 38 * Math.sin((i * 60 * Math.PI) / 180 + progress * 0.05)}%`,
                left: `${50 + 38 * Math.cos((i * 60 * Math.PI) / 180 + progress * 0.05)}%`,
                transform: 'translate(-50%, -50%)',
                opacity: 0.85,
                textShadow: `0 0 10px ${primaryColor}88`,
              }}
            >
              Cpte {code}
            </span>
          ))}

          {/* Halo central pulsatil */}
          <div
            className="absolute w-36 h-36 rounded-full"
            style={{
              background: `radial-gradient(circle, ${primaryColor}40 0%, transparent 70%)`,
              animation: 'pulseHalo 2.2s ease-in-out infinite',
            }}
          />

          {/* Cœur SYSCOHADA : Blason Grand Livre & Balance */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor}dd 0%, #4c1d95 60%, #1e1b4b 100%)`,
              borderColor: `${accentColor}88`,
              boxShadow: `0 0 35px ${primaryColor}66, inset 0 0 15px rgba(255,255,255,0.2)`,
            }}
          >
            <BookOpen className="w-9 h-9 text-amber-300 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-white tracking-widest mt-0.5">
              SYSCOHADA
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 2. FINANCE & TRÉSORERIE : Flux de capitaux & Ondes bancaires SWIFT
    // ═════════════════════════════════════════════════════════════════════════
    case 'treasury-flux':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Ondes concentriques de liquidités */}
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

          {/* Flux de billets / devises en orbite */}
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

          {/* Cœur Trésorerie */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #064e3b 100%)`,
              borderColor: `${primaryColor}aa`,
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Landmark className="w-10 h-10 text-emerald-100" />
            <span className="text-[9px] font-mono font-black text-emerald-200 tracking-wider">
              TRÉSORERIE
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 3. COLLABORATIF & CHAT : Constellation multipoint & Fréquences d'équipe
    // ═════════════════════════════════════════════════════════════════════════
    case 'synergy-constellation':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Ondes hertziennes radio / wifi concentriques */}
          {[130, 190, 250, 310].map((size, i) => (
            <div
              key={size}
              className="absolute rounded-full border border-dashed"
              style={{
                width: `${size}px`,
                height: `${size}px`,
                borderColor: `${primaryColor}${i === 0 ? '55' : '25'}`,
                animation: `spinSlow ${10 + i * 4}s linear infinite ${i % 2 === 0 ? '' : 'reverse'}`,
              }}
            />
          ))}

          {/* Lignes de liaison de la constellation */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-40">
            <line x1="50%" y1="50%" x2="25%" y2="25%" stroke={primaryColor} strokeWidth="1.5" strokeDasharray="4 2" />
            <line x1="50%" y1="50%" x2="75%" y2="25%" stroke={primaryColor} strokeWidth="1.5" strokeDasharray="4 2" />
            <line x1="50%" y1="50%" x2="80%" y2="70%" stroke={primaryColor} strokeWidth="1.5" strokeDasharray="4 2" />
            <line x1="50%" y1="50%" x2="20%" y2="70%" stroke={primaryColor} strokeWidth="1.5" strokeDasharray="4 2" />
            <line x1="50%" y1="50%" x2="50%" y2="88%" stroke={primaryColor} strokeWidth="1.5" strokeDasharray="4 2" />
          </svg>

          {/* Nœuds d'équipe satellites en orbite */}
          {[
            { label: 'QUAI', top: '22%', left: '22%' },
            { label: 'DISPATCH', top: '22%', left: '78%' },
            { label: 'COMPTA', top: '72%', left: '80%' },
            { label: 'FLOTTE', top: '72%', left: '20%' },
            { label: 'SÛRETÉ', top: '88%', left: '50%' },
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
                boxShadow: `0 0 15px ${primaryColor}44`,
                animation: `floatDot ${3 + i * 0.5}s ease-in-out infinite`,
              }}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>{node.label}</span>
            </div>
          ))}

          {/* Cœur Collaboratif */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #15803d 50%, #064e3b 100%)`,
              borderColor: `${accentColor}88`,
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <MessageSquare className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-amber-200 tracking-wider">
              SYNERGIE
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 4. PORT OPERATIONS & ACCONAGE : Radar Maritime Douala / Kribi
    // ═════════════════════════════════════════════════════════════════════════
    case 'radar-maritime':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Faisceau tournant de radar maritime à 360° */}
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: `conic-gradient(from 0deg, ${primaryColor}55 0deg, ${primaryColor}0d 60deg, transparent 90deg)`,
              animation: 'radarSweep 3.5s linear infinite',
            }}
          />

          {/* Anneaux concentriques nautiques */}
          {[120, 180, 240, 300].map((size, i) => (
            <div
              key={size}
              className="absolute rounded-full border"
              style={{
                width: `${size}px`,
                height: `${size}px`,
                borderColor: `${primaryColor}${i === 3 ? '22' : '33'}`,
              }}
            />
          ))}

          {/* Lignes de repères cardinaux */}
          <div className="absolute inset-x-0 h-px bg-sky-500/20" />
          <div className="absolute inset-y-0 w-px bg-sky-500/20" />

          {/* Échos de navires cargo détectés au radar */}
          <div
            className="absolute top-[28%] left-[68%] flex items-center gap-1 text-[10px] font-mono text-sky-300 font-bold animate-pulse"
          >
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400 shadow-md shadow-sky-400" />
            <span>CARGO ESCALE #421</span>
          </div>
          <div
            className="absolute bottom-[30%] left-[24%] flex items-center gap-1 text-[10px] font-mono text-amber-300 font-bold animate-pulse"
            style={{ animationDelay: '1.2s' }}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-md shadow-amber-400" />
            <span>REMORQUEUR PAD</span>
          </div>

          {/* Cœur Port Operations */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #0369a1 60%, #082f49 100%)`,
              borderColor: `${accentColor}88`,
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Ship className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-sky-100 tracking-wider">
              PORT 360°
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 5. TRANSIT & DOUANE : Scan laser de manifestes & Sceaux GUCE / SYDONIA
    // ═════════════════════════════════════════════════════════════════════════
    case 'customs-laser':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Scanner laser bleu cobalt de documents douaniers */}
          <div
            className="absolute inset-x-4 h-1.5 rounded-full blur-[2px]"
            style={{
              background: `linear-gradient(90deg, transparent, ${primaryColor}, #60a5fa, transparent)`,
              animation: 'ledgerScanSweep 2.5s ease-in-out infinite',
            }}
          />

          {/* Anneaux de certification GUCE */}
          <div
            className="absolute inset-4 rounded-full border-2 border-dashed border-blue-500/40"
            style={{ animation: 'spinSlow 10s linear infinite' }}
          />
          <div
            className="absolute inset-12 rounded-full border border-blue-400/30"
            style={{ animation: 'spinSlow 6s linear infinite reverse' }}
          />

          {/* Badges de contrôle douanier */}
          <div className="absolute top-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-blue-950 border border-blue-400 text-blue-200">
            GUCE CAMEROUN • SYDONIA++
          </div>
          <div className="absolute bottom-4 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-blue-950 border border-blue-400 text-blue-200">
            BESC / CONNAISSEMENT VALIDÉ
          </div>

          {/* Cœur Transit */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #1e40af 100%)`,
              borderColor: '#93c5fd',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <ShieldCheck className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-blue-200 tracking-wider">
              DOUANE
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 6. TRANSPORT & FLOTTE : Visée satellitaire GPS & Corridors CEMAC
    // ═════════════════════════════════════════════════════════════════════════
    case 'telematics-satellite':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Réticule de visée satellitaire cyan */}
          <div
            className="absolute inset-4 rounded-full border border-cyan-500/30"
            style={{ animation: 'spinSlow 16s linear infinite' }}
          />
          <div
            className="absolute inset-10 rounded-full border border-dashed border-cyan-400/40"
            style={{ animation: 'spinSlow 10s linear infinite reverse' }}
          />

          {/* Lignes de corridors routiers */}
          <div className="absolute inset-x-0 h-px bg-cyan-500/30" />
          <div className="absolute inset-y-0 w-px bg-cyan-500/30" />

          {/* Points de convois géolocalisés */}
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

          {/* Cœur Transport */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #0e7490 100%)`,
              borderColor: '#67e8f9',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Truck className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-cyan-100 tracking-wider">
              TÉLÉMATIQUE
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 7. MAGASIN & STOCK : Scan Lidar 3D & Alvéoles WMS
    // ═════════════════════════════════════════════════════════════════════════
    case 'wms-lidar':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Grille 3D isométrique d'entrepôt */}
          <div
            className="absolute inset-4 rounded-2xl border border-amber-500/30 opacity-40"
            style={{
              backgroundImage: 'linear-gradient(#f59e0b22 1px, transparent 1px), linear-gradient(90deg, #f59e0b22 1px, transparent 1px)',
              backgroundSize: '20px 20px',
            }}
          />

          {/* Faisceau laser scanner de codes-barres vertical */}
          <div
            className="absolute inset-x-8 h-1 rounded-full blur-[1px]"
            style={{
              background: 'linear-gradient(90deg, transparent, #ef4444, #f59e0b, transparent)',
              animation: 'ledgerScanSweep 2.2s ease-in-out infinite',
            }}
          />

          {/* Cubes de palettes en orbite */}
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

          {/* Cœur WMS */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #b45309 100%)`,
              borderColor: '#fde68a',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Boxes className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-slate-950 tracking-wider">
              STOCK WMS
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 8. PARC & GMAO : Double engrenages industriels & Diagnostic
    // ═════════════════════════════════════════════════════════════════════════
    case 'gmao-gears':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Engrenage supérieur rotatif */}
          <div
            className="absolute top-8 left-8 w-28 h-28 rounded-full border-4 border-dashed border-orange-500/40"
            style={{ animation: 'spinSlow 6s linear infinite' }}
          />
          {/* Engrenage inférieur rotatif en sens inverse */}
          <div
            className="absolute bottom-8 right-8 w-36 h-36 rounded-full border-4 border-dashed border-orange-400/40"
            style={{ animation: 'spinSlow 8s linear infinite reverse' }}
          />

          {/* Jauge de diagnostic */}
          <div className="absolute top-2 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-orange-950 border border-orange-500 text-orange-200">
            DIAGNOSTIC TÉLÉMÉTRIQUE GMAO
          </div>

          {/* Cœur GMAO */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #c2410c 100%)`,
              borderColor: '#fed7aa',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Wrench className="w-10 h-10 text-slate-950 drop-shadow" />
            <span className="text-[9px] font-mono font-black text-slate-950 tracking-wider">
              MAINTENANCE
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // 9. QHSE & SÉCURITÉ : Bouclier de protection ISPS & Vigilance
    // ═════════════════════════════════════════════════════════════════════════
    case 'isps-shield':
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          {/* Bouclier hexagonal de protection qui pulse */}
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
            CODE ISPS • ALERTE SÛRETÉ NIVEAU 1
          </div>

          {/* Cœur QHSE */}
          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #991b1b 100%)`,
              borderColor: '#fca5a5',
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <ShieldAlert className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-red-100 tracking-wider">
              SÛRETÉ ISPS
            </span>
          </div>
        </div>
      );

    // ═════════════════════════════════════════════════════════════════════════
    // PAR DÉFAUT / DASHBOARD / AUTRES : Gyroscope et boussole stratégique
    // ═════════════════════════════════════════════════════════════════════════
    default:
      return (
        <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
          <div
            className="absolute inset-2 rounded-full border-2 border-dashed"
            style={{
              borderColor: `${primaryColor}66`,
              animation: 'spinSlow 12s linear infinite',
            }}
          />
          <div
            className="absolute inset-8 rounded-full border"
            style={{
              borderColor: `${accentColor}66`,
              animation: 'spinSlow 7s linear infinite reverse',
            }}
          />
          <div
            className="absolute inset-16 rounded-full"
            style={{
              background: `radial-gradient(circle, ${primaryColor}40 0%, transparent 70%)`,
              animation: 'pulseHalo 2s ease-in-out infinite',
            }}
          />

          <div
            className="relative z-10 w-20 h-20 rounded-2xl flex flex-col items-center justify-center shadow-2xl border"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, #312e81 100%)`,
              borderColor: `${accentColor}aa`,
              boxShadow: `0 0 35px ${primaryColor}88`,
            }}
          >
            <Compass className="w-10 h-10 text-white drop-shadow" />
            <span className="text-[9px] font-mono font-black text-amber-200 tracking-wider">
              COCKPIT
            </span>
          </div>
        </div>
      );
  }
}

/**
 * Composant complet d'expérience de chargement de domaine
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
  const config = useMemo(
    () => resolveDomainLoadingConfig(targetDomain),
    [targetDomain]
  );

  const [internalProgress, setInternalProgress] = useState(0);

  // Gestion du cycle de progression fluide si non contrôlé par le parent
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
          setTimeout(onComplete, 350);
        }
      }
    }, 25);

    return () => clearInterval(interval);
  }, [externalProgress, durationMs, onComplete]);

  const activeProgress = typeof externalProgress === 'number' ? externalProgress : internalProgress;

  // Calcul du message d'étape courant selon la progression
  const currentStepMessage = useMemo(() => {
    const steps = config.steps;
    if (activeProgress < 28) return steps[0];
    if (activeProgress < 58) return steps[1];
    if (activeProgress < 88) return steps[2];
    return steps[3];
  }, [activeProgress, config.steps]);

  const containerClasses = fullScreen
    ? 'fixed inset-0 z-[120] flex flex-col items-center justify-between p-4 sm:p-8 md:p-12 overflow-hidden select-none text-white'
    : 'relative w-full min-h-[600px] flex flex-col items-center justify-between p-6 sm:p-10 overflow-hidden select-none text-white rounded-3xl border border-slate-800';

  return (
    <div
      className={containerClasses}
      style={{
        background: `radial-gradient(circle at center, ${config.primaryColor}22 0%, #030816 65%, #01040a 100%)`,
        backgroundColor: '#020611',
      }}
    >
      {/* ── 1. FOND PARTICULES & LUEURS ATMOSPHÉRIQUES DU DOMAINE ── */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {/* Grille fine high-tech adaptée à la teinte du module */}
        <div
          className="absolute inset-0 opacity-[0.05]"
          style={{
            backgroundImage: `linear-gradient(${config.primaryColor} 1px, transparent 1px), linear-gradient(90deg, ${config.primaryColor} 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />

        {/* Lueur diffuse centrale */}
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-[120px] opacity-25 pointer-events-none"
          style={{ backgroundColor: config.primaryColor }}
        />

        {/* Particules flottantes */}
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

      {/* ── 2. BANNIÈRE TÉLÉMÉTRIE SUPÉRIEURE ── */}
      <header className="relative z-10 w-full max-w-5xl flex items-center justify-between text-[11px] font-mono border-b pb-2 pt-1 border-slate-800">
        <div className="flex items-center gap-2" style={{ color: `${config.accentColor}cc` }}>
          <Compass className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '10s' }} />
          <span className="hidden sm:inline font-bold tracking-wider">{config.locationTag}</span>
        </div>

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

        <div className="hidden md:flex items-center gap-2">
          <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span className="text-emerald-400 font-bold">SYSTÈME OPÉRATIONNEL</span>
        </div>
      </header>

      {/* ── 3. CORPS CENTRAL : BRANDING EVO-LOG & NOM DU DOMAINE CIBLE ── */}
      <main className="relative z-10 flex flex-col items-center text-center my-auto max-w-3xl px-4 w-full">
        {/* Animation signature thématique du module */}
        <div className="mb-4">
          <DomainSignatureVisual config={config} progress={activeProgress} />
        </div>

        {/* Titre EVO-LOG étincelant avec reflets métalliques */}
        <div className="mb-1">
          <span
            className="text-xs sm:text-sm font-black tracking-[0.35em] uppercase px-3 py-1 rounded-full border inline-block mb-2 shadow-lg"
            style={{
              backgroundColor: `${config.primaryColor}1a`,
              borderColor: `${config.primaryColor}55`,
              color: config.accentColor,
            }}
          >
            TRANSITION DE DOMAINE EN COURS
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

        {/* Nom du domaine de destination bien en évidence */}
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

        {/* ── 4. BARRE DE PROGRESSION HIGH-TECH DU MODULE ── */}
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

          {/* Jauge principale avec glow de la couleur du domaine */}
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

          {/* Égaliseur télémétrique dynamique */}
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

          {/* Message télémétrique d'étape qui défile */}
          <div
            className="mt-3 px-2 text-xs font-mono text-center min-h-[22px] flex items-center justify-center transition-all duration-200"
            style={{ color: `${config.accentColor}ee` }}
          >
            {currentStepMessage}
          </div>
        </div>
      </main>

      {/* ── 5. PIED DE PAGE SÉCURITÉ & IDENTITÉ CADC ── */}
      <footer className="relative z-10 w-full max-w-5xl flex items-center justify-between text-[11px] text-slate-500 font-mono pt-2 border-t border-slate-800/80">
        <span>© 2026 Code Axis Digital Cameroun (CADC)</span>
        <span
          className="hidden sm:inline font-semibold"
          style={{ color: `${config.primaryColor}aa` }}
        >
          SSL 256-BIT • ARCHITECTURE ZERO MOCK • SYSTÈME INTÉGRÉ
        </span>
        <span>v2.0.0 EM-ERP</span>
      </footer>

      {/* ── 6. DÉCLARATION DES STYLES D'ANIMATION ── */}
      <style>{`
        @keyframes radarSweep { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes spinSlow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes floatDot { 0%, 100% { transform: translateY(0) scale(1); opacity: 0.35; } 50% { transform: translateY(-16px) scale(1.3); opacity: 0.9; } }
        @keyframes pulseHalo { 0%, 100% { opacity: 0.35; transform: scale(1); } 50% { opacity: 0.85; transform: scale(1.2); } }
        @keyframes pulseWave { 0% { transform: scale(0.85); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 0.3; } 100% { transform: scale(1.15); opacity: 0; } }
        @keyframes ledgerGridPulse { 0%, 100% { opacity: 0.15; } 50% { opacity: 0.35; } }
        @keyframes ledgerScanSweep { 0% { transform: translateY(-110px); opacity: 0; } 30% { opacity: 1; } 70% { opacity: 1; } 100% { transform: translateY(110px); opacity: 0; } }
      `}</style>
    </div>
  );
}

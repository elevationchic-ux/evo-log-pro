"use client";

import React, { useState, useRef, useMemo, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  X,
  Search,
  LayoutDashboard,
  Orbit,
  LayoutGrid,
  Pin,
  Unlock,
  ExternalLink,
  Sparkles,
  Compass,
  Zap,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { NAVIGATION_REGISTRY, ModuleNavConfig, SubModuleItem } from "@/config/navigationRegistry";
import { localizeTitle, localizeSubLabel } from "@/config/navI18n";
import { useSettings } from "@/components/layout/SettingsProvider";
import { useI18n } from "@/hooks/useI18n";
import { useSession } from "next-auth/react";
import { useDomainTransition } from "@/components/shared/DomainTransitionContext";

export default function SubModuleOrbitalBubble() {
  const pathname = usePathname();
  const router = useRouter();
  const { language } = useSettings();
  const t = useI18n();
  const { data: session } = useSession();
  const isSuperUser =
    Boolean((session?.user as any)?.is_superuser) ||
    Number((session?.user as any)?.role_level ?? 9) === 0;

  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [position, setPosition] = useState({ x: 20, y: 180 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef<{ startX: number; startY: number; posX: number; posY: number }>({
    startX: 0,
    startY: 0,
    posX: 0,
    posY: 0,
  });

  // Mode d'affichage : 'orb' (Orbe Gravitationnelle / Arbre de compétences) ou 'grid' (Grille classique)
  const [viewMode, setViewMode] = useState<"orb" | "grid">("orb");

  // Interaction Orbe Gravitationnelle :
  // Survol : affiche temporairement les sous-modules de ce module
  // Clic : fige (verrouille) le module pour pouvoir parcourir et choisir tranquillement
  const [hoveredModuleKey, setHoveredModuleKey] = useState<string | null>(null);
  const [pinnedModuleKey, setPinnedModuleKey] = useState<string | null>(null);
  const [hoveredSubKey, setHoveredSubKey] = useState<string | null>(null);

  // Mémorisation de la préférence de vue dans localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("evolog_orbital_view_mode");
      if (saved === "grid" || saved === "orb") {
        setViewMode(saved);
      }
    }
  }, []);

  const handleSetViewMode = (mode: "orb" | "grid") => {
    setViewMode(mode);
    if (typeof window !== "undefined") {
      localStorage.setItem("evolog_orbital_view_mode", mode);
    }
  };

  // Dimensions réelles du canvas gravitationnel
  const canvasRef = useRef<HTMLDivElement>(null);
  const [canvasDims, setCanvasDims] = useState({ width: 920, height: 600 });

  useEffect(() => {
    if (!isOpen || viewMode !== "orb") return;
    const updateDims = () => {
      if (canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        if (rect.width > 50 && rect.height > 50) {
          setCanvasDims({ width: Math.round(rect.width), height: Math.round(rect.height) });
        }
      }
    };
    updateDims();
    const ro = new ResizeObserver(updateDims);
    if (canvasRef.current) ro.observe(canvasRef.current);
    window.addEventListener("resize", updateDims);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", updateDims);
    };
  }, [isOpen, viewMode]);

  // TOUS les modules sont exposés dans la bulle flottante (exigence produit),
  // SAUF la console Super-Admin CADC, invisible pour un non-super-admin.
  const filteredNav: ModuleNavConfig[] = useMemo(() => {
    return Object.values(NAVIGATION_REGISTRY).filter(
      (m) => m.key !== "superadmin-cadc" || isSuperUser
    );
  }, [isSuperUser]);

  // Résolution du module actif à partir du pathname (pour colorer la bulle).
  const activeModuleKey =
    Object.keys(NAVIGATION_REGISTRY).find((k) => k !== "dashboard" && pathname.startsWith(`/${k}`)) ||
    (pathname.startsWith("/dashboard") || pathname === "/" ? "dashboard" : filteredNav[0]?.key);

  const activeOrbit =
    filteredNav.find((m) => m.key === activeModuleKey) || filteredNav[0] || NAVIGATION_REGISTRY.dashboard;
  const MainIcon = activeOrbit.icon || LayoutDashboard;

  // Filtre de recherche : module et sous-modules dont le libellé/chemin correspond.
  const q = query.trim().toLowerCase();
  const visibleModules = useMemo(() => {
    if (!q) return filteredNav;
    return filteredNav
      .map((m) => {
        const moduleMatch =
          m.title.toLowerCase().includes(q) ||
          (m.titleEn || "").toLowerCase().includes(q) ||
          m.key.includes(q);
        const subs = m.subModules.filter(
          (s) =>
            s.label.toLowerCase().includes(q) ||
            localizeSubLabel(s.label, language).toLowerCase().includes(q) ||
            s.path.toLowerCase().includes(q)
        );
        if (moduleMatch) return m;
        if (subs.length) return { ...m, subModules: subs };
        return null;
      })
      .filter(Boolean) as ModuleNavConfig[];
  }, [filteredNav, q, language]);

  const totalSubs = useMemo(() => {
    return filteredNav.reduce((acc, m) => acc + m.subModules.length, 0);
  }, [filteredNav]);

  // ── Drag FAB (souris + tactile) ──
  const beginDrag = (clientX: number, clientY: number) => {
    setIsDragging(false);
    dragStartRef.current = { startX: clientX, startY: clientY, posX: position.x, posY: position.y };
  };
  const moveDrag = (clientX: number, clientY: number) => {
    const deltaX = dragStartRef.current.startX - clientX;
    const deltaY = clientY - dragStartRef.current.startY;
    if (Math.abs(deltaX) > 4 || Math.abs(deltaY) > 4) setIsDragging(true);
    setPosition({
      x: Math.max(10, Math.min(window.innerWidth - 70, dragStartRef.current.posX + deltaX)),
      y: Math.max(80, Math.min(window.innerHeight - 80, dragStartRef.current.posY + deltaY)),
    });
  };

  const { triggerDomainTransition } = useDomainTransition();

  const navigate = (path: string) => {
    setIsOpen(false);
    const currentRoot = pathname ? pathname.replace(/^\/+/, "").split("/")[0] : "";
    const targetRoot = path ? path.replace(/^\/+/, "").split("/")[0] : "";
    if (currentRoot && targetRoot && currentRoot !== targetRoot) {
      triggerDomainTransition(path, 1700);
    } else {
      router.push(path);
    }
  };

  // Fermeture clavier : Échap replie le panneau
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (pinnedModuleKey) {
          setPinnedModuleKey(null);
        } else {
          setIsOpen(false);
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, pinnedModuleKey]);

  // ── Calculs géométriques pour l'Orbe Gravitationnelle ──
  const activeFocusKey = pinnedModuleKey || hoveredModuleKey;
  const focusedModule = useMemo(() => {
    return filteredNav.find((m) => m.key === activeFocusKey) || null;
  }, [filteredNav, activeFocusKey]);

  const { cx, cy, minDim, R_inner, R_outer, N_inner, N_outer } = useMemo(() => {
    const w = canvasDims.width;
    const h = canvasDims.height;
    const center_x = w / 2;
    const center_y = h / 2;
    const min_d = Math.min(w, h);
    const total = filteredNav.length;
    const inner_count = Math.min(9, Math.max(6, Math.floor(total * 0.35)));
    const outer_count = total - inner_count;
    const r_in = Math.max(110, min_d * 0.22);
    const r_out = Math.max(190, min_d * 0.38);
    return {
      cx: center_x,
      cy: center_y,
      minDim: min_d,
      R_inner: r_in,
      R_outer: r_out,
      N_inner: inner_count,
      N_outer: outer_count,
    };
  }, [canvasDims, filteredNav.length]);

  // Coordonnées de chaque module sur les anneaux orbitaux
  const moduleLayout = useMemo(() => {
    const coords: Record<
      string,
      { x: number; y: number; angle: number; ring: "inner" | "outer"; matchesSearch: boolean }
    > = {};

    filteredNav.forEach((mod, index) => {
      let angle: number;
      let radius: number;
      let ring: "inner" | "outer";

      if (index < N_inner) {
        ring = "inner";
        radius = R_inner;
        angle = (index / N_inner) * 2 * Math.PI - Math.PI / 2;
      } else {
        ring = "outer";
        radius = R_outer;
        const j = index - N_inner;
        angle = (j / N_outer) * 2 * Math.PI - Math.PI / 2 + Math.PI / N_outer;
      }

      const matchesSearch =
        !q ||
        mod.title.toLowerCase().includes(q) ||
        (mod.titleEn || "").toLowerCase().includes(q) ||
        mod.key.includes(q) ||
        mod.subModules.some(
          (s) =>
            s.label.toLowerCase().includes(q) ||
            localizeSubLabel(s.label, language).toLowerCase().includes(q)
        );

      coords[mod.key] = {
        x: Math.round(cx + radius * Math.cos(angle)),
        y: Math.round(cy + radius * Math.sin(angle)),
        angle,
        ring,
        matchesSearch,
      };
    });

    return coords;
  }, [filteredNav, N_inner, N_outer, R_inner, R_outer, cx, cy, q, language]);

  // Arbre de compétences (Skill Tree) : coordonnées des sous-modules reliés au module sélectionné
  const skillTreeNodes = useMemo(() => {
    if (!focusedModule) return [];
    const parent = moduleLayout[focusedModule.key];
    if (!parent) return [];

    const subs = focusedModule.subModules;
    const k = subs.length;
    if (k === 0) return [];

    // Direction radiale de base depuis le centre
    const parentAngle = parent.angle;
    // Branchement vers l'espace libre disponible
    const fanSpan = Math.min(Math.PI * 1.15, 0.36 * (k - 1) + 0.35);
    const startAngle = parentAngle - fanSpan / 2;

    const baseDist =
      parent.ring === "inner"
        ? Math.max(85, minDim * 0.16)
        : Math.max(75, minDim * 0.135);

    return subs.map((sub, idx) => {
      const angle = k === 1 ? parentAngle : startAngle + (idx / Math.max(1, k - 1)) * fanSpan;
      // Étagement pour éviter les collisions et créer des branches de compétences étagées
      const tierStagger = k > 4 ? (idx % 2 === 0 ? 0 : 36) : 0;
      const dist = baseDist + tierStagger;

      const rawX = parent.x + dist * Math.cos(angle);
      const rawY = parent.y + dist * Math.sin(angle);

      // Maintien strict dans les limites du canvas
      const padX = 80;
      const padY = 65;
      const clampedX = Math.max(padX, Math.min(canvasDims.width - padX, rawX));
      const clampedY = Math.max(padY, Math.min(canvasDims.height - padY, rawY));

      const matchesSearch =
        !q ||
        sub.label.toLowerCase().includes(q) ||
        localizeSubLabel(sub.label, language).toLowerCase().includes(q) ||
        sub.path.toLowerCase().includes(q);

      return {
        sub,
        idx,
        x: Math.round(clampedX),
        y: Math.round(clampedY),
        parentX: parent.x,
        parentY: parent.y,
        matchesSearch,
      };
    });
  }, [focusedModule, moduleLayout, minDim, canvasDims, q, language]);

  return (
    <>
      {/* ── Bouton flottant déplaçable (bord droit) ── */}
      <div
        style={{ right: `${position.x}px`, top: `${position.y}px` }}
        className="fixed z-[85] select-none cursor-grab active:cursor-grabbing"
      >
        <button
          onMouseDown={(e) => beginDrag(e.clientX, e.clientY)}
          onMouseMove={(e) => isDragging && moveDrag(e.clientX, e.clientY)}
          onMouseUp={() => window.setTimeout(() => setIsDragging(false), 0)}
          onTouchStart={(e) => beginDrag(e.touches[0].clientX, e.touches[0].clientY)}
          onTouchMove={(e) => isDragging && moveDrag(e.touches[0].clientX, e.touches[0].clientY)}
          onTouchEnd={() => window.setTimeout(() => setIsDragging(false), 0)}
          onClick={() => {
            if (!isDragging) setIsOpen((o) => !o);
          }}
          className={`relative w-14 h-14 rounded-full bg-slate-900 border-2 flex items-center justify-center shadow-2xl transition-transform hover:scale-110 active:scale-95 ${activeOrbit.glow}`}
          style={{ borderColor: activeOrbit.color }}
          aria-label={t.shell.bubbleTitle}
          title={t.shell.bubbleTitle}
        >
          <div
            className={`absolute inset-0 rounded-full blur-md opacity-60 animate-pulse bg-gradient-to-tr ${activeOrbit.bgGradient}`}
          />
          <div
            className={`relative w-11 h-11 rounded-full bg-gradient-to-tr ${activeOrbit.bgGradient} flex items-center justify-center text-white shadow-inner`}
          >
            {isOpen ? <X className="w-6 h-6" /> : <MainIcon className="w-6 h-6" />}
          </div>
          <span className="absolute -top-1 -right-1 bg-slate-950 text-amber-400 font-black text-[11px] px-2 py-0.5 rounded-full border border-amber-500/50 shadow-md">
            {filteredNav.length}
          </span>
        </button>
      </div>

      {/* ── Fenêtre modale : Sélecteur de mode + Contenu ── */}
      {isOpen && (
        <div className="fixed inset-0 z-[90] bg-slate-950/90 backdrop-blur-md flex items-stretch sm:items-center justify-center animate-in fade-in duration-200">
          <div className="absolute inset-0" onClick={() => setIsOpen(false)} aria-hidden="true" />

          <div
            className={`relative z-10 flex w-full h-full sm:rounded-2xl bg-slate-900 border-0 sm:border sm:border-slate-800 shadow-2xl flex-col overflow-hidden transition-all duration-300 ${
              viewMode === "orb"
                ? "sm:max-w-6xl sm:h-[90vh] sm:max-h-[920px]"
                : "sm:max-w-5xl sm:max-h-[88vh] sm:h-auto"
            }`}
          >
            {/* ── En-tête avec Sélecteur de Mode ── */}
            <div className="shrink-0 border-b border-slate-800 bg-slate-900/95 backdrop-blur px-4 py-3 flex flex-col gap-3">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="min-w-0 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-amber-500 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 shrink-0">
                    <Orbit className="w-4 h-4" />
                  </div>
                  <div>
                    <h2 className="text-sm font-black text-slate-100 truncate flex items-center gap-2">
                      {t.shell.bubbleTitle}
                      <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        {filteredNav.length} {t.shell.modules}
                      </span>
                    </h2>
                    <p className="text-[11px] text-slate-400">
                      {totalSubs} {t.shell.subModules} · Architecture End-to-End
                    </p>
                  </div>
                </div>

                {/* Commutateur de Mode (Orbe Gravitationnelle vs Grille Classique) */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 shadow-inner">
                    <button
                      type="button"
                      onClick={() => handleSetViewMode("orb")}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        viewMode === "orb"
                          ? "bg-gradient-to-r from-amber-500 to-indigo-600 text-white shadow-md shadow-amber-500/20"
                          : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                      }`}
                      title="Affichage en Orbe Gravitationnelle & Arbre de Compétences"
                    >
                      <Orbit className="w-3.5 h-3.5" />
                      <span>Orbe Gravitationnelle</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSetViewMode("grid")}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        viewMode === "grid"
                          ? "bg-slate-800 text-white shadow border border-slate-700"
                          : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                      }`}
                      title="Affichage en Liste / Grille Classique"
                    >
                      <LayoutGrid className="w-3.5 h-3.5" />
                      <span>Grille</span>
                    </button>
                  </div>

                  <button
                    onClick={() => setIsOpen(false)}
                    className="shrink-0 rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
                    aria-label={t.common.close}
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Barre de recherche & Indication d'interaction */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    autoFocus
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={
                      viewMode === "orb"
                        ? "Filtrer l'orbe ou rechercher un sous-module..."
                        : t.shell.bubbleSearch
                    }
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-slate-600 transition-colors"
                  />
                  {query && (
                    <button
                      onClick={() => setQuery("")}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 hover:text-slate-300"
                    >
                      Effacer
                    </button>
                  )}
                </div>

                {/* Astuce interactive selon le mode */}
                {viewMode === "orb" && (
                  <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] text-slate-400 shrink-0">
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping shrink-0" />
                    <span>
                      {pinnedModuleKey ? (
                        <span className="text-amber-300 font-medium">
                          Module fixé :{" "}
                          <strong>
                            {focusedModule ? localizeTitle(focusedModule, language) : ""}
                          </strong>
                        </span>
                      ) : (
                        <span>Survolez un module pour déployer son arbre · Cliquez pour figer</span>
                      )}
                    </span>
                    {pinnedModuleKey && (
                      <button
                        onClick={() => setPinnedModuleKey(null)}
                        className="ml-1 text-slate-400 hover:text-amber-300 flex items-center gap-1 font-bold underline"
                      >
                        <Unlock className="w-3 h-3" />
                        Libérer
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* ══════════════════════════════════════════════════════════════════
                MODE 1 : ORBE GRAVITATIONNELLE & ARBRE DE COMPÉTENCES
               ══════════════════════════════════════════════════════════════════ */}
            {viewMode === "orb" && (
              <div
                ref={canvasRef}
                className="relative flex-1 w-full h-full min-h-[460px] bg-slate-950 overflow-hidden select-none"
                onClick={(e) => {
                  // Clic sur l'espace vide pour déverrouiller
                  if (e.target === canvasRef.current || (e.target as HTMLElement).tagName === "svg") {
                    setPinnedModuleKey(null);
                  }
                }}
              >
                {/* ── Arrière-plan Cosmique & Champs Gravitationnels ── */}
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    background:
                      "radial-gradient(circle at 50% 50%, rgba(30, 41, 59, 0.45) 0%, rgba(2, 6, 23, 0.98) 75%)",
                  }}
                />

                {/* ── Traces SVG : Anneaux orbitaux, flux gravitationnels et branches de l'arbre ── */}
                <svg
                  className="absolute inset-0 w-full h-full pointer-events-none"
                  style={{ overflow: "visible" }}
                >
                  <defs>
                    {/* Filtre de lueur néon */}
                    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
                      <feGaussianBlur stdDeviation="3" result="blur" />
                      <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                    {/* Dégradé radar */}
                    <linearGradient id="orbit-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.4" />
                      <stop offset="50%" stopColor="#6366f1" stopOpacity="0.2" />
                      <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0.3" />
                    </linearGradient>
                  </defs>

                  {/* Anneau gravitationnel central */}
                  <circle
                    cx={cx}
                    cy={cy}
                    r={R_inner * 0.42}
                    fill="none"
                    stroke="#38bdf8"
                    strokeOpacity="0.2"
                    strokeWidth="1.5"
                    strokeDasharray="4 6"
                  />

                  {/* Anneau orbital interne */}
                  <circle
                    cx={cx}
                    cy={cy}
                    r={R_inner}
                    fill="none"
                    stroke="#6366f1"
                    strokeOpacity="0.25"
                    strokeWidth="1.5"
                    strokeDasharray="6 8"
                  />

                  {/* Anneau orbital externe */}
                  <circle
                    cx={cx}
                    cy={cy}
                    r={R_outer}
                    fill="none"
                    stroke="#a855f7"
                    strokeOpacity="0.2"
                    strokeWidth="1.5"
                    strokeDasharray="8 10"
                  />

                  {/* Trait de balayage gravitationnel / radar */}
                  <line
                    x1={cx}
                    y1={cy}
                    x2={cx + R_outer * 1.08 * Math.cos(Date.now() / 2500)}
                    y2={cy + R_outer * 1.08 * Math.sin(Date.now() / 2500)}
                    stroke="url(#orbit-grad)"
                    strokeWidth="1.5"
                    strokeOpacity="0.4"
                  />

                  {/* ── Liens SVG de l'Arbre de Compétences vers les Sous-Modules ── */}
                  {focusedModule && (
                    <g>
                      {/* Liens de constellation entre sous-modules consécutifs */}
                      {skillTreeNodes.map((node, i) => {
                        if (i === 0) return null;
                        const prev = skillTreeNodes[i - 1];
                        return (
                          <line
                            key={`tree-link-${i}`}
                            x1={prev.x}
                            y1={prev.y}
                            x2={node.x}
                            y2={node.y}
                            stroke={focusedModule.color}
                            strokeOpacity="0.28"
                            strokeWidth="1.5"
                            strokeDasharray="3 4"
                          />
                        );
                      })}

                      {/* Branches principales du module vers chaque sous-module */}
                      {skillTreeNodes.map((node, i) => {
                        const midX = (node.parentX + node.x) / 2;
                        const midY = (node.parentY + node.y) / 2;
                        // Légère courbure organique de la branche
                        const curveFactor = 0.15;
                        const ctrlX = midX + (midX - cx) * curveFactor;
                        const ctrlY = midY + (midY - cy) * curveFactor;
                        const pathD = `M ${node.parentX} ${node.parentY} Q ${ctrlX} ${ctrlY} ${node.x} ${node.y}`;

                        return (
                          <g key={`branch-${i}`}>
                            {/* Halo néon arrière */}
                            <path
                              d={pathD}
                              fill="none"
                              stroke={focusedModule.color}
                              strokeOpacity="0.35"
                              strokeWidth="5"
                              strokeLinecap="round"
                            />
                            {/* Laser d'énergie principal */}
                            <path
                              d={pathD}
                              fill="none"
                              stroke={focusedModule.color}
                              strokeWidth="2.5"
                              strokeDasharray="6 4"
                              strokeLinecap="round"
                            />
                            {/* Nodule lumineux à mi-chemin */}
                            <circle
                              cx={midX}
                              cy={midY}
                              r="2.5"
                              fill={focusedModule.color}
                              className="animate-ping"
                            />
                          </g>
                        );
                      })}
                    </g>
                  )}
                </svg>

                {/* ── Cœur Gravitationnel Central (EVO-LOG CADC Core) ── */}
                <div
                  style={{
                    left: `${cx}px`,
                    top: `${cy}px`,
                    transform: "translate(-50%, -50%)",
                  }}
                  onClick={() => setPinnedModuleKey(null)}
                  className="absolute z-20 flex flex-col items-center justify-center cursor-pointer group"
                  title="Noyau Central EVO-LOG CADC · Cliquez pour réinitialiser la vue"
                >
                  <div className="relative w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-slate-900 border-2 border-amber-500/60 flex items-center justify-center shadow-2xl shadow-amber-500/20 group-hover:scale-110 transition-transform">
                    <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-amber-500/30 to-indigo-600/30 blur-md animate-pulse" />
                    <Compass className="w-8 h-8 sm:w-9 sm:h-9 text-amber-400 group-hover:rotate-45 transition-transform duration-500" />
                    <span className="absolute -bottom-1 text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full bg-slate-950 text-amber-400 border border-amber-500/40 shadow">
                      CADC CORE
                    </span>
                  </div>
                  <span className="mt-2 text-[10px] font-bold text-slate-400 tracking-wider uppercase group-hover:text-amber-300 transition-colors">
                    {filteredNav.length} Pôles
                  </span>
                </div>

                {/* ── Nœuds des Modules Principaux (Planètes en Orbite) ── */}
                {filteredNav.map((mod) => {
                  const layout = moduleLayout[mod.key];
                  if (!layout) return null;

                  const isPinned = pinnedModuleKey === mod.key;
                  const isHovered = hoveredModuleKey === mod.key;
                  const isFocused = isPinned || isHovered;
                  const isActiveRoute = mod.key === activeModuleKey;
                  const ModIcon = mod.icon || LayoutDashboard;

                  // Opacité réduite si filtre de recherche actif et non correspondant
                  const opacity = q && !layout.matchesSearch ? "opacity-25" : "opacity-100";

                  return (
                    <div
                      key={mod.key}
                      style={{
                        left: `${layout.x}px`,
                        top: `${layout.y}px`,
                        transform: "translate(-50%, -50%)",
                      }}
                      className={`absolute z-30 transition-all duration-300 ${opacity}`}
                      onMouseEnter={() => {
                        if (!pinnedModuleKey) {
                          setHoveredModuleKey(mod.key);
                        }
                      }}
                      onMouseLeave={() => {
                        if (!pinnedModuleKey) {
                          setHoveredModuleKey(null);
                        }
                      }}
                    >
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Clic bascule l'état fixé / pinned
                          setPinnedModuleKey((prev) => (prev === mod.key ? null : mod.key));
                        }}
                        className={`relative rounded-full flex flex-col items-center justify-center transition-all ${
                          isFocused
                            ? "scale-125 z-40"
                            : "hover:scale-115 active:scale-95"
                        }`}
                        title={`${localizeTitle(mod, language)} · ${mod.subModules.length} sous-modules · Cliquez pour figer`}
                      >
                        {/* Anneau de lueur néon */}
                        <div
                          className={`absolute inset-0 rounded-full blur-md transition-opacity ${
                            isFocused
                              ? "opacity-90 animate-pulse"
                              : "opacity-40 group-hover:opacity-80"
                          }`}
                          style={{ backgroundColor: mod.color }}
                        />

                        {/* Corps orbital du module */}
                        <div
                          className={`relative w-11 h-11 sm:w-12 sm:h-12 rounded-full flex items-center justify-center text-white border-2 shadow-xl transition-colors ${
                            isPinned
                              ? "ring-4 ring-amber-400/80 border-white"
                              : isHovered
                              ? "ring-2 ring-white/60"
                              : isActiveRoute
                              ? "ring-2 ring-emerald-400/60"
                              : ""
                          }`}
                          style={{
                            borderColor: isPinned ? "#f59e0b" : mod.color,
                            background: `linear-gradient(135deg, ${mod.color}dd, #0f172a)`,
                          }}
                        >
                          <ModIcon className="w-5 h-5 sm:w-6 sm:h-6" />

                          {/* Badge indicateur de verrouillage / pin */}
                          {isPinned && (
                            <span className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-amber-500 text-slate-950 flex items-center justify-center shadow-lg border border-white">
                              <Pin className="w-3 h-3 fill-current" />
                            </span>
                          )}

                          {/* Badge nombre de sous-modules si non fixé */}
                          {!isPinned && (
                            <span className="absolute -bottom-1 -right-1 text-[9px] font-black px-1.5 py-0.2 rounded-full bg-slate-950 text-slate-200 border border-slate-700">
                              {mod.subModules.length}
                            </span>
                          )}
                        </div>

                        {/* Étiquette libellé sous le nœud */}
                        <span
                          className={`mt-1 text-[11px] font-bold text-center max-w-[90px] truncate px-1 rounded transition-colors ${
                            isFocused
                              ? "text-white bg-slate-950/90 shadow border border-slate-700"
                              : "text-slate-300 bg-slate-950/60"
                          }`}
                        >
                          {localizeTitle(mod, language)}
                        </span>
                      </button>
                    </div>
                  );
                })}

                {/* ── Nœuds Satellites : Arbre de Compétences (Sous-Modules) ── */}
                {focusedModule &&
                  skillTreeNodes.map((item) => {
                    const { sub, idx, x, y, matchesSearch } = item;
                    const SubIcon = sub.icon || LayoutDashboard;
                    const isSubHovered = hoveredSubKey === sub.path;
                    const isCurrentRoute = pathname === sub.path;
                    const opacity = q && !matchesSearch ? "opacity-30" : "opacity-100";

                    return (
                      <div
                        key={`skill-node-${sub.path}`}
                        style={{
                          left: `${x}px`,
                          top: `${y}px`,
                          transform: "translate(-50%, -50%)",
                          animationDelay: `${idx * 40}ms`,
                        }}
                        className={`absolute z-40 transition-all duration-200 animate-in zoom-in-75 ${opacity}`}
                        onMouseEnter={() => setHoveredSubKey(sub.path)}
                        onMouseLeave={() => setHoveredSubKey(null)}
                      >
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(sub.path);
                          }}
                          className={`group relative flex items-center gap-2 p-1.5 sm:p-2 rounded-xl backdrop-blur-md border transition-all text-left shadow-2xl ${
                            isSubHovered
                              ? "scale-110 bg-slate-800 border-white text-white z-50 ring-2"
                              : isCurrentRoute
                              ? "bg-slate-900 border-emerald-400 text-emerald-300 ring-1 ring-emerald-400/50"
                              : "bg-slate-900/90 border-slate-700 text-slate-200 hover:bg-slate-800 hover:border-slate-500"
                          }`}
                          style={
                            isSubHovered
                              ? {
                                  borderColor: focusedModule.color,
                                  boxShadow: `0 0 20px ${focusedModule.color}50`,
                                }
                              : undefined
                          }
                          title={`${localizeSubLabel(sub.label, language)} · Cliquer pour ouvrir`}
                        >
                          {/* Pastille orbe du sous-module */}
                          <div
                            className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center text-white shrink-0 shadow"
                            style={{
                              backgroundColor: `${focusedModule.color}25`,
                              borderColor: focusedModule.color,
                              borderWidth: "1.5px",
                            }}
                          >
                            <SubIcon
                              className="w-4 h-4"
                              style={{ color: focusedModule.color }}
                            />
                          </div>

                          {/* Libellé & T-Code / Badge */}
                          <div className="min-w-0 pr-1 max-w-[140px] sm:max-w-[170px]">
                            <div className="flex items-center gap-1">
                              <span className="text-[11px] sm:text-xs font-bold truncate group-hover:text-white">
                                {localizeSubLabel(sub.label, language)}
                              </span>
                            </div>
                            <div className="flex items-center gap-1.5 text-[9px] text-slate-400">
                              {sub.tcode && (
                                <span className="font-mono text-amber-400 bg-amber-400/10 px-1 py-0.2 rounded border border-amber-400/20">
                                  {sub.tcode}
                                </span>
                              )}
                              {sub.badge && (
                                <span className="text-slate-400 bg-slate-800 px-1 py-0.2 rounded">
                                  {sub.badge}
                                </span>
                              )}
                            </div>
                          </div>
                        </button>
                      </div>
                    );
                  })}

                {/* ── Dock HUD Inférieur : Inspecteur de Compétences & Accès Rapide ── */}
                {focusedModule && (
                  <div className="absolute bottom-3 left-3 right-3 z-50 flex items-center justify-between gap-3 p-3 rounded-2xl bg-slate-900/95 border border-slate-800 backdrop-blur-md shadow-2xl animate-in slide-in-from-bottom-3 duration-200">
                    <div className="flex items-center gap-3 min-w-0">
                      <div
                        className="w-9 h-9 rounded-xl flex items-center justify-center text-white shrink-0 shadow"
                        style={{
                          background: `linear-gradient(135deg, ${focusedModule.color}, #0f172a)`,
                        }}
                      >
                        {React.createElement(focusedModule.icon || LayoutDashboard, {
                          className: "w-5 h-5",
                        })}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs sm:text-sm font-black text-white truncate">
                            {localizeTitle(focusedModule, language)}
                          </span>
                          {pinnedModuleKey === focusedModule.key ? (
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1 shrink-0">
                              <Lock className="w-2.5 h-2.5" />
                              Fixé
                            </span>
                          ) : (
                            <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 shrink-0">
                              Aperçu
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 truncate">
                          {focusedModule.businessArea} · {focusedModule.subModules.length}{" "}
                          compétences disponibles
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        onClick={() => navigate(focusedModule.path)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 text-xs font-semibold border border-slate-700 hover:border-slate-600 transition-colors"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span className="hidden sm:inline">Hub principal</span>
                      </button>

                      {pinnedModuleKey === focusedModule.key ? (
                        <button
                          type="button"
                          onClick={() => setPinnedModuleKey(null)}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-semibold border border-amber-500/40 transition-colors"
                        >
                          <Unlock className="w-3.5 h-3.5" />
                          <span>Libérer</span>
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setPinnedModuleKey(focusedModule.key)}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-colors"
                        >
                          <Pin className="w-3.5 h-3.5" />
                          <span>Figer l'arbre</span>
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ══════════════════════════════════════════════════════════════════
                MODE 2 : GRILLE CLASSIQUE (Vue d'origine conservée intacte)
               ══════════════════════════════════════════════════════════════════ */}
            {viewMode === "grid" && (
              <div className="flex-1 overflow-y-auto p-3 sm:p-4">
                {visibleModules.length === 0 ? (
                  <div className="py-16 text-center text-sm text-slate-500">
                    {t.common.noResultsFor} « {query} »
                  </div>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                    {visibleModules.map((mod) => {
                      const ModIcon = mod.icon || LayoutDashboard;
                      const isActive = mod.key === activeModuleKey;
                      return (
                        <section
                          key={mod.key}
                          className={`rounded-xl border bg-slate-950/60 p-3 ${
                            isActive ? "border-slate-600" : "border-slate-800"
                          }`}
                          style={isActive ? { borderColor: `${mod.color}80` } : undefined}
                        >
                          <button
                            onClick={() => navigate(mod.path)}
                            className="w-full flex items-center gap-3 mb-2 text-left group"
                          >
                            <span
                              className={`shrink-0 w-9 h-9 rounded-lg bg-gradient-to-tr ${mod.bgGradient} text-white flex items-center justify-center shadow`}
                            >
                              <ModIcon className="w-5 h-5" />
                            </span>
                            <span className="min-w-0 flex-1">
                              <span className="block text-[13px] font-bold text-slate-100 truncate group-hover:text-white">
                                {localizeTitle(mod, language)}
                              </span>
                              <span className="block text-[11px] text-slate-500 truncate">
                                {mod.subModules.length} {t.shell.subModules}
                              </span>
                            </span>
                            <span
                              className="shrink-0 h-2 w-2 rounded-full"
                              style={{ backgroundColor: mod.color }}
                            />
                          </button>

                          <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
                            {mod.subModules.map((sub) => {
                              const SubIcon = sub.icon || LayoutDashboard;
                              const subActive = pathname === sub.path;
                              return (
                                <button
                                  key={`${mod.key}:${sub.path}`}
                                  onClick={() => navigate(sub.path)}
                                  title={localizeSubLabel(sub.label, language)}
                                  className={`flex items-center gap-1.5 rounded-lg border px-2 py-1.5 text-left transition-colors ${
                                    subActive
                                      ? "bg-slate-800 border-slate-600 text-white"
                                      : "bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 hover:border-slate-700"
                                  }`}
                                >
                                  <SubIcon
                                    className="w-3.5 h-3.5 shrink-0"
                                    style={{ color: mod.color }}
                                  />
                                  <span className="text-[11px] font-medium truncate">
                                    {localizeSubLabel(sub.label, language)}
                                  </span>
                                </button>
                              );
                            })}
                          </div>
                        </section>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}


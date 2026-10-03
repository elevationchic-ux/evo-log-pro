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
  Lock,
  ChevronRight,
  Layers,
  ArrowRight,
} from "lucide-react";
import {
  NAVIGATION_REGISTRY,
  ModuleNavConfig,
  SubModuleItem,
  resolveModuleKeyForPath,
} from "@/config/navigationRegistry";
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

  // Mode d'affichage : 'orb' (Orbe Gravitationnelle & Arbre) ou 'grid' (Grille classique)
  const [viewMode, setViewMode] = useState<"orb" | "grid">("orb");

  // Interaction Orbe Gravitationnelle :
  const [hoveredModuleKey, setHoveredModuleKey] = useState<string | null>(null);
  const [pinnedModuleKey, setPinnedModuleKey] = useState<string | null>(null);

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

  // Liste des modules autorisés
  const filteredNav: ModuleNavConfig[] = useMemo(() => {
    return (Object.values(NAVIGATION_REGISTRY) as ModuleNavConfig[]).filter(
      (m: ModuleNavConfig) => m.key !== "superadmin-cadc" || isSuperUser
    );
  }, [isSuperUser]);

  // Résolution du module actif à partir de l'URL actuelle
  const resolvedModuleKey = resolveModuleKeyForPath(pathname);
  const activeModuleKey =
    resolvedModuleKey !== "dashboard" && NAVIGATION_REGISTRY[resolvedModuleKey]
      ? resolvedModuleKey
      : pathname.startsWith("/dashboard") || pathname === "/"
      ? "dashboard"
      : filteredNav[0]?.key;

  const activeOrbit =
    filteredNav.find((m) => m.key === activeModuleKey) || filteredNav[0] || NAVIGATION_REGISTRY.dashboard;
  const MainIcon = activeOrbit.icon || LayoutDashboard;

  // Filtre de recherche
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

  // Module sélectionné : priorise le module épinglé, sinon le survolé, sinon l'actif par défaut
  const currentFocusedModule = useMemo(() => {
    const targetKey = pinnedModuleKey || hoveredModuleKey || activeModuleKey;
    return filteredNav.find((m) => m.key === targetKey) || filteredNav[0];
  }, [pinnedModuleKey, hoveredModuleKey, activeModuleKey, filteredNav]);

  // ── Drag FAB : mousemove/mouseup attachés sur window pour drag fluide même hors du bouton ──
  const isDraggingRef = useRef(false);

  const beginDrag = (clientX: number, clientY: number) => {
    isDraggingRef.current = false;
    setIsDragging(false);
    dragStartRef.current = { startX: clientX, startY: clientY, posX: position.x, posY: position.y };

    const onMouseMove = (e: MouseEvent) => {
      const deltaX = dragStartRef.current.startX - e.clientX;
      const deltaY = e.clientY - dragStartRef.current.startY;
      if (Math.abs(deltaX) > 4 || Math.abs(deltaY) > 4) {
        isDraggingRef.current = true;
        setIsDragging(true);
      }
      setPosition({
        x: Math.max(10, Math.min(window.innerWidth - 70, dragStartRef.current.posX + deltaX)),
        y: Math.max(80, Math.min(window.innerHeight - 80, dragStartRef.current.posY + deltaY)),
      });
    };

    const onMouseUp = () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      window.setTimeout(() => {
        isDraggingRef.current = false;
        setIsDragging(false);
      }, 0);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  const moveDragTouch = (clientX: number, clientY: number) => {
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

  // Fermeture clavier
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

  return (
    <>
      {/* ── Bouton flottant déplaçable (FAB) ── */}
      <div
        style={{ right: `${position.x}px`, top: `${position.y}px` }}
        className="fixed z-[85] select-none cursor-grab active:cursor-grabbing"
      >
        <button
          onMouseDown={(e) => { e.preventDefault(); beginDrag(e.clientX, e.clientY); }}
          onTouchStart={(e) => beginDrag(e.touches[0].clientX, e.touches[0].clientY)}
          onTouchMove={(e) => { e.preventDefault(); moveDragTouch(e.touches[0].clientX, e.touches[0].clientY); }}
          onTouchEnd={() => window.setTimeout(() => setIsDragging(false), 0)}
          onClick={() => {
            if (!isDraggingRef.current) setIsOpen((o) => !o);
          }}
          className={`relative w-14 h-14 rounded-full bg-slate-900 border-2 flex items-center justify-center shadow-2xl transition-transform ${isDragging ? 'cursor-grabbing scale-110' : 'cursor-grab hover:scale-105 active:scale-95'}`}
          style={{ borderColor: activeOrbit.color }}
          aria-label={t.shell.bubbleTitle}
          title={isDragging ? 'Relâchez pour repositionner' : t.shell.bubbleTitle}
        >
          {isDragging && (
            <span className="absolute -inset-1 rounded-full border-2 border-dashed border-slate-500/60 animate-spin" style={{ animationDuration: '3s' }} />
          )}
          <div
            className={`flex h-11 w-11 items-center justify-center rounded-full bg-slate-800 text-slate-100 transition-opacity ${isDragging ? 'opacity-80' : ''}`}
          >
            {isOpen ? <X className="w-6 h-6" /> : <MainIcon className="w-6 h-6" />}
          </div>
          <span className="absolute -top-1 -right-1 bg-slate-950 text-slate-300 font-semibold text-[10px] px-2 py-0.5 rounded-full border border-slate-700">
            {filteredNav.length}
          </span>
        </button>
      </div>

      {/* ── Fenêtre modale Plein Écran Adaptative ── */}
      {isOpen && (
        <div className="fixed inset-0 z-[90] bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-0 sm:p-4 md:p-6 animate-in fade-in duration-150">
          <div className="absolute inset-0" onClick={() => setIsOpen(false)} aria-hidden="true" />

          <div className="relative z-10 flex w-full h-full sm:h-[92vh] sm:max-w-6xl sm:rounded-2xl bg-slate-900/95 border-0 sm:border sm:border-slate-800 shadow-2xl flex-col overflow-hidden">
            {/* ── EN-TÊTE FIXE ── */}
            <header className="shrink-0 border-b border-slate-800 bg-slate-950/80 px-4 py-3 flex flex-col gap-2.5">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-200 shrink-0">
                    <Orbit className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h2 className="text-sm font-bold text-slate-100 truncate flex items-center gap-2">
                      {t.shell.bubbleTitle}
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        {filteredNav.length} {t.shell.modules}
                      </span>
                    </h2>
                    <p className="text-[11px] text-slate-400 truncate">
                      {totalSubs} {t.shell.subModules} · Navigation Portuaire & Douanière
                    </p>
                  </div>
                </div>

                {/* Sélecteur de Mode */}
                <div className="flex items-center gap-2 shrink-0">
                  <div className="flex items-center bg-slate-900 p-0.5 rounded-xl border border-slate-800 shadow-inner">
                    <button
                      type="button"
                      onClick={() => handleSetViewMode("orb")}
                      className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        viewMode === "orb"
                          ? "bg-slate-700 text-white"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                      title="Affichage Orbe Gravitationnelle & Arbre de Compétences"
                    >
                      <Orbit className="w-3.5 h-3.5" />
                      <span className="hidden sm:inline">Orbe & Arbre</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSetViewMode("grid")}
                      className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        viewMode === "grid"
                          ? "bg-slate-800 text-white shadow"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                      title="Affichage Grille Classique"
                    >
                      <LayoutGrid className="w-3.5 h-3.5" />
                      <span className="hidden sm:inline">Grille</span>
                    </button>
                  </div>

                  <button
                    onClick={() => setIsOpen(false)}
                    className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-slate-100 transition-colors"
                    aria-label={t.common.close}
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Barre de Recherche Simple et Rapide */}
              <div className="relative">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={
                    viewMode === "orb"
                      ? "Rechercher un module, code T-Code ou sous-module..."
                      : t.shell.bubbleSearch
                  }
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-8 py-1.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-slate-500 transition-colors"
                />
                {query && (
                  <button
                    onClick={() => setQuery("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 hover:text-slate-300"
                  >
                    ✕
                  </button>
                )}
              </div>
            </header>

            {/* ══════════════════════════════════════════════════════════════════
                MODE 1 : ORBE GRAVITATIONNELLE & ARBRE DE COMPÉTENCES
               ══════════════════════════════════════════════════════════════════ */}
            {viewMode === "orb" && (
              <div className="flex-1 flex flex-col md:flex-row overflow-hidden bg-slate-950">
                {/* ── ZONE 1 : SÉLECTEUR GRAVITATIONNEL DES MODULES ── */}
                {/* Sur Mobile : Défilement horizontal fluide / Sur PC : Colonne Orbitale structurée */}
                <div className="md:w-80 lg:w-96 shrink-0 border-b md:border-b-0 md:border-r border-slate-800/80 bg-slate-950/70 flex flex-col overflow-hidden">
                  <div className="p-3 border-b border-slate-800/60 bg-slate-900/40 flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-slate-500" />
                      Pôles & Modules ({filteredNav.length})
                    </span>
                    <span className="text-[10px] text-slate-400">
                      {pinnedModuleKey ? "Verrouillé" : "Survolez / Cliquez"}
                    </span>
                  </div>

                  {/* Liste des modules en cartes épurées sans halo baveux */}
                  <div className="flex-1 overflow-x-auto md:overflow-y-auto p-2 sm:p-3 flex md:flex-col gap-2 no-scrollbar">
                    {visibleModules.map((mod) => {
                      const isSelected = currentFocusedModule?.key === mod.key;
                      const isPinned = pinnedModuleKey === mod.key;
                      const ModIcon = mod.icon || LayoutDashboard;

                      return (
                        <button
                          key={mod.key}
                          type="button"
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
                          onClick={() => {
                            setPinnedModuleKey((prev) => (prev === mod.key ? null : mod.key));
                          }}
                          className={`shrink-0 md:w-full flex items-center gap-2.5 p-2 sm:p-2.5 rounded-xl text-left border transition-all ${
                            isSelected
                              ? "bg-slate-800/90 border-slate-600 shadow-md text-white"
                              : "bg-slate-900/50 border-slate-800/80 text-slate-300 hover:bg-slate-800/50 hover:border-slate-700"
                          }`}
                          style={
                            isSelected
                              ? {
                                  borderColor: mod.color,
                                  boxShadow: `inset 3px 0 0 0 ${mod.color}`,
                                }
                              : undefined
                          }
                        >
                          <div
                            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
                            style={{ backgroundColor: `${mod.color}22`, color: mod.color }}
                          >
                            <ModIcon className="w-4 h-4" />
                          </div>

                          <div className="min-w-0 pr-1 max-w-[130px] md:max-w-none md:flex-1">
                            <div className="flex items-center justify-between gap-1">
                              <span className="text-xs font-bold truncate text-slate-100">
                                {localizeTitle(mod, language)}
                              </span>
                              {isPinned && (
                                <Pin className="w-3 h-3 text-slate-400 shrink-0 fill-current" />
                              )}
                            </div>
                            <span className="block text-[10px] text-slate-400 truncate">
                              {mod.subModules.length} {t.shell.subModules} · {mod.businessArea}
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* ── ZONE 2 : ARBRE DE COMPÉTENCES DU MODULE (SKILL TREE) ── */}
                <div className="flex-1 flex flex-col overflow-hidden bg-slate-950/40">
                  {/* Bandeau d'information du Module Sélectionné */}
                  {currentFocusedModule && (
                    <div className="p-4 border-b border-slate-800/80 bg-slate-900/60 flex flex-wrap items-center justify-between gap-3 shrink-0">
                      <div className="flex items-center gap-3 min-w-0">
                        <div
                          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
                          style={{ backgroundColor: `${currentFocusedModule.color}22`, color: currentFocusedModule.color }}
                        >
                          {React.createElement(currentFocusedModule.icon || LayoutDashboard, {
                            className: "w-5 h-5",
                          })}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <h3 className="text-sm font-bold text-white truncate">
                              {localizeTitle(currentFocusedModule, language)}
                            </h3>
                            {pinnedModuleKey === currentFocusedModule.key ? (
                              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
                                <Lock className="w-2.5 h-2.5" />
                                Fixé
                              </span>
                            ) : (
                              <span className="text-[10px] text-slate-400 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">
                                Aperçu live
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400 truncate">
                            {currentFocusedModule.processPhase || currentFocusedModule.businessArea}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {pinnedModuleKey === currentFocusedModule.key ? (
                          <button
                            type="button"
                            onClick={() => setPinnedModuleKey(null)}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
                          >
                            <Unlock className="w-3.5 h-3.5" />
                            <span>Déverrouiller</span>
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => setPinnedModuleKey(currentFocusedModule.key)}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
                          >
                            <Pin className="w-3.5 h-3.5" />
                            <span>Verrouiller</span>
                          </button>
                        )}

                        <button
                          type="button"
                          onClick={() => navigate(currentFocusedModule.path)}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-on-primary hover:opacity-90 text-xs font-semibold transition-opacity"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          <span>Accéder au Hub</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Arbre de Compétences : Grille de Sous-Modules Connectés */}
                  <div className="flex-1 overflow-y-auto p-4 sm:p-6">
                    {currentFocusedModule?.subModules?.length === 0 ? (
                      <div className="py-16 text-center text-sm text-slate-500">
                        Aucun sous-module configuré dans ce pôle.
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-xs text-slate-400 font-semibold px-1">
                          <span className="flex items-center gap-1.5">
                            <Layers className="w-3.5 h-3.5 text-slate-400" />
                            Compétences & Processus Intégrés ({currentFocusedModule?.subModules.length})
                          </span>
                          <span className="text-[11px] text-slate-400">
                            Cliquez sur un sous-module pour ouvrir
                          </span>
                        </div>

                        {/* Grille des sous-modules comme un arbre de compétences */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                          {currentFocusedModule?.subModules.map((sub, idx) => {
                            const SubIcon = sub.icon || LayoutDashboard;
                            const isCurrent = pathname === sub.path;

                            return (
                              <button
                                key={`${currentFocusedModule.key}:${sub.path}`}
                                type="button"
                                onClick={() => navigate(sub.path)}
                                className={`group flex flex-col p-3 rounded-xl border text-left transition-all ${
                                  isCurrent
                                    ? "bg-slate-800 border-primary/50 text-white"
                                    : "bg-slate-900/80 border-slate-800 text-slate-300 hover:bg-slate-850 hover:border-slate-700 hover:text-white"
                                }`}
                              >
                                <div className="flex items-start justify-between gap-2 mb-2">
                                  <div
                                    className="w-8 h-8 rounded-lg flex items-center justify-center text-white shrink-0 shadow-sm"
                                    style={{
                                      backgroundColor: `${currentFocusedModule.color}25`,
                                      borderColor: currentFocusedModule.color,
                                      borderWidth: "1px",
                                    }}
                                  >
                                    <SubIcon
                                      className="w-4 h-4"
                                      style={{ color: currentFocusedModule.color }}
                                    />
                                  </div>

                                  <div className="flex items-center gap-1">
                                    {sub.tcode && (
                                      <span className="font-mono text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">
                                        {sub.tcode}
                                      </span>
                                    )}
                                    {sub.badge && (
                                      <span className="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">
                                        {sub.badge}
                                      </span>
                                    )}
                                  </div>
                                </div>

                                <div className="min-w-0 flex-1">
                                  <span className="block text-xs font-bold text-slate-100 group-hover:text-white transition-colors truncate">
                                    {localizeSubLabel(sub.label, language)}
                                  </span>
                                  {sub.description && (
                                    <span className="block text-[11px] text-slate-400 line-clamp-2 mt-1 leading-snug">
                                      {sub.description}
                                    </span>
                                  )}
                                </div>

                                <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 group-hover:text-slate-300">
                                  <span>{sub.businessProcess || "Processus direct"}</span>
                                  <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* ══════════════════════════════════════════════════════════════════
                MODE 2 : GRILLE CLASSIQUE (Vue d'origine conservée)
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
                              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
                              style={{ backgroundColor: `${mod.color}22`, color: mod.color }}
                            >
                              <ModIcon className="w-5 h-5" />
                            </span>
                            <span className="min-w-0 flex-1">
                              <span className="block text-[13px] font-bold text-slate-100 truncate group-hover:text-white">
                                {localizeTitle(mod, language)}
                              </span>
                              <span className="block text-[11px] text-slate-400 truncate">
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

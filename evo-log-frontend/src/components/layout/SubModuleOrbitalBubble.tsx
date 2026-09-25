"use client";

import React, { useState, useRef, useMemo, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { X, Search, LayoutDashboard } from "lucide-react";
import { NAVIGATION_REGISTRY, ModuleNavConfig } from "@/config/navigationRegistry";
import { localizeTitle, localizeSubLabel } from "@/config/navI18n";
import { useSettings } from "@/components/layout/SettingsProvider";
import { useI18n } from "@/hooks/useI18n";

export default function SubModuleOrbitalBubble() {
  const pathname = usePathname();
  const router = useRouter();
  const { language } = useSettings();
  const t = useI18n();

  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [position, setPosition] = useState({ x: 20, y: 180 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef<{ startX: number; startY: number; posX: number; posY: number }>({ startX: 0, startY: 0, posX: 0, posY: 0 });

  // TOUS les modules sont exposés dans la bulle flottante (exigence produit).
  const filteredNav: ModuleNavConfig[] = Object.values(NAVIGATION_REGISTRY);

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
        const moduleMatch = m.title.toLowerCase().includes(q) || (m.titleEn || '').toLowerCase().includes(q) || m.key.includes(q);
        const subs = m.subModules.filter(
          (s) => s.label.toLowerCase().includes(q) || localizeSubLabel(s.label, language).toLowerCase().includes(q) || s.path.toLowerCase().includes(q)
        );
        if (moduleMatch) return m;
        if (subs.length) return { ...m, subModules: subs };
        return null;
      })
      .filter(Boolean) as ModuleNavConfig[];
  }, [filteredNav, q]);

  const totalSubs = filteredNav.reduce((acc, m) => acc + m.subModules.length, 0);

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

  const navigate = (path: string) => {
    setIsOpen(false);
    router.push(path);
  };

  // Fermeture clavier : Échap replie le panneau (tous modules), aligné sur le reste du chrome.
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen]);

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
          onClick={() => { if (!isDragging) setIsOpen((o) => !o); }}
          className={`relative w-14 h-14 rounded-full bg-slate-900 border-2 flex items-center justify-center shadow-2xl transition-transform hover:scale-110 active:scale-95 ${activeOrbit.glow}`}
          style={{ borderColor: activeOrbit.color }}
          aria-label={t.shell.bubbleTitle}
          title={t.shell.bubbleTitle}
        >
          <div className={`absolute inset-0 rounded-full blur-md opacity-60 animate-pulse bg-gradient-to-tr ${activeOrbit.bgGradient}`} />
          <div className={`relative w-11 h-11 rounded-full bg-gradient-to-tr ${activeOrbit.bgGradient} flex items-center justify-center text-white shadow-inner`}>
            {isOpen ? <X className="w-6 h-6" /> : <MainIcon className="w-6 h-6" />}
          </div>
          <span className="absolute -top-1 -right-1 bg-slate-950 text-amber-400 font-black text-[10px] px-2 py-0.5 rounded-full border border-amber-500/50 shadow-md">
            {filteredNav.length}
          </span>
        </button>
      </div>

      {/* ── Panneau de navigation : tous modules + tous sous-modules ── */}
      {isOpen && (
        <div className="fixed inset-0 z-[90] bg-slate-950/90 backdrop-blur-md flex items-stretch sm:items-center justify-center animate-in fade-in duration-200">
          <div className="absolute inset-0" onClick={() => setIsOpen(false)} aria-hidden="true" />

          <div className="relative z-10 flex w-full h-full sm:h-auto sm:max-h-[88vh] sm:max-w-5xl sm:rounded-2xl bg-slate-900 border-0 sm:border sm:border-slate-800 shadow-2xl flex-col overflow-hidden">
            {/* En-tête */}
            <div className="shrink-0 border-b border-slate-800 bg-slate-900 px-4 py-3 flex flex-col gap-3">
              <div className="flex items-center gap-3">
                <div className="min-w-0 flex-1">
                  <h2 className="text-sm font-black text-slate-100 truncate">{t.shell.bubbleTitle}</h2>
                  <p className="text-[11px] text-slate-400">
                    {filteredNav.length} {t.shell.modules} · {totalSubs} {t.shell.subModules}
                  </p>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="shrink-0 rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
                  aria-label={t.common.close}
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={t.shell.bubbleSearch}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-slate-600"
                />
              </div>
            </div>

            {/* Corps : liste défilante de tous les modules et de leurs sous-modules */}
            <div className="flex-1 overflow-y-auto p-3 sm:p-4">
              {visibleModules.length === 0 ? (
                <div className="py-16 text-center text-sm text-slate-500">{t.common.noResultsFor} « {query} »</div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                  {visibleModules.map((mod) => {
                    const ModIcon = mod.icon || LayoutDashboard;
                    const isActive = mod.key === activeModuleKey;
                    return (
                      <section
                        key={mod.key}
                        className={`rounded-xl border bg-slate-950/60 p-3 ${isActive ? "border-slate-600" : "border-slate-800"}`}
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
                            <span className="block text-[13px] font-bold text-slate-100 truncate group-hover:text-white">{localizeTitle(mod, language)}</span>
                            <span className="block text-[10px] text-slate-500 truncate">{mod.subModules.length} {t.shell.subModules}</span>
                          </span>
                          <span className="shrink-0 h-2 w-2 rounded-full" style={{ backgroundColor: mod.color }} />
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
                                <SubIcon className="w-3.5 h-3.5 shrink-0" style={{ color: mod.color }} />
                                <span className="text-[11px] font-medium truncate">{localizeSubLabel(sub.label, language)}</span>
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
          </div>
        </div>
      )}
    </>
  );
}

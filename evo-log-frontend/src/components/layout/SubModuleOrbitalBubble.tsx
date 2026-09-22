"use client";

import React, { useState, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { X, Layers, LayoutDashboard } from "lucide-react";
import { NAVIGATION_REGISTRY, getFilteredNavigationForUser, ModuleNavConfig } from "@/config/navigationRegistry";

export default function SubModuleOrbitalBubble() {
  const pathname = usePathname();
  const router = useRouter();
  const { data: session } = useSession();

  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ x: 20, y: 180 }); // Distance relative du bord droit (px)
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef<{ startX: number; startY: number; posX: number; posY: number }>({ startX: 0, startY: 0, posX: 0, posY: 0 });

  // Navigation dynamique filtrée selon le profil RBAC de l'utilisateur
  const filteredNav: ModuleNavConfig[] = getFilteredNavigationForUser(session?.user as any);

  // Résolution intelligente du module actif à partir du pathname
  let activeModuleKey = Object.keys(NAVIGATION_REGISTRY).find(k => k !== "dashboard" && pathname.startsWith(`/${k}`));
  if (!activeModuleKey) {
    if (pathname.startsWith('/dashboard') || pathname === '/') {
      activeModuleKey = "dashboard";
    } else if (pathname.startsWith('/master-data') || pathname.startsWith('/suppliers') || pathname.startsWith('/tiers')) {
      activeModuleKey = "master-data";
    } else if (pathname.startsWith('/security')) {
      activeModuleKey = "qhse";
    } else {
      activeModuleKey = "magasin";
    }
  }

  // Chercher le module correspondant dans la liste filtrée RBAC
  const activeOrbit = filteredNav.find(m => m.key === activeModuleKey) || filteredNav[0] || NAVIGATION_REGISTRY.magasin;

  // Gestion du Dragging (Souris & Touch)
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(false);
    dragStartRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      posX: position.x,
      posY: position.y
    };

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = dragStartRef.current.startX - moveEvent.clientX;
      const deltaY = moveEvent.clientY - dragStartRef.current.startY;
      if (Math.abs(deltaX) > 4 || Math.abs(deltaY) > 4) {
        setIsDragging(true);
      }
      setPosition({
        x: Math.max(10, Math.min(window.innerWidth - 70, dragStartRef.current.posX + deltaX)),
        y: Math.max(80, Math.min(window.innerHeight - 80, dragStartRef.current.posY + deltaY))
      });
    };

    const handleMouseUp = () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    dragStartRef.current = {
      startX: touch.clientX,
      startY: touch.clientY,
      posX: position.x,
      posY: position.y
    };

    const handleTouchMove = (moveEvent: TouchEvent) => {
      const moveTouch = moveEvent.touches[0];
      const deltaX = dragStartRef.current.startX - moveTouch.clientX;
      const deltaY = moveTouch.clientY - dragStartRef.current.startY;
      if (Math.abs(deltaX) > 4 || Math.abs(deltaY) > 4) {
        setIsDragging(true);
      }
      setPosition({
        x: Math.max(10, Math.min(window.innerWidth - 70, dragStartRef.current.posX + deltaX)),
        y: Math.max(80, Math.min(window.innerHeight - 80, dragStartRef.current.posY + deltaY))
      });
    };

    const handleTouchEnd = () => {
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleTouchEnd);
    };

    window.addEventListener("touchmove", handleTouchMove);
    window.addEventListener("touchend", handleTouchEnd);
  };

  const MainIcon = activeOrbit.icon;
  const itemsCount = activeOrbit.subModules.length;
  // Calcul du rayon orbital dynamique selon le nombre de sous-modules (évite les chevauchements)
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 640;
  const orbitRadius = isMobile
    ? Math.max(130, Math.min(180, 110 + itemsCount * 5))
    : Math.max(190, Math.min(260, 160 + itemsCount * 7));

  return (
    <>
      {/* --- Bulle Flottante Déplaçable (Bord Droit) --- */}
      <div
        style={{ right: `${position.x}px`, top: `${position.y}px` }}
        className="fixed z-[85] select-none cursor-grab active:cursor-grabbing transition-transform duration-100"
      >
        <button
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
          onClick={() => {
            if (!isDragging) {
              setIsOpen(!isOpen);
            }
          }}
          className={`relative group w-14 h-14 rounded-full bg-slate-900 border-2 flex items-center justify-center shadow-2xl transition-all hover:scale-110 active:scale-95 ${activeOrbit.glow}`}
          style={{ borderColor: activeOrbit.color }}
          title={`Ouvrir les ${itemsCount} sous-modules de ${activeOrbit.title}`}
        >
          {/* Glowing Aura Effect */}
          <div
            className={`absolute inset-0 rounded-full blur-md opacity-60 animate-pulse bg-gradient-to-tr ${activeOrbit.bgGradient}`}
          />

          {/* Icon and Badge */}
          <div className={`relative w-11 h-11 rounded-full bg-gradient-to-tr ${activeOrbit.bgGradient} flex items-center justify-center text-white shadow-inner`}>
            {isOpen ? <X className="w-6 h-6 animate-in spin-in-90 duration-200" /> : <MainIcon className="w-6 h-6" />}
          </div>

          {/* Sub-module Count Badge */}
          <span className="absolute -top-1 -right-1 bg-slate-950 text-amber-400 font-black text-[10px] px-2 py-0.5 rounded-full border border-amber-500/50 shadow-md">
            {itemsCount}
          </span>
        </button>
      </div>

      {/* --- Overlay Modal Orbitale avec Animation 3D --- */}
      {isOpen && (
        <div className="fixed inset-0 z-[90] bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
          {/* Backdrop Click Closes */}
          <div className="absolute inset-0" onClick={() => setIsOpen(false)} />

          {/* Central Radial Container */}
          <div
            style={{ width: `${orbitRadius * 2 + 100}px`, height: `${orbitRadius * 2 + 100}px` }}
            className="relative flex items-center justify-center pointer-events-none transition-all duration-300 max-w-[95vw] max-h-[95vh]"
          >
            {/* Pulsating Orbital Ring */}
            <div
              style={{ width: `${orbitRadius * 2}px`, height: `${orbitRadius * 2}px`, borderColor: `${activeOrbit.color}66` }}
              className="absolute rounded-full border-2 border-dashed animate-spin-slow"
            />

            {/* Central Module Sphere */}
            {(() => {
              const MainIconComponent = activeOrbit.icon || LayoutDashboard;
              return (
                <div
                  className="relative z-10 w-28 h-28 sm:w-32 sm:h-32 rounded-full bg-slate-900 border-4 flex flex-col items-center justify-center p-2 text-center shadow-2xl pointer-events-auto cursor-pointer group hover:scale-105 transition-all"
                  style={{ borderColor: activeOrbit.color, boxShadow: `0 0 25px ${activeOrbit.color}40` }}
                  onClick={() => setIsOpen(false)}
                >
                  <div className={`w-12 h-12 rounded-full bg-gradient-to-tr ${activeOrbit.bgGradient} text-white flex items-center justify-center shadow-lg mb-1`}>
                    <MainIconComponent className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-[11px] font-black text-slate-100 truncate w-full px-1">{activeOrbit.title}</span>
                  <span className="text-[9px] font-bold" style={{ color: activeOrbit.color }}>Fermer ({itemsCount})</span>
                </div>
              );
            })()}

            {/* Orbiting Sub-Module Items */}
            {activeOrbit.subModules.map((item, index) => {
              const angle = (index / itemsCount) * 2 * Math.PI - Math.PI / 2;
              const x = Math.cos(angle) * orbitRadius;
              const y = Math.sin(angle) * orbitRadius;
              const ItemIconComponent = item.icon || Layers;
              const isActiveRoute = pathname === item.path;

              return (
                <div
                  key={item.path}
                  style={{ transform: `translate(${x}px, ${y}px)` }}
                  className="absolute pointer-events-auto transition-transform duration-300"
                >
                  <button
                    onClick={() => {
                      setIsOpen(false);
                      router.push(item.path);
                    }}
                    className={`flex flex-col items-center justify-center w-16 h-16 sm:w-18 sm:h-18 rounded-2xl p-2 border shadow-lg transition-all duration-200 hover:scale-110 group ${
                      isActiveRoute
                        ? 'bg-slate-900 text-white border-blue-500 shadow-blue-500/30'
                        : 'bg-slate-900/90 text-slate-200 border-slate-700/60 hover:bg-slate-800 hover:border-slate-500'
                    }`}
                  >
                    <ItemIconComponent className={`w-5 h-5 mb-1 transition-colors ${isActiveRoute ? 'text-blue-400' : 'text-slate-300 group-hover:text-white'}`} />

                    {/* Tooltip Label on Hover */}
                    <div className="absolute -bottom-8 whitespace-nowrap bg-slate-950 text-slate-100 font-bold text-[10px] sm:text-xs px-2.5 py-1 rounded-xl border border-slate-800 shadow-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                      {item.label}
                    </div>

                    {/* Optional Badge */}
                    {item.badge && (
                      <span className="absolute -top-2 -right-1 bg-amber-500 text-slate-950 font-black text-[9px] px-1.5 py-0.5 rounded-full border border-amber-300 shadow-sm">
                        {item.badge}
                      </span>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}

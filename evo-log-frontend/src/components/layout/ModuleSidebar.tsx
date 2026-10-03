"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "next-auth/react";
import { NAVIGATION_REGISTRY, ModuleNavConfig, resolveModuleKeyForPath } from "@/config/navigationRegistry";
import { localizeTitle, localizeSubLabel } from "@/config/navI18n";
import { useSettings } from "@/components/layout/SettingsProvider";
import { useDomainTransition } from "@/components/shared/DomainTransitionContext";
import {
  LayoutDashboard,
  Truck,
  Package,
  DollarSign,
  Users,
  ShieldAlert,
  Settings,
  X,
  ChevronRight,
  Building,
  UserCheck,
  Globe,
  Tag,
  Radio,
  Fuel,
  ShoppingCart,
  Landmark,
  BarChart3,
  Lock,
  AlertTriangle,
  ChevronLeft
} from "lucide-react";

export type ModuleType =
  | "admin"
  | "master-data"
  | "transport"
  | "finance"
  | "magasin"
  | "parc"
  | "audit"
  | "dashboard"
  | "rh"
  | "acconage"
  | "qhse"
  | "transit"
  | "maintenance"
  | "client-portal"
  | "cotations"
  | "tracking"
  | "fuel-guard"
  | "procurement"
  | "compliance"
  | "bi"
  | "settings";

interface ModuleSidebarProps {
  isCollapsed?: boolean;
  isMobile?: boolean;
  isOpen?: boolean;
  onClose?: () => void;
  onToggle?: () => void;
}

export default function ModuleSidebar({
  isCollapsed = false,
  isMobile = false,
  isOpen = false,
  onClose,
  onToggle,
}: ModuleSidebarProps) {
  const pathname = usePathname();
  const { data: session } = useSession();
  const { language } = useSettings();
  const { triggerDomainTransition } = useDomainTransition();

  // Access Warning Modal State
  const [deniedModalItem, setDeniedModalItem] = useState<{ label: string; key: string } | null>(null);

  const userRoles: string[] = (session?.user as any)?.roles || [];
  const userModules: string[] = (session?.user as any)?.modules_allowed || [];
  const isAdmin = userRoles.some(r => r.toUpperCase() === "ADMIN");
  // Console Super-Admin CADC : niveau hiérarchique 0 (ou compte super-utilisateur).
  const isSuperUser = Boolean((session?.user as any)?.is_superuser)
    || Number((session?.user as any)?.role_level ?? 9) === 0;

  const [expandedModule, setExpandedModule] = useState<string | null>(null);

  // Fermeture clavier : Echap replie d'abord la modale d'acces refuse, puis le
  // tiroir mobile. Sans cela, le clavier restait sans issue de sortie.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (deniedModalItem) { setDeniedModalItem(null); return; }
      if (isMobile && isOpen && onClose) onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [deniedModalItem, isMobile, isOpen, onClose]);

  // Tous les modules sont visibles partout (exigence produit). La restriction
  // d'accès réelle est appliquée côté API à chaque requête ; les modules hors
  // profil restent affichés mais grisés/cadenassés via checkModuleAccess.
  // EXCEPTION d'invisibilité : la console Super-Admin CADC n'est jamais affichée
  // (même grisée) à un non-super-admin : on ne doit pas divulguer son existence.
  const filteredNav: ModuleNavConfig[] = Object.values(NAVIGATION_REGISTRY).filter(
    (m) => m.key !== "superadmin-cadc" || isSuperUser
  );

  const checkModuleAccess = (itemKey: string): boolean => {
    if (isSuperUser) return true;
    if (isAdmin) return true;
    if (itemKey === "dashboard" || itemKey === "settings") return true;
    if (userModules.includes(itemKey)) return true;
    return false;
  };

  const toggleAccordion = (key: string) => {
    setExpandedModule(prev => (prev === key ? null : key));
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800 text-slate-300 w-full select-none">
      {/* Header / Logo : compact sur desktop (l'en-tête global occupe déjà 64px),
          complet uniquement dans le tiroir mobile qui recouvre l'en-tête. */}
      {isMobile ? (
        <div className="flex items-center justify-between h-16 px-4 border-b border-slate-800 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-primary text-on-primary font-black flex items-center justify-center">
              E
            </div>
            <div>
              <span className="font-black text-slate-100 tracking-wider text-sm block">EVO-LOG SaaS</span>
              <span className="text-[11px] text-slate-400 font-mono block">
                {isAdmin ? (language === 'en' ? 'Full Admin Access' : 'Accès Admin Total') : `${language === 'en' ? 'Profile' : 'Profil'} : ${userRoles[0] || (language === 'en' ? 'User' : 'Utilisateur')}`}
              </span>
            </div>
          </div>

          <button onClick={onClose} className="p-2 min-w-11 min-h-11 text-slate-400 hover:text-white" aria-label={language === 'en' ? 'Close menu' : 'Fermer le menu'}>
            <X className="w-5 h-5" />
          </button>
        </div>
      ) : (
        <div className="flex items-center h-9 px-3 border-b border-slate-800 shrink-0 gap-2">
          {!isCollapsed && (
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider truncate flex-1">
              {isAdmin ? (language === 'en' ? 'Full Admin Access' : 'Accès Admin Total') : `${language === 'en' ? 'Profile' : 'Profil'} : ${userRoles[0] || (language === 'en' ? 'User' : 'Utilisateur')}`}
            </span>
          )}
          {onToggle && (
            <button
              onClick={onToggle}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors ml-auto"
              title={isCollapsed ? (language === 'en' ? 'Expand sidebar' : 'Déplier la Sidebar') : (language === 'en' ? 'Collapse sidebar' : 'Rétracter la Sidebar')}
              aria-label={isCollapsed ? (language === 'en' ? 'Expand the sidebar' : 'Déplier la barre latérale') : (language === 'en' ? 'Collapse the sidebar' : 'Rétracter la barre latérale')}
              aria-expanded={!isCollapsed}
            >
              {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
            </button>
          )}
        </div>
      )}

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {filteredNav.map((item) => {
          // Identité résolue par propriété dans le registre : le module reste
          // surligné même si la page active vit sous un préfixe legacy.
          const isActive = resolveModuleKeyForPath(pathname) === item.key;
          const isAllowed = checkModuleAccess(item.key);
          const Icon = item.icon;
          const title = localizeTitle(item, language);
          const subItems = item.subModules || [];
          const isAccordionOpen = expandedModule === item.key || (isActive && expandedModule === null);

          if (!isAllowed) {
            return (
              <div
                key={item.path}
                onClick={() => setDeniedModalItem({ label: title, key: item.key })}
                title={language === 'en' ? `Module ${title} is not included in your profile. Click for details.` : `Module ${title} non inclus dans votre profil. Cliquez pour voir les détails.`}
                className={`flex items-center gap-3 py-2.5 rounded-xl text-sm font-semibold opacity-40 bg-slate-950/40 border border-slate-800 text-slate-500 cursor-not-allowed transition-all hover:opacity-65 hover:bg-slate-950/70 ${
                  isCollapsed ? "px-2 justify-center" : "px-3"
                }`}
              >
                <Icon className="w-5 h-5 shrink-0 text-slate-400" />
                {!isCollapsed && (
                  <span className="truncate flex-1 text-slate-500 line-through decoration-slate-600">{title}</span>
                )}
                {!isCollapsed && (
                  <Lock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                )}
              </div>
            );
          }

          return (
            <div key={item.path} className="space-y-1">
              <div className="flex items-center">
                <Link
                  href={item.path}
                  title={title}
                  onClick={(e) => {
                    if (isMobile && onClose) onClose();
                    // Ne déclencher l'animation de transition (1,7 s) que pour un
                    // VRAI changement de module (propriété registre), plus pour un
                    // simple changement de préfixe legacy au sein du même module.
                    const currentKey = resolveModuleKeyForPath(pathname);
                    const targetKey = resolveModuleKeyForPath(item.path);
                    if (currentKey && targetKey && currentKey !== targetKey) {
                      e.preventDefault();
                      triggerDomainTransition(item.path, 1700);
                    }
                  }}
                  className={`flex-1 min-w-0 flex items-center gap-3 py-2.5 rounded-r-lg text-sm font-semibold transition-colors group border border-transparent ${
                    isCollapsed ? "px-2 justify-center" : "px-3"
                  } ${
                    isActive
                      ? "bg-slate-800/60 text-slate-100"
                      : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/40"
                  }`}
                  style={isActive ? { boxShadow: `inset 2px 0 0 0 ${item.color}` } : undefined}
                >
                  <Icon className={`w-5 h-5 shrink-0 ${isActive ? "text-slate-100" : "text-slate-400 group-hover:text-slate-200"}`} />
                  {!isCollapsed && (
                    <span className="truncate min-w-0 flex-1">{title}</span>
                  )}
                  {!isCollapsed && isActive && (
                    <span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} aria-hidden="true" />
                  )}
                </Link>

                {!isCollapsed && subItems.length > 0 && (
                  <button
                    type="button"
                    onClick={() => toggleAccordion(item.key)}
                    className="p-2 min-w-9 min-h-9 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/80 transition-transform"
                    title={language === 'en' ? `View the ${subItems.length} sub-modules of ${title}` : `Voir les ${subItems.length} sous-modules de ${title}`}
                    aria-label={language === 'en' ? `View the ${subItems.length} sub-modules of ${title}` : `Voir les ${subItems.length} sous-modules de ${title}`}
                    aria-expanded={isAccordionOpen}
                  >
                    <ChevronRight className={`w-4 h-4 transition-transform duration-200 ${isAccordionOpen ? "rotate-90" : ""}`} style={isAccordionOpen ? { color: item.color } : undefined} />
                  </button>
                )}
              </div>

              {/* Accordéon Sous-modules */}
              {!isCollapsed && subItems.length > 0 && isAccordionOpen && (
                <div className="pl-8 pr-2 py-1 space-y-1 border-l-2 ml-4 animate-in slide-in-from-top-1 duration-150" style={{ borderColor: `${item.color}40` }}>
                  {subItems.map((sub) => {
                    const isSubActive = pathname === sub.path;
                    const SubIcon = sub.icon;
                    return (
                      <Link
                        key={sub.path}
                        href={sub.path}
                        title={localizeSubLabel(sub.label, language)}
                        onClick={() => isMobile && onClose && onClose()}
                        className={`flex min-w-0 items-center justify-between gap-2 py-1.5 px-2.5 min-h-9 text-xs rounded-r-md transition-colors group border border-transparent ${
                          isSubActive
                            ? "bg-slate-800/50 font-semibold text-slate-100"
                            : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/40 font-medium"
                        }`}
                        style={isSubActive ? { boxShadow: `inset 2px 0 0 0 ${item.color}` } : undefined}
                      >
                        <div className="flex min-w-0 flex-1 items-center gap-2">
                          {SubIcon && <SubIcon className="w-3.5 h-3.5 shrink-0 opacity-70 group-hover:opacity-100" />}
                          <span className="truncate min-w-0">{localizeSubLabel(sub.label, language)}</span>
                        </div>
                        {isSubActive && (
                          <span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} aria-hidden="true" />
                        )}
                        {sub.badge && (
                          <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 shrink-0">
                            {sub.badge}
                          </span>
                        )}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer Toggle Button */}
      {!isMobile && onToggle && (
        <div className="p-3 border-t border-slate-800 shrink-0">
          <button
            type="button"
            onClick={onToggle}
            className="w-full flex items-center justify-center gap-2 py-2 min-h-11 px-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
            aria-label={isCollapsed ? (language === "en" ? "Expand sidebar" : "Déplier la barre latérale") : (language === "en" ? "Collapse sidebar" : "Rétracter la barre latérale")}
            aria-expanded={!isCollapsed}
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4 text-slate-400" />
            ) : (
              <>
                <ChevronLeft className="w-4 h-4 text-slate-400" />
                <span>{language === "en" ? 'Collapse sidebar' : 'Rétracter la sidebar'}</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* 🔒 Modale d'avertissement Module Non Autorisé */}
      {deniedModalItem && (
        <div
          className="fixed inset-0 z-[100] bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto"
          onMouseDown={(e) => { if (e.target === e.currentTarget) setDeniedModalItem(null); }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="denied-module-title"
            className="bg-slate-900 border border-amber-500/40 rounded-3xl p-6 max-w-md w-full my-8 shadow-2xl space-y-4 animate-in zoom-in-95 duration-200 text-slate-100"
          >
            <div className="w-12 h-12 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded-2xl flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <div className="text-center space-y-2">
              <span className="text-[11px] font-black tracking-widest text-amber-400 uppercase bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20 inline-block">
                {language === "en" ? "Restricted Access" : "Accès Restreint"}
              </span>
              <h3 id="denied-module-title" className="text-lg font-black">
                {language === "en" ? "Module Not Authorized" : "Module Non Autorisé"}
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed font-medium bg-slate-950 p-3 rounded-2xl border border-slate-800">
                {language === "en" ? (
                  <>Restricted access: your profile <b className="text-amber-400">[{userRoles.join(", ") || "User"}]</b> is not allowed to open the module <b className="text-white">[{deniedModalItem.label}]</b>. Please contact the platform administrator.</>
                ) : (
                  <>Accès restreint : Votre profil <b className="text-amber-400">[{userRoles.join(", ") || "Utilisateur"}]</b> n'est pas autorisé à accéder au module <b className="text-white">[{deniedModalItem.label}]</b>. Veuillez contacter l'Admin CADC.</>
                )}
              </p>
              <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl text-left text-xs font-mono text-slate-400 space-y-1">
                <div>• {language === "en" ? "Module code" : "Code module"} : <span className="text-amber-400">{deniedModalItem.key}</span></div>
                <div>• {language === "en" ? "Your authorized modules" : "Vos modules autorisés"} : <span className="text-slate-200">{userModules.length > 0 ? userModules.join(", ") : (language === "en" ? "None" : "Aucun")}</span></div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setDeniedModalItem(null)}
              className="w-full py-3 min-h-11 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black rounded-xl text-xs hover:brightness-110 transition-all cursor-pointer shadow-lg shadow-amber-500/20"
            >
              {language === "en" ? "Got it / Close" : "Compris / Fermer"}
            </button>
          </div>
        </div>
      )}
    </div>
  );

  if (isMobile) {
    if (!isOpen) return null;
    return (
      <>
        {/* Voile opaque derriere le tiroir : le contenu reste lisible derriere
            et un tap a droite referme le menu (jusqu'ici seule la croix le pouvait). */}
        <div
          className="fixed inset-0 z-[55] bg-slate-950/80"
          onClick={() => onClose && onClose()}
          aria-hidden="true"
        />
        <div
          role="dialog"
          aria-modal="true"
          aria-label={language === "en" ? "Modules menu" : "Menu des modules"}
          className="fixed inset-y-0 left-0 z-[60] w-72 max-w-[86vw] shadow-2xl"
        >
          {sidebarContent}
        </div>
      </>
    );
  }

  return sidebarContent;
}

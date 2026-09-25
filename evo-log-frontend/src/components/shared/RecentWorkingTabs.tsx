'use client';

import React, { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useI18n } from '@/hooks/useI18n';

interface WorkingTab {
  path: string;
  label: string;
  icon: string;
  timestamp: number;
}

const STORAGE_KEY = 'evolog_working_tabs';
const MAX_TABS = 6;

const PATH_LABEL_MAP: Record<string, { label: string; icon: string }> = {
  '/dashboard/global': { label: 'Synthèse Exécutive', icon: 'dashboard' },
  '/dashboard/process-flow': { label: 'Pipeline Navire-Client', icon: 'schema' },
  '/portail-collaborateur': { label: 'Hub Collaborateurs', icon: 'hub' },
  '/portail-chauffeur': { label: 'Tournée Chauffeur', icon: 'local_shipping' },
  '/portail-frais': { label: 'Notes de Frais', icon: 'receipt_long' },
  '/portail-magasinier': { label: 'Magasin & Picking', icon: 'warehouse' },
  '/portail-technicien': { label: 'Atelier GMAO', icon: 'build' },
  '/portail-declarant': { label: 'Douane & DUM', icon: 'gavel' },
  '/portail-qhse': { label: 'Signalement QHSE', icon: 'health_and_safety' },
  '/portail-commercial': { label: 'Cotations Fret', icon: 'point_of_sale' },
  '/portail-employe': { label: 'Espace Salarié', icon: 'badge' },
  '/comptabilite-ohada/general-ledger': { label: 'Grand Livre', icon: 'menu_book' },
  '/comptabilite-ohada/journal': { label: 'Journal Écritures', icon: 'edit_note' },
  '/comptabilite-ohada/chart-accounts': { label: 'Plan SYSCOHADA', icon: 'account_tree' },
  '/comptabilite-ohada/tax-package-cemac': { label: 'Liasse Fiscale', icon: 'receipt' },
  '/finance-ohada/treasury': { label: 'Trésorerie & Banque', icon: 'account_balance' },
  '/finance-ohada/collections': { label: 'Recouvrement & DSO', icon: 'payments' },
  '/finance-ohada/suppliers': { label: 'Dettes Fournisseurs', icon: 'credit_card' },
  '/transport': { label: 'Tour de Contrôle', icon: 'radar' },
  '/transit-douane': { label: 'Transit & CAMCIS', icon: 'shield' },
  '/acconage': { label: 'Acconage Quai TOS', icon: 'directions_boat' },
  '/magasin': { label: 'Stock WMS MAD', icon: 'inventory_2' },
  '/maintenance': { label: 'Maintenance Parc', icon: 'construction' },
};

function getTabInfo(path: string): { label: string; icon: string } {
  if (PATH_LABEL_MAP[path]) return PATH_LABEL_MAP[path];

  // Try matching root segment
  for (const [key, val] of Object.entries(PATH_LABEL_MAP)) {
    if (path.startsWith(key)) return val;
  }

  // Fallback: format path segment
  const segment = path.split('/').filter(Boolean).pop() || 'Dossier';
  const label = segment
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
  return { label, icon: 'folder' };
}

export function RecentWorkingTabs() {
  const pathname = usePathname();
  const router = useRouter();
  const t = useI18n();
  const [tabs, setTabs] = useState<WorkingTab[]>([]);

  // Load from sessionStorage
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        setTabs(JSON.parse(stored));
      }
    } catch {
      // Ignore
    }
  }, []);

  // Update tabs on path change
  useEffect(() => {
    if (!pathname || pathname === '/' || pathname.startsWith('/login') || pathname.startsWith('/logout')) {
      return;
    }

    setTabs((prev) => {
      const { label, icon } = getTabInfo(pathname);
      const filtered = prev.filter((t) => t.path !== pathname);
      const updated: WorkingTab[] = [
        { path: pathname, label, icon, timestamp: Date.now() },
        ...filtered,
      ].slice(0, MAX_TABS);

      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch {
        // Ignore
      }
      return updated;
    });
  }, [pathname]);

  const handleClose = (e: React.MouseEvent, pathToRemove: string) => {
    e.stopPropagation();
    setTabs((prev) => {
      const updated = prev.filter((t) => t.path !== pathToRemove);
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch {
        // Ignore
      }
      // If closing active tab, switch to first remaining tab or dashboard
      if (pathname === pathToRemove) {
        const nextTab = updated[0];
        if (nextTab) {
          router.push(nextTab.path);
        }
      }
      return updated;
    });
  };

  if (tabs.length <= 1) {
    return null;
  }

  return (
    <nav
      aria-label={t.shell.recentTabsAria}
      className="hidden md:flex items-center gap-1.5 px-4 py-1.5 bg-surface-container-low border-b border-outline overflow-x-auto text-[12px] select-none scrollbar-none"
    >
      <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant/70 shrink-0 mr-1 flex items-center gap-1">
        <span className="material-symbols-outlined text-[13px]">tab</span>
        {t.shell.recentTabs}
      </span>

      <div className="flex items-center gap-1">
        {tabs.map((tab) => {
          const isActive = pathname === tab.path;
          return (
            <div
              key={tab.path}
              onClick={() => router.push(tab.path)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter') router.push(tab.path); }}
              className={`
                group flex items-center gap-1.5 px-2.5 py-1 rounded-lg transition-all duration-150 cursor-pointer
                ${
                  isActive
                    ? 'bg-surface border border-outline font-semibold text-primary shadow-xs'
                    : 'bg-transparent text-on-surface-variant hover:bg-surface/60 hover:text-on-surface'
                }
              `}
              title={tab.path}
            >
              <span className={`material-symbols-outlined text-[14px] ${isActive ? 'text-primary' : 'text-on-surface-variant'}`}>
                {tab.icon}
              </span>
              <span className="max-w-[130px] truncate">{tab.label}</span>
              <button
                type="button"
                onClick={(e) => handleClose(e, tab.path)}
                className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-surface-container hover:text-error transition-all"
                title={t.shell.closeTab}
                aria-label={`${t.shell.closeTab}`}
              >
                <span className="material-symbols-outlined text-[12px] block">close</span>
              </button>
            </div>
          );
        })}
      </div>
    </nav>
  );
}

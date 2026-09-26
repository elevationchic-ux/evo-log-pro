'use client';

import React, { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useI18n } from '@/hooks/useI18n';
import { useSettings } from '@/components/layout/SettingsProvider';

interface WorkingTab {
  path: string;
  label: string;
  icon: string;
  timestamp: number;
}

const STORAGE_KEY = 'evolog_working_tabs';
const MAX_TABS = 6;

type TabLabel = { fr: string; en: string; icon: string };

// Libellés bilingues : l'onglet est résolu à l'affichage selon la langue active,
// donc un onglet déjà enregistré bascule aussi tôt que la langue change.
const PATH_LABEL_MAP: Record<string, TabLabel> = {
  '/dashboard/global': { fr: 'Synthèse Exécutive', en: 'Executive Overview', icon: 'dashboard' },
  '/dashboard/process-flow': { fr: 'Pipeline Navire-Client', en: 'Vessel-to-Client Pipeline', icon: 'schema' },
  '/portail-collaborateur': { fr: 'Hub Collaborateurs', en: 'Staff Hub', icon: 'hub' },
  '/portail-chauffeur': { fr: 'Tournée Chauffeur', en: 'Driver Round', icon: 'local_shipping' },
  '/portail-frais': { fr: 'Notes de Frais', en: 'Expense Reports', icon: 'receipt_long' },
  '/portail-magasinier': { fr: 'Magasin & Picking', en: 'Warehouse & Picking', icon: 'warehouse' },
  '/portail-technicien': { fr: 'Atelier GMAO', en: 'Maintenance Workshop', icon: 'build' },
  '/portail-declarant': { fr: 'Douane & DUM', en: 'Customs & DUM', icon: 'gavel' },
  '/portail-qhse': { fr: 'Signalement QHSE', en: 'QHSE Reporting', icon: 'health_and_safety' },
  '/portail-commercial': { fr: 'Cotations Fret', en: 'Freight Quotations', icon: 'point_of_sale' },
  '/portail-employe': { fr: 'Espace Salarié', en: 'Employee Space', icon: 'badge' },
  '/comptabilite-ohada/general-ledger': { fr: 'Grand Livre', en: 'General Ledger', icon: 'menu_book' },
  '/comptabilite-ohada/journal': { fr: 'Journal Écritures', en: 'Journal Entries', icon: 'edit_note' },
  '/comptabilite-ohada/chart-accounts': { fr: 'Plan SYSCOHADA', en: 'SYSCOHADA Chart', icon: 'account_tree' },
  '/comptabilite-ohada/tax-package-cemac': { fr: 'Liasse Fiscale', en: 'Tax Package', icon: 'receipt' },
  '/finance-ohada/treasury': { fr: 'Trésorerie & Banque', en: 'Treasury & Banking', icon: 'account_balance' },
  '/finance-ohada/collections': { fr: 'Recouvrement & DSO', en: 'Collections & DSO', icon: 'payments' },
  '/finance-ohada/suppliers': { fr: 'Dettes Fournisseurs', en: 'Accounts Payable', icon: 'credit_card' },
  '/transport': { fr: 'Tour de Contrôle', en: 'Control Tower', icon: 'radar' },
  '/transit-douane': { fr: 'Transit & CAMCIS', en: 'Transit & CAMCIS', icon: 'shield' },
  '/acconage': { fr: 'Acconage Quai TOS', en: 'Stevedoring TOS', icon: 'directions_boat' },
  '/magasin': { fr: 'Stock WMS MAD', en: 'WMS Stock MAD', icon: 'inventory_2' },
  '/maintenance': { fr: 'Maintenance Parc', en: 'Fleet Maintenance', icon: 'construction' },
};

function getTabInfo(path: string, lang: 'fr' | 'en'): { label: string; icon: string } {
  const hit = PATH_LABEL_MAP[path]
    || Object.entries(PATH_LABEL_MAP).find(([key]) => path.startsWith(key))?.[1];
  if (hit) return { label: hit[lang], icon: hit.icon };

  // Repli : derniere segment du chemin, mis en casse lisible.
  const segment = path.split('/').filter(Boolean).pop() || (lang === 'en' ? 'Page' : 'Dossier');
  const label = segment
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
  return { label, icon: 'folder' };
}

export function RecentWorkingTabs() {
  const pathname = usePathname();
  const router = useRouter();
  const t = useI18n();
  const { language } = useSettings();
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
      const { label, icon } = getTabInfo(pathname, language);
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
          // Label rezolu au rendu (et pas lu du storage) : il suit la langue active.
          const display = getTabInfo(tab.path, language).label;
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

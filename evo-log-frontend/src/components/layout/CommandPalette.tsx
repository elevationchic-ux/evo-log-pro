"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, X } from "lucide-react";
import { NAVIGATION_REGISTRY } from "@/config/navigationRegistry";
import { localizeTitle, localizeSubLabel } from "@/config/navI18n";
import { useSettings } from "@/components/layout/SettingsProvider";
import { useI18n } from "@/hooks/useI18n";

interface NavEntry {
  key: string;
  label: string;
  path: string;
  icon: any;
  color: string;
  module: string;
  isModuleRoot: boolean;
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const router = useRouter();
  const { language } = useSettings();
  const t = useI18n();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setOpen(false);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  // Liste plate de TOUS les modules et sous-modules (source : registry).
  const allItems = useMemo<NavEntry[]>(() => {
    const items: NavEntry[] = [];
    for (const m of Object.values(NAVIGATION_REGISTRY)) {
      const title = localizeTitle(m, language);
      items.push({
        key: `module:${m.key}`,
        label: title,
        path: m.path,
        icon: m.icon,
        color: m.color,
        module: title,
        isModuleRoot: true,
      });
      for (const s of m.subModules) {
        items.push({
          key: `sub:${m.key}:${s.path}`,
          label: localizeSubLabel(s.label, language),
          path: s.path,
          icon: s.icon || m.icon,
          color: m.color,
          module: title,
          isModuleRoot: false,
        });
      }
    }
    return items;
  }, [language]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return allItems.slice(0, 40);
    return allItems.filter(
      (i) =>
        i.label.toLowerCase().includes(q) ||
        i.module.toLowerCase().includes(q) ||
        i.path.toLowerCase().includes(q)
    );
  }, [allItems, query]);

  if (!open) return null;

  const handleSelect = (path: string) => {
    setOpen(false);
    setQuery("");
    router.push(path);
  };

  return (
    <div className="fixed inset-0 z-[95] bg-black/70 backdrop-blur-sm flex items-start justify-center pt-24 p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden text-slate-100">
        <div className="flex items-center border-b border-slate-800 px-4 py-3">
          <Search className="w-5 h-5 text-slate-400 mr-3 shrink-0" />
          <input
            autoFocus
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t.shell.palettePlaceholder}
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none"
          />
          <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-200 p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-2 space-y-1">
          <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
            {t.shell.quickNav} · {query ? `${filtered.length} ${t.common.results}` : `${allItems.length} ${t.shell.modules}`}
          </div>

          {filtered.length === 0 ? (
            <div className="py-8 text-center text-sm text-slate-500">
              {t.common.noResultsFor} "{query}"
            </div>
          ) : (
            filtered.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.key}
                  onClick={() => handleSelect(item.path)}
                  className="w-full flex items-center px-3 py-2.5 rounded-xl text-sm text-slate-200 hover:bg-slate-800 transition-colors text-left group"
                >
                  <Icon className="w-4 h-4 mr-3 shrink-0" style={{ color: item.color }} />
                  <span className={`flex-1 truncate ${item.isModuleRoot ? "font-bold text-slate-100" : "font-medium"}`}>
                    {item.label}
                  </span>
                  {!item.isModuleRoot && (
                    <span className="ml-2 hidden sm:inline shrink-0 text-[10px] text-slate-500 truncate max-w-[10rem]">
                      {item.module}
                    </span>
                  )}
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

export default CommandPalette;

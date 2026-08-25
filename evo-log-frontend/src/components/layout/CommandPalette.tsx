'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { getFilteredNavigationForUser, ModuleNavConfig } from '@/config/navigationRegistry';
import { useSession } from 'next-auth/react';
import { Search, ArrowRight, X, Command, ChevronRight } from 'lucide-react';

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const pathname = usePathname();
  const { data: session } = useSession();
  const navItems: ModuleNavConfig[] = getFilteredNavigationForUser(session?.user as any);

  // Collect all navigable items (modules + sub-modules)
  const allItems = navItems.flatMap(item => {
    const moduleItem = {
      id: item.path,
      label: item.title,
      path: item.path,
      icon: item.icon,
      color: item.color,
      type: 'module' as const,
      subItems: [],
    };
    const subItems = (item.subModules || []).map(sub => ({
      id: sub.path,
      label: sub.label,
      path: sub.path,
      icon: sub.icon,
      color: item.color,
      type: 'sub' as const,
      parentTitle: item.title,
    }));
    return [moduleItem, ...subItems];
  });

  // Filter items based on query
  const filteredItems = query.length > 0
    ? allItems.filter(item => 
        item.label.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 8)
    : allItems.slice(0, 6);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
        setQuery('');
      }
      
      if (isOpen) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          setSelectedIndex(prev => Math.min(prev + 1, filteredItems.length - 1));
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setSelectedIndex(prev => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter' && filteredItems[selectedIndex]) {
          e.preventDefault();
          router.push(filteredItems[selectedIndex].path);
          setIsOpen(false);
          setQuery('');
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filteredItems, selectedIndex, router]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] pointer-events-none"
      >
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm pointer-events-auto"
          onClick={() => { setIsOpen(false); setQuery(''); }}
        />

        {/* Palette */}
        <motion.div
          initial={{ scale: 0.95, opacity: 0, y: -20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: -20 }}
          className="relative w-full max-w-xl mx-4 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden pointer-events-auto"
        >
          {/* Header */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-slate-800">
            <Command className="w-5 h-5 text-amber-400" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Rechercher un module, une page, une action..."
              className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 outline-none text-sm"
            />
            <kbd className="px-2 py-0.5 text-[10px] font-mono text-slate-500 bg-slate-800 rounded border border-slate-700">ESC</kbd>
            <button
              onClick={() => { setIsOpen(false); setQuery(''); }}
              className="p-1 text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Results */}
          <div className="max-h-[40vh] overflow-y-auto py-2">
            {filteredItems.length === 0 ? (
              <div className="px-4 py-8 text-center text-slate-500 text-sm">
                Aucun résultat pour "{query}"
              </div>
            ) : (
              filteredItems.map((item, index) => {
                const isActive = index === selectedIndex;
                const Icon = item.icon;
                const isCurrentPage = pathname === item.path;
                return (
                  <div key={item.id}>
                    {item.type === 'module' && index > 0 && query.length > 0 && (
                      <div className="px-4 py-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                        Modules
                      </div>
                    )}
                    <Link
                      href={item.path}
                      onClick={() => { setIsOpen(false); setQuery(''); }}
                      onMouseEnter={() => setSelectedIndex(index)}
                      className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                        isActive 
                          ? 'bg-slate-800/80' 
                          : 'hover:bg-slate-800/40'
                      }`}
                      style={isActive ? { borderLeft: `2px solid ${item.color}` } : {}}
                    >
                      {Icon && (
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                          style={{ backgroundColor: `${item.color}20` }}
                        >
                          <Icon className="w-4 h-4" style={{ color: item.color }} />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className={`truncate ${isActive ? 'text-white font-semibold' : 'text-slate-200'}`}>
                            {item.label}
                          </span>
                          {isCurrentPage && (
                            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shrink-0">
                              actuel
                            </span>
                          )}
                        </div>
                        {'parentTitle' in item && item.parentTitle && (
                          <span className="text-[10px] text-slate-500">{item.parentTitle}</span>
                        )}
                      </div>
                      {isActive && (
                        <ArrowRight className="w-4 h-4 text-slate-400 shrink-0" />
                      )}
                    </Link>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-4 py-2 border-t border-slate-800 text-[10px] text-slate-500">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-slate-800 rounded border border-slate-700">↑↓</kbd> naviguer
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-slate-800 rounded border border-slate-700">↵</kbd> ouvrir
              </span>
            </div>
            <span>{filteredItems.length} résultats</span>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

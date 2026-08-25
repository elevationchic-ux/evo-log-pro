'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { getFilteredNavigationForUser, ModuleNavConfig } from '@/config/navigationRegistry';
import { useSession } from 'next-auth/react';
import { X } from 'lucide-react';

export default function SubModuleOrbitalBubble() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { data: session } = useSession();
  const navItems: ModuleNavConfig[] = getFilteredNavigationForUser(session?.user as any);

  // Determine current module
  const currentModuleKey = navItems.find(item => pathname.startsWith(item.path))?.key || null;
  const currentModule = navItems.find(item => item.key === currentModuleKey);
  const subItems = currentModule?.subModules || [];

  // Calculate orbital positions in a circle
  const getOrbitalPosition = (index: number, total: number) => {
    const angle = (2 * Math.PI * index) / total - Math.PI / 2; // Start from top
    const radius = 100; // Orbit radius
    return {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
    };
  };

  return (
    <>
      {/* Trigger button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center text-white shadow-lg border-2 border-white/20 ${
          isOpen ? 'rotate-45' : ''
        }`}
        style={{
          background: currentModule ? `linear-gradient(135deg, ${currentModule.color}, ${currentModule.color}cc)` : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          boxShadow: currentModule ? `0 8px 32px ${currentModule.color}40` : '0 8px 32px #6366f140',
        }}
      >
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
      </motion.button>

      {/* Orbital menu */}
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-40 flex items-center justify-center pointer-events-none">
            {/* Backdrop */}
            <div 
              className="absolute inset-0 bg-black/60 backdrop-blur-sm pointer-events-auto"
              onClick={() => setIsOpen(false)}
            />

            {/* Center hub */}
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              className="relative w-64 h-64 pointer-events-auto"
            >
              {/* Center circle with module info */}
              <div
                className="absolute inset-0 m-auto w-20 h-20 rounded-full flex flex-col items-center justify-center text-white shadow-xl border-2 border-white/30 cursor-pointer"
                style={{
                  background: currentModule ? `linear-gradient(135deg, ${currentModule.color}, ${currentModule.color}cc)` : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  boxShadow: currentModule ? `0 0 40px ${currentModule.color}50` : '0 0 40px #6366f150',
                }}
                onClick={() => setIsOpen(false)}
              >
                {currentModule?.icon && <currentModule.icon className="w-5 h-5 mb-0.5" />}
                <span className="text-[8px] font-bold">{currentModule?.title?.split('&')[0] || 'Menu'}</span>
              </div>

              {/* Orbital sub-modules */}
              {subItems.map((sub, index) => {
                const pos = getOrbitalPosition(index, subItems.length);
                const isActive = pathname === sub.path;
                return (
                  <motion.div
                    key={sub.path}
                    initial={{ scale: 0, x: 0, y: 0, opacity: 0 }}
                    animate={{ scale: 1, x: pos.x, y: pos.y, opacity: 1 }}
                    exit={{ scale: 0, x: 0, y: 0, opacity: 0 }}
                    transition={{ 
                      type: 'spring', 
                      stiffness: 300, 
                      damping: 20,
                      delay: index * 0.05,
                    }}
                    className="absolute inset-0 m-auto"
                  >
                    <Link
                      href={sub.path}
                      onClick={() => setIsOpen(false)}
                      className={`block w-14 h-14 -ml-7 -mt-7 rounded-full flex flex-col items-center justify-center text-white text-[8px] font-bold shadow-lg border-2 transition-all hover:scale-110 ${
                        isActive ? 'border-white/50' : 'border-white/20'
                      }`}
                      style={{
                        background: isActive 
                          ? `linear-gradient(135deg, ${currentModule?.color || '#6366f1'}, ${currentModule?.color || '#6366f1'}cc)`
                          : 'linear-gradient(135deg, #1e293b, #0f172a)',
                        boxShadow: isActive ? `0 0 20px ${currentModule?.color || '#6366f1'}40` : '0 4px 15px #00000040',
                      }}
                    >
                      {sub.icon && <sub.icon className="w-4 h-4 mb-0.5" />}
                      <span className="truncate max-w-[32px]">{sub.label.split(' ')[0]}</span>
                      {sub.badge && (
                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-amber-400 rounded-full text-[6px] flex items-center justify-center text-slate-900 font-black">
                          {sub.badge.charAt(0)}
                        </span>
                      )}
                    </Link>
                  </motion.div>
                );
              })}
            </motion.div>

            {/* Close button */}
            <button
              onClick={() => setIsOpen(false)}
              className="fixed top-4 right-4 pointer-events-auto p-2 text-white/70 hover:text-white bg-white/10 rounded-full backdrop-blur-sm"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}

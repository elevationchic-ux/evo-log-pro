'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { Toaster } from 'sonner';

import ModuleSidebar from '@/components/layout/ModuleSidebar';
import { ModuleHeader } from '@/components/layout/ModuleHeader';
import SubModuleOrbitalBubble from '@/components/layout/SubModuleOrbitalBubble';
import CommandPalette from '@/components/layout/CommandPalette';
import { useModuleTheme } from '@/hooks/useModuleTheme';
import KeyboardShortcutHandler from '@/components/shared/KeyboardShortcutHandler';

function AppLayoutContent({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const pathname = usePathname();
  const { currentModule } = useModuleTheme();

  const [isMobileViewport, setIsMobileViewport] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  /* Responsive breakpoint */
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 1023px)');
    const sync = (e?: MediaQueryList | MediaQueryListEvent) => {
      const mobile = e ? (e as MediaQueryListEvent).matches : mq.matches;
      setIsMobileViewport(mobile);
      if (!mobile) setIsMobileSidebarOpen(false);
    };
    sync();
    mq.addEventListener('change', sync);
    return () => mq.removeEventListener('change', sync);
  }, []);

  /* Prevent body scroll when mobile drawer open */
  useEffect(() => {
    document.body.classList.toggle('overflow-hidden', isMobileViewport && isMobileSidebarOpen);
    return () => document.body.classList.remove('overflow-hidden');
  }, [isMobileViewport, isMobileSidebarOpen]);

  /* Auth guard */
  useEffect(() => {
    if (status === 'unauthenticated' && pathname !== '/logout') {
      router.push('/login');
    }
  }, [status, router, pathname]);

  if (status === 'loading') {
    return (
      <div className="fixed inset-0 bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-500 text-slate-950 font-black flex items-center justify-center text-xl animate-pulse">E</div>
          <div className="text-slate-400 text-sm font-mono animate-pulse">Chargement EVO-LOG...</div>
        </div>
      </div>
    );
  }

  if (status === 'unauthenticated') return null;

  const sidebarWidth = isSidebarCollapsed ? '72px' : '260px';

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 overflow-x-hidden">
      <Toaster position="top-right" richColors />

      {/* Sticky Header */}
      <ModuleHeader
        currentModule={currentModule as any}
        onMenuClick={() => {
          if (isMobileViewport) {
            setIsMobileSidebarOpen(prev => !prev);
          } else {
            setIsSidebarCollapsed(prev => !prev);
          }
        }}
      />

      {/* Body: sidebar + main */}
      <div className="relative flex flex-1 min-h-[calc(100vh-64px)]">

        {/* Mobile backdrop */}
        {isMobileViewport && isMobileSidebarOpen && (
          <div
            className="fixed inset-0 z-[55] bg-black/60 backdrop-blur-sm lg:hidden"
            onClick={() => setIsMobileSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <div
          className="flex-shrink-0 transition-[width] duration-[280ms] ease-[cubic-bezier(0.4,0,0.2,1)]"
          style={isMobileViewport ? { width: 0, overflow: 'visible' } : { width: sidebarWidth }}
        >
          <div className={`${isMobileViewport ? '' : 'sticky top-16 h-[calc(100vh-64px)]'}`}>
            <ModuleSidebar
              isCollapsed={isSidebarCollapsed}
              isMobile={isMobileViewport}
              isOpen={isMobileSidebarOpen}
              onClose={() => setIsMobileSidebarOpen(false)}
              onToggle={() => setIsSidebarCollapsed(prev => !prev)}
            />
          </div>
        </div>

        {/* Main content */}
        <main className="min-w-0 flex-1 overflow-x-hidden px-3 py-4 sm:px-4 sm:py-5 lg:px-6 lg:py-6">
          <div className="mx-auto w-full max-w-7xl">
            {children}
          </div>
        </main>
      </div>

      {/* Orbital navigation bubble */}
      <SubModuleOrbitalBubble />
      
      {/* Command palette */}
      <CommandPalette />
      
      {/* Keyboard shortcuts */}
      <KeyboardShortcutHandler />
    </div>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <AppLayoutContent>{children}</AppLayoutContent>;
}

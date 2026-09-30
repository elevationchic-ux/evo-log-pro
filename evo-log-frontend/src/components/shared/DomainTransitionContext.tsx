'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import DomainLoadingExperience from './DomainLoadingExperience';

interface DomainTransitionContextType {
  isTransitioning: boolean;
  targetDomain: string;
  triggerDomainTransition: (targetPath: string, durationMs?: number) => void;
}

const DomainTransitionContext = createContext<DomainTransitionContextType>({
  isTransitioning: false,
  targetDomain: 'dashboard',
  triggerDomainTransition: () => {},
});

export function DomainTransitionProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [targetDomain, setTargetDomain] = useState('dashboard');
  const [targetUrl, setTargetUrl] = useState('');

  const triggerDomainTransition = useCallback((path: string, durationMs = 1800) => {
    // Si on est déjà sur la même page, inutile de transitionner
    const cleanSegment = path.replace(/^\/+/, '').split('/')[0] || 'dashboard';
    setTargetDomain(cleanSegment);
    setTargetUrl(path);
    setIsTransitioning(true);

    // Après l'animation, on redirige et on retire l'overlay
    setTimeout(() => {
      router.push(path);
      setTimeout(() => {
        setIsTransitioning(false);
      }, 500);
    }, durationMs);
  }, [router]);

  return (
    <DomainTransitionContext.Provider
      value={{
        isTransitioning,
        targetDomain,
        triggerDomainTransition,
      }}
    >
      {children}

      {/* Overlay de transition inter-modules plein écran */}
      {isTransitioning && (
        <div className="fixed inset-0 z-[110] animate-in fade-in duration-300">
          <DomainLoadingExperience
            targetDomain={targetDomain}
            durationMs={1600}
            fullScreen={true}
          />
        </div>
      )}
    </DomainTransitionContext.Provider>
  );
}

export function useDomainTransition() {
  return useContext(DomainTransitionContext);
}

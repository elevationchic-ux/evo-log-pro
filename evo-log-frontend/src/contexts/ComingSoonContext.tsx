'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ComingSoonModal } from '@/components/ui/ComingSoonModal';

interface ComingSoonContextType {
  showComingSoon: (featureName?: string) => void;
}

const ComingSoonContext = createContext<ComingSoonContextType | undefined>(undefined);

export function ComingSoonProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [feature, setFeature] = useState<string | undefined>();

  const showComingSoon = (featureName?: string) => {
    setFeature(featureName);
    setIsOpen(true);
  };

  return (
    <ComingSoonContext.Provider value={{ showComingSoon }}>
      {children}
      <ComingSoonModal 
        isOpen={isOpen} 
        onClose={() => setIsOpen(false)} 
        featureName={feature} 
      />
    </ComingSoonContext.Provider>
  );
}

export function useComingSoon() {
  const context = useContext(ComingSoonContext);
  if (context === undefined) {
    throw new Error('useComingSoon must be used within a ComingSoonProvider');
  }
  return context;
}

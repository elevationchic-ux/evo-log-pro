'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export type ThemePreference = 'light' | 'dark' | 'system';

interface SettingsContextType {
  theme: ThemePreference;
  setTheme: (theme: ThemePreference) => void;
  toggleTheme: () => void;
  language: 'fr' | 'en';
  setLanguage: (lang: 'fr' | 'en') => void;
  // Sound controls  used by ModuleHeader for WebSocket alert sounds
  soundEnabled: boolean;
  toggleSound: () => void;
  showSoundBadge: boolean;
  triggerSoundBadge: () => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<ThemePreference>('light');
  const [language, setLanguage] = useState<'fr' | 'en'>('fr');
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showSoundBadge, setShowSoundBadge] = useState(false);

  const toggleTheme = useCallback(() => {
    setTheme(t => t === 'light' ? 'dark' : t === 'dark' ? 'system' : 'light');
  }, []);

  const toggleSound = useCallback(() => {
    setSoundEnabled(s => !s);
  }, []);

  /** Flash the sound badge indicator for 2 s when a critical alert fires */
  const triggerSoundBadge = useCallback(() => {
    setShowSoundBadge(true);
    setTimeout(() => setShowSoundBadge(false), 2000);
  }, []);

  return (
    <SettingsContext.Provider
      value={{
        theme,
        setTheme,
        toggleTheme,
        language,
        setLanguage,
        soundEnabled,
        toggleSound,
        showSoundBadge,
        triggerSoundBadge,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettings must be used within a SettingsProvider');
  return ctx;
}

'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';

const SOUND_SETTINGS_KEY = 'evolog_erp_sound_enabled';
const THEME_SETTINGS_KEY = 'evolog_erp_theme';
const LANG_SETTINGS_KEY = 'evolog_erp_language';

export type ThemePreference = 'light' | 'dark' | 'system';
export type LanguagePreference = 'fr' | 'en';

interface SettingsContextType {
  soundEnabled: boolean;
  toggleSound: () => void;
  showSoundBadge: boolean;
  triggerSoundBadge: () => void;
  theme: ThemePreference;
  setTheme: (theme: ThemePreference) => void;
  language: LanguagePreference;
  setLanguage: (lang: LanguagePreference) => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showSoundBadge, setShowSoundBadge] = useState(false);
  const [theme, setThemeState] = useState<ThemePreference>('system');
  const [language, setLanguageState] = useState<LanguagePreference>('fr');
  const soundBadgeTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Load all settings from localStorage on mount
    const savedSound = localStorage.getItem(SOUND_SETTINGS_KEY);
    if (savedSound !== null) setSoundEnabled(savedSound === 'true');

    const savedTheme = localStorage.getItem(THEME_SETTINGS_KEY) as ThemePreference;
    if (savedTheme) setThemeState(savedTheme);

    const savedLang = localStorage.getItem(LANG_SETTINGS_KEY) as LanguagePreference;
    if (savedLang) setLanguageState(savedLang);
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  const toggleSound = useCallback(() => {
    const newValue = !soundEnabled;
    setSoundEnabled(newValue);
    localStorage.setItem(SOUND_SETTINGS_KEY, String(newValue));
  }, [soundEnabled]);

  const setTheme = useCallback((newTheme: ThemePreference) => {
    setThemeState(newTheme);
    localStorage.setItem(THEME_SETTINGS_KEY, newTheme);
  }, []);

  const setLanguage = useCallback((newLang: LanguagePreference) => {
    setLanguageState(newLang);
    localStorage.setItem(LANG_SETTINGS_KEY, newLang);
  }, []);

  const triggerSoundBadge = useCallback(() => {
    setShowSoundBadge(true);
    if (soundBadgeTimeoutRef.current) {
      clearTimeout(soundBadgeTimeoutRef.current);
    }
    soundBadgeTimeoutRef.current = setTimeout(() => {
      setShowSoundBadge(false);
    }, 2000); // Show badge for 2 seconds
  }, []);

  const value = {
    soundEnabled,
    toggleSound,
    showSoundBadge,
    triggerSoundBadge,
    theme,
    setTheme,
    language,
    setLanguage,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
}

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
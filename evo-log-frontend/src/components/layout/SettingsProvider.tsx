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
  const [theme, setThemeState] = useState<ThemePreference>('dark');
  const [language, setLanguageState] = useState<LanguagePreference>('fr');
  const soundBadgeTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  // Refs pour le son de clic : lues dans le gestionnaire global sans re-binding.
  const soundEnabledRef = useRef(true);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const lastClickAtRef = useRef(0);

  useEffect(() => {
    // Load all settings from localStorage on mount
    const savedSound = localStorage.getItem(SOUND_SETTINGS_KEY);
    if (savedSound !== null) setSoundEnabled(savedSound === 'true');

    const savedTheme = localStorage.getItem(THEME_SETTINGS_KEY) as ThemePreference;
    if (savedTheme) setThemeState(savedTheme); // sombre par défaut, clair/système si mémorisé

    const savedLang = localStorage.getItem(LANG_SETTINGS_KEY) as LanguagePreference;
    if (savedLang) setLanguageState(savedLang);
  }, []);

  useEffect(() => {
    // Applique le thème choisi sur <html> (sombre par défaut, clair/système
    // en option). La classe effective pilote les tokens + filets CSS .dark/.light.
    const root = window.document.documentElement;
    const apply = (pref: ThemePreference) => {
      const isLight =
        pref === 'light' ||
        (pref === 'system' &&
          typeof window.matchMedia === 'function' &&
          window.matchMedia('(prefers-color-scheme: light)').matches);
      root.classList.toggle('light', isLight);
      root.classList.toggle('dark', !isLight);
      root.style.colorScheme = isLight ? 'light' : 'dark';
    };
    apply(theme);
    if (theme === 'system' && typeof window.matchMedia === 'function') {
      const mq = window.matchMedia('(prefers-color-scheme: light)');
      const onChange = () => apply('system');
      mq.addEventListener?.('change', onChange);
      return () => mq.removeEventListener?.('change', onChange);
    }
  }, [theme]);

  useEffect(() => {
    // La langue choisie doit être visible du DOM, pas seulement du state React :
    // lecteurs d'écran, hyphénation, traductions navigateur et `:lang()` en CSS
    // restent calés sur le <html lang="fr"> statique du layout sans cette ligne.
    window.document.documentElement.lang = language;
  }, [language]);

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

  // ── Son de clic sobre (Web Audio, aucun asset, respecting toggle) ──────────
  // feedback discret et « matière » sur les contrôles interactifs, pensé pour un
  // outil métier grand public : très court (~60 ms), très bas niveau (~ -26 dB),
  // filtré pour rester feutré. Aucun son si l'utilisateur coupe les notifications.
  useEffect(() => {
    soundEnabledRef.current = soundEnabled;
  }, [soundEnabled]);

  const ensureAudioCtx = useCallback((): AudioContext | null => {
    if (typeof window === 'undefined') return null;
    const AC = window.AudioContext || (window as any).webkitAudioContext;
    if (!AC) return null;
    if (!audioCtxRef.current) audioCtxRef.current = new AC();
    if (audioCtxRef.current.state === 'suspended') {
      // Le premier clic EST le geste utilisateur requis par la politique autoplay.
      void audioCtxRef.current.resume();
    }
    return audioCtxRef.current;
  }, []);

  const playClick = useCallback(() => {
    if (!soundEnabledRef.current) return;
    const now = Date.now();
    if (now - lastClickAtRef.current < 45) return; // anti-bond (un seul clic / 45 ms)
    lastClickAtRef.current = now;
    const ctx = ensureAudioCtx();
    if (!ctx) return;
    const t = ctx.currentTime;
    const osc = ctx.createOscillator();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(880, t);
    osc.frequency.exponentialRampToValueAtTime(660, t + 0.05);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(0.05, t + 0.004);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.06);
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.value = 2200;
    osc.connect(lp);
    lp.connect(gain);
    gain.connect(ctx.destination);
    osc.start(t);
    osc.stop(t + 0.07);
  }, [ensureAudioCtx]);

  useEffect(() => {
    // Uniquement les contrôles (pas les simples liens) pour rester sobre.
    const SEL =
      'button, [role="button"], [role="tab"], summary, input[type="submit"], input[type="checkbox"], input[type="radio"], select, [data-click-sound]';
    const onClick = (e: MouseEvent) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      if (!target.closest(SEL)) return;
      playClick();
    };
    document.addEventListener('click', onClick, true);
    return () => document.removeEventListener('click', onClick, true);
  }, [playClick]);

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
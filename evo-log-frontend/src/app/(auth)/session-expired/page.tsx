'use client'

import Link from 'next/link'
import { useI18n } from '@/hooks/useI18n'
import { useSettings, ThemePreference } from '@/components/layout/SettingsProvider'

export default function SessionExpiredPage() {
  const t = useI18n()
  const { theme: uiTheme, setTheme, language, setLanguage } = useSettings()

  const cycleTheme = () => {
    const themes: ThemePreference[] = ['light', 'dark', 'system']
    setTheme(themes[(themes.indexOf(uiTheme) + 1) % themes.length])
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 relative">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-blue-950" />
      <div className="absolute inset-0 opacity-5" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,.1) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.1) 1px,transparent 1px)', backgroundSize: '48px 48px' }} />

      <div className="absolute top-4 right-4 z-20 flex items-center gap-2">
        <button onClick={() => setLanguage(language === 'fr' ? 'en' : 'fr')} className="flex items-center gap-1 rounded border border-white/20 bg-white/10 px-2 py-1 text-[11px] font-bold uppercase text-white/70 backdrop-blur transition hover:bg-white/20">
          <span className="material-symbols-outlined text-[14px]">language</span>{language}
        </button>
        <button onClick={cycleTheme} className="rounded border border-white/20 bg-white/10 p-1.5 text-white/70 backdrop-blur transition hover:bg-white/20">
          <span className="material-symbols-outlined text-[16px]">{uiTheme === 'light' ? 'light_mode' : uiTheme === 'dark' ? 'dark_mode' : 'settings_brightness'}</span>
        </button>
      </div>

      <div className="relative z-10 w-full max-w-[420px] mx-4">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-600 rounded-2xl shadow-lg shadow-blue-500/40 mb-4">
            <span className="material-symbols-outlined text-white text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>precision_manufacturing</span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">EVO-LOG SaaS</h1>
          <p className="text-xs font-bold text-blue-300 uppercase tracking-[0.2em] mt-1">Operational Control Systems</p>
        </div>

        <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 dark:border-white/10 p-7 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <span className="material-symbols-outlined text-amber-600 dark:text-amber-400 text-[40px]" style={{ fontVariationSettings: "'FILL' 1" }}>timer_off</span>
            </div>
          </div>
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 mb-2">{t.auth.sessionExpiredTitle}</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">{t.auth.sessionExpiredBody}</p>
          <div className="flex items-start gap-2 p-3 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg mb-6 text-left">
            <span className="material-symbols-outlined text-blue-500 text-[18px] shrink-0 mt-0.5">info</span>
            <p className="text-xs text-slate-500 dark:text-slate-400">{t.auth.sessionExpiredInfo}</p>
          </div>
          <Link href="/login" className="flex items-center justify-center gap-2 w-full h-12 rounded-xl bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition">
            <span className="material-symbols-outlined text-[20px]">login</span>{t.auth.reconnectCta}
          </Link>
          <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-700 flex items-center justify-center gap-2 text-slate-400">
            <span className="material-symbols-outlined text-[16px]">verified_user</span>
            <p className="text-xs">{t.auth.mfaSecuredLabel}</p>
          </div>
        </div>
        <p className="text-center text-xs text-white/30 mt-4">v4.8.2-stable · © 2026 EVO-LOG LOGISTICS GROUP</p>
      </div>
    </div>
  )
}

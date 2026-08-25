'use client'

import { useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api-client'
import { useI18n } from '@/hooks/useI18n'
import { useSettings, ThemePreference } from '@/components/layout/SettingsProvider'

export default function ForgotPasswordPage() {
  const t = useI18n()
  const { theme: uiTheme, setTheme, language, setLanguage } = useSettings()
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [submittedEmail, setSubmittedEmail] = useState('')
  const [emailInput, setEmailInput] = useState('')
  const [emailError, setEmailError] = useState('')

  const cycleTheme = () => {
    const themes: ThemePreference[] = ['light', 'dark', 'system']
    setTheme(themes[(themes.indexOf(uiTheme) + 1) % themes.length])
  }

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!emailInput.trim()) {
      setEmailError('L\'email est requis')
      return
    }
    if (!validateEmail(emailInput)) {
      setEmailError('Email invalide')
      return
    }
    setEmailError('')
    setIsLoading(true)
    try { await api.post('/api/auth/forgot-password', { email: emailInput }) } catch { }
    finally { setSubmittedEmail(emailInput); setIsSuccess(true); setIsLoading(false) }
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

        <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 dark:border-white/10 p-7">
          {isSuccess ? (
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <span className="material-symbols-outlined text-green-600 dark:text-green-400 text-[40px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                </div>
              </div>
              <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 mb-1">{t.auth.forgotSuccessTitle}</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">{t.auth.forgotSuccessBody}</p>
              <p className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-4">{submittedEmail}</p>
              <p className="text-xs text-slate-400 dark:text-slate-500 mb-6">{t.auth.forgotSpamNote}</p>
              <Link href="/login" className="flex items-center justify-center gap-2 w-full h-11 rounded-xl bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 transition">
                <span className="material-symbols-outlined text-[18px]">arrow_back</span>{t.auth.backToLogin}
              </Link>
            </div>
          ) : (
            <>
              <div className="mb-5">
                <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">{t.auth.forgotTitle}</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{t.auth.forgotSubtitle}</p>
              </div>
              <form onSubmit={onSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1.5">{t.auth.emailInstitutionalLabel}</label>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-[18px]">alternate_email</span>
                    <input value={emailInput} onChange={(e) => { setEmailInput(e.target.value); if (emailError) setEmailError('') }} type="email" placeholder="user@EVO-LOG.com" disabled={isLoading}
                      className="w-full h-11 pl-9 pr-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all" />
                  </div>
                  {emailError && <p className="text-red-500 text-xs mt-1">{emailError}</p>}
                </div>
                <button type="submit" disabled={isLoading} className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-blue-500/30 transition-all disabled:opacity-70">
                  {isLoading ? <><span className="material-symbols-outlined animate-spin text-[20px]">sync</span><span>{t.auth.forgotSending}</span></> : <><span>{t.auth.forgotCta}</span><span className="material-symbols-outlined text-[20px]">send</span></>}
                </button>
                <div className="text-center pt-2 border-t border-slate-100 dark:border-slate-700">
                  <Link href="/login" className="text-sm text-blue-500 hover:underline inline-flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">arrow_back</span>{t.auth.backToLogin}
                  </Link>
                </div>
              </form>
            </>
          )}
        </div>
        <p className="text-center text-xs text-white/30 mt-4">v4.8.2-stable · © 2026 EVO-LOG LOGISTICS GROUP</p>
      </div>
    </div>
  )
}

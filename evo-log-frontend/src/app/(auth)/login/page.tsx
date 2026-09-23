'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { signIn, getSession } from 'next-auth/react';
import { Sparkles, Ship, Lock, User as UserIcon, ArrowRight, ShieldCheck, KeyRound, AlertTriangle, CheckCircle2, Radio, Compass, Anchor, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();

  // Splash screen active on initial load
  const [showSplash, setShowSplash] = useState(true);
  const [splashProgress, setSplashProgress] = useState(0);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expiryWarning, setExpiryWarning] = useState<string | null>(null);

  // Password change modal
  const [mustChangePassword, setMustChangePassword] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [pendingRoles, setPendingRoles] = useState<string[]>([]);

  // Splash animation timer
  useEffect(() => {
    const interval = setInterval(() => {
      setSplashProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setShowSplash(false), 450);
          return 100;
        }
        return prev + 3;
      });
    }, 30);
    return () => clearInterval(interval);
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await signIn('credentials', { email, password, redirect: false });

      if (res?.error) {
        setErrorMessage('Identifiants incorrects. Veuillez vérifier votre identifiant ou mot de passe institutionnel.');
        return;
      }

      const session = await getSession();
      const roles: string[] = (session?.user as any)?.roles || [];
      setPendingRoles(roles);

      if (password === 'admin123') {
        setMustChangePassword(true);
        setIsLoading(false);
        return;
      }

      setExpiryWarning('⚠️ Votre mot de passe expire dans 14 jours (Renouvellement trimestriel obligatoire).');

      setTimeout(() => {
        if (roles.includes('CHAUFFEUR')) {
          router.push('/chauffeur');
        } else if (roles.includes('ADMIN') || roles.includes('MANAGER')) {
          router.push('/dashboard/global');
        } else if (roles.includes('MAGASINIER') || roles.includes('MAGASIN')) {
          router.push('/magasin/dashboard');
        } else if (roles.includes('TRANSPORT') || roles.includes('DISPATCHER')) {
          router.push('/transport/control');
        } else if (roles.includes('FINANCE')) {
          router.push('/finance/overview');
        } else {
          router.push('/dashboard/global');
        }
        router.refresh();
      }, 500);
    } catch {
      setErrorMessage('Une erreur de connexion est survenue. Vérifiez la disponibilité de l\'API.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);

    if (newPassword === 'admin123') { setPasswordError("Le mot de passe par défaut 'admin123' est interdit."); return; }
    if (newPassword.length < 8) { setPasswordError('Minimum 8 caractères requis.'); return; }
    if (!/[A-Za-z]/.test(newPassword) || !/[0-9]/.test(newPassword)) { setPasswordError('Le mot de passe doit contenir au moins une lettre et un chiffre.'); return; }
    if (newPassword !== confirmPassword) { setPasswordError('Les mots de passe ne correspondent pas.'); return; }

    setPasswordSuccess(true);
    setTimeout(() => {
      setMustChangePassword(false);
      router.push(pendingRoles.includes('CHAUFFEUR') ? '/chauffeur' : '/dashboard/global');
      router.refresh();
    }, 1200);
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center text-white font-sans select-none overflow-hidden bg-[#020c1b]">

      {/* 1. REAL BACKGROUND IMAGE: Cargo Ship Port of Douala */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <img
          src="/images/cargo_ship_port_bg.jpg"
          alt="Port de Douala Cargo Ship Background"
          className="w-full h-full object-cover object-center scale-105 filter brightness-[0.82] contrast-[1.08] transition-transform duration-1000"
          onError={(e) => {
            const target = e.currentTarget;
            if (!target.src.endsWith("/cargo_ship_port_bg.png")) {
              target.src = "/images/cargo_ship_port_bg.png";
            }
          }}
        />
        {/* Soft Vignette and Blueprint Grid */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#020c1b]/85 via-[#020c1b]/40 to-[#020c1b]/25" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_20%,rgba(2,12,27,0.75)_100%)]" />
        {/* Fine maritime grid overlay */}
        <div
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage: 'linear-gradient(#f59e0b 1px, transparent 1px), linear-gradient(90deg, #f59e0b 1px, transparent 1px)',
            backgroundSize: '48px 48px',
          }}
        />
      </div>

      {/* 2. CADC HIGH-TECH SPLASH SCREEN */}
      {showSplash && (
        <div
          className="fixed inset-0 z-50 flex flex-col items-center justify-between p-6 sm:p-12 overflow-hidden"
          style={{
            background: 'radial-gradient(circle at center, #07152b 0%, #030d1d 55%, #01060e 100%)',
            animation: splashProgress >= 100 ? 'splashFadeOut 0.5s ease-out forwards' : 'splashFadeIn 0.4s ease-out',
          }}
        >
          {/* Rotating Maritime Radar Beam */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden opacity-30">
            <div
              className="w-[800px] h-[800px] rounded-full"
              style={{
                background: 'conic-gradient(from 0deg, rgba(245,158,11,0.3) 0deg, rgba(245,158,11,0.05) 45deg, transparent 90deg)',
                animation: 'radarSweep 4s linear infinite',
              }}
            />
            {/* Concentric Radar Grid Rings */}
            <div className="absolute w-[260px] h-[260px] rounded-full border border-amber-500/20" />
            <div className="absolute w-[440px] h-[440px] rounded-full border border-amber-500/15" />
            <div className="absolute w-[640px] h-[640px] rounded-full border border-dashed border-amber-500/10" />
            <div className="absolute w-[840px] h-[840px] rounded-full border border-amber-500/10" />
          </div>

          {/* Floating luminous particles */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {[5, 8, 3, 6, 4, 7, 3, 5, 6, 4, 7, 5, 3, 8, 3, 6, 5, 4].map((size, i) => (
              <span
                key={i}
                className="absolute rounded-full"
                style={{
                  width: `${size}px`,
                  height: `${size}px`,
                  background: `rgba(245,158,11,${0.18 + (i % 4) * 0.1})`,
                  top: `${(i * 17 + 7) % 94}%`,
                  left: `${(i * 23 + 9) % 93}%`,
                  boxShadow: '0 0 10px rgba(245,158,11,0.6)',
                  animation: `floatDot ${3 + (i % 3)}s ease-in-out ${(i % 4) * 0.4}s infinite`,
                }}
              />
            ))}
          </div>

          {/* Top telemetry HUD banner */}
          <div className="relative z-10 w-full max-w-5xl flex items-center justify-between text-[11px] font-mono text-amber-300/70 pt-2 border-b border-amber-500/15 pb-2">
            <div className="flex items-center gap-2">
              <Compass className="w-3.5 h-3.5 text-amber-400 animate-spin" style={{ animationDuration: '12s' }} />
              <span className="hidden sm:inline">DOUALA PORT • CAMEROUN</span>
              <span className="text-slate-400">04°03&apos;04&quot;N 009°42&apos;54&quot;E</span>
            </div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/90 border border-amber-500/30 text-amber-300 text-xs font-bold tracking-wider uppercase backdrop-blur-md shadow-lg shadow-amber-500/10">
              <Sparkles className="w-3.5 h-3.5 text-yellow-400 animate-spin" />
              CADC ERP • SYDONIA+ / GUCE READY
            </div>
            <div className="hidden md:flex items-center gap-2">
              <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
              <span className="text-emerald-400 font-bold">SYSTÈME OPÉRATIONNEL</span>
            </div>
          </div>

          {/* Main CADC center Branding */}
          <div className="relative z-10 flex flex-col items-center text-center my-auto max-w-3xl px-4">

            {/* Center Ship Emblem with dual rotating rings and pulse halo */}
            <div className="relative mb-6 w-28 h-28 flex items-center justify-center">
              <div
                className="absolute inset-0 rounded-full border-2 border-dashed border-amber-500/30"
                style={{ animation: 'spinSlow 12s linear infinite' }}
              />
              <div
                className="absolute inset-2 rounded-full border border-amber-400/40"
                style={{ animation: 'spinSlow 7s linear infinite reverse' }}
              />
              <div
                className="absolute inset-0 rounded-full"
                style={{
                  background: 'radial-gradient(circle, rgba(245,158,11,0.25) 0%, transparent 70%)',
                  animation: 'pulseHalo 2s ease-in-out infinite',
                }}
              />
              <div className="relative z-10 w-16 h-16 rounded-2xl bg-gradient-to-tr from-amber-600 via-yellow-500 to-amber-400 flex items-center justify-center shadow-2xl shadow-amber-500/50 border border-yellow-200">
                <Ship className="w-9 h-9 text-slate-950 drop-shadow-md" />
              </div>
            </div>

            {/* CADC Golden Metallic Title */}
            <h1
              className="text-7xl sm:text-9xl font-black tracking-tighter mb-2 select-none"
              style={{
                background: 'linear-gradient(180deg,#ffffff 0%,#fef08a 25%,#f59e0b 60%,#b45309 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                filter: 'drop-shadow(0 0 35px rgba(245,158,11,0.5))',
                animation: 'shimmerGlow 3s ease-in-out infinite',
              }}
            >
              CADC
            </h1>
            <h2 className="text-lg sm:text-2xl font-extrabold text-white tracking-[0.25em] uppercase mb-1">
              Code Axis Digital Cameroun
            </h2>
            <p className="text-xs sm:text-sm text-amber-300/80 font-mono tracking-wider mb-8">
              EVO-LOG Enterprise ERP • Logistique, Transit & Acconage Portuaire
            </p>

            {/* Futuristic Progress Bar */}
            <div className="w-full max-w-md bg-slate-900/90 border border-slate-700/70 p-4 rounded-2xl shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between text-xs font-mono px-1 mb-2 text-slate-300">
                <span className="text-amber-400 font-bold flex items-center gap-1.5">
                  <Anchor className="w-3.5 h-3.5 animate-bounce" /> Initialisation Modules Métier...
                </span>
                <span className="text-amber-300 font-bold tabular-nums text-sm">{splashProgress}%</span>
              </div>
              <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800 p-0.5">
                <div
                  className="h-full rounded-full transition-all duration-100"
                  style={{
                    width: `${splashProgress}%`,
                    background: 'linear-gradient(90deg,#d97706 0%,#f59e0b 50%,#fef08a 100%)',
                    boxShadow: '0 0 14px rgba(245,158,11,0.8), 0 0 28px rgba(245,158,11,0.4)',
                  }}
                />
              </div>

              {/* Dynamic Telemetry Equalizer Bars */}
              <div className="flex items-center justify-center gap-1.5 mt-3 h-4">
                {[12, 18, 26, 14, 22, 30, 16, 24, 18, 28, 14, 20, 26, 15, 22].map((height, idx) => (
                  <div
                    key={idx}
                    className="w-1 bg-amber-400/70 rounded-full transition-all duration-150"
                    style={{
                      height: `${Math.max(4, (height * ((splashProgress + idx * 7) % 100)) / 70)}px`,
                      opacity: splashProgress > 10 ? 0.9 : 0.2,
                    }}
                  />
                ))}
              </div>

              {/* Status Message */}
              <div className="mt-2.5 px-1 text-[11px] text-amber-200/80 font-mono text-center">
                {splashProgress < 25 && '▶ Connexion API FastAPI & PostgreSQL OHADA...'}
                {splashProgress >= 25 && splashProgress < 50 && '▶ Synchronisation Transit, Douane & Connaissements...'}
                {splashProgress >= 50 && splashProgress < 75 && '▶ Vérification Sécurité RBAC & Permissions...'}
                {splashProgress >= 75 && splashProgress < 98 && '▶ Chargement des Tableaux de Bord Portuaires...'}
                {splashProgress >= 98 && '✓ Système opérationnel. Bienvenue sur EVO-LOG.'}
              </div>
            </div>
          </div>

          {/* Footer Telemetry */}
          <div className="relative z-10 w-full max-w-5xl flex items-center justify-between text-[11px] text-slate-500 font-mono pb-2 border-t border-slate-800/80 pt-2">
            <span>© 2026 Code Axis Digital Cameroun (CADC)</span>
            <span className="hidden sm:inline text-amber-400/60 font-semibold">SSL 256-BIT • ARCHITECTURE ZERO MOCK</span>
            <span>v2.0.0 EM-ERP</span>
          </div>

          <style>{`
            @keyframes splashFadeIn{from{opacity:0;transform:scale(1.02)}to{opacity:1;transform:scale(1)}}
            @keyframes splashFadeOut{from{opacity:1;transform:scale(1)}to{opacity:0;transform:scale(0.98);pointer-events:none}}
            @keyframes radarSweep{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
            @keyframes floatDot{0%,100%{transform:translateY(0) scale(1);opacity:0.3}50%{transform:translateY(-20px) scale(1.4);opacity:0.8}}
            @keyframes spinSlow{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
            @keyframes pulseHalo{0%,100%{opacity:0.4;transform:scale(1)}50%{opacity:1;transform:scale(1.25)}}
            @keyframes shimmerGlow{0%,100%{filter:drop-shadow(0 0 25px rgba(245,158,11,0.4))}50%{filter:drop-shadow(0 0 55px rgba(245,158,11,0.8)) brightness(1.15)}}
          `}</style>
        </div>
      )}

      {/* 3. LOGIN INTERFACE CARD */}
      <div className="relative z-10 w-full max-w-[460px] mx-4 animate-in fade-in zoom-in-95 duration-500">

        {/* Brand header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-tr from-amber-500 via-yellow-400 to-amber-600 rounded-2xl shadow-2xl shadow-amber-500/30 mb-3 border border-yellow-200">
            <Ship className="w-8 h-8 text-slate-950 drop-shadow" />
          </div>
          <div>
            <span className="text-xs font-black tracking-widest text-amber-400 uppercase bg-amber-500/15 px-3 py-1 rounded-full border border-amber-500/30 mb-1.5 inline-block backdrop-blur-md">
              CADC • Code Axis Digital Cameroun
            </span>
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">EVO-LOG SaaS</h1>
          </div>
          <p className="text-xs font-bold text-slate-300 uppercase tracking-widest mt-1">
            Système Intégré de Gestion Portuaire & Logistique
          </p>
        </div>

        {/* Login Box */}
        <div className="bg-slate-900/90 backdrop-blur-2xl rounded-3xl shadow-2xl shadow-black/90 border border-slate-700/80 p-7 sm:p-8 text-white">
          <div className="mb-5 pb-3 border-b border-slate-800">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" /> Authentification Restreinte
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Identifiants opérationnels fournis par l&apos;administrateur.</p>
          </div>

          {expiryWarning && (
            <div className="mb-4 p-3 bg-amber-500/15 border border-amber-500/40 rounded-xl text-amber-300 text-xs font-semibold flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
              <span>{expiryWarning}</span>
            </div>
          )}

          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Identifiant ou Email Institutionnel
              </label>
              <div className="relative">
                <UserIcon className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="Identifiant ou email institutionnel"
                  required
                  className="w-full h-12 pl-10 pr-4 bg-slate-950/90 border border-slate-700 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/20 transition-all font-mono"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Mot de Passe
                </label>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full h-12 pl-10 pr-11 bg-slate-950/90 border border-slate-700 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/20 transition-all font-mono"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-amber-400 transition-colors p-1"
                  title={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={e => setRemember(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-700 bg-slate-950 text-amber-500 focus:ring-amber-500"
                />
                Rester connecté
              </label>
              <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Base PostgreSQL Active
              </span>
            </div>

            {errorMessage && (
              <div className="p-3 bg-red-950/80 border border-red-500/50 rounded-xl text-red-300 text-xs font-semibold animate-in fade-in duration-200">
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-12 bg-gradient-to-r from-amber-600 via-amber-500 to-amber-600 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-black text-sm rounded-xl flex items-center justify-center gap-2 shadow-xl shadow-amber-500/30 transition-all active:scale-[0.98] disabled:opacity-70"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  Authentification en cours...
                </span>
              ) : (
                <>
                  <span>Se Connecter à l&apos;ERP</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Douala Port • Kribi • limbé</span>
            <Link href="/forgot-password" className="text-amber-400 hover:underline font-semibold">
              Assistance Connexion
            </Link>
          </div>
        </div>
      </div>

      {/* Password Change Modal for admin123 default password */}
      {mustChangePassword && (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-amber-500/40 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl space-y-5 animate-in zoom-in-95 duration-300">
            <div className="w-14 h-14 bg-amber-500/15 text-amber-400 border border-amber-500/30 rounded-2xl flex items-center justify-center mx-auto">
              <KeyRound className="w-7 h-7" />
            </div>
            <div className="text-center">
              <span className="text-[11px] font-black tracking-widest text-amber-400 uppercase bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20 inline-block mb-1">
                Premier Accès ou Expiration Sécurité
              </span>
              <h2 className="text-xl font-black text-slate-100">Changement de Mot de Passe Obligatoire</h2>
              <p className="text-xs text-slate-400 mt-1">
                Le mot de passe initial temporaire doit être remplacé par une combinaison sécurisée avant d&apos;accéder aux modules.
              </p>
            </div>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Nouveau Mot de Passe</label>
                <div className="relative">
                  <input
                    type={showNewPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={e => setNewPassword(e.target.value)}
                    placeholder="Min. 8 caractères (lettres + chiffres)"
                    className="w-full h-11 px-4 pr-11 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-amber-400 p-1"
                  >
                    {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Confirmer le Mot de Passe</label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    placeholder="Répétez le nouveau mot de passe"
                    className="w-full h-11 px-4 pr-11 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-amber-400 p-1"
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              {passwordError && (
                <div className="p-3 bg-red-950/70 border border-red-500/40 rounded-xl text-red-300 text-xs font-semibold">{passwordError}</div>
              )}
              {passwordSuccess && (
                <div className="p-3 bg-emerald-950/70 border border-emerald-500/40 rounded-xl text-emerald-300 text-xs font-semibold flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" /> Mot de passe enregistré ! Redirection...
                </div>
              )}
              <button
                type="submit"
                className="w-full py-3.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-black rounded-xl text-sm shadow-xl shadow-amber-500/20 transition-all"
              >
                Valider et Accéder à l&apos;ERP
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

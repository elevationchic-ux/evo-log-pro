'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { signIn, getSession } from 'next-auth/react';
import { Sparkles, Ship, Lock, Mail, ArrowRight, ShieldCheck, KeyRound, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();

  // Splash screen  active on every page load
  const [showSplash, setShowSplash] = useState(true);
  const [splashProgress, setSplashProgress] = useState(0);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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

  // Splash animation
  useEffect(() => {
    const interval = setInterval(() => {
      setSplashProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setShowSplash(false), 300);
          return 100;
        }
        return prev + 4;
      });
    }, 35);
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
        setErrorMessage('Identifiants incorrects. Vérifiez votre email et mot de passe.');
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
      setErrorMessage('Une erreur est survenue. Réessayez.');
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
    <div className="fixed inset-0 flex items-center justify-center bg-slate-950 text-white font-sans select-none overflow-hidden">

      {/* CADC SPLASH SCREEN */}
      {showSplash && (
        <div className="fixed inset-0 z-50 bg-black text-white flex flex-col items-center justify-between p-6 sm:p-12 animate-in fade-in duration-300">
          <div className="z-10 pt-4">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900/80 border border-amber-500/30 text-amber-300 text-xs font-bold tracking-wider uppercase backdrop-blur-md">
              <Sparkles className="w-3.5 h-3.5 text-yellow-400 animate-spin" />
              Initialisation Sécurisée CADC ERP
            </div>
          </div>

          <div className="z-10 flex flex-col items-center text-center my-auto max-w-3xl px-4">
            <h1 className="text-6xl sm:text-9xl font-black tracking-tighter bg-gradient-to-b from-amber-100 via-amber-300 to-amber-600 bg-clip-text text-transparent drop-shadow-[0_0_45px_rgba(245,158,11,0.45)] mb-3">
              CADC
            </h1>
            <h2 className="text-xl sm:text-3xl font-extrabold text-white tracking-widest uppercase mb-6">
              Code Axis Digital Cameroun
            </h2>

            <div className="w-full max-w-sm bg-slate-900/90 border border-slate-800 p-2 rounded-2xl shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between text-xs font-mono px-3 mb-1.5 text-slate-400">
                <span className="text-amber-400 font-bold flex items-center gap-1.5">
                  <Ship className="w-3.5 h-3.5 animate-bounce" /> Chargement du Système...
                </span>
                <span className="text-amber-300 font-bold">{splashProgress}%</span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-amber-500 via-yellow-400 to-amber-300 rounded-full transition-all duration-75 shadow-[0_0_12px_#f59e0b]"
                  style={{ width: `${splashProgress}%` }}
                />
              </div>
            </div>
          </div>

          <div className="z-10 pb-4 text-center text-xs text-slate-500 font-mono">
            © 2026 Code Axis Digital Cameroun (CADC) • Tous droits réservés
          </div>
        </div>
      )}

      {/* Background */}
      <div className="absolute inset-0 z-0">
        <img
          src="/images/cargo_ship_port_bg.png"
          alt="Port"
          className="w-full h-full object-cover object-center scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/85 to-slate-900/60 backdrop-blur-[2px]" />
      </div>

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-[440px] mx-4 animate-in fade-in zoom-in-95 duration-500">
        <div className="text-center mb-5">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-tr from-amber-500 via-yellow-400 to-amber-600 rounded-2xl shadow-xl shadow-amber-500/20 mb-3 border border-amber-300/40">
            <Ship className="w-8 h-8 text-slate-950" />
          </div>
          <div>
            <span className="text-xs font-black tracking-widest text-amber-400 uppercase bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20 mb-1 inline-block">
              CADC • Code Axis Digital Cameroun
            </span>
            <h1 className="text-3xl font-black text-white tracking-tight">EVO-LOG SaaS</h1>
          </div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-1">
            Authentification Administrateur & Personnel
          </p>
        </div>

        <div className="bg-slate-900/90 backdrop-blur-2xl rounded-3xl shadow-2xl shadow-black/80 border border-slate-800 p-7 text-white">
          <div className="mb-5 pb-3 border-b border-slate-800/80">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" /> Authentification Restreinte
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Saisissez l&apos;identifiant attribué par votre administrateur.</p>
          </div>

          {expiryWarning && (
            <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-xs font-semibold flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
              <span>{expiryWarning}</span>
            </div>
          )}

          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Identifiant / Email Institutionnel
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="kamga@evo-log.cm"
                  required
                  className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all font-mono"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Mot de Passe
                </label>
                <span className="text-[11px] text-amber-400 font-mono">Défaut: admin123</span>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all font-mono"
                />
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
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Création Admin Uniquement
              </span>
            </div>

            {errorMessage && (
              <div className="p-3 bg-red-950/60 border border-red-500/40 rounded-xl text-red-300 text-xs font-semibold animate-in fade-in duration-200">
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-12 bg-gradient-to-r from-amber-600 via-amber-500 to-amber-600 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-black text-sm rounded-xl flex items-center justify-center gap-2 shadow-xl shadow-amber-500/20 transition-all active:scale-[0.98] disabled:opacity-70"
            >
              {isLoading ? 'Connexion en cours...' : <><span>Se Connecter à l&apos;ERP</span><ArrowRight className="w-4 h-4" /></>}
            </button>
          </form>

          <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>Seul l&apos;Admin crée les comptes</span>
            <Link href="/forgot-password" className="text-amber-400 hover:underline font-semibold">
              Mot de passe oublié ?
            </Link>
          </div>
        </div>
      </div>

      {/* Password Change Modal */}
      {mustChangePassword && (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-amber-500/40 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl space-y-5 animate-in zoom-in-95 duration-300">
            <div className="w-14 h-14 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded-2xl flex items-center justify-center mx-auto">
              <KeyRound className="w-7 h-7" />
            </div>
            <div className="text-center">
              <span className="text-[11px] font-black tracking-widest text-amber-400 uppercase bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20 inline-block mb-1">
                Premier Accès ou Expiration 90 jours
              </span>
              <h2 className="text-xl font-black text-slate-100">Changement de Mot de Passe Obligatoire</h2>
              <p className="text-xs text-slate-400 mt-1">
                Le mot de passe par défaut <b className="text-amber-300">admin123</b> doit être immédiatement remplacé.
              </p>
            </div>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Nouveau Mot de Passe</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  placeholder="Min. 8 caractères (lettres + chiffres)"
                  className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Confirmer le Mot de Passe</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                  placeholder="Répétez le nouveau mot de passe"
                  className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                  required
                />
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
                Enregistrer le Nouveau Mot de Passe
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

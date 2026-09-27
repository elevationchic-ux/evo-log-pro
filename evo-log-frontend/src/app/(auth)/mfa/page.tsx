'use client';

// src/app/(auth)/mfa/page.tsx — Second facteur de la connexion.
//
// Cette page n'a jamais été une formalité : elle échange le jeton 2FA délivré
// par POST /auth/login contre une vraie session via POST /auth/2fa/verify. Le
// backend seul décide si le code (TOTP ou code de secours à usage unique) est
// bon. Sans jeton en attente, il n'y a rien à vérifier : on l'affiche au lieu
// de laisser un champ de code vide qui « fonctionnerait » quoi qu'il arrive.

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { signOut } from 'next-auth/react';
import { toast } from 'sonner';
import {
  ShieldCheck,
  ArrowRight,
  ArrowLeft,
  KeyRound,
  Eye,
  EyeOff,
  Loader2,
  TriangleAlert,
  CircleHelp,
} from 'lucide-react';
import { apiClient, authAPI } from '@/lib/api-client';
import { establishSession } from '@/lib/login-session';
import { landingRouteFor } from '@/lib/auth';
import {
  clearTwoFactorChallenge,
  readTwoFactorChallenge,
  type TwoFactorChallenge,
} from '@/lib/2fa-challenge';
import { useSettings } from '@/components/layout/SettingsProvider';

export const dynamic = 'force-dynamic';

type Phase = 'checking' | 'code' | 'rotate' | 'done';
type CodeKind = 'totp' | 'recovery';

/** Validation identique à celle du backend (validate_password_strength) pour
 *  ne pas envoyer une requête déjà condamnée. */
function checkNewPassword(value: string): string | null {
  if (value === 'admin123') return "Le mot de passe par défaut « admin123 » est interdit.";
  if (value.length < 8) return 'Minimum 8 caractères requis.';
  if (!/[A-Za-z]/.test(value) || !/[0-9]/.test(value)) {
    return 'Le mot de passe doit contenir au moins une lettre et un chiffre.';
  }
  return null;
}

export default function MfaPage() {
  const router = useRouter();
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';

  const t = useCallback(
    (fr: string, en: string) => (lang === 'en' ? en : fr),
    [lang],
  );

  const [challenge, setChallenge] = useState<TwoFactorChallenge | null>(null);
  const [phase, setPhase] = useState<Phase>('checking');
  const [kind, setKind] = useState<CodeKind>('totp');
  const [code, setCode] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Étape « mot de passe à faire expirer » : ouverte uniquement si le backend
  // le réclame (users.must_change_password) après la validation du 2FA.
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [revealNew, setRevealNew] = useState(false);
  const [rotateError, setRotateError] = useState<string | null>(null);
  const [rolesAfterVerify, setRolesAfterVerify] = useState<string[]>([]);

  useEffect(() => {
    const found = readTwoFactorChallenge();
    setChallenge(found);
    setPhase(found ? 'code' : 'checking');
    if (!found) clearTwoFactorChallenge();
  }, []);

  const switchKind = (next: CodeKind) => {
    setKind(next);
    setCode('');
    setError(null);
  };

  const backToLogin = useCallback(() => {
    clearTwoFactorChallenge();
    router.push('/login');
  }, [router]);

  const verify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!challenge?.two_factor_token) return;
    const valeur = code.trim();
    if (kind === 'totp' && !/^\d{6}$/.test(valeur)) {
      setError(t('Le code TOTP doit contenir exactement 6 chiffres.', 'The TOTP code must contain exactly 6 digits.'));
      return;
    }
    if (kind === 'recovery' && valeur.replace(/[^0-9a-zA-Z]/g, '').length < 8) {
      setError(t('Code de secours incomplet (format attendu : XXXX-XXXX).', 'Recovery code incomplete (expected format: XXXX-XXXX).'));
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const res = await authAPI.verify2FA({ two_factor_token: challenge.two_factor_token, code: valeur });
      const data = res.data || {};
      if (!data.access_token) {
        setError(t('Le serveur a validé le code mais n’a livré aucun jeton de session.', 'The server validated the code but returned no session token.'));
        return;
      }
      const outcome = await establishSession(data.access_token);
      if (!outcome.ok) {
        setError(outcome.message || t("La session n'a pas pu être ouverte.", 'The session could not be opened.'));
        return;
      }
      clearTwoFactorChallenge();
      setRolesAfterVerify(outcome.roles);

      if (outcome.mustChangePassword) {
        // Le gate passe avant l'atterrissage : rester sur un compte dont le
        // mot de passe initial n'a pas été remplacé serait le contourner.
        setPhase('rotate');
        setSubmitting(false);
        return;
      }

      setPhase('done');
      toast.success(t('Double authentification validée.', 'Two-factor authentication verified.'));
      router.push(landingRouteFor(outcome.roles));
      router.refresh();
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;
      if (status === 401) {
        setError(t(
          "Code refusé par le serveur. Vérifiez l’heure de votre application d’authentification, ou utilisez un code de secours.",
          'Code rejected by the server. Check the clock of your authenticator app, or use a recovery code.',
        ));
      } else if (typeof detail === 'string' && detail) {
        setError(detail);
      } else if (err?.response) {
        setError(t('Le serveur a refusé la vérification.', 'The server refused the verification.'));
      } else {
        setError(t('API injoignable. Vérifiez votre connexion puis réessayez.', 'API unreachable. Check your connection and try again.'));
      }
      setSubmitting(false);
    }
  };

  const rotate = async (e: React.FormEvent) => {
    e.preventDefault();
    setRotateError(null);
    if (!currentPassword) {
      setRotateError(t('Le mot de passe actuel est requis.', 'Current password is required.'));
      return;
    }
    const invalide = checkNewPassword(newPassword);
    if (invalide) { setRotateError(invalide); return; }
    if (newPassword !== confirmPassword) {
      setRotateError(t('Les mots de passe ne correspondent pas.', 'Passwords do not match.'));
      return;
    }
    setSubmitting(true);
    try {
      await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPhase('done');
      toast.success(t('Mot de passe mis à jour.', 'Password updated.'));
      router.push(landingRouteFor(rolesAfterVerify));
      router.refresh();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setRotateError(typeof detail === 'string' && detail
        ? detail
        : t('Le serveur a refusé le changement de mot de passe.', 'The server refused the password change.'));
      setSubmitting(false);
    }
  };

  /** Abandonner la rotation = rester connecté avec le mot de passe imposé :
   *  on déconnecte plutôt que de laisser le gate ouvert. */
  const abandon = () => {
    clearTwoFactorChallenge();
    signOut({ callbackUrl: '/login' });
  };

  const identifiant = challenge?.identifier || '';

  const hint = useMemo(() => (
    kind === 'totp'
      ? t('Saisissez le code à 6 chiffres généré par votre application d’authentification.',
          'Enter the 6-digit code generated by your authenticator app.')
      : t('Les codes de secours sont à usage unique : celui-ci sera consommé et définitivement désactivé.',
          'Recovery codes are single use: this one will be consumed and permanently disabled.')
  ), [kind, t]);

  if (phase === 'checking') {
    return (
      <Shell>
        <div className="flex items-center gap-3 text-slate-400 text-sm">
          <Loader2 className="w-5 h-5 animate-spin" />
          {t('Reprise de la vérification en attente…', 'Resuming the pending verification…')}
        </div>
      </Shell>
    );
  }

  if (!challenge) {
    return (
      <Shell>
        <div className="flex items-start gap-3 p-4 bg-amber-500/10 border border-amber-500/30 rounded-2xl">
          <TriangleAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-sm font-bold text-amber-300">
              {t('Aucune vérification en attente', 'No verification pending')}
            </p>
            <p className="text-xs text-slate-400 leading-relaxed">
              {t(
                "Cette page n'affiche un champ de code que lorsqu'un mot de passe vient d'être validé et que le compte exige un second facteur. Le jeton de vérification expire aussi au bout de 5 minutes.",
                'This page only shows a code field once a password has just been validated and the account requires a second factor. The verification token also expires after 5 minutes.',
              )}
            </p>
          </div>
        </div>
        <Link
          href="/login"
          className="mt-6 w-full min-h-11 inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-sm transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          {t('Retour à la connexion', 'Back to sign in')}
        </Link>
      </Shell>
    );
  }

  if (phase === 'rotate') {
    return (
      <Shell>
        <div className="w-12 h-12 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded-2xl flex items-center justify-center mb-5">
          <KeyRound className="w-6 h-6" />
        </div>
        <h1 className="text-xl font-black text-slate-100 mb-1">
          {t('Changement de mot de passe obligatoire', 'Password change required')}
        </h1>
        <p className="text-xs text-slate-400 mb-6 leading-relaxed">
          {t(
            'Le second facteur est validé, mais le mot de passe initial de ce compte n’a jamais été remplacé. Les modules restent fermés jusqu’à sa mise à jour.',
            'The second factor is verified, but this account’s initial password has never been replaced. Modules stay locked until it is updated.',
          )}
        </p>
        <form onSubmit={rotate} className="space-y-4">
          <Field
            label={t('Mot de passe actuel', 'Current password')}
            value={currentPassword}
            onChange={setCurrentPassword}
            reveal={false}
            placeholder={t('Mot de passe saisi à l’étape précédente', 'Password entered at the previous step')}
          />
          <Field
            label={t('Nouveau mot de passe', 'New password')}
            value={newPassword}
            onChange={setNewPassword}
            reveal={revealNew}
            onToggleReveal={() => setRevealNew((v) => !v)}
            placeholder={t('Min. 8 caractères (lettres + chiffres)', 'Min. 8 characters (letters + digits)')}
          />
          <Field
            label={t('Confirmer le mot de passe', 'Confirm password')}
            value={confirmPassword}
            onChange={setConfirmPassword}
            reveal={revealNew}
            placeholder={t('Répétez le nouveau mot de passe', 'Repeat the new password')}
          />
          {rotateError && (
            <div className="p-3 bg-red-950/70 border border-red-500/40 rounded-xl text-red-300 text-xs font-semibold">
              {rotateError}
            </div>
          )}
          <button
            type="submit"
            disabled={submitting}
            className="w-full min-h-11 py-3 px-4 bg-amber-500 hover:bg-amber-400 text-slate-950 font-black rounded-xl text-sm disabled:opacity-60 transition-colors"
          >
            {submitting
              ? t('Enregistrement…', 'Saving…')
              : t('Valider et accéder à l’ERP', 'Validate and enter the ERP')}
          </button>
          <button
            type="button"
            onClick={abandon}
            className="w-full min-h-11 py-3 px-4 text-slate-400 hover:text-slate-200 text-xs font-semibold transition-colors"
          >
            {t('Abandonner et me déconnecter', 'Cancel and sign me out')}
          </button>
        </form>
      </Shell>
    );
  }

  return (
    <Shell>
      <div className="w-12 h-12 bg-indigo-500/10 text-indigo-400 rounded-2xl flex items-center justify-center mb-6">
        <ShieldCheck className="w-6 h-6" />
      </div>
      <h1 className="text-2xl font-black text-slate-50 mb-2">
        {t('Double authentification', 'Two-factor authentication')}
      </h1>
      <p className="text-sm text-slate-400 mb-6 leading-relaxed">
        {t(
          'Le mot de passe de',
          'The password of',
        )}{' '}
        <span className="text-slate-200 font-semibold break-all">{identifiant}</span>{' '}
        {t('a été reconnu. Second facteur requis.', 'was accepted. A second factor is required.')}
      </p>

      <div className="flex gap-1 p-1 bg-slate-950 border border-slate-800 rounded-xl mb-5">
        <KindTab
          active={kind === 'totp'}
          onClick={() => switchKind('totp')}
          label={t('Code authentificateur', 'Authenticator code')}
        />
        <KindTab
          active={kind === 'recovery'}
          onClick={() => switchKind('recovery')}
          label={t('Code de secours', 'Recovery code')}
        />
      </div>

      <form onSubmit={verify} className="space-y-4">
        <div>
          <label
            htmlFor="2fa-code"
            className="block text-[11px] font-bold text-slate-400 uppercase mb-2"
          >
            {kind === 'totp'
              ? t('Code TOTP (6 chiffres)', 'TOTP code (6 digits)')
              : t('Code de secours (XXXX-XXXX)', 'Recovery code (XXXX-XXXX)')}
          </label>
          <input
            id="2fa-code"
            type="text"
            name="2fa-code"
            autoComplete="one-time-code"
            inputMode={kind === 'totp' ? 'numeric' : 'text'}
            autoCapitalize="characters"
            maxLength={kind === 'totp' ? 6 : 12}
            value={code}
            onChange={(e) => {
              const brut = e.target.value;
              setCode(kind === 'totp' ? brut.replace(/\D/g, '').slice(0, 6) : brut.toUpperCase().replace(/[^0-9A-Z-]/g, '').slice(0, 12));
              if (error) setError(null);
            }}
            placeholder={kind === 'totp' ? '123456' : 'ABCD-1234'}
            className="w-full min-h-11 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-center text-2xl font-mono tracking-widest text-indigo-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
          />
          <p className="text-[11px] text-slate-500 mt-2 leading-relaxed">{hint}</p>
        </div>

        {error && (
          <div className="p-3 bg-red-950/70 border border-red-500/40 rounded-xl text-red-300 text-xs font-semibold leading-relaxed">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting || !code}
          className="w-full min-h-11 py-3.5 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl flex items-center justify-center gap-2 text-sm transition-colors"
        >
          {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
          {t('Vérifier et se connecter', 'Verify and sign in')}
        </button>
      </form>

      <div className="mt-6 pt-5 border-t border-slate-800 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <button
          type="button"
          onClick={backToLogin}
          className="min-h-11 inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          {t('Recommencer la connexion', 'Restart sign in')}
        </button>
        <Link
          href="/forgot-password"
          className="min-h-11 inline-flex items-center gap-2 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          <CircleHelp className="w-4 h-4" />
          {t('Plusieurs appareils perdus ?', 'Lost several devices?')}
        </Link>
      </div>

      <p className="mt-5 text-[11px] text-slate-600 leading-relaxed">
        {t(
          'Le jeton de cette étape expire côté serveur au bout de 5 minutes : au-delà, relancez la connexion.',
          'This step’s token expires server-side after 5 minutes: past that, restart the sign in.',
        )}
      </p>
    </Shell>
  );
}

/* ------------------------------------------------------------------ */

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl">
        {children}
      </div>
    </div>
  );
}

function KindTab({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`flex-1 min-h-11 rounded-lg px-3 text-xs font-bold transition-colors ${
        active
          ? 'bg-indigo-600 text-white'
          : 'text-slate-400 hover:text-slate-200'
      }`}
    >
      {label}
    </button>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  reveal,
  onToggleReveal,
  autoComplete,
  toggleLabel,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  reveal: boolean;
  onToggleReveal?: () => void;
  autoComplete: 'current-password' | 'new-password';
  toggleLabel?: string;
}) {
  return (
    <div>
      <label className="block text-[11px] font-bold text-slate-300 uppercase mb-1">{label}</label>
      <div className="relative">
        <input
          type={reveal ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          className="w-full min-h-11 px-4 pr-11 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500 font-mono"
        />
        {onToggleReveal && (
          <button
            type="button"
            onClick={onToggleReveal}
            aria-label={toggleLabel}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 inline-flex items-center justify-center text-slate-400 hover:text-amber-400 transition-colors"
          >
            {reveal ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>
    </div>
  );
}

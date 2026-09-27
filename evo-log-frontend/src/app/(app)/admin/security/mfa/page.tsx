'use client';

/**
 * K-Admin · Sécurité — Double authentification (2FA / TOTP).
 *
 * Cette écran configure le second facteur du compte **connecté** : le backend
 * ne connaît la 2FA que par utilisateur (colonnes users.two_factor_*), il
 * n’existe aucune politique d’entreprise à activer pour tout un tenant, et
 * cette page ne prétend pas le faire.
 *
 * Source unique de vérité : /api/v1/auth/2fa/{status,setup,enable,disable} et
 * /api/v1/auth/2fa/recovery-codes. Le QR est généré localement à partir de
 * l’otpauth_uri renvoyée par le serveur — jamais une image distante, qui
 * divulguerait le secret à un tiers. Les codes de secours en clair n’existent
 * qu’au moment de leur émission : la base ne stocke que leurs hachages, donc
 * aucune liste « déjà utilisée » n’est reconstituée ici.
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ShieldCheck, ShieldOff, RefreshCw, KeyRound, QrCode, Copy, Download,
  Smartphone, Loader2, AlertTriangle, CheckCircle2, Eye, EyeOff,
} from 'lucide-react';
import QRCode from 'qrcode';
import { toast } from 'sonner';
import { authAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { DataErrorState } from '@/components/shared/StatePanels';
import { classifyApiError, type ApiErrorInfo } from '@/hooks/useApi';

interface Status2FA {
  two_factor_enabled: boolean;
  configured: boolean;
  confirmed_at: string | null;
  recovery_codes_total: number;
  recovery_codes_remaining: number;
  recovery_codes_issued_at: string | null;
}

interface RecoverySnapshot {
  configured: boolean;
  total: number;
  remaining: number;
  used: number;
  issued_at: string | null;
}

/** Secret base32 débité en blocs de 4 : plus lisible sur un petit écran. */
function grouperSecret(secret: string): string {
  return (secret || '').toUpperCase().replace(/(.{4})/g, '$1 ').trim();
}

/** Libellé du compte tel qu’encodé dans l’URI otpauth (EVO-LOG:alice). */
function labelDepuisUri(uri: string): string {
  try {
    const brut = decodeURIComponent(uri.split('?')[0].replace(/^otpauth:\/\/totp\//, ''));
    return brut.includes(':') ? brut.split(':').slice(1).join(':') : brut;
  } catch {
    return '';
  }
}

function detailErreur(err: any, fr: string, en: string): string {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string' && detail) return detail;
  return err?.response ? fr : en;
}

export default function AdminSecurityMfaPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = useCallback(
    (fr: string, en: string) => (lang === 'en' ? en : fr),
    [lang],
  );
  const locale = lang === 'en' ? 'en-GB' : 'fr-FR';

  const [status, setStatus] = useState<Status2FA | null>(null);
  const [recovery, setRecovery] = useState<RecoverySnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<ApiErrorInfo | null>(null);
  const [busy, setBusy] = useState<null | 'setup' | 'enable' | 'disable' | 'regen'>(null);

  // Étape 1 : secret en attente de confirmation.
  const [provision, setProvision] = useState<{ secret: string; otpauth_uri: string; reset: boolean } | null>(null);
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null);
  const [qrError, setQrError] = useState<string | null>(null);
  const [showSecret, setShowSecret] = useState(false);
  const [code, setCode] = useState('');

  // Codes tout juste émis : seuls instants où ils existent en clair.
  const [freshCodes, setFreshCodes] = useState<string[] | null>(null);

  // Zones exigeant le mot de passe (désactivation, régénération).
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const passwordRef = useRef<HTMLInputElement | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [st, rc] = await Promise.all([
        authAPI.get2FAStatus(),
        authAPI.getRecoveryCodesStatus().catch(() => null),
      ]);
      setStatus(st.data as Status2FA);
      if (rc?.data) setRecovery(rc.data as RecoverySnapshot);
    } catch (err) {
      setLoadError(classifyApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // Génération locale du QR : l’URI otpauth reste dans le navigateur.
  useEffect(() => {
    let annule = false;
    if (!provision?.otpauth_uri) {
      setQrDataUrl(null);
      return;
    }
    setQrError(null);
    QRCode.toDataURL(provision.otpauth_uri, { width: 320, margin: 1, errorCorrectionLevel: 'M' })
      .then((url) => { if (!annule) setQrDataUrl(url); })
      .catch((err) => {
        if (!annule) {
          setQrDataUrl(null);
          setQrError(t(
            'Le QR n’a pas pu être dessiné localement. Saisissez la clé manuellement dans l’application.',
            'The QR could not be rendered locally. Enter the key manually in your app.',
          ));
          void err;
        }
      });
    return () => { annule = true; };
  }, [provision, t]);

  const formatDate = useCallback((iso: string | null | undefined): string => {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '—';
    return d.toLocaleString(locale, { dateStyle: 'medium', timeStyle: 'short' });
  }, [locale]);

  const demarrerSetup = async () => {
    setBusy('setup');
    setActionError(null);
    try {
      const res = await authAPI.setup2FA();
      setProvision({
        secret: res.data.secret,
        otpauth_uri: res.data.otpauth_uri,
        reset: !!res.data.reset,
      });
      setCode('');
      setFreshCodes(null);
      toast.success(t(
        'Clé générée. Scannez le QR puis confirmez avec un code.',
        'Key generated. Scan the QR then confirm with a code.',
      ));
      if (res.data.reset) setStatus((s) => (s ? { ...s, two_factor_enabled: false, confirmed_at: null } : s));
    } catch (err: any) {
      setActionError(detailErreur(err,
        'Le serveur a refusé la génération de la clé.',
        'The server refused to generate the key.'));
    } finally {
      setBusy(null);
    }
  };

  /** Changer de téléphone : le secret courant doit prouver la possession avant
   *  d’être remplacé (sans code valide, la 2FA resterait active sur lancien). */
  const reinitialiserAvecCode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!/^\d{6}$/.test(code.trim())) {
      setActionError(t('Le code doit contenir 6 chiffres.', 'The code must be 6 digits.'));
      return;
    }
    setBusy('setup');
    setActionError(null);
    try {
      const res = await authAPI.setup2FA(code.trim());
      setProvision({ secret: res.data.secret, otpauth_uri: res.data.otpauth_uri, reset: !!res.data.reset });
      setCode('');
      toast.success(t('Nouvelle clé émise.', 'New key issued.'));
    } catch (err: any) {
      setActionError(detailErreur(err,
        'Réinitialisation refusée.',
        'Reset refused.'));
    } finally {
      setBusy(null);
    }
  };

  const activer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!/^\d{6}$/.test(code.trim())) {
      setActionError(t('Le code doit contenir 6 chiffres.', 'The code must be 6 digits.'));
      return;
    }
    setBusy('enable');
    setActionError(null);
    try {
      const res = await authAPI.enable2FA(code.trim());
      setFreshCodes(Array.isArray(res.data.recovery_codes) ? res.data.recovery_codes : []);
      setProvision(null);
      setCode('');
      setShowSecret(false);
      toast.success(t('Double authentification activée.', 'Two-factor authentication enabled.'));
      await load();
    } catch (err: any) {
      setActionError(detailErreur(err,
        'Activation refusée : le code ne correspond pas.',
        'Activation refused: the code does not match.'));
    } finally {
      setBusy(null);
    }
  };

  const desactiver = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password) {
      setActionError(t('Le mot de passe est requis.', 'Password is required.'));
      return;
    }
    setBusy('disable');
    setActionError(null);
    try {
      await authAPI.disable2FA(password);
      setPassword('');
      setProvision(null);
      setFreshCodes(null);
      setCode('');
      toast.success(t('Double authentification désactivée.', 'Two-factor authentication disabled.'));
      await load();
    } catch (err: any) {
      setActionError(detailErreur(err,
        'Désactivation refusée par le serveur.',
        'Disable refused by the server.'));
    } finally {
      setBusy(null);
    }
  };

  const regenerer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password) {
      setActionError(t('Le mot de passe est requis.', 'Password is required.'));
      return;
    }
    setBusy('regen');
    setActionError(null);
    try {
      const res = await authAPI.regenerateRecoveryCodes(password);
      setFreshCodes(Array.isArray(res.data.recovery_codes) ? res.data.recovery_codes : []);
      setPassword('');
      toast.success(t(
        'Nouveaux codes émis : les anciens ne fonctionnent plus.',
        'New codes issued: the previous ones no longer work.',
      ));
      await load();
    } catch (err: any) {
      setActionError(detailErreur(err,
        'Régénération refusée par le serveur.',
        'Regeneration refused by the server.'));
    } finally {
      setBusy(null);
    }
  };

  const copier = async (valeur: string, libelle: string) => {
    try {
      await navigator.clipboard.writeText(valeur);
      toast.success(t(`${libelle} copié.`, `${libelle} copied.`));
    } catch {
      toast.error(t(
        'Copie impossible : le navigateur a bloqué laccès au presse-papiers.',
        'Copy failed: the browser blocked clipboard access.',
      ));
    }
  };

  const telechargerCodes = () => {
    if (!freshCodes?.length) return;
    const contenu = [
      'EVO-LOG — codes de secours 2FA',
      `Compte : ${labelDepuisUri(provision?.otpauth_uri || '') || '—'}`,
      `Émis le : ${new Date().toLocaleString(locale)}`,
      '',
      ...freshCodes,
      '',
      'Chaque code est à usage unique. Conservez cette fiche hors ligne.',
    ].join('\n');
    const blob = new Blob([contenu], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `codes-secours-2fa-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const compte = useMemo(
    () => labelDepuisUri(provision?.otpauth_uri || ''),
    [provision],
  );

  const actif = !!status?.two_factor_enabled;
  const enAttente = !actif && !!status?.configured && !provision;

  return (
    <div className="space-y-4 p-4 sm:p-6">
      {/* En-tête */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3 min-w-0">
          <div className="p-2.5 bg-indigo-500/10 rounded-xl text-indigo-400 shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              {t('Double authentification', 'Two-factor authentication')}
            </h1>
            <p className="text-sm text-on-surface-variant">
              {t(
                'Second facteur (TOTP) du compte connecté, réglé auprès de /auth/2fa.',
                'Second factor (TOTP) for the signed-in account, handled by /auth/2fa.',
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span
            className={`inline-flex items-center gap-2 px-3 py-2 min-h-11 rounded-xl border text-xs font-bold ${
              actif
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : 'bg-slate-800/60 border-slate-700 text-slate-300'
            }`}
          >
            {actif ? <CheckCircle2 className="w-4 h-4" /> : <ShieldOff className="w-4 h-4" />}
            {actif
              ? t('2FA active', '2FA enabled')
              : t('2FA inactive', '2FA disabled')}
          </span>
          <button
            type="button"
            onClick={load}
            disabled={loading}
            aria-label={t('Recharger', 'Reload')}
            className="p-2.5 min-h-11 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {loadError ? (
        <DataErrorState error={loadError} onRetry={load} />
      ) : loading && !status ? (
        <div className="p-8 flex items-center justify-center gap-3 text-on-surface-variant text-sm bg-surface border border-outline rounded-2xl">
          <Loader2 className="w-5 h-5 animate-spin" />
          {t('Lecture de l’état 2FA…', 'Reading 2FA state…')}
        </div>
      ) : (
        <>
          {/* Corps de métier : un seul message à la fois, lisible */}
          {actionError && (
            <div className="p-3 sm:p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-300 text-xs sm:text-sm font-semibold flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <span className="min-w-0 break-words">{actionError}</span>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Carte 1 — Application d’authentification */}
            <section className="lg:col-span-2 bg-surface border border-outline rounded-2xl p-4 sm:p-5 space-y-4">
              <header className="flex items-center gap-2">
                <QrCode className="w-5 h-5 text-indigo-400" />
                <h2 className="text-base sm:text-lg font-bold text-on-surface">
                  {t('Application d’authentification', 'Authenticator app')}
                </h2>
              </header>

              {actif && !provision && (
                <div className="space-y-4">
                  <p className="text-sm text-on-surface-variant leading-relaxed">
                    {t(
                      `Le second facteur protège ce compte depuis le ${formatDate(status?.confirmed_at)}.`,
                      `The second factor has protected this account since ${formatDate(status?.confirmed_at)}.`,
                    )}
                  </p>
                  <form onSubmit={reinitialiserAvecCode} className="space-y-3 p-4 bg-surface-container-low rounded-xl border border-outline">
                    <label htmlFor="rotate-code" className="block text-[11px] font-bold uppercase tracking-wider text-on-surface-variant">
                      {t('Changer d’appareil — code courant requis', 'Switch device — current code required')}
                    </label>
                    <p className="text-xs text-on-surface-variant leading-relaxed">
                      {t(
                        'Une nouvelle clé annule lancienne. Le serveur exige un code en cours pour la délivrer : sans lui, la 2FA ne peut pas être désarmée.',
                        'A new key voids the old one. The server requires a live code to issue it: without it, 2FA cannot be disarmed.',
                      )}
                    </p>
                    <div className="flex flex-col sm:flex-row gap-2">
                      <input
                        id="rotate-code"
                        value={code}
                        onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        inputMode="numeric"
                        autoComplete="one-time-code"
                        placeholder="123456"
                        className="w-full sm:flex-1 min-h-11 px-4 py-2 bg-surface border border-outline rounded-xl text-sm text-on-surface text-center font-mono tracking-widest focus:outline-none focus:border-indigo-500"
                      />
                      <button
                        type="submit"
                        disabled={busy !== null || code.length !== 6}
                        className="min-h-11 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-colors"
                      >
                        {busy === 'setup'
                          ? t('Émission…', 'Issuing…')
                          : t('Émettre une nouvelle clé', 'Issue a new key')}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {enAttente && (
                <p className="text-sm text-on-surface-variant leading-relaxed">
                  {t(
                    'Une clé est déjà en attente sur ce compte mais n’a jamais été confirmée. Générez-en une nouvelle pour repartir de zéro.',
                    'A key is already pending on this account but was never confirmed. Generate a new one to start over.',
                  )}
                </p>
              )}

              {!actif && (provision ? (
                <div className="space-y-4">
                  <div className="flex flex-col sm:flex-row gap-4 sm:items-start">
                    {/* Le QR doit rester noir sur blanc pour se scanner : seule
                        enclave claire de linterface, et purement technique. */}
                    <div className="bg-white p-3 rounded-xl border border-outline self-center sm:self-start">
                      {qrDataUrl ? (
                        <img
                          src={qrDataUrl}
                          alt={t('QR otpauth de la clé TOTP', 'otpauth QR code of the TOTP key')}
                          className="w-[180px] h-[180px] sm:w-[200px] sm:h-[200px] block"
                        />
                      ) : (
                        <div className="w-[180px] h-[180px] sm:w-[200px] sm:h-[200px] flex items-center justify-center text-center text-xs text-slate-500">
                          {qrError || t('Dessin du QR…', 'Rendering QR…')}
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0 space-y-3">
                      <p className="text-sm text-on-surface-variant leading-relaxed">
                        {t(
                          'Scannez ce QR dans Google Authenticator, Authy ou FreeOTP. Le code reste dans votre navigateur : aucune image ne part chez un tiers.',
                          'Scan this QR in Google Authenticator, Authy or FreeOTP. The code never leaves your browser: no image is sent to a third party.',
                        )}
                      </p>
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant">
                            {t('Clé manuelle', 'Manual key')}
                          </span>
                          <button
                            type="button"
                            onClick={() => copier(provision!.secret, t('la clé', 'the key'))}
                            className="inline-flex items-center gap-1 min-h-11 px-2 text-[11px] font-semibold text-on-surface-variant hover:text-indigo-400 transition-colors"
                          >
                            <Copy className="w-3.5 h-3.5" /> {t('Copier', 'Copy')}
                          </button>
                        </div>
                        <button
                          type="button"
                          onClick={() => setShowSecret((v) => !v)}
                          className="w-full flex items-center justify-between gap-2 min-h-11 px-3 py-2 bg-surface border border-outline rounded-xl text-left"
                        >
                          <code className="font-mono text-sm text-on-surface break-all">
                            {showSecret ? grouperSecret(provision!.secret) : '••••  ••••  ••••  ••••'}
                          </code>
                          {showSecret ? <EyeOff className="w-4 h-4 text-on-surface-variant shrink-0" /> : <Eye className="w-4 h-4 text-on-surface-variant shrink-0" />}
                        </button>
                        <p className="mt-1 text-[11px] text-on-surface-variant">
                          {compte
                            ? t(`Compte enregistré sous « ${compte} »`, `Account registered as “${compte}”`)
                            : t('Compte lu depuis lURI otpauth.', 'Account read from the otpauth URI.')}
                        </p>
                      </div>
                      <form onSubmit={activer} className="space-y-2">
                        <label htmlFor="enable-code" className="block text-[11px] font-bold uppercase tracking-wider text-on-surface-variant">
                          {t('Code de confirmation (6 chiffres)', 'Confirmation code (6 digits)')}
                        </label>
                        <div className="flex flex-col sm:flex-row gap-2">
                          <input
                            id="enable-code"
                            value={code}
                            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                            inputMode="numeric"
                            autoComplete="one-time-code"
                            placeholder="123456"
                            className="w-full sm:flex-1 min-h-11 px-4 py-2 bg-surface border border-outline rounded-xl text-sm text-on-surface text-center font-mono tracking-widest focus:outline-none focus:border-indigo-500"
                          />
                          <button
                            type="submit"
                            disabled={busy !== null || code.length !== 6}
                            className="min-h-11 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-colors"
                          >
                            {busy === 'enable'
                              ? t('Activation…', 'Enabling…')
                              : t('Activer la 2FA', 'Enable 2FA')}
                          </button>
                        </div>
                      </form>
                      <button
                        type="button"
                        onClick={() => { setProvision(null); setCode(''); setShowSecret(false); }}
                        className="min-h-11 inline-flex items-center gap-2 text-xs font-semibold text-on-surface-variant hover:text-on-surface transition-colors"
                      >
                        <Smartphone className="w-4 h-4" />
                        {t('Annuler cette émission', 'Cancel this issuance')}
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-on-surface-variant leading-relaxed">
                    {t(
                      'Aucun second facteur actif. L’activation génère une clé, que vous confirmez avec un code de votre application.',
                      'No second factor active. Enabling generates a key, which you confirm with a code from your app.',
                    )}
                  </p>
                  <button
                    type="button"
                    onClick={demarrerSetup}
                    disabled={busy !== null}
                    className="min-h-11 px-4 py-2.5 rounded-xl text-sm font-bold bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-colors"
                  >
                    {busy === 'setup'
                      ? t('Génération…', 'Generating…')
                      : t('Générer une clé TOTP', 'Generate a TOTP key')}
                  </button>
                </div>
              ))}
            </section>

            {/* Carte 2 — Codes de secours */}
            <section className="bg-surface border border-outline rounded-2xl p-4 sm:p-5 space-y-4">
              <header className="flex items-center gap-2">
                <KeyRound className="w-5 h-5 text-indigo-400" />
                <h2 className="text-base sm:text-lg font-bold text-on-surface">
                  {t('Codes de secours', 'Recovery codes')}
                </h2>
              </header>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-surface-container-low border border-outline rounded-xl">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
                    {t('Utilisables', 'Usable')}
                  </div>
                  <div className="mt-1 text-2xl font-bold text-on-surface tabular-nums">
                    {recovery?.remaining ?? status?.recovery_codes_remaining ?? 0}
                  </div>
                </div>
                <div className="p-3 bg-surface-container-low border border-outline rounded-xl">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
                    {t('Consommés', 'Consumed')}
                  </div>
                  <div className="mt-1 text-2xl font-bold text-on-surface tabular-nums">
                    {recovery?.used ?? Math.max((recovery?.total ?? status?.recovery_codes_total ?? 0) - (recovery?.remaining ?? status?.recovery_codes_remaining ?? 0), 0)}
                  </div>
                </div>
              </div>

              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                {recovery?.issued_at
                  ? t(`Jeu émis le ${formatDate(recovery.issued_at)}.`, `Set issued on ${formatDate(recovery.issued_at)}.`)
                  : t('Aucun jeu de codes émis pour le moment.', 'No code set issued yet.')}
              </p>

              {freshCodes?.length ? (
                <div className="space-y-3">
                  <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-[11px] text-amber-200 leading-relaxed">
                    {t(
                      'Affichés une seule fois : fermez cette page et ils ne seront jamais relus. Conservez-les hors ligne.',
                      'Shown once: close this page and they are never readable again. Keep them offline.',
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {freshCodes.map((c) => (
                      <button
                        key={c}
                        type="button"
                        onClick={() => copier(c, t('le code', 'the code'))}
                        className="min-h-11 px-2 py-2 bg-surface border border-outline rounded-xl text-xs font-mono text-on-surface hover:border-indigo-500 transition-colors"
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={telechargerCodes}
                    className="w-full min-h-11 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    {t('Télécharger la fiche (.txt)', 'Download the sheet (.txt)')}
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-xs text-on-surface-variant leading-relaxed">
                    {t(
                      'Chaque code sert une seule fois, au moment de la connexion, quand l’application d’authentification est inaccessible.',
                      'Each code is single use, at sign-in, when the authenticator app is unreachable.',
                    )}
                  </p>
                  {actif ? (
                    <form onSubmit={regenerer} className="space-y-2">
                      <label htmlFor="regen-password" className="block text-[11px] font-bold uppercase tracking-wider text-on-surface-variant">
                        {t('Mot de passe du compte', 'Account password')}
                      </label>
                      <input
                        id="regen-password"
                        ref={passwordRef}
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        autoComplete="current-password"
                        className="w-full min-h-11 px-4 py-2 bg-surface border border-outline rounded-xl text-sm text-on-surface focus:outline-none focus:border-indigo-500"
                      />
                      <button
                        type="submit"
                        disabled={busy !== null || !password}
                        className="w-full min-h-11 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold border border-outline text-on-surface hover:bg-surface-container disabled:opacity-50 transition-colors"
                      >
                        {busy === 'regen'
                          ? t('Émission…', 'Issuing…')
                          : t('Régénérer les codes', 'Regenerate codes')}
                      </button>
                      <p className="text-[11px] text-on-surface-variant leading-relaxed">
                        {t(
                          'La régénération remplace le jeu entier : les codes précédents cessent immédiatement de fonctionner.',
                          'Regenerating replaces the whole set: previous codes stop working immediately.',
                        )}
                      </p>
                    </form>
                  ) : (
                    <p className="text-[11px] text-on-surface-variant">
                      {t(
                        'Les codes sont émis automatiquement à l’activation de la 2FA.',
                        'Codes are issued automatically when 2FA is enabled.',
                      )}
                    </p>
                  )}
                </div>
              )}
            </section>

            {/* Carte 3 — Désactivation (zone sensible) */}
            <section className="lg:col-span-3 bg-surface border border-red-500/30 rounded-2xl p-4 sm:p-5">
              <header className="flex items-center gap-2 mb-3">
                <ShieldOff className="w-5 h-5 text-red-400" />
                <h2 className="text-base sm:text-lg font-bold text-on-surface">
                  {t('Désactiver le second facteur', 'Disable the second factor')}
                </h2>
              </header>
              {actif ? (
                <form onSubmit={desactiver} className="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-3 sm:items-end">
                  <div>
                    <label htmlFor="disable-password" className="block text-[11px] font-bold uppercase tracking-wider text-on-surface-variant mb-1">
                      {t('Mot de passe du compte', 'Account password')}
                    </label>
                    <div className="relative">
                      <input
                        id="disable-password"
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        autoComplete="current-password"
                        className="w-full min-h-11 px-4 pr-11 bg-surface border border-outline rounded-xl text-sm text-on-surface focus:outline-none focus:border-red-500"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword((v) => !v)}
                        aria-label={showPassword ? t('Masquer', 'Hide') : t('Afficher', 'Show')}
                        className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 inline-flex items-center justify-center text-on-surface-variant hover:text-on-surface transition-colors"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    <p className="mt-1 text-[11px] text-on-surface-variant leading-relaxed">
                      {t(
                        'Le serveur supprime aussi la clé et les codes de secours : ils resteraient des trousseaux orphelins.',
                        'The server also deletes the key and the recovery codes: they would stay as orphan access sets.',
                      )}
                    </p>
                  </div>
                  <button
                    type="submit"
                    disabled={busy !== null || !password}
                    className="min-h-11 px-4 py-2.5 rounded-xl text-xs font-bold bg-red-600 hover:bg-red-500 text-white disabled:opacity-50 transition-colors"
                  >
                    {busy === 'disable'
                      ? t('Désactivation…', 'Disabling…')
                      : t('Désactiver la 2FA', 'Disable 2FA')}
                  </button>
                </form>
              ) : (
                <p className="text-xs text-on-surface-variant">
                  {t(
                    'Aucun second facteur à désactiver sur ce compte.',
                    'No second factor to disable on this account.',
                  )}
                </p>
              )}
            </section>
          </div>

          {/* Notes d’honnêteté : ce que les chiffres de cette page ne disent pas */}
          <p className="text-[11px] text-on-surface-variant leading-relaxed">
            {t(
              'Fenêtre de validité TOTP : ±30 secondes autour du code courant (réglage serveur). Le jeton intermédiaire délivré à la connexion expire au bout de 5 minutes. Les codes de secours sont stockés sous forme de hachages : l’API ne renvoie que le solde utilisable, jamais la liste — un code déjà consommé ne peut donc pas être représenté ici. Cette page règle le compte connecté ; le 2FA des autres collaborateurs se configure depuis leur propre session.',
              'TOTP validity window: ±30 seconds around the current code (server setting). The intermediate token issued at sign-in expires after 5 minutes. Recovery codes are stored as hashes: the API returns only the usable balance, never the list — so an already consumed code cannot be shown here. This page configures the signed-in account; colleagues set 2FA from their own session.',
            )}
          </p>
        </>
      )}
    </div>
  );
}

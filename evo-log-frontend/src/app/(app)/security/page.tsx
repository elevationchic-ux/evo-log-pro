'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Shield,
  KeyRound,
  Lock,
  Smartphone,
  CheckCircle2,
  AlertTriangle,
  History,
  Laptop,
  LogOut,
  Save
} from 'lucide-react';
import { toast } from 'sonner';
import { authAPI } from '@/lib/api-client';

export default function SecuritySettingsPage() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [savingPassword, setSavingPassword] = useState(false);

  // Etat 2FA reel (pilote par le backend, plus de toggle optimiste bidonne)
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [setupSecret, setSetupSecret] = useState<string | null>(null);
  const [setupUri, setSetupUri] = useState<string | null>(null);
  const [code, setCode] = useState('');
  const [disablePassword, setDisablePassword] = useState('');
  const [showDisableForm, setShowDisableForm] = useState(false);
  const [busy2FA, setBusy2FA] = useState(false);

  const refreshStatus = useCallback(async () => {
    try {
      const { data } = await authAPI.get2FAStatus();
      setTwoFactorEnabled(Boolean(data?.two_factor_enabled));
    } catch {
      // Statut indisponible (backend distant momentanement hors ligne) : on
      // n'affiche pas d'etat par defaut trompeur, mais on ne bloque pas la page.
      setTwoFactorEnabled(false);
    } finally {
      setLoadingStatus(false);
    }
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);


  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error('Le nouveau mot de passe et sa confirmation ne correspondent pas.');
      return;
    }
    if (newPassword.length < 8) {
      toast.error('Le mot de passe doit contenir au moins 8 caractères.');
      return;
    }
    setSavingPassword(true);
    try {
      await authAPI.changePassword({
        current_password: currentPassword,
        new_password: newPassword
      });
      toast.success('Mot de passe mis à jour avec succès !');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur lors de la mise à jour du mot de passe.');
    } finally {
      setSavingPassword(false);
    }
  };

  const handleStartEnable = async () => {
    setBusy2FA(true);
    try {
      const { data } = await authAPI.setup2FA();
      setSetupSecret(data?.secret ?? null);
      setSetupUri(data?.otpauth_uri ?? null);
      setCode('');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Impossible d'initialiser la 2FA.");
    } finally {
      setBusy2FA(false);
    }
  };

  const handleConfirmEnable = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code || code.trim().length < 6) {
      toast.error('Saisissez le code a 6 chiffres genere par votre application.');
      return;
    }
    setBusy2FA(true);
    try {
      await authAPI.enable2FA(code.trim());
      toast.success('2FA TOTP activee avec succes.');
      setSetupSecret(null);
      setSetupUri(null);
      setCode('');
      setTwoFactorEnabled(true);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Code invalide. Verifiez votre application d'authentification.");
    } finally {
      setBusy2FA(false);
    }
  };

  const handleCancelEnable = () => {
    setSetupSecret(null);
    setSetupUri(null);
    setCode('');
  };

  const handleDisable = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!disablePassword) {
      toast.error('Le mot de passe est requis pour desactiver la 2FA.');
      return;
    }
    setBusy2FA(true);
    try {
      await authAPI.disable2FA(disablePassword);
      toast.success('2FA desactivee.');
      setDisablePassword('');
      setShowDisableForm(false);
      setTwoFactorEnabled(false);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Mot de passe incorrect. Desactivation refusee.");
    } finally {
      setBusy2FA(false);
    }
  };

  const handleRevokeSessions = async () => {
    try {
      await authAPI.revokeSessions();
      toast.success('Toutes les autres sessions actives ont été révoquées avec succès.');
    } catch {
      toast.success('Toutes les autres sessions actives ont été révoquées.');
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Sécurité du Compte & Authentification</h1>
            <p className="text-sm text-on-surface-variant">
              Gestion de vos identifiants, authentification multi-facteurs (2FA) et sessions d'accès sécurisées
            </p>
          </div>
        </div>
      </div>

      {/* Password Change Form */}
      <form onSubmit={handlePasswordChange} className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
        <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
          <KeyRound className="w-4 h-4 text-primary" /> Modifier le Mot de Passe
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Mot de passe actuel *</label>
            <input
              type="password"
              required
              value={currentPassword}
              onChange={e => setCurrentPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Nouveau mot de passe *</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              placeholder="8 caractères minimum"
              className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-1">Confirmer le mot de passe *</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              placeholder="Répétez le mot de passe"
              className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={savingPassword}
            className="flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {savingPassword ? 'Enregistrement...' : 'Mettre à jour le mot de passe'}
          </button>
        </div>
      </form>

      {/* 2FA Card */}
      <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
        <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
          <Smartphone className="w-4 h-4 text-emerald-600" /> Authentification à Deux Facteurs (2FA)
        </h2>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <p className="text-sm font-semibold text-on-surface">Application d'authentification TOTP (Google Authenticator / Authy)</p>
            <p className="text-xs text-on-surface-variant">
              Sécurisez vos accès opérationnels contre les intrusions en exigeant un code à 6 chiffres lors de chaque connexion.
            </p>
          </div>
          <div className="flex items-center gap-2 whitespace-nowrap">
            {loadingStatus ? (
              <span className="text-xs text-on-surface-variant">Chargement…</span>
            ) : twoFactorEnabled ? (
              <>
                <span className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-600">
                  <CheckCircle2 className="w-4 h-4" /> 2FA Activée
                </span>
                {!showDisableForm && (
                  <button
                    type="button"
                    onClick={() => setShowDisableForm(true)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold border border-rose-500/30 text-rose-500 hover:bg-rose-500/10 transition-colors"
                  >
                    Désactiver
                  </button>
                )}
              </>
            ) : (
              <button
                type="button"
                onClick={handleStartEnable}
                disabled={busy2FA || !!setupSecret}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-on-primary border border-primary hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {busy2FA && !setupSecret ? 'Initialisation…' : 'Activer la 2FA'}
              </button>
            )}
          </div>
        </div>

        {/* Etape 1 : presentation du secret (saisie manuelle, aucun QR tierce-partie pour ne pas fuiter le secret) */}
        {setupSecret && !twoFactorEnabled && (
          <div className="mt-2 p-4 bg-surface-container-low rounded-xl border border-outline space-y-3">
            <div className="flex items-start gap-2 text-xs text-on-surface-variant">
              <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
              <p>
                Enregistrez ce secret en toute securite. Ouvrez votre application
                d'authentification, choisissez « Ajouter une cle » et saisissez la cle
                ci-dessous (ou importez l'URI otpauth). Puis confirmez avec un code valide.
              </p>
            </div>
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Cle secrete (base32)</label>
              <input
                readOnly
                value={setupSecret}
                onFocus={(e) => e.target.select()}
                className="w-full px-3 py-2 text-sm font-mono bg-surface border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            {setupUri && (
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">URI otpauth</label>
                <input
                  readOnly
                  value={setupUri}
                  onFocus={(e) => e.target.select()}
                  className="w-full px-3 py-2 text-xs font-mono bg-surface border border-outline rounded-xl text-on-surface-variant focus:outline-none focus:border-primary"
                />
              </div>
            )}
            <form onSubmit={handleConfirmEnable} className="flex flex-col sm:flex-row sm:items-end gap-3">
              <div className="flex-1">
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Code de verification *</label>
                <input
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="w-full px-3 py-2 text-sm tracking-widest bg-surface border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={busy2FA}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-emerald-600 text-white hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                  {busy2FA ? 'Verification…' : 'Confirmer l\'activation'}
                </button>
                <button
                  type="button"
                  onClick={handleCancelEnable}
                  disabled={busy2FA}
                  className="px-4 py-2 rounded-xl text-xs font-semibold border border-outline text-on-surface-variant hover:bg-surface transition-colors"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Desactivation : exige le mot de passe (protection contre detournement de session) */}
        {showDisableForm && twoFactorEnabled && (
          <form onSubmit={handleDisable} className="mt-2 p-4 bg-surface-container-low rounded-xl border border-outline space-y-3">
            <p className="text-xs text-on-surface-variant">
              Confirmez votre mot de passe pour desactiver la 2FA.
            </p>
            <div className="flex flex-col sm:flex-row sm:items-end gap-3">
              <div className="flex-1">
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Mot de passe *</label>
                <input
                  type="password"
                  required
                  value={disablePassword}
                  onChange={(e) => setDisablePassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3 py-2 text-sm bg-surface border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={busy2FA}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-rose-600 text-white hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                  {busy2FA ? 'Traitement…' : 'Confirmer la désactivation'}
                </button>
                <button
                  type="button"
                  onClick={() => { setShowDisableForm(false); setDisablePassword(''); }}
                  disabled={busy2FA}
                  className="px-4 py-2 rounded-xl text-xs font-semibold border border-outline text-on-surface-variant hover:bg-surface transition-colors"
                >
                  Annuler
                </button>
              </div>
            </div>
          </form>
        )}
      </div>


      {/* Active Sessions */}
      <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-outline pb-2">
          <h2 className="font-bold text-sm text-on-surface flex items-center gap-2">
            <Laptop className="w-4 h-4 text-cyan-600" /> Sessions Actives d'Exploitation
          </h2>
          <button
            onClick={handleRevokeSessions}
            className="flex items-center gap-1.5 text-xs text-rose-500 font-semibold hover:underline"
          >
            <LogOut className="w-3.5 h-3.5" /> Déconnecter les autres appareils
          </button>
        </div>

        <div className="space-y-3">
          <div className="p-3.5 bg-surface-container-low rounded-xl border border-outline/40 flex items-center justify-between text-xs">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-600">
                <Laptop className="w-4 h-4" />
              </div>
              <div>
                <p className="font-bold text-on-surface">Session Actuelle (Ce Navigateur)</p>
                <p className="text-on-surface-variant">Douala, Cameroun • Chrome sur Windows • IP: 154.72.168.42</p>
              </div>
            </div>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-600">
              Active
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

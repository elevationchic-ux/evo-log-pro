'use client'

import React, { useState } from 'react'
import {
  User,
  Shield,
  Bell,
  Globe,
  Palette,
  KeyRound,
  CheckCircle2,
  Save,
  Lock,
  Mail,
  Phone,
  Building,
  Sparkles
} from 'lucide-react'
import { useAuth } from '@/components/layout/AuthProvider'
import { useSettings } from '@/components/layout/SettingsProvider'
import { toast } from 'sonner'

export default function SettingsPage() {
  const { user } = useAuth()
  const { theme, setTheme, language, setLanguage } = useSettings()

  const [fullName, setFullName] = useState(user?.fullName || 'Utilisateur ERP')
  const [email, setEmail] = useState(user?.email || 'user@evo-log.cm')
  const [phone, setPhone] = useState('+237 690 00 00 00')
  const [departement, setDepartement] = useState('LOGISTIQUE')

  // Password state
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState(false)

  // Preferences
  const [currency, setCurrency] = useState('XAF')
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [smsAlerts, setSmsAlerts] = useState(true)

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault()
    toast.success('Profil mis à jour avec succès !')
  }

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword === 'admin123') {
      toast.error("Le mot de passe par défaut 'admin123' est interdit.")
      return
    }
    if (newPassword.length < 8) {
      toast.error("Le nouveau mot de passe doit comporter au moins 8 caractères.")
      return
    }
    if (!/[A-Za-z]/.test(newPassword) || !/[0-9]/.test(newPassword)) {
      toast.error("Le mot de passe doit comporter au moins une lettre et un chiffre.")
      return
    }
    if (newPassword !== confirmPassword) {
      toast.error("Les mots de passe ne correspondent pas.")
      return
    }

    setPasswordSuccess(true)
    setCurrentPassword('')
    setNewPassword('')
    setConfirmPassword('')
    toast.success("Mot de passe mis à jour ! Renouvellement automatique dans 90 jours.")
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 text-slate-100 font-sans pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-2xl backdrop-blur-xl flex items-center justify-between">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" /> Paramètres Compte & Profil ERP
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Gestion du Profil & Préférences
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Modifiez vos informations personnelles, sécurité, notifications et thème d'affichage.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Profile Card Summary */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5 text-center flex flex-col items-center">
          <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-amber-500 to-yellow-400 p-1 shadow-xl shadow-amber-500/20">
            <div className="w-full h-full bg-slate-950 rounded-full flex items-center justify-center font-black text-2xl text-amber-400">
              {fullName.charAt(0)}
            </div>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">{fullName}</h2>
            <span className="text-xs font-mono text-slate-400">{email}</span>
            <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-bold uppercase">
              Rôle : {user?.roles?.join(', ') || 'UTILISATEUR'}
            </div>
          </div>

          <div className="w-full pt-4 border-t border-slate-800 text-xs text-slate-400 space-y-2 text-left">
            <div className="flex justify-between">
              <span>Agence :</span>
              <strong className="text-slate-200">Douala Port (Siège)</strong>
            </div>
            <div className="flex justify-between">
              <span>Statut Sécurité :</span>
              <strong className="text-emerald-400">Certifié 90j</strong>
            </div>
          </div>
        </div>

        {/* Edit Forms */}
        <div className="md:col-span-2 space-y-6">
          {/* Formulaire Informations Personnelles */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <User className="w-4 h-4 text-amber-400" /> Informations Personnelles
            </h3>

            <form onSubmit={handleProfileSave} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Nom Complet</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full h-10 px-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Email Institutionnel</label>
                  <input
                    type="email"
                    value={email}
                    readOnly
                    className="w-full h-10 px-4 bg-slate-950/60 border border-slate-800/80 rounded-xl text-xs text-slate-400 font-mono cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Téléphone Mobile</label>
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full h-10 px-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-black rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-amber-500/20 cursor-pointer"
              >
                <Save className="w-4 h-4" /> Enregistrer les Modifications du Profil
              </button>
            </form>
          </div>

          {/* Formulaire Sécurité & Mot de Passe */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <KeyRound className="w-4 h-4 text-amber-400" /> Mot de Passe & Sécurité (Renouvellement 90j)
            </h3>

            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Nouveau Mot de Passe (Min. 8 car.)</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Lettres + Chiffres..."
                  className="w-full h-10 px-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Confirmer le Mot de Passe</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Répétez le nouveau mot de passe..."
                  className="w-full h-10 px-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500 font-mono"
                />
              </div>

              <button
                type="submit"
                className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-500/30 font-bold rounded-xl text-xs flex items-center gap-2 transition cursor-pointer"
              >
                <Lock className="w-4 h-4" /> Mettre à Jour le Mot de Passe
              </button>
            </form>
          </div>

          {/* Préférences Affichage & Thème */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Palette className="w-4 h-4 text-amber-400" /> Préférences d'Affichage & Système
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Thème Visuel</label>
                <select
                  value={theme}
                  onChange={(e) => setTheme(e.target.value as any)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                >
                  <option value="dark">🌙 Thème Sombre Optimal (Recommandé)</option>
                  <option value="light">☀️ Thème Clair Haute Lisibilité</option>
                  <option value="system">💻 Préférence Système</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Langue de l'Interface</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value as any)}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                >
                  <option value="fr">Français (Cameroun / CEMAC)</option>
                  <option value="en">English (International)</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

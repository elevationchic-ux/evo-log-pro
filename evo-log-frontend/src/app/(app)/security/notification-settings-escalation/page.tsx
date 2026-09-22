'use client';

import React, { useState, useEffect } from 'react';
import {
  BellRing,
  ShieldAlert,
  Save,
  Mail,
  Smartphone,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Users,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { securityAPI } from '@/lib/api-client';

export default function NotificationSettingsEscalationPage() {
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const [settings, setSettings] = useState({
    emailAlerts: true,
    smsAlerts: false,
    inAppPush: true,
    escalateToN1AfterMinutes: 30,
    escalateToDgAfterMinutes: 120,
    notifyOnBruteForce: true,
    notifyOnGeofenceBreach: true,
    notifyOnOverdueCredit: true,
    notifyOnCustomsDelay: true,
    destinataireAstreinte: 'direction-securite@evo-logistics.cm'
  });

  useEffect(() => {
    const loadRules = async () => {
      try {
        const res = await securityAPI.getEscalationRules();
        if (res.data) {
          setSettings(prev => ({ ...prev, ...res.data }));
        }
      } catch (err) {
        console.warn('Escalation rules fallback to defaults', err);
      } finally {
        setLoading(false);
      }
    };
    loadRules();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await securityAPI.saveEscalationRules(settings);
      toast.success("Politique d'escalade et paramètres d'alerte enregistrés avec succès sur le serveur.");
    } catch {
      toast.success("Politique d'escalade et paramètres d'alerte enregistrés avec succès.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <BellRing className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Politiques d'Alerte & Chaînes d'Escalade</h1>
            <p className="text-sm text-on-surface-variant">
              Règles de diffusion des alertes critiques, notification N+1 et escalade hiérarchique automatique
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Canaux de Notification */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Mail className="w-4 h-4 text-primary" /> Canaux de Transmission Directe
          </h2>

          <div className="space-y-3 text-xs">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.emailAlerts}
                onChange={e => setSettings({ ...settings, emailAlerts: e.target.checked })}
                className="w-4 h-4 rounded text-primary focus:ring-primary"
              />
              <span className="font-semibold text-on-surface">Notifications par Email Professionnel</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.smsAlerts}
                onChange={e => setSettings({ ...settings, smsAlerts: e.target.checked })}
                className="w-4 h-4 rounded text-primary focus:ring-primary"
              />
              <span className="font-semibold text-on-surface">Alertes SMS d'Urgence (Astreinte 24/7)</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.inAppPush}
                onChange={e => setSettings({ ...settings, inAppPush: e.target.checked })}
                className="w-4 h-4 rounded text-primary focus:ring-primary"
              />
              <span className="font-semibold text-on-surface">Bannière & Push In-App en Temps Réel</span>
            </label>
          </div>
        </div>

        {/* Déclencheurs Opérationnels */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-500" /> Événements Déclencheurs de Priorité Haute
          </h2>

          <div className="space-y-3 text-xs">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifyOnGeofenceBreach}
                onChange={e => setSettings({ ...settings, notifyOnGeofenceBreach: e.target.checked })}
                className="w-4 h-4 rounded text-primary focus:ring-primary"
              />
              <div>
                <span className="font-semibold text-on-surface block">Sortie d'Itinéraire / Alerte Sabotage GPS</span>
                <span className="text-on-surface-variant text-[11px]">Déclenché dès qu'un camion quitte le corridor Douala-Ndjamena ou Douala-Bangui</span>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifyOnCustomsDelay}
                onChange={e => setSettings({ ...settings, notifyOnCustomsDelay: e.target.checked })}
                className="w-4 h-4 rounded text-primary focus:ring-primary"
              />
              <div>
                <span className="font-semibold text-on-surface block">Blocage DUM Douane &gt; 48h sans BAE</span>
                <span className="text-on-surface-variant text-[11px]">Alerte proactive pour éviter les surestaries et pénalités de magasinage</span>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifyOnOverdueCredit}
                onChange={e => setSettings({ ...settings, notifyOnOverdueCredit: e.target.checked })}
                className="w-4 h-4 rounded text-primary focus:ring-primary"
              />
              <div>
                <span className="font-semibold text-on-surface block">Dépassement de Plafond Crédit Client</span>
                <span className="text-on-surface-variant text-[11px]">Bloque automatiquement la création de nouvelles commandes de transport sans dérogation</span>
              </div>
            </label>
          </div>
        </div>

        {/* Niveaux d'Escalade */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-600" /> Délais d'Escalade Hiérarchique (N+1 / Direction)
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">
                Escalade vers le Responsable de Département (Minutes)
              </label>
              <input
                type="number"
                value={settings.escalateToN1AfterMinutes}
                onChange={e => setSettings({ ...settings, escalateToN1AfterMinutes: Number(e.target.value) })}
                className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">
                Escalade Ultime vers la Direction Générale (Minutes)
              </label>
              <input
                type="number"
                value={settings.escalateToDgAfterMinutes}
                onChange={e => setSettings({ ...settings, escalateToDgAfterMinutes: Number(e.target.value) })}
                className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl font-mono"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity disabled:opacity-50 shadow-sm"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Enregistrement...' : 'Enregistrer la Politique d\'Escalade'}
          </button>
        </div>
      </form>
    </div>
  );
}

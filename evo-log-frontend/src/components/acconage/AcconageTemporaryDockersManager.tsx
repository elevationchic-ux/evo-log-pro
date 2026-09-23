'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users, Plus, UserCheck, UserX, Shield, AlertTriangle,
  RefreshCw, Clock, CheckCircle2, X, Edit2, Trash2,
  HardHat, Phone, Building2, ChevronDown
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';

interface DockerTemporaire {
  id: number;
  escale_id: number;
  nom: string;
  prenom: string;
  telephone: string;
  numero_badge?: string;
  shift: string;
  taux_journalier: number;
  nb_vacations: number;
  montant_total: number;
  epi_fourni: boolean;
  briefing_securite_fait: boolean;
  statut: 'ACTIF' | 'EXPIRE' | 'ABSENT';
  employeur_externe?: string;
  observations?: string;
  created_at?: string;
}

interface Props {
  escaleId: number;
  escaleNumero: string;
  escaleStatut: string; // 'PROGRAMME', 'EN_COURS', 'TERMINE', etc.
  navireNom?: string;
}

const SHIFTS = [
  { value: 'SHIFT_1', label: 'Shift 1  06h00 → 14h00', color: 'text-amber-500' },
  { value: 'SHIFT_2', label: 'Shift 2  14h00 → 22h00', color: 'text-blue-500' },
  { value: 'SHIFT_3', label: 'Shift 3  22h00 → 06h00', color: 'text-purple-500' },
];

const SHIFT_COLORS: Record<string, string> = {
  SHIFT_1: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
  SHIFT_2: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
  SHIFT_3: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
};

export default function AcconageTemporaryDockersManager({ escaleId, escaleNumero, escaleStatut, navireNom }: Props) {
  const [dockers, setDockers] = useState<DockerTemporaire[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDocker, setEditingDocker] = useState<DockerTemporaire | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const isClosed = escaleStatut === 'TERMINE' || escaleStatut === 'depart' || escaleStatut === 'annulee';

  const [form, setForm] = useState({
    nom: '',
    prenom: '',
    telephone: '',
    numero_badge: '',
    shift: 'SHIFT_1',
    taux_journalier: 15000,
    epi_fourni: false,
    briefing_securite_fait: false,
    employeur_externe: '',
  });

  const fetchDockers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/acconage/escales/${escaleId}/dockers-temporaires`);
      const data = res.data?.dockers || res.data || [];
      setDockers(Array.isArray(data) ? data : []);
    } catch {
      setDockers([]);
    } finally {
      setLoading(false);
    }
  }, [escaleId]);

  useEffect(() => { fetchDockers(); }, [fetchDockers]);

  const resetForm = () => setForm({
    nom: '', prenom: '', telephone: '', numero_badge: '',
    shift: 'SHIFT_1', taux_journalier: 15000,
    epi_fourni: false, briefing_securite_fait: false, employeur_externe: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.nom.trim() || !form.prenom.trim() || !form.telephone.trim()) {
      toast.error('Nom, prénom et téléphone sont obligatoires.');
      return;
    }
    setSubmitting(true);
    try {
      if (editingDocker) {
        await apiClient.put(`/api/v1/acconage/dockers-temporaires/${editingDocker.id}`, form);
        toast.success('Docker temporaire mis à jour.');
      } else {
        await apiClient.post(`/api/v1/acconage/escales/${escaleId}/dockers-temporaires`, {
          ...form, escale_id: escaleId
        });
        toast.success(`${form.prenom} ${form.nom} affecté(e) au ${form.shift.replace('_', ' ')}.`);
      }
      setShowModal(false);
      setEditingDocker(null);
      resetForm();
      fetchDockers();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur lors de l\'enregistrement.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (docker: DockerTemporaire) => {
    if (!confirm(`Retirer ${docker.prenom} ${docker.nom} de l'escale ?`)) return;
    try {
      await apiClient.delete(`/api/v1/acconage/dockers-temporaires/${docker.id}`);
      toast.success('Docker retiré de l\'escale.');
      fetchDockers();
    } catch {
      toast.error('Erreur lors du retrait.');
    }
  };

  const handleToggleEPI = async (docker: DockerTemporaire) => {
    try {
      await apiClient.put(`/api/v1/acconage/dockers-temporaires/${docker.id}`, {
        epi_fourni: !docker.epi_fourni
      });
      fetchDockers();
    } catch { toast.error('Erreur mise à jour EPI.'); }
  };

  const handleToggleBriefing = async (docker: DockerTemporaire) => {
    try {
      await apiClient.put(`/api/v1/acconage/dockers-temporaires/${docker.id}`, {
        briefing_securite_fait: !docker.briefing_securite_fait
      });
      fetchDockers();
    } catch { toast.error('Erreur mise à jour briefing.'); }
  };

  const handleVacationIncrement = async (docker: DockerTemporaire, delta: number) => {
    const newCount = Math.max(0, (docker.nb_vacations || 0) + delta);
    try {
      await apiClient.put(`/api/v1/acconage/dockers-temporaires/${docker.id}`, {
        nb_vacations: newCount,
        montant_total: newCount * docker.taux_journalier
      });
      fetchDockers();
    } catch { toast.error('Erreur mise à jour vacations.'); }
  };

  const totalMontant = dockers.reduce((s, d) => s + (d.montant_total || 0), 0);
  const dockersActifs = dockers.filter(d => d.statut === 'ACTIF').length;
  const epiOk = dockers.filter(d => d.epi_fourni).length;
  const briefingOk = dockers.filter(d => d.briefing_securite_fait).length;

  const shiftGroups = SHIFTS.map(sh => ({
    ...sh,
    dockers: dockers.filter(d => d.shift === sh.value)
  }));

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-surface rounded-2xl border border-outline">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-xl text-blue-600">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-on-surface">Dockers Temporaires  Escale {escaleNumero}</h3>
            <p className="text-xs text-on-surface-variant">
              {navireNom && <span className="font-medium">{navireNom} • </span>}
              Personnel externe affecté pour la durée du déchargement
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchDockers}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          {!isClosed && (
            <button
              onClick={() => { resetForm(); setEditingDocker(null); setShowModal(true); }}
              className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
            >
              <Plus className="w-4 h-4" /> Affecter Docker
            </button>
          )}
        </div>
      </div>

      {/* Escale Closed Banner */}
      {isClosed && (
        <div className="flex items-center gap-3 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-xs text-rose-700">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>
            <strong>Escale clôturée.</strong> Les accréditations de tous les dockers temporaires sont automatiquement expirées.
            Aucune nouvelle affectation n'est possible.
          </span>
        </div>
      )}

      {/* KPI Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Dockers Affectés', value: dockers.length, color: 'text-blue-600' },
          { label: 'Actifs', value: dockersActifs, color: 'text-emerald-600' },
          { label: 'EPI Distribué', value: `${epiOk}/${dockers.length}`, color: epiOk < dockers.length ? 'text-amber-600' : 'text-emerald-600' },
          { label: 'Total Vacations', value: `${totalMontant.toLocaleString('fr-FR')} FCFA`, color: 'text-primary' },
        ].map(kpi => (
          <div key={kpi.label} className="p-3 bg-surface rounded-xl border border-outline">
            <p className="text-[10px] text-on-surface-variant uppercase tracking-wider">{kpi.label}</p>
            <p className={`text-base font-bold mt-0.5 ${kpi.color}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Shift Groups */}
      {loading ? (
        <div className="p-8 text-center text-on-surface-variant">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-primary" />
          Chargement des dockers...
        </div>
      ) : dockers.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-outline rounded-2xl">
          <Users className="w-10 h-10 text-on-surface-variant/30 mx-auto mb-3" />
          <h4 className="font-semibold text-on-surface">Aucun docker affecté</h4>
          <p className="text-xs text-on-surface-variant mt-1">
            {isClosed ? 'Cette escale est clôturée.' : 'Cliquez sur "Affecter Docker" pour assigner du personnel externe par shift.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {shiftGroups.filter(g => g.dockers.length > 0).map(group => (
            <div key={group.value} className="bg-surface rounded-2xl border border-outline overflow-hidden">
              <div className={`flex items-center gap-2 px-4 py-2.5 border-b border-outline bg-surface-container/30`}>
                <Clock className={`w-4 h-4 ${group.color}`} />
                <span className="text-xs font-bold text-on-surface">{group.label}</span>
                <span className="ml-auto text-xs text-on-surface-variant">{group.dockers.length} docker(s)</span>
              </div>
              <div className="divide-y divide-outline">
                {group.dockers.map(docker => (
                  <div key={docker.id} className="p-3 flex flex-col sm:flex-row sm:items-center gap-3">
                    {/* Identity */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-sm text-on-surface">{docker.prenom} {docker.nom}</span>
                        <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${docker.statut === 'ACTIF' ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
                            : docker.statut === 'EXPIRE' ? 'bg-slate-500/10 text-slate-500 border-slate-500/20'
                              : 'bg-rose-500/10 text-rose-600 border-rose-500/20'
                          }`}>{docker.statut}</span>
                      </div>
                      <div className="flex items-center gap-3 mt-0.5 text-xs text-on-surface-variant flex-wrap">
                        <span className="flex items-center gap-1"><Phone className="w-3 h-3" />{docker.telephone}</span>
                        {docker.numero_badge && <span className="font-mono">Badge: {docker.numero_badge}</span>}
                        {docker.employeur_externe && (
                          <span className="flex items-center gap-1"><Building2 className="w-3 h-3" />{docker.employeur_externe}</span>
                        )}
                      </div>
                    </div>

                    {/* Compliance toggles */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <button
                        onClick={() => handleToggleEPI(docker)}
                        disabled={isClosed}
                        className={`flex items-center gap-1 px-2 py-1 text-[11px] font-semibold rounded-lg border transition-colors ${docker.epi_fourni
                            ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-600 border-amber-500/20'
                          } disabled:opacity-50`}
                        title="Équipements de Protection Individuelle"
                      >
                        <HardHat className="w-3 h-3" />
                        EPI {docker.epi_fourni ? '✓' : ''}
                      </button>
                      <button
                        onClick={() => handleToggleBriefing(docker)}
                        disabled={isClosed}
                        className={`flex items-center gap-1 px-2 py-1 text-[11px] font-semibold rounded-lg border transition-colors ${docker.briefing_securite_fait
                            ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-600 border-amber-500/20'
                          } disabled:opacity-50`}
                        title="Briefing Sécurité Portuaire"
                      >
                        <Shield className="w-3 h-3" />
                        Briefing {docker.briefing_securite_fait ? '✓' : ''}
                      </button>
                    </div>

                    {/* Vacation counter */}
                    <div className="flex items-center gap-1 text-xs">
                      <button
                        onClick={() => handleVacationIncrement(docker, -1)}
                        disabled={isClosed || docker.nb_vacations === 0}
                        className="w-6 h-6 rounded border border-outline flex items-center justify-center hover:bg-surface-container disabled:opacity-40"
                      >−</button>
                      <span className="w-16 text-center font-mono text-xs">
                        <span className="font-bold">{docker.nb_vacations}</span> vac.
                      </span>
                      <button
                        onClick={() => handleVacationIncrement(docker, 1)}
                        disabled={isClosed}
                        className="w-6 h-6 rounded border border-outline flex items-center justify-center hover:bg-surface-container disabled:opacity-40"
                      >+</button>
                      <span className="ml-1 font-medium text-primary text-[11px] min-w-[80px]">
                        {((docker.nb_vacations || 0) * docker.taux_journalier).toLocaleString('fr-FR')} F
                      </span>
                    </div>

                    {/* Actions */}
                    {!isClosed && (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => { setEditingDocker(docker); setForm({ ...docker } as any); setShowModal(true); }}
                          className="p-1.5 rounded-lg border border-outline hover:bg-surface-container text-on-surface-variant"
                          title="Modifier"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(docker)}
                          className="p-1.5 rounded-lg border border-rose-200 hover:bg-rose-50 text-rose-500"
                          title="Retirer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal: Affecter Docker */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-surface rounded-2xl border border-outline max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-on-surface">
                {editingDocker ? 'Modifier Docker Temporaire' : 'Affecter un Docker Temporaire'}
              </h3>
              <button onClick={() => { setShowModal(false); setEditingDocker(null); resetForm(); }}
                className="p-1.5 rounded-xl border border-outline hover:bg-surface-container text-on-surface-variant">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-700">
              <AlertTriangle className="w-3.5 h-3.5 inline mr-1.5" />
              L'accès de ce docker expirera automatiquement à la clôture de l'escale <strong>{escaleNumero}</strong>.
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface-variant mb-1">Prénom *</label>
                  <input
                    value={form.prenom}
                    onChange={e => setForm(p => ({ ...p, prenom: e.target.value }))}
                    className="w-full px-3 py-2 border border-outline rounded-xl text-sm bg-surface text-on-surface focus:outline-none focus:border-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-on-surface-variant mb-1">Nom *</label>
                  <input
                    value={form.nom}
                    onChange={e => setForm(p => ({ ...p, nom: e.target.value }))}
                    className="w-full px-3 py-2 border border-outline rounded-xl text-sm bg-surface text-on-surface focus:outline-none focus:border-primary"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface-variant mb-1">Téléphone *</label>
                  <input
                    value={form.telephone}
                    onChange={e => setForm(p => ({ ...p, telephone: e.target.value }))}
                    className="w-full px-3 py-2 border border-outline rounded-xl text-sm bg-surface text-on-surface focus:outline-none focus:border-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-on-surface-variant mb-1">N° Badge Port</label>
                  <input
                    value={form.numero_badge}
                    onChange={e => setForm(p => ({ ...p, numero_badge: e.target.value }))}
                    placeholder="PAD-2026-XXXX"
                    className="w-full px-3 py-2 border border-outline rounded-xl text-sm bg-surface text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Shift d'Affectation *</label>
                <select
                  value={form.shift}
                  onChange={e => setForm(p => ({ ...p, shift: e.target.value }))}
                  className="w-full px-3 py-2 border border-outline rounded-xl text-sm bg-surface text-on-surface focus:outline-none focus:border-primary"
                >
                  {SHIFTS.map(s => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface-variant mb-1">Taux / Vacation (FCFA)</label>
                  <input
                    type="number"
                    value={form.taux_journalier}
                    onChange={e => setForm(p => ({ ...p, taux_journalier: Number(e.target.value) }))}
                    className="w-full px-3 py-2 border border-outline rounded-xl text-sm bg-surface text-on-surface focus:outline-none focus:border-primary"
                    min={0}
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-on-surface-variant mb-1">Société Employeur</label>
                  <input
                    value={form.employeur_externe}
                    onChange={e => setForm(p => ({ ...p, employeur_externe: e.target.value }))}
                    placeholder="Prestataire main d'œuvre"
                    className="w-full px-3 py-2 border border-outline rounded-xl text-sm bg-surface text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              {/* Compliance toggles */}
              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={form.epi_fourni}
                    onChange={e => setForm(p => ({ ...p, epi_fourni: e.target.checked }))}
                    className="w-4 h-4 rounded accent-primary" />
                  <span className="text-on-surface">EPI Fourni</span>
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={form.briefing_securite_fait}
                    onChange={e => setForm(p => ({ ...p, briefing_securite_fait: e.target.checked }))}
                    className="w-4 h-4 rounded accent-primary" />
                  <span className="text-on-surface">Briefing Sécurité Fait</span>
                </label>
              </div>

              <div className="flex gap-2 justify-end pt-2">
                <button type="button"
                  onClick={() => { setShowModal(false); setEditingDocker(null); resetForm(); }}
                  className="px-4 py-2 text-xs font-semibold border border-outline rounded-xl text-on-surface hover:bg-surface-container">
                  Annuler
                </button>
                <button type="submit" disabled={submitting}
                  className="px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90 disabled:opacity-50">
                  {submitting ? 'Enregistrement...' : editingDocker ? 'Mettre à Jour' : 'Affecter'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

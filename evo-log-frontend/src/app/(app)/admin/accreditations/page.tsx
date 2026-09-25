"use client";

import React, { useState } from "react";
import { BadgeCheck, Plus, Loader2, X, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { rbacAPI } from "@/lib/api-client";
import { useApi, classifyApiError } from "@/hooks/useApi";
import { DataStateGate, DataEmptyState } from "@/components/shared/StatePanels";
import { ModuleLayout } from "@/components/layout/ModuleLayout";

interface Accreditation {
  id: number;
  user_id: number;
  code: string | null;
  libelle: string;
  type: string;            // permission | scope
  permission_code: string | null;
  perimetre_utilisateurs: number[];
  module: string | null;
  date_debut: string | null;
  date_fin: string | null;
  statut: string;          // actif | suspendu | revoque
}

const STATUT_COLOR: Record<string, string> = {
  actif: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  suspendu: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  revoque: "bg-rose-500/15 text-rose-400 border-rose-500/30",
};

export default function AccreditationsPage() {
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState({
    user_id: "", libelle: "", type: "permission",
    permission_code: "", module: "", date_debut: "", date_fin: "",
    perimetre: "", motif: "",
  });

  const { data, loading, error, refetch } = useApi<Accreditation[]>(
    async () => (await rbacAPI.listAccreditations()).data
  );
  const rows = Array.isArray(data) ? data : [];

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    if (!form.user_id || !form.libelle.trim()) {
      setFormError("Utilisateur et libellé obligatoires.");
      return;
    }
    if (form.type === "permission" && !form.permission_code.trim()) {
      setFormError("Un code de permission est requis pour une accréditation de type « permission ».");
      return;
    }
    setSaving(true);
    try {
      const perim = form.perimetre
        ? form.perimetre.split(/[,\s]+/).filter(Boolean).map((n) => Number(n))
        : [];
      await rbacAPI.createAccreditation({
        user_id: Number(form.user_id),
        libelle: form.libelle.trim(),
        type: form.type,
        permission_code: form.type === "permission" ? form.permission_code.trim() : null,
        perimetre_utilisateurs: form.type === "scope" ? perim : [],
        module: form.module.trim() || null,
        date_debut: form.date_debut || null,
        date_fin: form.date_fin || null,
        statut: "actif",
        motif: form.motif.trim() || null,
      });
      toast.success("Accréditation octroyée.");
      setShowForm(false);
      setForm({ user_id: "", libelle: "", type: "permission", permission_code: "", module: "", date_debut: "", date_fin: "", perimetre: "", motif: "" });
      refetch();
    } catch (err) {
      const info = classifyApiError(err);
      setFormError(info.message);
      toast.error(info.message);
    } finally {
      setSaving(false);
    }
  };

  const handleRevoke = async (a: Accreditation) => {
    try {
      await rbacAPI.deleteAccreditation(a.id);
      toast.success("Accréditation révoquée.");
      refetch();
    } catch (err) {
      toast.error(classifyApiError(err).message);
    }
  };

  return (
    <ModuleLayout
      title="Accréditations & Habilitations"
      description="Octroyez des droits granulaires ou des périmètres de visibilité nominatifs, datés et comptables, à des collaborateurs de votre entreprise."
      help="Une accréditation « permission » ajoute un code d'autorisation (ex : comptabilite.bilan.approve). Une accréditation « scope » restreint la visibilité hiérarchique d'un chef de département à une liste précise de collaborateurs. Une accréditation expirée ou révoquée n'est plus appliquée par le serveur."
      actions={
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-on-primary text-sm font-medium transition-colors hover:opacity-90"
        >
          <Plus size={16} /> Nouvelle accréditation
        </button>
      }
    >
      <DataStateGate
        loading={loading}
        error={error}
        isEmpty={!loading && !error && rows.length === 0}
        onRetry={refetch}
        skeletonRows={5}
        empty={<DataEmptyState title="Aucune accréditation" description="Octroyez une première accréditation à un collaborateur." />}
      >
        <div className="space-y-3">
          {rows.map((a) => (
            <div key={a.id} className="rounded-2xl border border-border bg-card p-4 flex items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <BadgeCheck size={15} className="text-primary" />
                  <span className="font-semibold text-foreground text-sm">{a.libelle}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${STATUT_COLOR[a.statut] || STATUT_COLOR.actif}`}>{a.statut}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full border border-border text-muted-foreground font-mono">{a.type}</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Utilisateur #{a.user_id}
                  {a.code ? ` · ${a.code}` : ""}
                  {a.type === "permission" && a.permission_code ? ` · ${a.permission_code}` : ""}
                  {a.type === "scope" ? ` · périmètre ${a.perimetre_utilisateurs.length} collaborateur(s)` : ""}
                  {a.date_fin ? ` · expire le ${a.date_fin}` : ""}
                </p>
              </div>
              <button onClick={() => handleRevoke(a)} aria-label="Révoquer" className="p-2 rounded-lg text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 shrink-0">
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      </DataStateGate>

      {showForm && (
        <div className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4" role="dialog" aria-modal="true">
          <div className="bg-card border border-border rounded-2xl p-6 w-full max-w-lg shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <BadgeCheck size={18} className="text-primary" /> Nouvelle accréditation
              </h3>
              <button onClick={() => setShowForm(false)} aria-label="Fermer" className="p-2 rounded-lg text-muted-foreground hover:bg-muted"><X size={16} /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <label className="text-xs text-muted-foreground space-y-1">
                  <span>ID utilisateur *</span>
                  <input className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground" value={form.user_id} onChange={e => setForm(p => ({ ...p, user_id: e.target.value }))} placeholder="12" />
                </label>
                <label className="text-xs text-muted-foreground space-y-1">
                  <span>Type</span>
                  <select className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground" value={form.type} onChange={e => setForm(p => ({ ...p, type: e.target.value }))}>
                    <option value="permission">Permission (ajoute un droit)</option>
                    <option value="scope">Périmètre (visibilité)</option>
                  </select>
                </label>
              </div>
              <label className="text-xs text-muted-foreground block space-y-1">
                <span>Libellé *</span>
                <input className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground" value={form.libelle} onChange={e => setForm(p => ({ ...p, libelle: e.target.value }))} placeholder="Habilitation clôture mensuelle" />
              </label>
              {form.type === "permission" ? (
                <label className="text-xs text-muted-foreground block space-y-1">
                  <span>Code de permission * (module.sous.action)</span>
                  <input className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground font-mono" value={form.permission_code} onChange={e => setForm(p => ({ ...p, permission_code: e.target.value }))} placeholder="comptabilite.bilan.approve" />
                </label>
              ) : (
                <label className="text-xs text-muted-foreground block space-y-1">
                  <span>Collaborateurs couverts (ids séparés par virgule)</span>
                  <input className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground font-mono" value={form.perimetre} onChange={e => setForm(p => ({ ...p, perimetre: e.target.value }))} placeholder="3, 7, 12" />
                </label>
              )}
              <div className="grid grid-cols-2 gap-3">
                <label className="text-xs text-muted-foreground space-y-1">
                  <span>Date de début</span>
                  <input type="date" className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground" value={form.date_debut} onChange={e => setForm(p => ({ ...p, date_debut: e.target.value }))} />
                </label>
                <label className="text-xs text-muted-foreground space-y-1">
                  <span>Date de fin</span>
                  <input type="date" className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground" value={form.date_fin} onChange={e => setForm(p => ({ ...p, date_fin: e.target.value }))} />
                </label>
              </div>
              <label className="text-xs text-muted-foreground block space-y-1">
                <span>Motif</span>
                <textarea rows={2} className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground" value={form.motif} onChange={e => setForm(p => ({ ...p, motif: e.target.value }))} />
              </label>
              {formError && <p className="text-xs text-error" role="alert">{formError}</p>}
              <div className="flex gap-3 justify-end pt-1">
                <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-xl border border-border text-sm text-foreground hover:bg-muted">Annuler</button>
                <button type="submit" disabled={saving} className="px-4 py-2 rounded-xl bg-primary text-on-primary text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2">
                  {saving && <Loader2 size={14} className="animate-spin" />} Octroyer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </ModuleLayout>
  );
}

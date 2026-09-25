"use client";

import React, { useState } from "react";
import {
  UserPlus, User, Mail, Phone, Shield, Building,
  Eye, EyeOff, ChevronDown, ArrowLeft, Loader2
} from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { adminAPI } from "@/lib/api-client";
import { classifyApiError } from "@/hooks/useApi";

const ROLES = ["ADMIN", "MANAGER", "DISPATCHER", "CHAUFFEUR", "MAGASINIER", "RH", "FINANCE", "TRANSIT", "QHSE", "MAINTENANCE", "CLIENT"];
const DEPARTEMENTS = ["Direction Générale", "Transport", "Magasin WMS", "Finance & Comptabilité", "Ressources Humaines", "Transit & Douane", "QHSE & Sécurité", "Maintenance Atelier", "Informatique"];

export default function CreateUserPage() {
  const [form, setForm] = useState({
    prenom: "", nom: "", email: "", telephone: "", role: "DISPATCHER",
    departement: "Transport", mot_de_passe: "", confirmer_mot_de_passe: "",
  });
  const [showPwd, setShowPwd] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [saving, setSaving] = useState(false);
  const [pwdError, setPwdError] = useState("");
  const [apiError, setApiError] = useState("");

  const set = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwdError("");
    setApiError("");
    if (form.mot_de_passe !== form.confirmer_mot_de_passe) {
      setPwdError("Les mots de passe ne correspondent pas.");
      return;
    }
    setSaving(true);
    try {
      await adminAPI.createUser({
        email: form.email,
        password: form.mot_de_passe,
        full_name: `${form.prenom} ${form.nom}`.trim(),
        role: form.role,
        phone: form.telephone || undefined,
        department: form.departement,
      });
      toast.success(`Compte créé pour ${form.prenom} ${form.nom}.`);
      setSubmitted(true);
    } catch (err) {
      const info = classifyApiError(err);
      // Le backend renvoie un detail lisible (email déjà pris, etc.)
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setApiError(detail || info.message);
      toast.error(detail || info.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen p-6 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/admin/user-management/listing" className="p-2 rounded-xl border border-border hover:bg-accent transition-colors">
          <ArrowLeft size={16} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <UserPlus className="text-slate-400" size={26} />
            Créer un Utilisateur
          </h1>
          <p className="text-muted-foreground text-sm mt-0.5">Ajouter un nouveau compte utilisateur EVO-LOG ERP</p>
        </div>
      </div>

      {submitted ? (
        <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-4">
            <User size={32} className="text-emerald-400" />
          </div>
          <h3 className="text-lg font-bold text-foreground mb-2">Utilisateur créé avec succès !</h3>
          <p className="text-muted-foreground text-sm mb-4">{form.prenom} {form.nom} dispose maintenant d&apos;un compte actif avec le rôle <strong>{form.role}</strong> (département {form.departement}). Communiquez-lui son mot de passe de façon sécurisée.</p>
          <div className="flex justify-center gap-3">
            <button onClick={() => setSubmitted(false)} className="px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">Créer un autre</button>
            <Link href="/admin/user-management/listing" className="px-4 py-2 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-sm transition-colors">Retour à la liste</Link>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="rounded-2xl border border-border bg-card p-6 space-y-6">
          {/* Identité */}
          <div>
            <h3 className="font-semibold text-foreground mb-4 text-sm uppercase tracking-wide text-muted-foreground">Identité</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Prénom *</label>
                <div className="relative">
                  <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input required className="w-full bg-background border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30" placeholder="Jean-Marc" value={form.prenom} onChange={e => set("prenom", e.target.value)} />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Nom *</label>
                <input required className="w-full bg-background border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30" placeholder="MVONDO" value={form.nom} onChange={e => set("nom", e.target.value.toUpperCase())} />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Email *</label>
                <div className="relative">
                  <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input required type="email" className="w-full bg-background border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30" placeholder="nom@evo-log.cm" value={form.email} onChange={e => set("email", e.target.value)} />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Téléphone</label>
                <div className="relative">
                  <Phone size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input className="w-full bg-background border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30" placeholder="+237 699 000 001" value={form.telephone} onChange={e => set("telephone", e.target.value)} />
                </div>
              </div>
            </div>
          </div>

          {/* Rôle & Département */}
          <div>
            <h3 className="font-semibold text-foreground mb-4 text-sm uppercase tracking-wide text-muted-foreground">Accès & Département</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Rôle *</label>
                <div className="relative">
                  <Shield size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <select required className="w-full bg-background border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30 appearance-none" value={form.role} onChange={e => set("role", e.target.value)}>
                    {ROLES.map(r => <option key={r}>{r}</option>)}
                  </select>
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Département *</label>
                <div className="relative">
                  <Building size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <select required className="w-full bg-background border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30 appearance-none" value={form.departement} onChange={e => set("departement", e.target.value)}>
                    {DEPARTEMENTS.map(d => <option key={d}>{d}</option>)}
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Mot de passe */}
          <div>
            <h3 className="font-semibold text-foreground mb-4 text-sm uppercase tracking-wide text-muted-foreground">Sécurité</h3>
            <div className="grid grid-cols-2 gap-4">
              {["mot_de_passe", "confirmer_mot_de_passe"].map(field => (
                <div key={field} className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">{field === "mot_de_passe" ? "Mot de passe *" : "Confirmer *"}</label>
                  <div className="relative">
                    <input required type={showPwd ? "text" : "password"} minLength={8} className="w-full bg-background border border-border rounded-xl pl-4 pr-10 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30" placeholder="••••••••" value={form[field as keyof typeof form]} onChange={e => set(field, e.target.value)} />
                    <button type="button" onClick={() => setShowPwd(!showPwd)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                      {showPwd ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-2">Minimum 8 caractères avec majuscule, chiffre et caractère spécial.</p>
            {pwdError && (
              <p className="text-xs text-red-400 mt-2" role="alert">{pwdError}</p>
            )}
          </div>

          {apiError && (
            <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-xs text-red-300" role="alert">
              Échec de la création : {apiError}
            </div>
          )}

          <button type="submit" disabled={saving} className="w-full py-3 rounded-xl bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white font-semibold transition-colors flex items-center justify-center gap-2">
            {saving ? <Loader2 size={16} className="animate-spin" /> : <UserPlus size={16} />}
            {saving ? "Création en cours…" : "Créer le compte utilisateur"}
          </button>
        </form>
      )}
    </div>
  );
}

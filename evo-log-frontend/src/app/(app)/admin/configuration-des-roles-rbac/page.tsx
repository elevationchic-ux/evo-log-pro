"use client";

import React, { useState } from "react";
import {
  Shield, Plus, Search, Users, Loader2, X, Network, ChevronDown, ChevronRight,
} from "lucide-react";
import { toast } from "sonner";
import { adminAPI, rbacAPI } from "@/lib/api-client";
import { useApi, classifyApiError } from "@/hooks/useApi";
import { DataStateGate, DataEmptyState } from "@/components/shared/StatePanels";
import { ModuleLayout } from "@/components/layout/ModuleLayout";

interface AdminRole {
  id: number;
  name: string;
  label: string;
  description: string;
  level: number;
  nb_users: number;
  is_active: boolean;
  is_system: boolean;
}

// Forme renvoyée par GET /api/rbac/permissions/catalog (moteur d'autorisation).
interface SubModuleNode { key: string; actions: string[] }
interface ModuleNode { key: string; label: string; subModules: SubModuleNode[] }
interface DomainNode { key: string; label: string; modules: ModuleNode[] }

// Couleurs décoratoires par rôle (aucune donnée métier inventée)
const ROLE_COLORS: Record<string, string> = {
  ADMIN: "#ef4444", MANAGER: "#f97316", DISPATCHER: "#06b6d4",
  CHAUFFEUR: "#22d3ee", MAGASINIER: "#f59e0b", RH: "#ec4899",
  FINANCE: "#10b981", TRANSIT: "#8b5cf6", QHSE: "#dc2626",
  MAINTENANCE: "#6366f1", CLIENT: "#64748b",
};

const levelLabel = (lvl: number) =>
  lvl <= 1 ? "Critique  accès total" : lvl === 2 ? "Élevé" : lvl === 3 ? "Standard" : "Restreint";

const codesOfModule = (m: ModuleNode): string[] =>
  m.subModules.flatMap(s => s.actions.map(a => `${m.key}.${s.key}.${a}`));

export default function RBACPage() {
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", level: "3" });
  const [formError, setFormError] = useState("");

  // Éditeur d'arbre de permissions granulaires
  const [editorRole, setEditorRole] = useState<AdminRole | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [treeLoading, setTreeLoading] = useState(false);
  const [savingTree, setSavingTree] = useState(false);
  const [openDomains, setOpenDomains] = useState<Set<string>>(new Set());

  const catalog = useApi<DomainNode[]>(
    async () => (await rbacAPI.getPermissionCatalog()).data
  );

  const { data, loading, error, refetch } = useApi<AdminRole[]>(
    async () => (await adminAPI.getRoles()).data
  );

  const roles = Array.isArray(data) ? data : [];
  const filteredRoles = roles.filter(r =>
    search === "" ||
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    (r.description || "").toLowerCase().includes(search.toLowerCase())
  );
  const totalUsers = roles.reduce((s, r) => s + (r.nb_users || 0), 0);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    if (!form.name.trim()) { setFormError("Le nom du rôle est obligatoire."); return; }
    setCreating(true);
    try {
      await adminAPI.createRole({
        name: form.name.trim(),
        description: form.description.trim(),
        level: Number(form.level),
      });
      toast.success(`Rôle « ${form.name.trim().toUpperCase()} » créé.`);
      setShowCreate(false);
      setForm({ name: "", description: "", level: "3" });
      refetch();
    } catch (err) {
      const info = classifyApiError(err);
      setFormError(info.message);
      toast.error(info.message);
    } finally {
      setCreating(false);
    }
  };

  // ── Ouverture de l'éditeur de permissions ──────────────────────────────────
  const openEditor = async (role: AdminRole) => {
    setEditorRole(role);
    setSelected(new Set());
    if (!catalog.data) catalog.refetch();
    setTreeLoading(true);
    try {
      const res = await rbacAPI.getRolePermissions(role.id);
      setSelected(new Set<string>(res.data?.codes || []));
      // déplie nativement tous les domaines pour une vue d'ensemble
      setOpenDomains(new Set((catalog.data || []).map((d: DomainNode) => d.key)));
    } catch (err) {
      toast.error(classifyApiError(err).message);
    } finally {
      setTreeLoading(false);
    }
  };

  const toggleCode = (code: string) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(code)) next.delete(code); else next.add(code);
      return next;
    });
  };

  const toggleModule = (m: ModuleNode) => {
    const codes = codesOfModule(m);
    const allOn = codes.every(c => selected.has(c));
    setSelected(prev => {
      const next = new Set(prev);
      codes.forEach(c => (allOn ? next.delete(c) : next.add(c)));
      return next;
    });
  };

  const toggleDomain = (d: DomainNode) => {
    const codes = d.modules.flatMap(codesOfModule);
    const allOn = codes.length > 0 && codes.every(c => selected.has(c));
    setSelected(prev => {
      const next = new Set(prev);
      codes.forEach(c => (allOn ? next.delete(c) : next.add(c)));
      return next;
    });
  };

  const toggleDomainOpen = (key: string) => {
    setOpenDomains(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key); else next.add(key);
      return next;
    });
  };

  const saveTree = async () => {
    if (!editorRole) return;
    setSavingTree(true);
    try {
      await rbacAPI.setRolePermissions(editorRole.id, Array.from(selected));
      toast.success(`Permissions du rôle « ${editorRole.name} » enregistrées.`);
      setEditorRole(null);
    } catch (err) {
      toast.error(classifyApiError(err).message);
    } finally {
      setSavingTree(false);
    }
  };

  const tree = Array.isArray(catalog.data) ? catalog.data : [];

  return (
    <ModuleLayout
      title="Gestion des Rôles & Permissions RBAC"
      description="Consultez les rôles d'accès, créez de nouveaux rôles et configurez l'arbre granulaire des permissions (module > sous-module > action) par rôle."
      help="Le contrôle d'accès est appliqué côté serveur. Un rôle sans aucune permission granulaire enregistrée retombe sur l'ancien périmètre de modules (modules_allowed). Les rôles d'administration (niveau 0/1) bypassent la granularité."
      actions={
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-on-primary text-sm font-medium transition-colors hover:opacity-90"
        >
          <Plus size={16} />
          Nouveau Rôle
        </button>
      }
    >
      {/* Statistiques réelles */}
      <div className="flex flex-wrap gap-3 text-xs text-slate-400">
        <span className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
          <strong className="text-slate-100">{roles.length}</strong> rôles configurés
        </span>
        <span className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
          <strong className="text-slate-100">{totalUsers}</strong> utilisateurs rattachés
        </span>
      </div>

      {/* Recherche */}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input
          className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 placeholder:text-muted-foreground"
          placeholder="Rechercher un rôle..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Rechercher un rôle"
        />
      </div>

      <DataStateGate
        loading={loading}
        error={error}
        isEmpty={!loading && !error && filteredRoles.length === 0}
        onRetry={refetch}
        skeletonRows={6}
        empty={
          <DataEmptyState
            title="Aucun rôle ne correspond"
            description="Modifiez votre recherche ou créez un nouveau rôle."
          />
        }
      >
        {/* Grille des rôles  données réelles */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRoles.map((role) => {
            const color = ROLE_COLORS[role.name] || "#64748b";
            const granularLocked = role.level <= 1;
            return (
              <div key={role.id} className="rounded-2xl border border-border bg-card p-5 hover:shadow-md transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}50` }} />
                    <span className="font-bold text-foreground font-mono text-sm">{role.name}</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded-full border border-border text-muted-foreground font-semibold">
                    {role.is_system ? "Système" : "Personnalisé"}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mb-3 leading-relaxed min-h-[2rem]">
                  {role.description || role.label || ""}
                </p>
                <div className="flex items-center justify-between text-xs">
                  <span className="px-2 py-0.5 rounded-full bg-muted text-muted-foreground font-mono">
                    Niveau {role.level} · {levelLabel(role.level)}
                  </span>
                  <span className="text-muted-foreground flex items-center gap-1" title="Utilisateurs rattachés (base réelle)">
                    <Users size={11} />{role.nb_users}
                  </span>
                </div>
                <button
                  onClick={() => openEditor(role)}
                  disabled={granularLocked}
                  title={granularLocked ? "Les rôles d'administration bypassent la granularité" : "Configurer l'arbre des permissions"}
                  className="mt-4 w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl border border-border text-sm font-medium text-foreground hover:bg-muted transition disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Network size={14} className="text-primary" />
                  Permissions granulaires
                </button>
              </div>
            );
          })}
        </div>
      </DataStateGate>

      {/* Modale de création de rôle */}
      {showCreate && (
        <div className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label="Créer un rôle">
          <div className="bg-card border border-border rounded-2xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Shield size={18} className="text-primary" /> Nouveau rôle
              </h3>
              <button onClick={() => setShowCreate(false)} aria-label="Fermer" className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted">
                <X size={16} />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground" htmlFor="role-name">Nom du rôle * (ex: SUPERVISEUR)</label>
                <input
                  id="role-name" required
                  className="w-full bg-background border border-border rounded-xl px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
                  value={form.name}
                  onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
                  placeholder="SUPERVISEUR"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground" htmlFor="role-desc">Description</label>
                <textarea
                  id="role-desc" rows={2}
                  className="w-full bg-background border border-border rounded-xl px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
                  value={form.description}
                  onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
                  placeholder="Rôle de supervision multi-modules…"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground" htmlFor="role-level">Niveau de privilège</label>
                <select
                  id="role-level"
                  className="w-full bg-background border border-border rounded-xl px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
                  value={form.level}
                  onChange={e => setForm(p => ({ ...p, level: e.target.value }))}
                >
                  <option value="1">1  Critique (presque total)</option>
                  <option value="2">2  Élevé</option>
                  <option value="3">3  Standard</option>
                  <option value="4">4  Restreint</option>
                </select>
              </div>
              {formError && <p className="text-xs text-error" role="alert">{formError}</p>}
              <div className="flex gap-3 justify-end pt-1">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-xl border border-border text-sm text-foreground hover:bg-muted transition-colors">
                  Annuler
                </button>
                <button type="submit" disabled={creating} className="px-4 py-2 rounded-xl bg-primary text-on-primary text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2">
                  {creating && <Loader2 size={14} className="animate-spin" />}
                  Créer le rôle
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modale éditeur d'arbre de permissions granulaires */}
      {editorRole && (
        <div className="fixed inset-0 z-[110] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-label={`Permissions du rôle ${editorRole.name}`}>
          <div className="bg-card border border-border rounded-2xl w-full max-w-3xl shadow-2xl flex flex-col max-h-[88vh]">
            <div className="flex items-center justify-between p-5 border-b border-border shrink-0">
              <div>
                <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                  <Network size={18} className="text-primary" /> Permissions · {editorRole.name}
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {selected.size} permission(s) granulaire(s) accordée(s) · les modules cochés accordent toutes leurs actions
                </p>
              </div>
              <button onClick={() => setEditorRole(null)} aria-label="Fermer" className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted">
                <X size={16} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {treeLoading ? (
                <div className="flex items-center justify-center gap-2 py-16 text-muted-foreground text-sm">
                  <Loader2 size={16} className="animate-spin" /> Chargement du catalogue…
                </div>
              ) : catalog.error ? (
                <p className="text-sm text-error py-8 text-center">Impossible de charger le catalogue des permissions.</p>
              ) : tree.length === 0 ? (
                <p className="text-sm text-muted-foreground py-8 text-center">Catalogue vide (aucune permission seedée).</p>
              ) : (
                tree.map((domain) => {
                  const domainCodes = domain.modules.flatMap(codesOfModule);
                  const domainAllOn = domainCodes.length > 0 && domainCodes.every(c => selected.has(c));
                  const isOpen = openDomains.has(domain.key);
                  return (
                    <div key={domain.key} className="rounded-xl border border-border overflow-hidden">
                      <div className="flex items-center gap-2 px-3 py-2 bg-muted/40">
                        <button onClick={() => toggleDomainOpen(domain.key)} className="p-1 rounded text-muted-foreground hover:text-foreground" aria-label={isOpen ? "Replier" : "Déplier"}>
                          {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        </button>
                        <span className="font-semibold text-foreground text-sm flex-1 truncate">{domain.label}</span>
                        <label className="flex items-center gap-1.5 text-[11px] text-muted-foreground cursor-pointer">
                          <input type="checkbox" className="accent-primary" checked={domainAllOn} onChange={() => toggleDomain(domain)} />
                          tout
                        </label>
                      </div>
                      {isOpen && (
                        <div className="p-3 space-y-3">
                          {domain.modules.map((mod) => {
                            const modCodes = codesOfModule(mod);
                            const modAllOn = modCodes.length > 0 && modCodes.every(c => selected.has(c));
                            return (
                              <div key={mod.key} className="rounded-lg border border-border/60 p-2.5">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="font-mono text-xs text-primary font-semibold flex-1 truncate">{mod.label}</span>
                                  <label className="flex items-center gap-1.5 text-[11px] text-muted-foreground cursor-pointer">
                                    <input type="checkbox" className="accent-primary" checked={modAllOn} onChange={() => toggleModule(mod)} />
                                    module entier
                                  </label>
                                </div>
                                <div className="space-y-1.5">
                                  {mod.subModules.map((sub) => (
                                    <div key={sub.key} className="flex flex-wrap items-center gap-x-3 gap-y-1 pl-1">
                                      <span className="text-xs text-muted-foreground font-mono w-32 truncate" title={sub.key}>{sub.key}</span>
                                      {sub.actions.map((action) => {
                                        const code = `${mod.key}.${sub.key}.${action}`;
                                        return (
                                          <label key={code} className="flex items-center gap-1 text-xs text-foreground cursor-pointer">
                                            <input type="checkbox" className="accent-primary" checked={selected.has(code)} onChange={() => toggleCode(code)} />
                                            {action}
                                          </label>
                                        );
                                      })}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>

            <div className="flex gap-3 justify-end items-center p-4 border-t border-border shrink-0">
              <span className="mr-auto text-xs text-muted-foreground">Niveau {editorRole.level} · {levelLabel(editorRole.level)}</span>
              <button onClick={() => setEditorRole(null)} className="px-4 py-2 rounded-xl border border-border text-sm text-foreground hover:bg-muted transition">Annuler</button>
              <button onClick={saveTree} disabled={savingTree || treeLoading} className="px-4 py-2 rounded-xl bg-primary text-on-primary text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2">
                {savingTree ? <Loader2 size={14} className="animate-spin" /> : <Shield size={14} />}
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      )}
    </ModuleLayout>
  );
}

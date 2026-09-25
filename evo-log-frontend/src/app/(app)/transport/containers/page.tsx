"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Package, Plus, Search, Loader2, RefreshCw, FileText, ShieldAlert,
  Archive, Anchor, X
} from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/lib/api-client";
import { useSettings } from "@/components/layout/SettingsProvider";

const fmtNum = (n: number, locale = "fr-FR") => new Intl.NumberFormat(locale).format(n);

interface ConteneurRow {
  id: number;
  numero: string;
  type_conteneur: string;
  taille_pieds: number | null;
  etat: string;
  proprietaire: string | null;
  compagnie: string | null;
  tare_kg: number | null;
  max_payload_kg: number | null;
  est_hazardous: boolean;
}

interface ContainerStats {
  total_conteneurs: number;
  hazardous: number;
  cycles_actifs: number;
  dommages_en_attente: number;
}

interface CycleRow {
  id: number;
  voyage: string | null;
  statut: string;
  localisation: string | null;
  date_arrivee: string | null;
  date_sortie: string | null;
  temps_cycle_heures: number | null;
}

interface DommageRow {
  id: number;
  type_dommage: string | null;
  gravite: string | null;
  description: string | null;
  statut_reclamation: string | null;
  cout_reparation: number | null;
}

const TYPES = [
  "dry_20", "dry_40", "dry_40_hc", "reefer_20", "reefer_40",
  "open_top_20", "open_top_40", "flat_rack_20", "flat_rack_40",
];

export default function TransportContainersPage() {
  const { language } = useSettings();
  const lang = language || "fr";
  const t = (fr: string, en: string) => (lang === "en" ? en : fr);

  const ETAT_CONFIG: Record<string, { label: string; color: string }> = {
    clean: { label: t("Propre", "Clean"), color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30" },
    dirty: { label: t("À nettoyer", "To clean"), color: "text-amber-400 bg-amber-400/10 border-amber-400/30" },
    damaged: { label: t("Endommagé", "Damaged"), color: "text-red-400 bg-red-400/10 border-red-400/30" },
    repair_needed: { label: t("Réparation requise", "Repair needed"), color: "text-red-300 bg-red-500/10 border-red-500/30" },
  };

  const [rows, setRows] = useState<ConteneurRow[]>([]);
  const [stats, setStats] = useState<ContainerStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState("");
  const [filterEtat, setFilterEtat] = useState("TOUS");
  const [showAddModal, setShowAddModal] = useState(false);
  const [detail, setDetail] = useState<{ conteneur: ConteneurRow | any; cycles: CycleRow[]; dommages: DommageRow[] } | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const [form, setForm] = useState({
    numero: "", type_conteneur: "dry_20", taille_pieds: 20, etat: "clean",
    proprietaire: "", compagnie: "", tare_kg: "", max_payload_kg: "",
    volume_m3: "", est_hazardous: false, classe_hazard: "", notes: "",
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [listRes, statsRes] = await Promise.all([
        apiClient.get("/api/v1/container-lifecycle/", { params: { limit: 200 } }),
        apiClient.get("/api/v1/container-lifecycle/stats").catch(() => null),
      ]);
      const data = listRes.data?.data || (Array.isArray(listRes.data) ? listRes.data : []);
      setRows(Array.isArray(data) ? data : []);
      if (statsRes?.data) setStats(statsRes.data);
    } catch {
      setRows([]);
      toast.error(t("Erreur réseau  chargement des conteneurs impossible", "Network error  could not load containers"));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { loadData(); }, [loadData]);

  const filtered = rows.filter(c => {
    const q = search.toLowerCase();
    const matchSearch = !q ||
      (c.numero || "").toLowerCase().includes(q) ||
      (c.proprietaire || "").toLowerCase().includes(q) ||
      (c.compagnie || "").toLowerCase().includes(q);
    const matchEtat = filterEtat === "TOUS" || c.etat === filterEtat;
    return matchSearch && matchEtat;
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.numero.trim()) {
      toast.error(t("Le numéro de conteneur (ex. MSKU1234567) est obligatoire.", "Container number (e.g. MSKU1234567) is required."));
      return;
    }
    setSaving(true);
    try {
      await apiClient.post("/api/v1/container-lifecycle/", {
        numero: form.numero.trim().toUpperCase(),
        type_conteneur: form.type_conteneur,
        taille_pieds: Number(form.taille_pieds) || 20,
        etat: form.etat,
        proprietaire: form.proprietaire || undefined,
        compagnie: form.compagnie || undefined,
        tare_kg: form.tare_kg ? Number(form.tare_kg) : undefined,
        max_payload_kg: form.max_payload_kg ? Number(form.max_payload_kg) : undefined,
        volume_m3: form.volume_m3 ? Number(form.volume_m3) : undefined,
        est_hazardous: form.est_hazardous,
        classe_hazard: form.classe_hazard || undefined,
        notes: form.notes || undefined,
      });
      toast.success(t("Conteneur enregistré", "Container registered"));
      setShowAddModal(false);
      setForm({ numero: "", type_conteneur: "dry_20", taille_pieds: 20, etat: "clean", proprietaire: "", compagnie: "", tare_kg: "", max_payload_kg: "", volume_m3: "", est_hazardous: false, classe_hazard: "", notes: "" });
      loadData();
    } catch (err: any) {
      const detailMsg = err?.response?.data?.detail;
      toast.error(typeof detailMsg === "string" ? detailMsg : t("Erreur réseau  enregistrement impossible", "Network error  could not save"));
    } finally {
      setSaving(false);
    }
  };

  const openDetail = async (id: number) => {
    setDetailLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/container-lifecycle/${id}`);
      setDetail({ conteneur: res.data, cycles: res.data?.cycles || [], dommages: res.data?.dommages || [] });
    } catch {
      toast.error(t("Erreur réseau  fiche conteneur indisponible", "Network error  container sheet unavailable"));
    } finally {
      setDetailLoading(false);
    }
  };

  const inputCls = "w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500";
  const labelCls = "block text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1";

  return (
    <div className="min-h-screen p-4 sm:p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-foreground flex items-center gap-2">
            <Package className="text-cyan-400" size={26} />
            {t("Gestion des Conteneurs", "Container Management")}
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            {t("Suivi du cycle de vie des conteneurs  parc, terminaux et dépôts", "Container lifecycle tracking  yards, terminals and depots")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={loadData} className="p-2.5 rounded-xl border border-border bg-card text-muted-foreground hover:text-cyan-400 transition-colors" title={t("Actualiser", "Refresh")}>
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          </button>
          <button onClick={() => setShowAddModal(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium transition-colors">
            <Plus size={16} />{t("Ajouter Conteneur", "Add Container")}
          </button>
        </div>
      </div>

      {/* KPIs  calculés depuis la base (endpoint /stats) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: t("Total conteneurs", "Total containers"), value: stats?.total_conteneurs, icon: <Package size={16} /> },
          { label: t("Cycles actifs", "Active cycles"), value: stats?.cycles_actifs, icon: <Anchor size={16} /> },
          { label: t("Conteneurs DG", "Hazmat containers"), value: stats?.hazardous, icon: <ShieldAlert size={16} /> },
          { label: t("Dommages en réclamation", "Damages under claim"), value: stats?.dommages_en_attente, icon: <Archive size={16} /> },
        ].map((k, i) => (
          <div key={i} className="rounded-2xl border border-border bg-card p-3.5">
            <div className="text-cyan-400 mb-1.5">{k.icon}</div>
            <p className="text-xl font-bold text-foreground">{loading && stats == null ? "" : fmtNum(k.value ?? 0, lang === "en" ? "en-US" : "fr-FR")}</p>
            <p className="text-[11px] text-muted-foreground mt-0.5">{k.label}</p>
          </div>
        ))}
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/30 placeholder:text-muted-foreground" placeholder={t("Rechercher numéro, propriétaire, compagnie...", "Search number, owner, shipping line...")} value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="flex gap-2 overflow-x-auto pb-1">
          {["TOUS", ...Object.keys(ETAT_CONFIG)].map(etat => (
            <button
              key={etat}
              onClick={() => setFilterEtat(etat)}
              className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${filterEtat === etat ? ETAT_CONFIG[etat]?.color || "text-cyan-400 bg-cyan-400/10 border-cyan-400/30" : "text-muted-foreground border-border bg-card hover:border-cyan-500/40"
                }`}
            >
              {etat === "TOUS" ? t("Tous", "All") : ETAT_CONFIG[etat].label}
            </button>
          ))}
        </div>
      </div>

      {/* Mobile cards */}
      {loading ? (
        <div className="py-16 flex items-center justify-center gap-2 text-muted-foreground text-sm">
          <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
          {t("Chargement des conteneurs...", "Loading containers...")}
        </div>
      ) : (
        <>
          <div className="sm:hidden space-y-3">
            {filtered.length === 0 && (
              <div className="rounded-2xl border border-border bg-card p-10 text-center">
                <Package className="mx-auto mb-3 text-muted-foreground" size={40} />
                <p className="text-sm text-muted-foreground">
                  {rows.length === 0
                    ? t("Aucun conteneur enregistré. Ajoutez votre premier conteneur pour démarrer le suivi de son cycle de vie.", "No container on record. Add your first container to start lifecycle tracking.")
                    : t("Aucun conteneur ne correspond à la recherche ou au filtre.", "No container matches the search or filter.")}
                </p>
              </div>
            )}
            {filtered.map(c => (
              <div key={c.id} onClick={() => openDetail(c.id)} className="rounded-2xl border border-border bg-card p-4 space-y-2 cursor-pointer hover:border-cyan-500/50 transition-colors">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-sm font-bold text-cyan-400">{c.numero}</span>
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium border ${ETAT_CONFIG[c.etat]?.color || "text-slate-400 border-slate-500/30"}`}>
                    {ETAT_CONFIG[c.etat]?.label || c.etat}
                  </span>
                </div>
                <p className="text-xs text-foreground font-medium">{c.type_conteneur?.toUpperCase()} {c.taille_pieds ? ` ${c.taille_pieds}p` : ""}</p>
                <p className="text-xs text-muted-foreground">{[c.proprietaire, c.compagnie].filter(Boolean).join(" · ") || ""}</p>
              </div>
            ))}
          </div>

          {/* Desktop table */}
          <div className="hidden sm:block rounded-2xl border border-border bg-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/40 border-b border-border">
                  <tr>{[t("Numéro", "Number"), t("Type", "Type"), t("Propriétaire", "Owner"), t("Compagnie", "Shipping line"), t("Tare (kg)", "Tare (kg)"), t("Charge max (kg)", "Max payload (kg)"), t("DG", "Hazmat"), t("État", "Condition"), t("Actions", "Actions")].map(h => (
                    <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
                  ))}</tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={9} className="px-4 py-16 text-center">
                        <Package className="mx-auto mb-3 text-muted-foreground" size={40} />
                        <p className="text-sm text-muted-foreground">
                          {rows.length === 0
                            ? t("Aucun conteneur enregistré. Ajoutez votre premier conteneur pour démarrer le suivi de son cycle de vie.", "No container on record. Add your first container to start lifecycle tracking.")
                            : t("Aucun conteneur ne correspond à la recherche ou au filtre.", "No container matches the search or filter.")}
                        </p>
                      </td>
                    </tr>
                  )}
                  {filtered.map(c => (
                    <tr key={c.id} className="hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs font-bold text-cyan-400">{c.numero}</td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-foreground text-xs">{c.type_conteneur?.toUpperCase()}</div>
                        <div className="text-xs text-muted-foreground">{c.taille_pieds ? `${c.taille_pieds} pieds` : ""}</div>
                      </td>
                      <td className="px-4 py-3 text-sm text-foreground">{c.proprietaire || ""}</td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">{c.compagnie || ""}</td>
                      <td className="px-4 py-3 text-sm text-foreground font-mono text-xs">{c.tare_kg ? fmtNum(c.tare_kg, lang === "en" ? "en-US" : "fr-FR") : ""}</td>
                      <td className="px-4 py-3 text-sm text-foreground font-mono text-xs">{c.max_payload_kg ? fmtNum(c.max_payload_kg, lang === "en" ? "en-US" : "fr-FR") : ""}</td>
                      <td className="px-4 py-3 text-xs">{c.est_hazardous ? <ShieldAlert size={14} className="text-red-400" /> : ""}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium border ${ETAT_CONFIG[c.etat]?.color || "text-slate-400 border-slate-500/30"}`}>
                          {ETAT_CONFIG[c.etat]?.label || c.etat}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => openDetail(c.id)}
                          title={t("Voir la fiche conteneur", "View container sheet")}
                          className="p-1.5 rounded-lg hover:bg-cyan-500/10 text-muted-foreground hover:text-cyan-400 transition-colors"
                        ><FileText size={14} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-border pb-3">
              <h3 className="font-bold text-foreground text-base">{t("Enregistrer un conteneur", "Register a container")}</h3>
              <button onClick={() => setShowAddModal(false)} className="text-muted-foreground hover:text-foreground"><X size={18} /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="sm:col-span-2">
                  <label className={labelCls}>{t("Numéro ISO *", "ISO number *")}</label>
                  <input className={`${inputCls} font-mono`} placeholder="MSKU1234567" value={form.numero} onChange={e => setForm({ ...form, numero: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t("Type", "Type")}</label>
                  <select className={inputCls} value={form.type_conteneur} onChange={e => setForm({ ...form, type_conteneur: e.target.value })}>
                    {TYPES.map(tt => <option key={tt} value={tt}>{tt.toUpperCase()}</option>)}
                  </select>
                </div>
                <div>
                  <label className={labelCls}>{t("Taille (pieds)", "Size (feet)")} </label>
                  <select className={inputCls} value={form.taille_pieds} onChange={e => setForm({ ...form, taille_pieds: Number(e.target.value) })}>
                    <option value={20}>20</option><option value={40}>40</option><option value={45}>45</option>
                  </select>
                </div>
                <div>
                  <label className={labelCls}>{t("État", "Condition")}</label>
                  <select className={inputCls} value={form.etat} onChange={e => setForm({ ...form, etat: e.target.value })}>
                    <option value="clean">{t("Propre", "Clean")}</option>
                    <option value="dirty">{t("À nettoyer", "To clean")}</option>
                    <option value="damaged">{t("Endommagé", "Damaged")}</option>
                    <option value="repair_needed">{t("Réparation requise", "Repair needed")}</option>
                  </select>
                </div>
                <div>
                  <label className={labelCls}>{t("Propriétaire", "Owner")}</label>
                  <input className={inputCls} value={form.proprietaire} onChange={e => setForm({ ...form, proprietaire: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t("Compagnie maritime", "Shipping line")}</label>
                  <input className={inputCls} value={form.compagnie} onChange={e => setForm({ ...form, compagnie: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t("Tare (kg)", "Tare (kg)")}</label>
                  <input type="number" min="0" className={`${inputCls} font-mono`} value={form.tare_kg} onChange={e => setForm({ ...form, tare_kg: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t("Charge max (kg)", "Max payload (kg)")}</label>
                  <input type="number" min="0" className={`${inputCls} font-mono`} value={form.max_payload_kg} onChange={e => setForm({ ...form, max_payload_kg: e.target.value })} />
                </div>
                <div>
                  <label className={labelCls}>{t("Volume (m³)", "Volume (m³)")}</label>
                  <input type="number" min="0" className={`${inputCls} font-mono`} value={form.volume_m3} onChange={e => setForm({ ...form, volume_m3: e.target.value })} />
                </div>
                <label className="flex items-center gap-2 text-xs text-foreground cursor-pointer sm:col-span-2">
                  <input type="checkbox" className="accent-cyan-500" checked={form.est_hazardous} onChange={e => setForm({ ...form, est_hazardous: e.target.checked })} />
                  {t("Matières dangereuses (DG)", "Dangerous goods (Hazmat)")}
                </label>
                {form.est_hazardous && (
                  <div className="sm:col-span-2">
                    <label className={labelCls}>{t("Classe IMDG", "IMDG class")}</label>
                    <input className={inputCls} placeholder="Ex. 3  Liquides inflammables" value={form.classe_hazard} onChange={e => setForm({ ...form, classe_hazard: e.target.value })} />
                  </div>
                )}
                <div className="sm:col-span-2">
                  <label className={labelCls}>{t("Notes", "Notes")}</label>
                  <textarea rows={2} className={`${inputCls} resize-none`} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} />
                </div>
              </div>
              <button type="submit" disabled={saving} className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs rounded-xl disabled:opacity-50 flex items-center justify-center gap-2">
                {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                {t("Enregistrer le conteneur", "Save container")}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {(detail || detailLoading) && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => !detailLoading && setDetail(null)}>
          <div className="bg-card border border-border rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 space-y-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            {detailLoading ? (
              <div className="py-12 flex items-center justify-center gap-2 text-muted-foreground text-sm">
                <Loader2 className="w-5 h-5 animate-spin text-cyan-400" /> {t("Chargement de la fiche...", "Loading sheet...")}
              </div>
            ) : detail ? (
              <>
                <div className="flex justify-between items-center border-b border-border pb-3">
                  <h3 className="font-bold text-foreground text-base font-mono text-cyan-400">{detail.conteneur?.numero}</h3>
                  <button onClick={() => setDetail(null)} className="text-muted-foreground hover:text-foreground"><X size={18} /></button>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div><p className="text-muted-foreground">{t("Type", "Type")}</p><p className="font-bold text-foreground">{detail.conteneur?.type_conteneur?.toUpperCase()} {detail.conteneur?.taille_pieds ? `${detail.conteneur.taille_pieds}p` : ""}</p></div>
                  <div><p className="text-muted-foreground">{t("État", "Condition")}</p><p className="font-bold text-foreground">{ETAT_CONFIG[detail.conteneur?.etat]?.label || detail.conteneur?.etat}</p></div>
                  <div><p className="text-muted-foreground">{t("Propriétaire", "Owner")}</p><p className="font-bold text-foreground">{detail.conteneur?.proprietaire || ""}</p></div>
                  <div><p className="text-muted-foreground">{t("Tare", "Tare")}</p><p className="font-bold text-foreground">{detail.conteneur?.tare_kg ? `${fmtNum(detail.conteneur.tare_kg, lang === "en" ? "en-US" : "fr-FR")} kg` : ""}</p></div>
                </div>

                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">{t("Derniers cycles de vie", "Recent life cycles")}</h4>
                  {detail.cycles.length === 0 ? (
                    <p className="text-xs text-muted-foreground bg-slate-950/40 border border-border rounded-xl p-3">{t("Aucun cycle enregistré pour ce conteneur.", "No cycle recorded for this container.")}</p>
                  ) : (
                    <div className="space-y-1.5">
                      {detail.cycles.map(cy => (
                        <div key={cy.id} className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs bg-slate-950/40 border border-border rounded-xl px-3 py-2">
                          <span className="font-bold text-cyan-400">{cy.statut}</span>
                          <span className="text-foreground font-mono">{cy.voyage || ""}</span>
                          <span className="text-muted-foreground">{cy.localisation || ""}</span>
                          <span className="text-muted-foreground">{cy.date_arrivee ? new Date(cy.date_arrivee).toLocaleDateString(lang === "en" ? "en-GB" : "fr-FR") : ""}{cy.date_sortie ? ` → ${new Date(cy.date_sortie).toLocaleDateString(lang === "en" ? "en-GB" : "fr-FR")}` : ""}</span>
                          {cy.temps_cycle_heures != null && <span className="text-slate-400 font-mono ml-auto">{fmtNum(cy.temps_cycle_heures, lang === "en" ? "en-US" : "fr-FR")} h</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {detail.dommages.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">{t("Dommages & réclamations", "Damages & claims")}</h4>
                    <div className="space-y-1.5">
                      {detail.dommages.map(d => (
                        <div key={d.id} className="text-xs bg-slate-950/40 border border-red-500/20 rounded-xl px-3 py-2">
                          <span className="font-bold text-red-400">{d.type_dommage || t("Dommage", "Damage")} ({d.gravite || ""})</span>
                          <p className="text-muted-foreground mt-0.5">{d.description || ""}</p>
                          <p className="text-slate-400 mt-0.5">{t("Réclamation", "Claim")}: {d.statut_reclamation} {d.cout_reparation ? ` ${fmtNum(d.cout_reparation, lang === "en" ? "en-US" : "fr-FR")} FCFA` : ""}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

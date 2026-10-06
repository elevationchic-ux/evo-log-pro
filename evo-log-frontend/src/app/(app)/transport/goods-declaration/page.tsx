"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  FileText, Plus, Search, AlertTriangle, CheckCircle, Clock,
  Eye, RefreshCw, X, Calculator
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";

// Contrat réel du backend app/routers/v1/goods_declaration.py (DUM / CAMCIS) :
// GET  /api/v1/transport/goods-declarations/        -> {total, skip, limit, items[]}
// GET  /api/v1/transport/goods-declarations/stats   -> agrégats réels
// POST /api/v1/transport/goods-declarations/        -> DUMCreate (liquidation estimative)
// GET  /{id} · POST /{id}/liquidate · DELETE /{id}
// Statuts réels en base (chaînes stockées par le routeur) : en_attente | valide | liquidé.
interface DumItem {
  id: number;
  numero_dum: string;
  type_operation?: string | null;
  regime_douanier?: string | null;
  bureau_douane?: string | null;
  date_depot?: string | null;
  declarant?: string | null;
  importateur?: string | null;
  marchandise?: string | null;
  nomenclature?: string | null;
  poids_brut?: number | null;
  valeur_caf?: number | null;
  valeur_douane_xaf?: number | null;
  droits_douane?: number | null;
  tva?: number | null;
  montant_total?: number | null;
  statut?: string | null;
  reference_sydonia?: string | null;
  date_validation?: string | null;
}

interface DumDetail extends DumItem {
  poids_net?: number | null;
  nombre_colis?: number | null;
  valeur_fob?: number | null;
  devise?: string | null;
  taux_change?: number | null;
  centimes_additionnels?: number | null;
  timbre_usage?: number | null;
  notes?: string | null;
  date_liquidation?: string | null;
  agent_douane?: string | null;
  validations: {
    id: number;
    numero_bv: string;
    validateur?: string | null;
    resultat?: string | null;
    date_validation?: string | null;
  }[];
}

interface DumStats {
  total_declarations: number;
  en_attente: number;
  validees: number;
  liquidees: number;
  valeur_douane_totale_xaf: number;
  droits_douane_total_xaf: number;
  tva_douaniere_total_xaf: number;
  recettes_fiscales_totales_xaf: number;
}

const STATUT_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  en_attente: { label: "En attente", color: "text-amber-400 bg-amber-400/10 border-amber-400/30", icon: <Clock size={12} /> },
  valide: { label: "Validée", color: "text-blue-400 bg-blue-400/10 border-blue-400/30", icon: <CheckCircle size={12} /> },
  "liquidé": { label: "Liquidée", color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30", icon: <CheckCircle size={12} /> },
};

const fmtNum = (n: number | null | undefined) =>
  n == null ? "Non enregistré" : new Intl.NumberFormat("fr-FR").format(Math.round(n));

export default function GoodsDeclarationPage() {
  const [declarations, setDeclarations] = useState<DumItem[]>([]);
  const [stats, setStats] = useState<DumStats | null>(null);
  const [search, setSearch] = useState("");
  const [filterStatut, setFilterStatut] = useState("");
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [detail, setDetail] = useState<DumDetail | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    declarant: "",
    importateur: "",
    marchandise: "",
    type_operation: "import",
    regime_douanier: "Mise à la consommation",
    bureau_douane: "",
    nomenclature: "",
    poids_brut: "",
    valeur_caf: "",
    devise: "USD",
    taux_change: "",
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search.trim()) params.set("search", search.trim());
      if (filterStatut) params.set("statut", filterStatut);
      const [listRes, statsRes] = await Promise.all([
        apiClient.get(`/api/v1/transport/goods-declarations/?${params.toString()}`),
        apiClient.get("/api/v1/transport/goods-declarations/stats"),
      ]);
      setDeclarations(listRes.data.items ?? []);
      setStats(statsRes.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Impossible de charger les déclarations DUM");
    } finally {
      setLoading(false);
    }
  }, [search, filterStatut]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const openDetail = async (id: number) => {
    try {
      const res = await apiClient.get(`/api/v1/transport/goods-declarations/${id}`);
      setDetail(res.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Déclaration introuvable");
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await apiClient.post("/api/v1/transport/goods-declarations/", {
        declarant: form.declarant,
        importateur: form.importateur,
        marchandise: form.marchandise,
        type_operation: form.type_operation,
        regime_douanier: form.regime_douanier,
        bureau_douane: form.bureau_douane || undefined,
        nomenclature: form.nomenclature || undefined,
        poids_brut: form.poids_brut ? parseFloat(form.poids_brut) : undefined,
        valeur_caf: form.valeur_caf ? parseFloat(form.valeur_caf) : undefined,
        devise: form.devise,
        taux_change: form.taux_change ? parseFloat(form.taux_change) : undefined,
      });
      // Message du serveur restitué tel quel : liquidation ESTIMATIVE,
      // rien n'est télétransmis à SYDONIA depuis cette page.
      toast.success(res.data?.message || "DUM enregistrée localement (estimation)");
      setShowForm(false);
      setForm({ ...form, declarant: "", importateur: "", marchandise: "", poids_brut: "", valeur_caf: "", taux_change: "" });
      fetchData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur création DUM");
    } finally {
      setSubmitting(false);
    }
  };

  const handleLiquidate = async (id: number) => {
    try {
      const res = await apiClient.post(`/api/v1/transport/goods-declarations/${id}/liquidate`, null);
      toast.success(res.data?.message || "Déclaration liquidée");
      fetchData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur liquidation");
    }
  };

  const kpis = [
    { label: "Total DUM", value: stats ? String(stats.total_declarations) : "…", sub: "déclarations en base", color: "text-cyan-400 border-cyan-500/20 bg-cyan-500/5" },
    { label: "En attente", value: stats ? String(stats.en_attente) : "…", sub: "à valider", color: "text-amber-400 border-amber-500/20 bg-amber-500/5" },
    { label: "Liquidées", value: stats ? String(stats.liquidees) : "…", sub: "droits acquittés", color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/5" },
    { label: "Recettes fiscales", value: stats ? `${fmtNum(stats.recettes_fiscales_totales_xaf)} XAF` : "…", sub: "cumul estimé + liquidé", color: "text-indigo-400 border-indigo-500/20 bg-indigo-500/5" },
  ];

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <FileText className="text-cyan-500" size={28} />
            Déclarations Unique de Marchandises (DUM)
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Régime douanier CEMAC / Cameroun — liquidation calculée localement, non télétransmise à SYDONIA.
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchData} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium transition-colors">
            <Plus size={16} />
            Nouvelle Déclaration
          </button>
        </div>
      </div>

      {/* KPIs : agrégats réels de /stats (grand livre, pas la page courante) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {kpis.map((k, i) => (
          <div key={i} className={`rounded-2xl border p-4 ${k.color}`}>
            <p className="text-xs text-muted-foreground">{k.label}</p>
            <p className="text-2xl font-bold text-foreground mt-1">{k.value}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{k.sub}</p>
          </div>
        ))}
      </div>

      {/* Filtres : paramètres serveur search / statut (pas de faux filtrage local) */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/30 placeholder:text-muted-foreground"
            placeholder="Rechercher n° DUM, déclarant, importateur, marchandise, code SH..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/30" value={filterStatut} onChange={(e) => setFilterStatut(e.target.value)}>
          <option value="">Tous les statuts</option>
          {Object.entries(STATUT_CONFIG).map(([v, cfg]) => <option key={v} value={v}>{cfg.label}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>
                {["N° DUM", "Importateur", "Déclarant", "Régime", "Marchandise", "Poids brut (kg)", "Valeur CAF", "Droits + taxes (XAF)", "Statut", "Actions"].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {declarations.length === 0 && !loading ? (
                <tr>
                  <td colSpan={10} className="px-4 py-8 text-center text-muted-foreground text-sm">
                    Aucune DUM enregistrée pour ce filtre.
                  </td>
                </tr>
              ) : declarations.map((d) => {
                const cfg = STATUT_CONFIG[d.statut ?? ""] || { label: d.statut || "—", color: "text-slate-400 bg-slate-400/10 border-slate-400/30", icon: <AlertTriangle size={12} /> };
                return (
                  <tr key={d.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-cyan-400">{d.numero_dum}</td>
                    <td className="px-4 py-3">{d.importateur || "Non enregistré"}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{d.declarant || "Non enregistré"}</td>
                    <td className="px-4 py-3 text-xs">
                      <div>{d.regime_douanier || "Non enregistré"}</div>
                      <div className="text-muted-foreground">{d.bureau_douane || "Bureau non enregistré"}</div>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground max-w-[180px] truncate">
                      {d.marchandise || "Non enregistrée"}
                      {d.nomenclature ? ` (${d.nomenclature})` : ""}
                    </td>
                    <td className="px-4 py-3 text-center text-muted-foreground">{fmtNum(d.poids_brut)}</td>
                    <td className="px-4 py-3 text-center">{d.valeur_caf != null ? `${fmtNum(d.valeur_caf)} ${d.devise ?? ""}` : "Non enregistrée"}</td>
                    <td className="px-4 py-3 text-center font-bold">{fmtNum(d.montant_total)}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${cfg.color}`}>
                        {cfg.icon}{cfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button onClick={() => openDetail(d.id)} className="p-1.5 rounded-lg hover:bg-cyan-500/10 text-muted-foreground hover:text-cyan-400 transition-colors" title="Voir le détail">
                          <Eye size={14} />
                        </button>
                        {d.statut !== "liquidé" && (
                          <button onClick={() => handleLiquidate(d.id)} className="p-1.5 rounded-lg hover:bg-emerald-500/10 text-muted-foreground hover:text-emerald-400 transition-colors" title="Liquider">
                            <Calculator size={14} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modale création : champs réels de DUMCreate */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <form onClick={(e) => e.stopPropagation()} onSubmit={handleCreate} className="bg-card border border-border rounded-2xl p-6 w-full max-w-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-foreground">Nouvelle DUM</h2>
              <button type="button" onClick={() => setShowForm(false)} className="p-1 text-muted-foreground hover:text-foreground"><X size={18} /></button>
            </div>
            <p className="text-xs text-amber-400 flex items-center gap-1.5">
              <AlertTriangle size={13} /> La liquidation produite est une ESTIMATION locale : le document n'est pas télétransmis à SYDONIA.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Déclarant (obligatoire)</label>
                <input required value={form.declarant} onChange={(e) => setForm({ ...form, declarant: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm focus:ring-2 focus:ring-cyan-500/30 outline-none" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Importateur (obligatoire)</label>
                <input required value={form.importateur} onChange={(e) => setForm({ ...form, importateur: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm focus:ring-2 focus:ring-cyan-500/30 outline-none" />
              </div>
              <div className="sm:col-span-2">
                <label className="text-xs font-bold text-slate-300 block mb-1">Marchandise (obligatoire)</label>
                <input required value={form.marchandise} onChange={(e) => setForm({ ...form, marchandise: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm focus:ring-2 focus:ring-cyan-500/30 outline-none" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Type d'opération</label>
                <select value={form.type_operation} onChange={(e) => setForm({ ...form, type_operation: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm">
                  <option value="import">Import</option>
                  <option value="export">Export</option>
                  <option value="transit">Transit</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Régime douanier</label>
                <input value={form.regime_douanier} onChange={(e) => setForm({ ...form, regime_douanier: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Bureau des douanes</label>
                <input value={form.bureau_douane} onChange={(e) => setForm({ ...form, bureau_douane: e.target.value })} placeholder="Ex: DLA-PORT VII" className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Nomenclature (code SH)</label>
                <input value={form.nomenclature} onChange={(e) => setForm({ ...form, nomenclature: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Poids brut (kg)</label>
                <input type="number" step="0.01" value={form.poids_brut} onChange={(e) => setForm({ ...form, poids_brut: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Valeur CAF ({form.devise})</label>
                <input type="number" step="0.01" value={form.valeur_caf} onChange={(e) => setForm({ ...form, valeur_caf: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Devise</label>
                <select value={form.devise} onChange={(e) => setForm({ ...form, devise: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm">
                  <option>USD</option><option>EUR</option><option>XAF</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Taux de change (vide = taux BEAC enregistré)</label>
                <input type="number" step="0.001" value={form.taux_change} onChange={(e) => setForm({ ...form, taux_change: e.target.value })} className="w-full px-3 py-2 rounded-xl border border-border bg-background text-sm" />
              </div>
            </div>
            <button type="submit" disabled={submitting} className="w-full py-3 rounded-xl bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 text-white text-sm font-bold transition-colors">
              {submitting ? "Enregistrement..." : "Enregistrer la DUM (liquidation estimative)"}
            </button>
          </form>
        </div>
      )}

      {/* Modale détail : données réelles de GET /{id} incluant les validations BV */}
      {detail && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4" onClick={() => setDetail(null)}>
          <div onClick={(e) => e.stopPropagation()} className="bg-card border border-border rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-foreground font-mono text-cyan-400">{detail.numero_dum}</h2>
              <button onClick={() => setDetail(null)} className="p-1 text-muted-foreground hover:text-foreground"><X size={18} /></button>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[
                ["Statut", STATUT_CONFIG[detail.statut ?? ""]?.label ?? (detail.statut || "—")],
                ["Type / Régime", `${detail.type_operation ?? "—"} · ${detail.regime_douanier ?? "—"}`],
                ["Bureau", detail.bureau_douane || "Non enregistré"],
                ["Date de dépôt", detail.date_depot ? new Date(detail.date_depot).toLocaleDateString("fr-FR") : "Non enregistrée"],
                ["Déclarant (agrément)", `${detail.declarant || "—"}${detail.numero_agrement ? ` (${detail.numero_agrement})` : ""}`],
                ["Importateur (contribuable)", `${detail.importateur || "—"}${detail.numero_contribuable ? ` (${detail.numero_contribuable})` : ""}`],
                ["Marchandise / code SH", `${detail.marchandise || "—"}${detail.nomenclature ? ` (${detail.nomenclature})` : ""}`],
                ["Poids brut / net", `${fmtNum(detail.poids_brut)} / ${detail.poids_net != null ? fmtNum(detail.poids_net) : "non enregistré"} kg`],
                ["Valeur FOB / CAF", `${detail.valeur_fob != null ? fmtNum(detail.valeur_fob) : "—"} / ${detail.valeur_caf != null ? fmtNum(detail.valeur_caf) : "—"} ${detail.devise ?? ""}`],
                ["Taux appliqué", detail.taux_change != null ? String(detail.taux_change) : "Non enregistré"],
                ["Valeur en douane", `${fmtNum(detail.valeur_douane_xaf)} XAF`],
                ["Droits + centimes", `${fmtNum(detail.droits_douane)} + ${fmtNum(detail.centimes_additionnels)} XAF`],
                ["TVA + timbre", `${fmtNum(detail.tva)} + ${fmtNum(detail.timbre_usage)} XAF`],
                ["Montant total", `${fmtNum(detail.montant_total)} XAF`],
                ["Référence SYDONIA", detail.reference_sydonia || "Non télétransmise (estimation locale)"],
                ["Agent des douanes", detail.agent_douane || "—"],
              ].map(([label, value]) => (
                <div key={label as string}>
                  <p className="text-xs text-muted-foreground">{label}</p>
                  <p className="font-medium text-foreground">{value}</p>
                </div>
              ))}
            </div>
            <div>
              <p className="text-xs font-bold text-muted-foreground uppercase mb-2">Visas de vérification (BV)</p>
              {detail.validations.length === 0 ? (
                <p className="text-sm text-muted-foreground">Aucune validation enregistrée.</p>
              ) : (
                <ul className="text-sm space-y-1">
                  {detail.validations.map((bv) => (
                    <li key={bv.id} className="flex gap-2 text-muted-foreground">
                      <CheckCircle size={14} className="text-emerald-400 mt-0.5 shrink-0" />
                      <span>{bv.numero_bv} — {bv.resultat || "résultat non enregistré"}{bv.validateur ? ` par ${bv.validateur}` : ""}{bv.date_validation ? ` le ${new Date(bv.date_validation).toLocaleDateString("fr-FR")}` : ""}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            {detail.notes && <p className="text-sm text-muted-foreground border-t border-border pt-3">{detail.notes}</p>}
          </div>
        </div>
      )}
    </div>
  );
}

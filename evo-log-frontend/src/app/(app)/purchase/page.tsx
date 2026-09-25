"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  ShoppingCart, Plus, Search, Eye, FileText, Loader2, Send,
} from "lucide-react";
import { toast } from "sonner";
import api from "@/lib/api";
import { useSettings } from "@/components/layout/SettingsProvider";

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(Math.round(n || 0));

interface PurchaseOrder {
  id: number;
  numero_bc: string;
  fournisseur_id: number | null;
  date_prevue_livraison: string | null;
  destinataire: string | null;
  lieu_livraison: string | null;
  conditions_paiement: string | null;
  montant_total: number | null;
  devise: string | null;
  statut: string | null;
}

interface Requisition {
  id: number;
  reference: string;
  designation: string;
  description: string | null;
  quantite: number | null;
  prix_estime: number | null;
  devise: string | null;
  demandeur: string | null;
  service: string | null;
  urgence: boolean | null;
  statut: string;
}

interface Fournisseur { id: number; name: string; code: string | null; }

function statutStyle(statut: string | null): string {
  const s = (statut || "").toLowerCase();
  if (s.includes("approuv") || s.includes("valid") || s.includes("approuvee"))
    return "text-emerald-400 bg-emerald-400/10 border-emerald-400/30";
  if (s.includes("rejet"))
    return "text-red-400 bg-red-400/10 border-red-400/30";
  if (s.includes("soumis") || s.includes("attente") || s.includes("en_cours"))
    return "text-amber-400 bg-amber-400/10 border-amber-400/30";
  return "text-slate-400 bg-slate-400/10 border-slate-400/30";
}

export default function PurchasePage() {
  const { language } = useSettings();
  const lang = language === "en" ? "en" : "fr";
  const t = (fr: string, en: string) => (lang === "en" ? en : fr);

  const [activeTab, setActiveTab] = useState<"po" | "req">("po");
  const [search, setSearch] = useState("");

  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [reqs, setReqs] = useState<Requisition[]>([]);
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [loading, setLoading] = useState(true);

  const [poModal, setPoModal] = useState(false);
  const [reqModal, setReqModal] = useState(false);
  const [saving, setSaving] = useState(false);

  const [poForm, setPoForm] = useState({
    fournisseur_id: 0,
    destinataire: "",
    lieu_livraison: "",
    date_prevue_livraison: "",
    conditions_paiement: "30 jours",
  });
  const [reqForm, setReqForm] = useState({
    designation: "",
    description: "",
    quantite: 1,
    prix_estime: 0,
    service: "",
    urgence: false,
  });

  const fournisseurName = useCallback((id: number | null) => {
    if (id == null) return "";
    const f = fournisseurs.find(x => x.id === id);
    return f ? f.name : `#${id}`;
  }, [fournisseurs]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [poRes, reqRes, fourRes] = await Promise.all([
        api.get("/api/v1/acquisition/bons-commande", { params: { limit: 200 } }).catch(() => ({ data: [] })),
        api.get("/api/v1/purchase/requisitions", { params: { limit: 200 } }).catch(() => ({ data: { items: [] } })),
        api.get("/api/v1/tiers/fournisseurs/", { params: { limit: 500 } }).catch(() => ({ data: [] })),
      ]);
      const poRows = Array.isArray(poRes.data) ? poRes.data : (poRes.data?.items ?? []);
      setPos(poRows);
      const reqPayload = reqRes.data;
      const reqRows = Array.isArray(reqPayload) ? reqPayload : (reqPayload?.items ?? reqPayload?.data ?? []);
      setReqs(reqRows);
      const fRows = Array.isArray(fourRes.data) ? fourRes.data : (fourRes.data?.items ?? []);
      setFournisseurs(fRows);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t("Erreur de chargement", "Failed to load"));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { load(); }, [load]);

  const createPO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!poForm.fournisseur_id) { toast.error(t("Sélectionnez un fournisseur.", "Select a supplier.")); return; }
    setSaving(true);
    try {
      const numero_bc = `BC-${new Date().getFullYear()}-${Date.now().toString().slice(-6)}`;
      await api.post("/api/v1/acquisition/bons-commande", {
        numero_bc,
        fournisseur_id: poForm.fournisseur_id,
        date_prevue_livraison: poForm.date_prevue_livraison || new Date().toISOString().slice(0, 10),
        destinataire: poForm.destinataire || "Service Achats",
        lieu_livraison: poForm.lieu_livraison || "Entrepôt principal",
        conditions_paiement: poForm.conditions_paiement || "30 jours",
      });
      toast.success(t("Bon de commande créé.", "Purchase order created."));
      setPoModal(false);
      setPoForm({ fournisseur_id: 0, destinataire: "", lieu_livraison: "", date_prevue_livraison: "", conditions_paiement: "30 jours" });
      await load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t("Échec de la création du bon de commande.", "Failed to create purchase order."));
    } finally {
      setSaving(false);
    }
  };

  const validerPO = async (id: number) => {
    try {
      await api.put(`/api/v1/acquisition/bons-commande/${id}/valider`);
      toast.success(t("Bon de commande validé.", "Purchase order validated."));
      await load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t("Échec de la validation.", "Validation failed."));
    }
  };

  const createReq = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reqForm.designation.trim()) { toast.error(t("La désignation est obligatoire.", "Designation is required.")); return; }
    setSaving(true);
    try {
      await api.post("/api/v1/purchase/requisitions", {
        designation: reqForm.designation,
        description: reqForm.description || null,
        quantite: reqForm.quantite,
        prix_estime: reqForm.prix_estime,
        service: reqForm.service || null,
        urgence: reqForm.urgence,
      });
      toast.success(t("Réquisition créée.", "Requisition created."));
      setReqModal(false);
      setReqForm({ designation: "", description: "", quantite: 1, prix_estime: 0, service: "", urgence: false });
      await load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t("Échec de la création de la réquisition.", "Failed to create requisition."));
    } finally {
      setSaving(false);
    }
  };

  const reqAction = async (id: number, action: "submit" | "approve" | "reject") => {
    try {
      await api.post(`/api/v1/purchase/requisitions/${id}/${action}`);
      toast.success(
        action === "submit" ? t("Réquisition soumise.", "Requisition submitted.")
          : action === "approve" ? t("Réquisition approuvée.", "Requisition approved.")
            : t("Réquisition rejetée.", "Requisition rejected.")
      );
      await load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t("Action impossible.", "Action failed."));
    }
  };

  const q = search.toLowerCase();
  const filteredPOs = pos.filter(p =>
    (p.numero_bc || "").toLowerCase().includes(q) ||
    fournisseurName(p.fournisseur_id).toLowerCase().includes(q) ||
    (p.destinataire || "").toLowerCase().includes(q)
  );
  const filteredReqs = reqs.filter(r =>
    (r.reference || "").toLowerCase().includes(q) ||
    (r.designation || "").toLowerCase().includes(q) ||
    (r.demandeur || "").toLowerCase().includes(q)
  );

  const poEnAttente = pos.filter(p => (p.statut || "").toLowerCase().includes("attente") || (p.statut || "").toLowerCase().includes("brouillon")).length;
  const budgetEngage = pos.reduce((s, p) => s + (p.montant_total || 0), 0);

  return (
    <div className="min-h-screen p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <ShoppingCart className="text-violet-400" size={28} />
            {t("Achats & Procurement", "Purchasing & Procurement")}
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">{t("Bons de commande, réquisitions et suivi fournisseurs", "Purchase orders, requisitions and supplier tracking")}</p>
        </div>
        <button
          onClick={() => (activeTab === "po" ? setPoModal(true) : setReqModal(true))}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          {activeTab === "po" ? t("Nouveau Bon de Commande", "New Purchase Order") : t("Nouvelle Réquisition", "New Requisition")}
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: t("BC En Attente", "POs Pending"), value: poEnAttente, color: "text-amber-400", bg: "border-amber-500/20 bg-amber-500/5" },
          { label: t("Budget Engagé", "Committed Budget"), value: `${fmtNum(budgetEngage / 1000)}K XAF`, color: "text-violet-400", bg: "border-violet-500/20 bg-violet-500/5" },
          { label: t("Total Bons de Commande", "Total Purchase Orders"), value: pos.length, color: "text-blue-400", bg: "border-blue-500/20 bg-blue-500/5" },
          { label: t("Réquisitions", "Requisitions"), value: reqs.length, color: "text-blue-400", bg: "border-blue-500/20 bg-blue-500/5" },
        ].map((k, i) => (
          <div key={i} className={`rounded-2xl border p-4 ${k.bg}`}>
            <p className="text-xs text-muted-foreground">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-muted/50 rounded-xl w-fit border border-border">
        {[{ id: "po", label: t("Bons de Commande", "Purchase Orders") }, { id: "req", label: t("Réquisitions", "Requisitions") }].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id as any)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id ? "bg-card text-foreground shadow-sm border border-border" : "text-muted-foreground hover:text-foreground"}`}>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30 placeholder:text-muted-foreground" placeholder={t("Rechercher...", "Search...")} value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24 text-muted-foreground gap-2">
          <Loader2 className="animate-spin" size={20} /> {t("Chargement…", "Loading…")}
        </div>
      ) : activeTab === "po" ? (
        <div className="rounded-2xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/40 border-b border-border">
                <tr>{[t("Référence", "Reference"), t("Fournisseur", "Supplier"), t("Destinataire", "Recipient"), t("Livraison", "Delivery"), t("Montant", "Amount"), t("Statut", "Status"), t("Actions", "Actions")].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
                ))}</tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredPOs.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-16 text-center">
                      <ShoppingCart className="mx-auto mb-3 text-muted-foreground" size={40} />
                      <p className="text-sm text-muted-foreground">
                        {pos.length === 0 ? t("Aucun bon de commande.", "No purchase orders.") : t("Aucun bon de commande ne correspond à la recherche.", "No purchase order matches the search.")}
                      </p>
                    </td>
                  </tr>
                )}
                {filteredPOs.map(po => (
                  <tr key={po.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-violet-400">{po.numero_bc}</td>
                    <td className="px-4 py-3 text-sm text-foreground font-medium">{fournisseurName(po.fournisseur_id)}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{po.destinataire || ""}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{po.date_prevue_livraison ? new Date(po.date_prevue_livraison).toLocaleDateString(lang === "en" ? "en-US" : "fr-FR") : ""}</td>
                    <td className="px-4 py-3 font-bold text-foreground">{po.montant_total != null ? fmtNum(po.montant_total) : ""}</td>
                    <td className="px-4 py-3"><span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${statutStyle(po.statut)}`}>{(po.statut || "").toUpperCase()}</span></td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button onClick={() => toast.info(`${po.numero_bc}  ${fournisseurName(po.fournisseur_id)} (${po.lieu_livraison || ""})`)} aria-label={t("Voir le bon de commande", "View purchase order")} className="p-1.5 rounded-lg hover:bg-violet-500/10 text-muted-foreground hover:text-violet-400 transition-colors"><Eye size={14} /></button>
                        {!((po.statut || "").toLowerCase().includes("valid")) && (
                          <button onClick={() => validerPO(po.id)} className="px-2 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors">{t("Valider", "Validate")}</button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredReqs.length === 0 && (
            <div className="rounded-2xl border border-border bg-card p-16 text-center">
              <FileText className="mx-auto mb-3 text-muted-foreground" size={40} />
              <p className="text-sm text-muted-foreground">
                {reqs.length === 0 ? t("Aucune réquisition.", "No requisitions.") : t("Aucune réquisition ne correspond à la recherche.", "No requisition matches the search.")}
              </p>
            </div>
          )}
          {filteredReqs.map(req => {
            const montant = (req.prix_estime || 0) * (req.quantite || 1);
            const st = (req.statut || "").toLowerCase();
            return (
              <div key={req.id} className="rounded-2xl border border-border bg-card p-4 hover:shadow-md transition-all">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono text-xs text-violet-400">{req.reference}</span>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${statutStyle(req.statut)}`}>{(req.statut || "").toUpperCase()}</span>
                      {req.urgence && <span className="text-xs text-red-400 font-bold bg-red-400/10 px-2 py-0.5 rounded-full border border-red-400/30">{t("URGENT", "URGENT")}</span>}
                    </div>
                    <p className="font-semibold text-foreground">{req.designation}</p>
                    {req.description && <p className="text-xs text-muted-foreground mt-0.5">{req.description}</p>}
                    <p className="text-xs text-muted-foreground mt-1">{t("Demandeur", "Requester")} : <span className="text-foreground">{req.demandeur || ""}</span> {req.service ? <>· {req.service}</> : null} · Qté {fmtNum(req.quantite || 0)}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-lg font-bold text-violet-400">{fmtNum(montant)}</p>
                    <p className="text-xs text-muted-foreground">{req.devise || "XAF"} {t("estimé", "est.")}</p>
                    <div className="flex flex-wrap gap-1 mt-2 justify-end">
                      {st === "brouillon" && (
                        <button onClick={() => reqAction(req.id, "submit")} className="px-2 py-1 rounded-lg text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:bg-blue-500/20 transition-colors flex items-center gap-1"><Send size={12} />{t("Soumettre", "Submit")}</button>
                      )}
                      {st === "soumise" && (
                        <>
                          <button onClick={() => reqAction(req.id, "approve")} className="px-2 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors">{t("Approuver", "Approve")}</button>
                          <button onClick={() => reqAction(req.id, "reject")} className="px-2 py-1 rounded-lg text-xs bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors">{t("Rejeter", "Reject")}</button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal Bon de commande */}
      {poModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-border rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-foreground mb-4">{t("Nouveau Bon de Commande", "New Purchase Order")}</h3>
            <form onSubmit={createPO} className="space-y-4">
              <div>
                <label className="block text-xs text-muted-foreground mb-1">{t("Fournisseur *", "Supplier *")}</label>
                <select required value={poForm.fournisseur_id} onChange={e => setPoForm({ ...poForm, fournisseur_id: Number(e.target.value) })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30">
                  <option value={0}>{t(" Sélectionner ", " Select ")}</option>
                  {fournisseurs.map(f => <option key={f.id} value={f.id}>{f.name}{f.code ? ` (${f.code})` : ""}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">{t("Destinataire", "Recipient")}</label>
                  <input value={poForm.destinataire} onChange={e => setPoForm({ ...poForm, destinataire: e.target.value })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30" />
                </div>
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">{t("Lieu de livraison", "Delivery location")}</label>
                  <input value={poForm.lieu_livraison} onChange={e => setPoForm({ ...poForm, lieu_livraison: e.target.value })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30" />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">{t("Livraison prévue", "Expected delivery")}</label>
                  <input type="date" value={poForm.date_prevue_livraison} onChange={e => setPoForm({ ...poForm, date_prevue_livraison: e.target.value })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30" />
                </div>
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">{t("Conditions de paiement", "Payment terms")}</label>
                  <input value={poForm.conditions_paiement} onChange={e => setPoForm({ ...poForm, conditions_paiement: e.target.value })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30" />
                </div>
              </div>
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
                <button type="button" onClick={() => setPoModal(false)} disabled={saving} className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground disabled:opacity-50">{t("Annuler", "Cancel")}</button>
                <button type="submit" disabled={saving} className="px-5 py-2 bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium rounded-xl transition disabled:opacity-60">{saving ? t("Enregistrement…", "Saving…") : t("Créer", "Create")}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Réquisition */}
      {reqModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-border rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-foreground mb-4">{t("Nouvelle Réquisition", "New Requisition")}</h3>
            <form onSubmit={createReq} className="space-y-4">
              <div>
                <label className="block text-xs text-muted-foreground mb-1">{t("Désignation *", "Designation *")}</label>
                <input required value={reqForm.designation} onChange={e => setReqForm({ ...reqForm, designation: e.target.value })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30" />
              </div>
              <div>
                <label className="block text-xs text-muted-foreground mb-1">{t("Description", "Description")}</label>
                <textarea value={reqForm.description} onChange={e => setReqForm({ ...reqForm, description: e.target.value })} rows={2} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30" />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">{t("Quantité", "Quantity")}</label>
                  <input type="number" min={0} value={reqForm.quantite || ""} onChange={e => setReqForm({ ...reqForm, quantite: parseFloat(e.target.value) || 0 })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30 font-mono" />
                </div>
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">{t("Prix estimé (XAF)", "Est. price (XAF)")}</label>
                  <input type="number" min={0} value={reqForm.prix_estime || ""} onChange={e => setReqForm({ ...reqForm, prix_estime: parseFloat(e.target.value) || 0 })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30 font-mono" />
                </div>
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">{t("Service", "Department")}</label>
                  <input value={reqForm.service} onChange={e => setReqForm({ ...reqForm, service: e.target.value })} className="w-full px-3 py-2 text-sm bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-violet-500/30" />
                </div>
              </div>
              <label className="flex items-center gap-2 text-sm text-foreground">
                <input type="checkbox" checked={reqForm.urgence} onChange={e => setReqForm({ ...reqForm, urgence: e.target.checked })} className="accent-violet-600" />
                {t("Urgence", "Urgent")}
              </label>
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
                <button type="button" onClick={() => setReqModal(false)} disabled={saving} className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground disabled:opacity-50">{t("Annuler", "Cancel")}</button>
                <button type="submit" disabled={saving} className="px-5 py-2 bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium rounded-xl transition disabled:opacity-60">{saving ? t("Enregistrement…", "Saving…") : t("Créer", "Create")}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

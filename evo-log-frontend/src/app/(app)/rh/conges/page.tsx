"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Calendar, Plus, Search, CheckCircle, Clock, XCircle, Users, Download,
  AlertTriangle, Loader2, Plane, MessageSquare,
} from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/lib/api-client";
import { useSettings } from "@/components/layout/SettingsProvider";

/**
 * Congés du personnel vus par la fonction RH / le N+1.
 *
 * Les clés des tableaux de correspondance ci-dessous sont les VALEURS d'enum
 * rendues par l'API (`conge_annuel`, `en_attente`…), pas le nom de leurs
 * membres. Comparer `statut === "EN_ATTENTE"` ne matchait jamais : les boutons
 * de décision n'étaient jamais affichés et les compteurs restaient à zéro.
 */

interface CongeRequest {
  id: number;
  employe_id: number;
  employe_nom: string;
  employe_role: string;
  type_conge: string;
  date_debut: string;
  date_fin: string;
  jours_ouvrables: number;
  motif: string | null;
  statut: string;
  date_demande?: string | null;
  commentaire_superviseur?: string | null;
  motif_refus?: string | null;
}

const TYPES: Record<string, { fr: string; en: string; cls: string }> = {
  conge_annuel: { fr: "Annuel", en: "Annual", cls: "text-sky-400 bg-sky-400/10 border-sky-400/30" },
  conge_maladie: { fr: "Maladie", en: "Sick leave", cls: "text-red-400 bg-red-400/10 border-red-400/30" },
  conge_maternite: { fr: "Maternité", en: "Maternity", cls: "text-pink-400 bg-pink-400/10 border-pink-400/30" },
  conge_paternite: { fr: "Paternité", en: "Paternity", cls: "text-indigo-400 bg-indigo-400/10 border-indigo-400/30" },
  conge_exceptionnel: { fr: "Exceptionnel", en: "Special", cls: "text-amber-400 bg-amber-400/10 border-amber-400/30" },
  conge_sans_solde: { fr: "Sans solde", en: "Unpaid", cls: "text-slate-400 bg-slate-400/10 border-slate-400/30" },
  absence_autorisee: { fr: "Absence autorisée", en: "Authorised absence", cls: "text-teal-400 bg-teal-400/10 border-teal-400/30" },
};

const STATUTS: Record<string, { fr: string; en: string; cls: string; icon: React.ReactNode }> = {
  en_attente: { fr: "En attente", en: "Pending", cls: "text-amber-400 bg-amber-400/10 border-amber-400/30", icon: <Clock size={12} /> },
  approuve: { fr: "Approuvé", en: "Approved", cls: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30", icon: <CheckCircle size={12} /> },
  en_cours: { fr: "En cours", en: "In progress", cls: "text-emerald-300 bg-emerald-300/10 border-emerald-300/30", icon: <Plane size={12} /> },
  termine: { fr: "Terminé", en: "Completed", cls: "text-slate-300 bg-slate-300/10 border-slate-300/30", icon: <CheckCircle size={12} /> },
  refuse: { fr: "Refusé", en: "Rejected", cls: "text-red-400 bg-red-400/10 border-red-400/30", icon: <XCircle size={12} /> },
  annule: { fr: "Annulé", en: "Cancelled", cls: "text-slate-400 bg-slate-400/10 border-slate-400/30", icon: <XCircle size={12} /> },
};

export default function RHCongesPage() {
  const { language } = useSettings();
  const lang = language || "fr";
  const t = useCallback((fr: string, en: string) => (lang === "en" ? en : fr), [lang]);
  const locale = lang === "en" ? "en-GB" : "fr-FR";
  const router = useRouter();

  const [conges, setConges] = useState<CongeRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [filterStatut, setFilterStatut] = useState("TOUS");
  const [refusOuvert, setRefusOuvert] = useState<number | null>(null);
  const [motifRefus, setMotifRefus] = useState("");
  const [enCours, setEnCours] = useState<number | null>(null);

  const chargerConges = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await apiClient.get("/api/v1/chef-personnel/conges");
      const data = res?.data;
      setConges(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setLoadError(
        typeof e?.response?.data?.detail === "string"
          ? e.response.data.detail
          : t("Les demandes de congés n’ont pas pu être chargées.", "Leave requests could not be loaded.")
      );
      setConges([]);
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    chargerConges();
  }, [chargerConges]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return conges.filter((c) => {
      const cible = `${c.employe_nom ?? ""} ${c.employe_role ?? ""} ${c.motif ?? ""}`.toLowerCase();
      return (!q || cible.includes(q)) && (filterStatut === "TOUS" || c.statut === filterStatut);
    });
  }, [conges, search, filterStatut]);

  const decider = async (id: number, decision: "APPROUVER" | "REJETER", commentaire = "") => {
    setEnCours(id);
    try {
      await apiClient.post(`/api/v1/chef-personnel/conges/${id}/decision`, { decision, commentaire });
      toast.success(decision === "APPROUVER" ? t("Demande approuvée.", "Request approved.") : t("Demande refusée.", "Request rejected."));
      setRefusOuvert(null);
      setMotifRefus("");
      chargerConges();
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      if (e?.response?.status === 403) {
        toast.error(t("Accès réservé : casquette RH, DRH ou Direction.", "Restricted: HR, HR Director or Management role required."));
      } else {
        toast.error(typeof detail === "string" ? detail : t("Décision impossible.", "Could not record the decision."));
      }
    } finally {
      setEnCours(null);
    }
  };

  const exporterCSV = () => {
    if (filtered.length === 0) {
      toast.error(t("Aucune demande à exporter.", "No request to export."));
      return;
    }
    const heads = [
      t("Demande", "Request"), t("Employé", "Employee"), t("Casquette", "Role"),
      t("Type", "Type"), t("Début", "Start"), t("Fin", "End"),
      t("Jours", "Days"), t("Motif", "Reason"), t("Statut", "Status"),
      t("Motif du refus", "Rejection reason"),
    ];
    const lignes = filtered.map((c) =>
      [
        c.id, c.employe_nom, c.employe_role, libelleType(c.type_conge),
        c.date_debut, c.date_fin, c.jours_ouvrables, c.motif ?? "",
        libelleStatut(c.statut), c.motif_refus ?? "",
      ]
        .map((v) => `"${String(v).replace(/"/g, '""')}"`)
        .join(",")
    );
    const csv = "\ufeff" + heads.join(",") + "\n" + lignes.join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8;" }));
    const lien = document.createElement("a");
    lien.href = url;
    lien.setAttribute("download", `Conges_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(lien);
    lien.click();
    document.body.removeChild(lien);
    URL.revokeObjectURL(url);
    toast.success(t("Export généré.", "Export generated."));
  };

  function libelleType(valeur: string) {
    const cfg = TYPES[valeur];
    return cfg ? t(cfg.fr, cfg.en) : valeur || "-";
  }

  function libelleStatut(valeur: string) {
    const cfg = STATUTS[valeur];
    return cfg ? t(cfg.fr, cfg.en) : valeur || "-";
  }

  const couleurType = (valeur: string) =>
    TYPES[valeur]?.cls ?? "text-slate-400 bg-slate-400/10 border-slate-400/30";

  const couleurStatut = (valeur: string) =>
    STATUTS[valeur]?.cls ?? "text-slate-400 bg-slate-400/10 border-slate-400/30";

  const iconeStatut = (valeur: string) => STATUTS[valeur]?.icon ?? null;

  const dateCourte = (iso?: string | null) =>
    iso ? new Date(iso).toLocaleDateString(locale, { day: "2-digit", month: "short", year: "numeric" }) : "-";

  const nb = (cle: string) => conges.filter((c) => c.statut === cle).length;
  const joursAccordes = conges
    .filter((c) => c.statut === "approuve" || c.statut === "en_cours" || c.statut === "termine")
    .reduce((s, c) => s + (c.jours_ouvrables || 0), 0);

  const kpis = [
    { cle: "en_attente", label: t("En attente", "Pending"), valeur: nb("en_attente"), cls: "text-amber-400 bg-amber-400/10 border-amber-400/20" },
    { cle: "approuve", label: t("Approuvées", "Approved"), valeur: nb("approuve"), cls: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20" },
    { cle: "refuse", label: t("Refusées", "Rejected"), valeur: nb("refuse"), cls: "text-red-400 bg-red-400/10 border-red-400/20" },
    { cle: "jours", label: t("Jours accordés", "Days granted"), valeur: joursAccordes, cls: "text-sky-400 bg-sky-400/10 border-sky-400/20" },
  ];

  const badgeStatut = (c: CongeRequest) => (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium ${couleurStatut(c.statut)}`}>
      {iconeStatut(c.statut)}
      {libelleStatut(c.statut)}
    </span>
  );

  const actions = (c: CongeRequest) => {
    if (c.statut !== "en_attente") {
      return (
        <span className="text-xs text-muted-foreground">
          {c.motif_refus
            ? `${t("Motif du refus", "Rejection reason")} : ${c.motif_refus}`
            : c.commentaire_superviseur
              ? c.commentaire_superviseur
              : "-"}
        </span>
      );
    }
    if (refusOuvert === c.id) {
      return (
        <div className="space-y-2">
          <textarea
            autoFocus
            rows={2}
            value={motifRefus}
            onChange={(e) => setMotifRefus(e.target.value)}
            placeholder={t("Motif du refus (facultatif)", "Rejection reason (optional)")}
            className="w-full min-w-[180px] rounded-lg border border-border bg-slate-900/60 px-2 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-pink-500/40"
          />
          <div className="flex gap-1.5">
            <button
              disabled={enCours === c.id}
              onClick={() => decider(c.id, "REJETER", motifRefus)}
              className="min-h-[36px] rounded-lg bg-red-600 px-3 py-1 text-xs font-medium text-white hover:bg-red-700 disabled:opacity-50"
            >
              {enCours === c.id ? <Loader2 size={12} className="animate-spin" /> : t("Confirmer le refus", "Confirm rejection")}
            </button>
            <button
              onClick={() => { setRefusOuvert(null); setMotifRefus(""); }}
              className="min-h-[36px] rounded-lg border border-border px-3 py-1 text-xs text-muted-foreground hover:bg-accent"
            >
              {t("Annuler", "Cancel")}
            </button>
          </div>
        </div>
      );
    }
    return (
      <div className="flex flex-wrap gap-1.5">
        <button
          disabled={enCours === c.id}
          onClick={() => decider(c.id, "APPROUVER")}
          className="flex min-h-[36px] items-center gap-1 rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-400 transition-colors hover:bg-emerald-500/20 disabled:opacity-50"
        >
          {enCours === c.id ? <Loader2 size={12} className="animate-spin" /> : <CheckCircle size={12} />}
          {t("Approuver", "Approve")}
        </button>
        <button
          disabled={enCours === c.id}
          onClick={() => setRefusOuvert(c.id)}
          className="flex min-h-[36px] items-center gap-1 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-400 transition-colors hover:bg-red-500/20 disabled:opacity-50"
        >
          <XCircle size={12} />
          {t("Refuser", "Reject")}
        </button>
      </div>
    );
  };

  return (
    <div className="min-h-screen space-y-5 p-4 sm:p-6">
      {/* En-tete */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-bold text-foreground sm:text-2xl">
            <Calendar className="text-pink-500" size={26} />
            {t("Congés & Absences", "Leave & Absences")}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {t(
              "Validation des demandes de congés déposées par le personnel.",
              "Approval of leave requests filed by staff."
            )}
          </p>
        </div>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:flex lg:shrink-0">
          <button
            onClick={exporterCSV}
            className="flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-accent"
          >
            <Download size={16} />
            {t("Exporter CSV", "Export CSV")}
          </button>
          <button
            // La demande se dépose par le salarié lui-même (portail self-service) :
            // l'API n'ouvre la création qu'au demandeur, la fonction RH ne peut
            // pas la rédiger à sa place.
            onClick={() => router.push("/portail-employe?tab=conges")}
            className="flex min-h-[44px] items-center justify-center gap-2 rounded-xl bg-pink-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-pink-700"
          >
            <Plus size={16} />
            {t("Nouvelle demande", "New request")}
          </button>
        </div>
      </div>

      {/* KPI */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {kpis.map((k) => (
          <div key={k.cle} className={`rounded-2xl border p-4 ${k.cls}`}>
            <p className="text-xs opacity-80">{k.label}</p>
            <p className="mt-1 text-2xl font-bold">{loading ? "-" : k.valeur}</p>
          </div>
        ))}
      </div>

      {/* Filtres */}
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
        <div className="relative lg:flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            inputMode="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("Rechercher un employé, un motif…", "Search an employee, a reason…")}
            className="min-h-[44px] w-full rounded-xl border border-border bg-card py-2.5 pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-pink-500/40"
          />
        </div>
        <select
          value={filterStatut}
          onChange={(e) => setFilterStatut(e.target.value)}
          aria-label={t("Filtrer par statut", "Filter by status")}
          className="min-h-[44px] rounded-xl border border-border bg-card px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-pink-500/40"
        >
          <option value="TOUS">{t("Tous les statuts", "All statuses")}</option>
          {Object.keys(STATUTS).map((s) => (
            <option key={s} value={s}>{t(STATUTS[s].fr, STATUTS[s].en)}</option>
          ))}
        </select>
      </div>

      {loadError && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          <span className="flex items-center gap-2">
            <AlertTriangle size={16} className="shrink-0" />
            {loadError}
          </span>
          <button onClick={chargerConges} className="min-h-[40px] rounded-lg border border-red-500/40 px-3 py-1.5 font-medium hover:bg-red-500/20">
            {t("Réessayer", "Try again")}
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center gap-2 rounded-2xl border border-border bg-card py-16 text-sm text-muted-foreground">
          <Loader2 size={16} className="animate-spin" />
          {t("Chargement des demandes…", "Loading requests…")}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-2xl border border-border bg-card p-10 text-center">
          <Users size={36} className="mx-auto mb-3 text-muted-foreground" />
          <p className="font-medium text-foreground">
            {conges.length === 0
              ? t("Aucune demande de congé déposée.", "No leave request filed.")
              : t("Aucune demande ne correspond à ces critères.", "No request matches these filters.")}
          </p>
        </div>
      ) : (
        <>
          {/* Tableau : ecran large */}
          <div className="hidden overflow-x-auto rounded-2xl border border-border bg-card md:block">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="border-b border-border bg-muted/40 text-xs uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-semibold">{t("Employé", "Employee")}</th>
                  <th className="px-4 py-3 font-semibold">{t("Type de congé", "Leave type")}</th>
                  <th className="px-4 py-3 font-semibold">{t("Période", "Period")}</th>
                  <th className="px-4 py-3 text-center font-semibold">{t("Jours", "Days")}</th>
                  <th className="px-4 py-3 font-semibold">{t("Motif", "Reason")}</th>
                  <th className="px-4 py-3 font-semibold">{t("Statut", "Status")}</th>
                  <th className="px-4 py-3 font-semibold">{t("Décision", "Decision")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map((c) => (
                  <tr key={c.id} className="transition-colors hover:bg-muted/30">
                    <td className="px-4 py-3">
                      <div className="font-medium text-foreground">{c.employe_nom}</div>
                      <div className="text-xs text-muted-foreground">{c.employe_role}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${couleurType(c.type_conge)}`}>
                        {libelleType(c.type_conge)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-foreground">
                      <div>{dateCourte(c.date_debut)}</div>
                      <div className="text-xs text-muted-foreground">→ {dateCourte(c.date_fin)}</div>
                    </td>
                    <td className="px-4 py-3 text-center font-bold text-foreground">{c.jours_ouvrables}</td>
                    <td className="max-w-[200px] truncate px-4 py-3 text-xs text-muted-foreground" title={c.motif || ""}>
                      {c.motif || "-"}
                    </td>
                    <td className="px-4 py-3">{badgeStatut(c)}</td>
                    <td className="px-4 py-3">{actions(c)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Cartes : mobile et tablette portrait */}
          <div className="space-y-3 md:hidden">
            {filtered.map((c) => (
              <div key={c.id} className="rounded-2xl border border-border bg-card p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-foreground">{c.employe_nom}</p>
                    <p className="truncate text-xs text-muted-foreground">{c.employe_role}</p>
                  </div>
                  {badgeStatut(c)}
                </div>
                <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
                  <div>
                    <dt className="text-muted-foreground">{t("Type", "Type")}</dt>
                    <dd className={`mt-0.5 inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium ${couleurType(c.type_conge)}`}>
                      {libelleType(c.type_conge)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">{t("Jours", "Days")}</dt>
                    <dd className="font-bold text-foreground">{c.jours_ouvrables}</dd>
                  </div>
                  <div className="col-span-2">
                    <dt className="text-muted-foreground">{t("Période", "Period")}</dt>
                    <dd className="text-foreground">{dateCourte(c.date_debut)} → {dateCourte(c.date_fin)}</dd>
                  </div>
                  {!!c.motif && (
                    <div className="col-span-2">
                      <dt className="text-muted-foreground">{t("Motif", "Reason")}</dt>
                      <dd className="text-foreground">{c.motif}</dd>
                    </div>
                  )}
                </dl>
                <div className="mt-3 border-t border-border pt-3">{actions(c)}</div>
              </div>
            ))}
          </div>

          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <MessageSquare size={13} />
            {filtered.length} / {conges.length} {t("demande(s) affichée(s)", "request(s) shown")}
          </p>
        </>
      )}
    </div>
  );
}

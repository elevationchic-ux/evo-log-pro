"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Anchor, ArrowLeft, RefreshCw, Ship } from "lucide-react";
import { toast } from "sonner";
import api from "@/lib/api";
import { useSettings } from "@/components/layout/SettingsProvider";

interface Escale {
  id: number;
  numero_escale: string;
  poste_quai?: string | null;
  date_arrivee_prevue?: string | null;
  date_arrivee_reelle?: string | null;
  date_depart_reelle?: string | null;
  marchandise?: string | null;
  tonnage?: number | null;
  nombre_conteneurs?: number | null;
  agent?: string | null;
  statut?: string | null;
}

const STATUT_STYLE: Record<string, string> = {
  planifiee: "bg-slate-500/10 text-slate-300 border-slate-500/20",
  en_cours: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  terminee: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  annulee: "bg-red-500/10 text-red-400 border-red-500/20",
};

export default function StevedoringOperationsPage() {
  const { language } = useSettings();
  const lang = language === "en" ? "en" : "fr";
  const t = (fr: string, en: string) => (lang === "en" ? en : fr);

  const [escales, setEscales] = useState<Escale[]>([]);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/v1/acconage/escales", { params: { limit: 200 } });
      const data = res.data;
      setEscales(Array.isArray(data) ? data : (data?.items ?? []));
      setLoaded(true);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t("Erreur de chargement", "Failed to load"));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="min-h-screen space-y-6 bg-slate-950 p-4 text-slate-100 sm:p-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Link
            href="/port-operations"
            className="rounded-xl border border-slate-800 bg-slate-900 p-2 text-slate-400 transition hover:text-white"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div className="rounded-2xl border border-amber-500/40 bg-amber-600/20 p-2.5 text-amber-400">
            <Anchor className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white sm:text-2xl">{t("Manutention Portuaire", "Port Stevedoring")}</h1>
            <p className="text-sm text-slate-400">{t("Escales enregistrées (acconage)", "Registered vessel calls (cargo handling)")}</p>
          </div>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          {t("Actualiser", "Refresh")}
        </button>
      </div>

      {/* Escales list */}
      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-800 p-5">
          <h3 className="flex items-center gap-2 text-base font-bold text-white">
            <Ship className="h-4 w-4 text-amber-400" /> {t("Escales", "Vessel calls")}
          </h3>
          <span className="font-mono text-xs text-slate-400">{escales.length}</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="border-b border-slate-800 bg-slate-950 text-xs font-bold uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-5 py-4">{t("N° Escale", "Call No.")}</th>
                <th className="px-5 py-4">{t("Poste à quai", "Berth")}</th>
                <th className="px-5 py-4">{t("Marchandise", "Cargo")}</th>
                <th className="px-5 py-4 text-right">{t("Tonnage", "Tonnage")}</th>
                <th className="px-5 py-4 text-right">{t("Conteneurs", "Containers")}</th>
                <th className="px-5 py-4">{t("Arrivée", "Arrival")}</th>
                <th className="px-5 py-4">{t("Statut", "Status")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {escales.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-10 text-center text-sm text-slate-500">
                    {loaded
                      ? t("Aucune escale enregistrée.", "No vessel call recorded.")
                      : t("Chargement…", "Loading…")}
                  </td>
                </tr>
              ) : (
                escales.map((e) => (
                  <tr key={e.id} className="transition-colors hover:bg-slate-800/40">
                    <td className="px-5 py-4 font-mono text-xs text-amber-400">{e.numero_escale}</td>
                    <td className="px-5 py-4 text-slate-300">{e.poste_quai || ""}</td>
                    <td className="px-5 py-4 text-slate-300">{e.marchandise || ""}</td>
                    <td className="px-5 py-4 text-right font-mono text-slate-100">
                      {e.tonnage != null ? Number(e.tonnage).toLocaleString("fr-FR") : ""}
                    </td>
                    <td className="px-5 py-4 text-right font-mono text-slate-100">{e.nombre_conteneurs ?? ""}</td>
                    <td className="px-5 py-4 whitespace-nowrap text-slate-400">
                      {e.date_arrivee_reelle || e.date_arrivee_prevue || ""}
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${STATUT_STYLE[String(e.statut)] || "bg-slate-500/10 text-slate-300 border-slate-500/20"
                          }`}
                      >
                        {e.statut || ""}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

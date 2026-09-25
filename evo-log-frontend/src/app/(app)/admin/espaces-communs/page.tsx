"use client";

import React, { useState } from "react";
import { Globe, Loader2, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { rbacAPI } from "@/lib/api-client";
import { useApi, classifyApiError } from "@/hooks/useApi";
import { DataStateGate } from "@/components/shared/StatePanels";
import { ModuleLayout } from "@/components/layout/ModuleLayout";

interface SharedRow {
  id: number;
  company_id: number;
  module_key: string;
  libelle: string | null;
  autorise_tous_utilisateurs: boolean;
}

// Référentiel des modules communément ouverts à toute l'entreprise (aucune
// donnée métier inventée : ce sont les clés reconnues par le moteur backend).
const KNOWN_MODULES: { key: string; libelle: string }[] = [
  { key: "rh-mon-espace", libelle: "Portail RH self-service (mes infos, mes congés)" },
  { key: "chat", libelle: "Messagerie / chat interne" },
  { key: "notifications", libelle: "Centre de notifications" },
  { key: "documents-partages", libelle: "Documents communs de l'entreprise" },
  { key: "annuaire", libelle: "Annuaire interne des collaborateurs" },
];

export default function EspacesCommunsPage() {
  const [busy, setBusy] = useState<string | null>(null);

  const { data, loading, error, refetch } = useApi<SharedRow[]>(
    async () => (await rbacAPI.listSharedAccess()).data
  );
  const rows = Array.isArray(data) ? data : [];
  const byKey = new Map(rows.map(r => [r.module_key.toLowerCase(), r]));

  const toggle = async (key: string, libelle: string, nextValue: boolean) => {
    setBusy(key);
    try {
      await rbacAPI.setSharedAccess({ module_key: key, libelle, autorise_tous_utilisateurs: nextValue });
      toast.success(`Module « ${key} » ${nextValue ? "ouvert à tous" : "restreint"}.`);
      refetch();
    } catch (err) {
      toast.error(classifyApiError(err).message);
    } finally {
      setBusy(null);
    }
  };

  const seedDefaults = async () => {
    setBusy("__seed__");
    try {
      const res = await rbacAPI.seedSharedAccess();
      toast.success(`${res.data?.created ?? 0} module(s) commun(s) initialisé(s).`);
      refetch();
    } catch (err) {
      toast.error(classifyApiError(err).message);
    } finally {
      setBusy(null);
    }
  };

  // Modules additionnels activés par l'entreprise hors référentiel connu.
  const extra = rows.filter(r => !KNOWN_MODULES.some(k => k.key === r.module_key.toLowerCase()));

  return (
    <ModuleLayout
      title="Espaces communs par entreprise"
      description="Décidez quels modules sont accessibles à TOUS les collaborateurs authentifiés de votre entreprise, quel que soit leur rôle (portail RH self-service, messagerie interne, etc.)."
      help="Un module commun reste ouvert à tout utilisateur du tenant tant que le levier est activé. Le désactiver crée une exception explicite qui s'impose au serveur d'autorisation."
      actions={
        <button onClick={seedDefaults} disabled={busy === "__seed__"} className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm text-foreground hover:bg-muted transition disabled:opacity-50">
          {busy === "__seed__" ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
          Initialiser les communs
        </button>
      }
    >
      <DataStateGate loading={loading} error={error} isEmpty={false} onRetry={refetch} skeletonRows={5}>
        <div className="space-y-3">
          {KNOWN_MODULES.map((m) => {
            const row = byKey.get(m.key);
            // Défaut : ouvert à tous (aligné sur le moteur backend). Désactivé
            // uniquement si une ligne explicite autorise=false existe.
            const enabled = row ? row.autorise_tous_utilisateurs : true;
            return (
              <div key={m.key} className="rounded-2xl border border-border bg-card p-4 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 min-w-0">
                  <Globe size={18} className={enabled ? "text-primary" : "text-muted-foreground"} />
                  <div className="min-w-0">
                    <p className="font-semibold text-foreground text-sm truncate">{m.libelle}</p>
                    <p className="text-xs text-muted-foreground font-mono">{m.key}</p>
                  </div>
                </div>
                <button
                  role="switch"
                  aria-checked={enabled}
                  onClick={() => toggle(m.key, m.libelle, !enabled)}
                  disabled={busy === m.key}
                  className={`relative w-11 h-6 rounded-full transition-colors shrink-0 ${enabled ? "bg-primary" : "bg-muted"}`}
                >
                  <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${enabled ? "translate-x-5" : ""}`} />
                </button>
              </div>
            );
          })}

          {extra.length > 0 && (
            <div className="pt-2">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Modules spécifiques à l'entreprise</h4>
              <div className="space-y-3">
                {extra.map((r) => (
                  <div key={r.id} className="rounded-2xl border border-border bg-card p-4 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 min-w-0">
                      <Globe size={18} className={r.autorise_tous_utilisateurs ? "text-primary" : "text-muted-foreground"} />
                      <div className="min-w-0">
                        <p className="font-semibold text-foreground text-sm truncate">{r.libelle || r.module_key}</p>
                        <p className="text-xs text-muted-foreground font-mono">{r.module_key}</p>
                      </div>
                    </div>
                    <button
                      role="switch"
                      aria-checked={r.autorise_tous_utilisateurs}
                      onClick={() => toggle(r.module_key, r.libelle || "", !r.autorise_tous_utilisateurs)}
                      disabled={busy === r.module_key}
                      className={`relative w-11 h-6 rounded-full transition-colors shrink-0 ${r.autorise_tous_utilisateurs ? "bg-primary" : "bg-muted"}`}
                    >
                      <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${r.autorise_tous_utilisateurs ? "translate-x-5" : ""}`} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </DataStateGate>
    </ModuleLayout>
  );
}

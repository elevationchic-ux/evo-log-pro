"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Truck,
  Package,
  FileText,
  DollarSign,
  Users,
  Search,
  Plus,
  ShieldCheck,
  Building,
  Wrench,
  X
} from "lucide-react";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const router = useRouter();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setOpen(false);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  if (!open) return null;

  const navItems = [
    { label: "Gestion du Transport & Flotte", path: "/transport/control", icon: Truck, color: "text-orange-400" },
    { label: "Entrepôt & Magasin (Mag3)", path: "/magasin/dashboard", icon: Package, color: "text-red-400" },
    { label: "Comptabilité & Finance", path: "/finance/overview", icon: DollarSign, color: "text-violet-400" },
    { label: "K-Acconage & Operations Quai", path: "/acconage", icon: Building, color: "text-cyan-400" },
    { label: "K-QHSE & Inspections Sécurité", path: "/qhse", icon: ShieldCheck, color: "text-rose-400" },
    { label: "K-Maintenance & Atelier", path: "/maintenance", icon: Wrench, color: "text-amber-400" },
    { label: "Tiers, Clients & Fournisseurs", path: "/master-data/tiers", icon: Users, color: "text-emerald-400" },
  ];

  const filteredItems = navItems.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (path: string) => {
    setOpen(false);
    setQuery("");
    router.push(path);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center pt-24 p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden text-slate-100">
        <div className="flex items-center border-b border-slate-800 px-4 py-3">
          <Search className="w-5 h-5 text-slate-400 mr-3 shrink-0" />
          <input
            autoFocus
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Recherche Omnibox ERP : module, camion, bon d'enlèvement... (Cmd + K)"
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none"
          />
          <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-200 p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto p-2 space-y-1">
          <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
            Navigation Rapide
          </div>

          {filteredItems.length === 0 ? (
            <div className="py-8 text-center text-sm text-slate-500">
              Aucun résultat pour "{query}"
            </div>
          ) : (
            filteredItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.path}
                  onClick={() => handleSelect(item.path)}
                  className="w-full flex items-center px-3 py-2.5 rounded-xl text-sm text-slate-200 hover:bg-slate-800 transition-colors text-left group"
                >
                  <Icon className={`w-4 h-4 mr-3 shrink-0 ${item.color}`} />
                  <span className="flex-1 font-semibold">{item.label}</span>
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

export default CommandPalette;


"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Layers, Plus, Search, Edit, Trash2, Package, Loader2, X } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/lib/api-client";
import { useSettings } from "@/components/layout/SettingsProvider";

const REGISTRY = "categories-articles";

type ArticleCategory = {
  id: number;
  code: string;
  nom: string;
  description: string;
  icon: string;
  articles: number;
  couleur: string;
};

const COLORS = ["#ec4899", "#8b5cf6", "#06b6d4", "#f59e0b", "#10b981", "#6366f1", "#ef4444", "#14b8a6"];

export default function ArticleCategoriesPage() {
  const { language } = useSettings();
  const lang = language || "fr";
  const t = (fr: string, en: string) => (lang === "en" ? en : fr);

  const [categories, setCategories] = useState<ArticleCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newCat, setNewCat] = useState({ code: "", nom: "", description: "", icon: "📦" });

  const loadCategories = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/registres/${REGISTRY}`);
      const list = Array.isArray(res?.data) ? res.data : (res?.data?.items || []);
      setCategories(list.map((e: any, idx: number) => {
        const p = e.payload || {};
        return {
          id: e.id,
          code: p.code || e.reference || "",
          nom: p.nom || "",
          description: p.description || "",
          icon: p.icon || "📦",
          articles: p.articles || 0,
          couleur: p.couleur || COLORS[idx % COLORS.length],
        };
      }));
    } catch {
      setCategories([]);
      toast.error(t("Erreur réseau  chargement des catégories impossible", "Network error  could not load categories"));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { loadCategories(); }, [loadCategories]);

  const filtered = categories.filter(c =>
    search === "" ||
    c.nom.toLowerCase().includes(search.toLowerCase()) ||
    c.code.toLowerCase().includes(search.toLowerCase())
  );

  const handleAdd = async () => {
    if (!newCat.code || !newCat.nom) return;
    setSaving(true);
    try {
      await apiClient.post(`/api/v1/registres/${REGISTRY}`, {
        reference: newCat.code,
        statut: "ACTIF",
        code: newCat.code,
        nom: newCat.nom,
        description: newCat.description,
        icon: newCat.icon,
        articles: 0,
        couleur: COLORS[categories.length % COLORS.length],
      });
      toast.success(t("Catégorie créée", "Category created"));
      setShowForm(false);
      setNewCat({ code: "", nom: "", description: "", icon: "📦" });
      loadCategories();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t("Erreur  catégorie non enregistrée", "Error  category not saved"));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm(t("Supprimer cette catégorie ?", "Delete this category?"))) return;
    try {
      await apiClient.delete(`/api/v1/registres/${REGISTRY}/${id}`);
      toast.success(t("Catégorie supprimée", "Category deleted"));
      loadCategories();
    } catch {
      toast.error(t("Erreur  suppression impossible", "Error  could not delete"));
    }
  };

  const totalArticles = categories.reduce((s, c) => s + c.articles, 0);

  return (
    <div className="min-h-screen p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Layers className="text-pink-400" size={28} />
            {t("Catégories Articles", "Item Categories")}
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            {t("Gestion des catégories du catalogue articles WMS", "WMS item catalog category management")}  {categories.length} {t("catégories", "categories")}
          </p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-700 text-white text-sm font-medium transition-colors">
          <Plus size={16} />{t("Nouvelle Catégorie", "New Category")}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">{t("Total Catégories", "Total Categories")}</p>
          <p className="text-2xl font-bold text-foreground mt-1">{categories.length}</p>
        </div>
        <div className="rounded-2xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">{t("Total Articles", "Total Items")}</p>
          <p className="text-2xl font-bold text-pink-400 mt-1">{totalArticles}</p>
        </div>
        <div className="rounded-2xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">{t("Moy. Articles/Cat.", "Avg. Items/Cat.")}</p>
          <p className="text-2xl font-bold text-muted-foreground mt-1">{categories.length > 0 ? Math.round(totalArticles / categories.length) : 0}</p>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input
          className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30 placeholder:text-muted-foreground"
          placeholder={t("Rechercher catégorie...", "Search category...")}
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {/* Form */}
      {showForm && (
        <div className="rounded-2xl border border-pink-500/30 bg-pink-500/5 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-foreground">{t("Nouvelle Catégorie", "New Category")}</h3>
            <button onClick={() => setShowForm(false)} className="text-muted-foreground hover:text-foreground"><X size={16} /></button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30" placeholder={t("Code (ex: CARBURANT)", "Code (e.g. FUEL)")} value={newCat.code} onChange={e => setNewCat(p => ({ ...p, code: e.target.value.toUpperCase() }))} />
            <input className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30" placeholder={t("Nom catégorie", "Category name")} value={newCat.nom} onChange={e => setNewCat(p => ({ ...p, nom: e.target.value }))} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30" placeholder={t("Description", "Description")} value={newCat.description} onChange={e => setNewCat(p => ({ ...p, description: e.target.value }))} />
            <input className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30" placeholder={t("Icône (emoji)", "Icon (emoji)")} value={newCat.icon} onChange={e => setNewCat(p => ({ ...p, icon: e.target.value }))} />
          </div>
          <div className="flex gap-2">
            <button onClick={handleAdd} disabled={saving} className="px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-700 text-white text-sm font-medium transition-colors disabled:opacity-50 flex items-center gap-2">
              {saving && <Loader2 size={14} className="animate-spin" />}{t("Créer", "Create")}
            </button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">{t("Annuler", "Cancel")}</button>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={24} className="animate-spin text-pink-400" />
        </div>
      )}

      {/* Grid */}
      {!loading && filtered.length === 0 && (
        <div className="rounded-2xl border border-border bg-card p-12 text-center">
          <Layers size={48} className="mx-auto text-muted-foreground/40 mb-3" />
          <h3 className="font-semibold text-foreground">{t("Aucune catégorie définie", "No categories defined")}</h3>
          <p className="text-xs text-muted-foreground mt-1 max-w-md mx-auto mb-4">
            {t("Créez vos catégories pour organiser le catalogue articles de l'entrepôt.", "Create categories to organize your warehouse item catalog.")}
          </p>
          <button onClick={() => setShowForm(true)} className="px-4 py-2 bg-pink-600 text-white rounded-xl font-bold text-xs hover:bg-pink-700">
            + {t("Créer la première catégorie", "Create first category")}
          </button>
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(cat => (
            <div key={cat.id} className="rounded-2xl border border-border bg-card p-5 hover:shadow-md transition-all group">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl" style={{ backgroundColor: `${cat.couleur}20`, border: `1px solid ${cat.couleur}40` }}>
                    {cat.icon}
                  </div>
                  <div>
                    <p className="font-bold text-foreground text-sm">{cat.nom}</p>
                    <p className="text-xs font-mono text-muted-foreground">{cat.code}</p>
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => handleDelete(cat.id)} className="p-1.5 rounded-lg hover:bg-red-500/10 text-muted-foreground hover:text-red-400 transition-colors" title={t("Supprimer", "Delete")}>
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mb-3">{cat.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <Package size={11} /> {cat.articles} {t("articles", "items")}
                </span>
                <div className="w-16 h-1 rounded-full bg-muted">
                  <div className="h-1 rounded-full" style={{ width: `${Math.min(100, cat.articles)}%`, backgroundColor: cat.couleur }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

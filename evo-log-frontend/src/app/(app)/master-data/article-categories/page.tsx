"use client";

import React, { useState } from "react";
import { Layers, Plus, Search, Edit, Trash2, Package, Tag, Fuel, Wrench, Globe } from "lucide-react";

const CATEGORIES = [
  { id: 1, code: "CONTENEUR", nom: "Conteneurs Maritimes", description: "20ft, 40ft, HC, RF, OT, FR", icon: "ðŸ“¦", articles: 6, couleur: "#06b6d4" },
  { id: 2, code: "CARBURANT", nom: "Carburants & Lubrifiants", description: "Gasoil, essence, huiles moteur", icon: "â›½", articles: 3, couleur: "#f97316" },
  { id: 3, code: "EMBALLAGE", nom: "Emballages & Conditionnement", description: "Palettes, caisses, housses", icon: "ðŸ“«", articles: 4, couleur: "#f59e0b" },
  { id: 4, code: "PIECE_RECHANGE", nom: "PiÃ¨ces de Rechange", description: "Auto, poids lourds, pneumatiques", icon: "ðŸ”§", articles: 12, couleur: "#6366f1" },
  { id: 5, code: "MARCHANDISE", nom: "Marchandises GÃ©nÃ©rales", description: "Fret divers et nÃ©goce", icon: "ðŸ“ƒ", articles: 8, couleur: "#10b981" },
  { id: 6, code: "FOURNITURE", nom: "Fournitures & Consommables", description: "MatÃ©riel de bureau, EPI, consommables", icon: "ðŸ‚ï¸", articles: 5, couleur: "#8b5cf6" },
];

export default function ArticleCategoriesPage() {
  const [categories, setCategories] = useState(CATEGORIES);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [newCat, setNewCat] = useState({ code: "", nom: "", description: "" });

  const filtered = categories.filter(c =>
    search === "" || c.nom.toLowerCase().includes(search.toLowerCase()) || c.code.toLowerCase().includes(search.toLowerCase())
  );

  const handleAdd = () => {
    if (!newCat.code || !newCat.nom) return;
    setCategories(prev => [...prev, { id: prev.length + 1, ...newCat, icon: "ðŸ“¦", articles: 0, couleur: "#64748b" }]);
    setNewCat({ code: "", nom: "", description: "" });
    setShowForm(false);
  };

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Layers className="text-pink-400" size={28} />
            CatÃ©gories Articles
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">Gestion des catÃ©gories du catalogue articles WMS â€” {categories.length} catÃ©gories</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-700 text-white text-sm font-medium transition-colors">
          <Plus size={16} />Nouvelle CatÃ©gorie
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Total CatÃ©gories</p>
          <p className="text-2xl font-bold text-foreground mt-1">{categories.length}</p>
        </div>
        <div className="rounded-2xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Total Articles</p>
          <p className="text-2xl font-bold text-pink-400 mt-1">{categories.reduce((s, c) => s + c.articles, 0)}</p>
        </div>
        <div className="rounded-2xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Moy. Articles/Cat.</p>
          <p className="text-2xl font-bold text-muted-foreground mt-1">{Math.round(categories.reduce((s, c) => s + c.articles, 0) / categories.length)}</p>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30 placeholder:text-muted-foreground" placeholder="Rechercher catÃ©gorie..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {/* Form */}
      {showForm && (
        <div className="rounded-2xl border border-pink-500/30 bg-pink-500/5 p-5 space-y-3">
          <h3 className="font-semibold text-foreground">Nouvelle CatÃ©gorie</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30" placeholder="Code (ex: CARBURANT)" value={newCat.code} onChange={e => setNewCat(p => ({ ...p, code: e.target.value.toUpperCase() }))} />
            <input className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30" placeholder="Nom catÃ©gorie" value={newCat.nom} onChange={e => setNewCat(p => ({ ...p, nom: e.target.value }))} />
            <input className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30" placeholder="Description" value={newCat.description} onChange={e => setNewCat(p => ({ ...p, description: e.target.value }))} />
          </div>
          <div className="flex gap-2">
            <button onClick={handleAdd} className="px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-700 text-white text-sm font-medium transition-colors">CrÃ©er</button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">Annuler</button>
          </div>
        </div>
      )}

      {/* Grid */}
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
                <button className="p-1.5 rounded-lg hover:bg-amber-500/10 text-muted-foreground hover:text-amber-400 transition-colors"><Edit size={13} /></button>
                <button className="p-1.5 rounded-lg hover:bg-red-500/10 text-muted-foreground hover:text-red-400 transition-colors"><Trash2 size={13} /></button>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mb-3">{cat.description}</p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Package size={11} /> {cat.articles} articles
              </span>
              <div className="w-16 h-1 rounded-full bg-muted">
                <div className="h-1 rounded-full" style={{ width: `${Math.min(100, cat.articles * 8)}%`, backgroundColor: cat.couleur }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Database,
  Plus,
  Search,
  Package,
  Users,
  Layers,
  FileText,
  RefreshCw,
  Edit,
  Trash2,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { masterDataAPI, tiersAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function MasterDataPage() {
  const [activeTab, setActiveTab] = useState<'articles' | 'tiers' | 'incoterms' | 'containers'>('articles');
  const [loading, setLoading] = useState(true);
  const [articles, setArticles] = useState<any[]>([]);
  const [tiers, setTiers] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  // Creation modal
  const [isArticleModalOpen, setIsArticleModalOpen] = useState(false);
  const [newArticle, setNewArticle] = useState({
    code: '',
    designation: '',
    categorie: 'MARCHANDISE',
    unite: 'PC',
    prix_unitaire: '',
    code_sh: ''
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [artRes, tiersRes] = await Promise.allSettled([
        masterDataAPI.getArticles({ limit: 50 }),
        tiersAPI.getTiers({ limit: 50 })
      ]);

      if (artRes.status === 'fulfilled') {
        const raw = artRes.value.data?.items || artRes.value.data || [];
        setArticles(Array.isArray(raw) ? raw : []);
      }
      if (tiersRes.status === 'fulfilled') {
        const raw = tiersRes.value.data?.items || tiersRes.value.data || [];
        setTiers(Array.isArray(raw) ? raw : []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateArticle = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await masterDataAPI.createArticle({
        code: newArticle.code,
        designation: newArticle.designation,
        categorie: newArticle.categorie,
        unite: newArticle.unite,
        prix_unitaire: Number(newArticle.prix_unitaire || 0),
        code_sh: newArticle.code_sh
      });
      toast.success('Nouvel article créé avec succès dans le référentiel.');
      setIsArticleModalOpen(false);
      setNewArticle({ code: '', designation: '', categorie: 'MARCHANDISE', unite: 'PC', prix_unitaire: '', code_sh: '' });
      loadData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création de l'article.");
    }
  };

  const filteredArticles = articles.filter(a => {
    const q = searchQuery.toLowerCase();
    return !q || (a.code && a.code.toLowerCase().includes(q)) || (a.designation && a.designation.toLowerCase().includes(q));
  });

  const filteredTiers = tiers.filter(t => {
    const q = searchQuery.toLowerCase();
    return !q || (t.nom && t.nom.toLowerCase().includes(q)) || (t.raison_sociale && t.raison_sociale.toLowerCase().includes(q)) || (t.nif && t.nif.toLowerCase().includes(q));
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Données de Référence (Master Data)</h1>
            <p className="text-sm text-on-surface-variant">
              Nomenclature des articles, référentiel des tiers B2B, incoterms et typologies conteneurs
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadData}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          {activeTab === 'articles' && (
            <button
              onClick={() => setIsArticleModalOpen(true)}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
            >
              <Plus className="w-4 h-4" /> Nouvel Article
            </button>
          )}
          {activeTab === 'tiers' && (
            <Link
              href="/fournisseurs"
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
            >
              <Plus className="w-4 h-4" /> Gérer Prestataires & Tiers
            </Link>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-outline gap-6 text-sm font-semibold">
        {[
          { id: 'articles', label: 'Articles & Marchandises', icon: Package, count: articles.length },
          { id: 'tiers', label: 'Tiers & Chargeurs', icon: Users, count: tiers.length },
          { id: 'incoterms', label: 'Incoterms 2020', icon: FileText },
          { id: 'containers', label: 'Normes Conteneurs ISO', icon: Layers },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 pb-3 border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
            {tab.count !== undefined && (
              <span className="px-2 py-0.5 rounded-full text-xs bg-surface-container font-mono">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Search Filter */}
      {(activeTab === 'articles' || activeTab === 'tiers') && (
        <div className="relative max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant" />
          <input
            type="text"
            placeholder={activeTab === 'articles' ? 'Rechercher un code, libellé...' : 'Rechercher un client, NIF...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
      )}

      {/* Tab 1: Articles */}
      {activeTab === 'articles' && (
        <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-on-surface">
              <thead className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline">
                <tr>
                  <th className="px-5 py-3">Code Article</th>
                  <th className="px-5 py-3">Désignation</th>
                  <th className="px-5 py-3">Catégorie</th>
                  <th className="px-5 py-3 text-center">Unité</th>
                  <th className="px-5 py-3 text-right">P.U. Moyen</th>
                  <th className="px-5 py-3 text-right">Code SH / Douane</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline/30 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="p-12 text-center text-on-surface-variant font-sans">
                      Chargement des articles de référence...
                    </td>
                  </tr>
                ) : filteredArticles.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-12 text-center font-sans">
                      <Package className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
                      <h3 className="font-semibold text-on-surface text-base">Aucun article référencé</h3>
                      <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
                        Alimentez votre référentiel article pour standardiser vos bons de livraison et mouvements magasin.
                      </p>
                    </td>
                  </tr>
                ) : (
                  filteredArticles.map((a, idx) => (
                    <tr key={a.id || idx} className="hover:bg-surface-container/50 transition-colors">
                      <td className="px-5 py-3.5 font-bold text-primary">{a.code || `ART-${a.id}`}</td>
                      <td className="px-5 py-3.5 font-sans font-medium text-on-surface">{a.designation || a.nom}</td>
                      <td className="px-5 py-3.5 font-sans text-xs text-on-surface-variant">{a.categorie || 'Standard'}</td>
                      <td className="px-5 py-3.5 text-center text-xs">{a.unite || 'PC'}</td>
                      <td className="px-5 py-3.5 text-right font-bold text-on-surface">
                        {Number(a.prix_unitaire || 0).toLocaleString('fr-FR')} FCFA
                      </td>
                      <td className="px-5 py-3.5 text-right text-xs text-on-surface-variant">{a.code_sh || 'N/A'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Tiers */}
      {activeTab === 'tiers' && (
        <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-on-surface">
              <thead className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline">
                <tr>
                  <th className="px-5 py-3">Raison Sociale</th>
                  <th className="px-5 py-3">Type</th>
                  <th className="px-5 py-3">NIF / Identifiant Fiscal</th>
                  <th className="px-5 py-3">Contact Téléphone / Email</th>
                  <th className="px-5 py-3 text-right">Fiche Détaillée</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline/30">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="p-12 text-center text-on-surface-variant">
                      Chargement des tiers...
                    </td>
                  </tr>
                ) : filteredTiers.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-12 text-center">
                      <Users className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
                      <h3 className="font-semibold text-on-surface text-base">Aucun tiers enregistré</h3>
                      <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
                        Vos chargeurs, transitaires partenaires et transporteurs tiers apparaîtront ici.
                      </p>
                    </td>
                  </tr>
                ) : (
                  filteredTiers.map((t, idx) => (
                    <tr key={t.id || idx} className="hover:bg-surface-container/50 transition-colors">
                      <td className="px-5 py-3.5 font-bold text-on-surface">{t.nom || t.raison_sociale}</td>
                      <td className="px-5 py-3.5 text-xs text-on-surface-variant">{t.type || 'Client B2B'}</td>
                      <td className="px-5 py-3.5 font-mono text-xs">{t.nif || 'Non renseigné'}</td>
                      <td className="px-5 py-3.5 text-xs text-on-surface-variant">{t.telephone || t.email || 'N/A'}</td>
                      <td className="px-5 py-3.5 text-right">
                        <Link
                          href={`/master-data/tiers/${t.id}`}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:underline"
                        >
                          Consulter <ExternalLink className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Incoterms */}
      {activeTab === 'incoterms' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { code: 'EXW', nom: 'Ex Works (À l\'usine)', desc: 'Le vendeur met la marchandise à disposition dans ses locaux.' },
            { code: 'FOB', nom: 'Free On Board (Franco à bord)', desc: 'Le vendeur livre à bord du navire désigné au port d\'embarquement.' },
            { code: 'CIF', nom: 'Cost, Insurance and Freight', desc: 'Le vendeur prend en charge fret maritime et assurance jusqu\'au port d\'arrivée.' },
            { code: 'CFR', nom: 'Cost and Freight', desc: 'Fret maritime payé par l\'expéditeur jusqu\'au port de débarquement.' },
            { code: 'DAP', nom: 'Delivered At Place (Rendu au lieu de destination)', desc: 'Marchandise mise à disposition non déchargée au lieu de livraison convenu.' },
            { code: 'DDP', nom: 'Delivered Duty Paid (Rendu droits acquittés)', desc: 'Le vendeur assume l\'ensemble des coûts et formalités douanières d\'importation.' },
          ].map((inc) => (
            <div key={inc.code} className="bg-surface border border-outline rounded-2xl p-4 space-y-2">
              <span className="inline-block px-2.5 py-1 rounded-lg bg-primary/10 text-primary font-mono font-bold text-xs">
                {inc.code}
              </span>
              <h3 className="font-bold text-sm text-on-surface">{inc.nom}</h3>
              <p className="text-xs text-on-surface-variant">{inc.desc}</p>
            </div>
          ))}
        </div>
      )}

      {/* Tab 4: Containers */}
      {activeTab === 'containers' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { type: "20' DRY Standard", teu: 1, chargeMax: '28 200 kg', volume: '33.2 m³' },
            { type: "40' DRY Standard", teu: 2, chargeMax: '26 700 kg', volume: '67.7 m³' },
            { type: "40' High Cube (HC)", teu: 2, chargeMax: '26 500 kg', volume: '76.4 m³' },
            { type: "40' Reefer Frigorifique", teu: 2, chargeMax: '29 500 kg', volume: '67.0 m³' },
            { type: "20' Open Top", teu: 1, chargeMax: '28 000 kg', volume: '32.5 m³' },
            { type: "Flat Rack 40'", teu: 2, chargeMax: '40 000 kg', volume: 'Colis Lourds' },
            { type: "Tank / Citerne ISO", teu: 1, chargeMax: '30 000 L', volume: 'Liquides/Chimie' },
            { type: "45' High Cube Pallet Wide", teu: 2.25, chargeMax: '29 000 kg', volume: '86.0 m³' },
          ].map((c) => (
            <div key={c.type} className="bg-surface border border-outline rounded-2xl p-4 space-y-1.5">
              <span className="inline-block px-2 py-0.5 rounded-lg bg-cyan-500/10 text-cyan-600 font-mono font-bold text-xs">
                {c.teu} TEU / EVP
              </span>
              <h3 className="font-bold text-sm text-on-surface">{c.type}</h3>
              <div className="text-xs text-on-surface-variant pt-1 border-t border-outline/30 space-y-0.5">
                <p>Charge utile : <span className="font-medium text-on-surface">{c.chargeMax}</span></p>
                <p>Volume utile : <span className="font-medium text-on-surface">{c.volume}</span></p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Creation Article */}
      {isArticleModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-lg p-6 space-y-4 text-on-surface shadow-2xl">
            <h2 className="text-lg font-bold">Ajouter un Article au Référentiel</h2>
            <form onSubmit={handleCreateArticle} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold mb-1">Code Article *</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: ART-PNEU-315"
                  value={newArticle.code}
                  onChange={e => setNewArticle({ ...newArticle, code: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold mb-1">Désignation *</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: Pneu Poids Lourd 315/80 R22.5"
                  value={newArticle.designation}
                  onChange={e => setNewArticle({ ...newArticle, designation: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold mb-1">Unité</label>
                  <input
                    type="text"
                    value={newArticle.unite}
                    onChange={e => setNewArticle({ ...newArticle, unite: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold mb-1">Prix Unitaire Estimé (FCFA)</label>
                  <input
                    type="number"
                    value={newArticle.prix_unitaire}
                    onChange={e => setNewArticle({ ...newArticle, prix_unitaire: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl font-mono"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-outline">
                <button
                  type="button"
                  onClick={() => setIsArticleModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold border border-outline rounded-xl"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-semibold bg-primary text-on-primary rounded-xl"
                >
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

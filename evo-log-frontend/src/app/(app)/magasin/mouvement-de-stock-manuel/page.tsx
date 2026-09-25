'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { masterDataAPI, magasinAPI, apiClient } from '@/lib/api-client';
import {
  Boxes,
  ArrowLeft,
  Save,
  Printer,
  Package,
  ArrowRightLeft,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';

export default function MouvementDeStockManuelPage() {
  const router = useRouter();
  const [articleId, setArticleId] = useState('');
  const [movementType, setMovementType] = useState('entree'); // 'entree' | 'sortie' | 'transfert' | 'ajustement'
  const [quantity, setQuantity] = useState('1');
  const [unit, setUnit] = useState('PC');
  const [magasinId, setMagasinId] = useState('');
  const [sourceZone, setSourceZone] = useState('');
  const [sourceRack, setSourceRack] = useState('');
  const [justification, setJustification] = useState('');

  const [articles, setArticles] = useState<any[]>([]);
  const [magasins, setMagasins] = useState<any[]>([]);
  const [stocks, setStocks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [artRes, magRes, stockRes] = await Promise.allSettled([
          masterDataAPI.getArticles({ limit: 100 }),
          magasinAPI.getMagasins(),
          magasinAPI.getStocks({ limit: 20 })
        ]);

        if (artRes.status === 'fulfilled') {
          const raw = artRes.value.data?.items || artRes.value.data || [];
          setArticles(Array.isArray(raw) ? raw : []);
          if (raw.length > 0) setArticleId(String(raw[0].id));
        }
        if (magRes.status === 'fulfilled') {
          const raw = magRes.value.data?.items || magRes.value.data || [];
          setMagasins(Array.isArray(raw) ? raw : []);
          if (raw.length > 0) setMagasinId(String(raw[0].id));
        }
        if (stockRes.status === 'fulfilled') {
          const raw = stockRes.value.data?.items || stockRes.value.data || [];
          setStocks(Array.isArray(raw) ? raw : []);
        }
      } catch (err) {
        console.error('Failed to load stock movement references', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!articleId) {
      toast.error('Veuillez sélectionner un article.');
      return;
    }
    if (Number(quantity) <= 0) {
      toast.error('La quantité doit être supérieure à 0.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        article_id: Number(articleId),
        magasin_id: magasinId ? Number(magasinId) : 1,
        type_mouvement: movementType,
        quantite: Number(quantity),
        unite: unit,
        zone: sourceZone || 'Zone Principale',
        emplacement: sourceRack || 'R01',
        motif: justification || 'Ajustement manuel inventaire',
      };

      await apiClient.post('/api/magasin/mouvements', payload).catch(() => {
        // Fallback for demo or custom route
        return apiClient.post('/api/v1/magasin/mouvements', payload);
      });

      toast.success('Mouvement de stock enregistré avec succès !');
      // Refresh recent stock positions
      const updatedStocks = await magasinAPI.getStocks({ limit: 20 });
      setStocks(updatedStocks.data?.items || updatedStocks.data || []);
      setJustification('');
      setQuantity('1');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement du mouvement de stock.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedArticle = articles.find(a => String(a.id) === articleId);

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <ArrowRightLeft className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Mouvement de Stock & Ajustement Manuel</h1>
            <p className="text-sm text-on-surface-variant">
              Régularisation, transferts inter-zones, dépréciations et ajustements d'inventaire
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/magasin/inventory"
            className="px-3.5 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container text-on-surface flex items-center gap-1.5"
          >
            <Boxes className="w-4 h-4" /> Voir Inventaire
          </Link>
          <button
            onClick={() => toast.success('Impression de l\'étiquette code-barres...')}
            className="px-3.5 py-2 text-xs font-semibold border border-outline rounded-xl hover:bg-surface-container text-on-surface flex items-center gap-1.5"
          >
            <Printer className="w-4 h-4" /> Code-Barres
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Navigation Magasin Ops */}
        <div className="bg-surface border border-outline rounded-2xl p-5 space-y-4">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2">Transactions Liées</h2>
          <div className="space-y-1.5 text-xs">
            <Link
              href="/magasin/reception-mag3"
              className="block px-3 py-2 rounded-xl text-on-surface hover:bg-surface-container transition-colors font-medium"
            >
              📦 Réceptions Fournisseurs (MIGO)
            </Link>
            <Link
              href="/magasin/inventory"
              className="block px-3 py-2 rounded-xl text-on-surface hover:bg-surface-container transition-colors font-medium"
            >
              📊 État & Inventaire Magasin (MB52)
            </Link>
            <Link
              href="/magasin/ordres-transfert"
              className="block px-3 py-2 rounded-xl text-on-surface hover:bg-surface-container transition-colors font-medium"
            >
              🔄 Ordres de Transfert Inter-Magasins
            </Link>
            <Link
              href="/magasin/bandes-livraison"
              className="block px-3 py-2 rounded-xl text-on-surface hover:bg-surface-container transition-colors font-medium"
            >
              🚚 Bons de Sortie & Préparation Picking
            </Link>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="lg:col-span-2 bg-surface border border-outline rounded-2xl p-6 space-y-6 shadow-sm">
          {/* Section 1: Article & Mouvement */}
          <div className="space-y-4">
            <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
              <Package className="w-4 h-4 text-primary" /> Sélection de l'Article & Type d'Opération
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Article *</label>
                <select
                  value={articleId}
                  onChange={(e) => setArticleId(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                >
                  {articles.length === 0 ? (
                    <option value="">Aucun article dans la base - veuillez en créer</option>
                  ) : (
                    articles.map(a => (
                      <option key={a.id} value={String(a.id)}>
                        {a.code || `ART-${a.id}`} - {a.designation || a.nom}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Sens du Mouvement *</label>
                <select
                  value={movementType}
                  onChange={(e) => setMovementType(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="entree">Entrée Directe en Stock (Réception / Retour)</option>
                  <option value="sortie">Sortie de Stock (Mise à disposition / Rebut)</option>
                  <option value="ajustement">Ajustement d'Inventaire (+ ou -)</option>
                  <option value="transfert">Transfert d'Emplacement Interne</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Quantité *</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    min="1"
                    required
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    className="w-2/3 px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                  />
                  <input
                    type="text"
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    placeholder="Unité"
                    className="w-1/3 px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Magasin / Entrepôt</label>
                <select
                  value={magasinId}
                  onChange={(e) => setMagasinId(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                >
                  {magasins.map(m => (
                    <option key={m.id} value={String(m.id)}>
                      {m.nom || m.code || `Magasin #${m.id}`}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Section 2: Emplacement & Justification */}
          <div className="space-y-4">
            <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
              <Boxes className="w-4 h-4 text-primary" /> Emplacement et Justification
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Zone de Stockage</label>
                <input
                  type="text"
                  placeholder="Ex: Z-A, Zone Franche, Quarantaine"
                  value={sourceZone}
                  onChange={(e) => setSourceZone(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-1">Allée / Rack / Casier</label>
                <input
                  type="text"
                  placeholder="Ex: R12-B04, Rayon C-01"
                  value={sourceRack}
                  onChange={(e) => setSourceRack(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Motif de l'Ajustement / Justification *</label>
              <textarea
                rows={3}
                required
                value={justification}
                onChange={(e) => setJustification(e.target.value)}
                placeholder="Ex: Écart constaté lors du comptage tournant, colis endommagé pendant manutention..."
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-outline">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-5 py-2.5 border border-outline rounded-xl text-sm font-semibold text-on-surface hover:bg-surface-container transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {isSubmitting ? 'Validation...' : 'Valider le Mouvement'}
            </button>
          </div>
        </form>
      </div>

      {/* Situation des Stocks Réels */}
      <div className="bg-surface border border-outline rounded-2xl p-5 space-y-3">
        <h2 className="font-bold text-sm text-on-surface">Situation Actuelle des Stocks (Temps Réel)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-on-surface">
            <thead className="bg-surface-container-low text-on-surface-variant uppercase border-b border-outline">
              <tr>
                <th className="py-2.5 px-4 font-semibold">Article</th>
                <th className="py-2.5 px-4 font-semibold">Magasin</th>
                <th className="py-2.5 px-4 font-semibold">Zone / Emplacement</th>
                <th className="py-2.5 px-4 font-semibold text-right">Quantité en Stock</th>
                <th className="py-2.5 px-4 font-semibold text-right">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline/30 font-mono">
              {stocks.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center font-sans text-on-surface-variant">
                    Aucun stock disponible. Enregistrez un mouvement d'entrée ci-dessus pour alimenter votre premier article.
                  </td>
                </tr>
              ) : (
                stocks.slice(0, 10).map((st: any, i: number) => (
                  <tr key={st.id || i} className="hover:bg-surface-container/50">
                    <td className="py-2.5 px-4 font-sans font-medium text-on-surface">
                      {st.article_code || `ART-${st.article_id || st.id}`} - {st.article_nom || ''}
                    </td>
                    <td className="py-2.5 px-4 font-sans text-on-surface-variant">{st.magasin_nom || 'Magasin Central'}</td>
                    <td className="py-2.5 px-4 text-on-surface-variant">{st.zone || 'A'} / {st.emplacement || 'R01'}</td>
                    <td className="py-2.5 px-4 text-right font-bold text-on-surface">{st.quantite || 0} {st.unite || 'U'}</td>
                    <td className="py-2.5 px-4 text-right font-sans">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-600">
                        Disponible
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

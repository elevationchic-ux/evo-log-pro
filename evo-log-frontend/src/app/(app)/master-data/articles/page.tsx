'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { masterDataAPI } from '@/lib/api-client'
import GenericDataPage from '@/components/ui/GenericDataPage'
import { Package, Layers, DollarSign, CheckCircle, X, AlertCircle, Archive } from 'lucide-react'

// ── KPI Card ────────────────────────────────────────────────────────────────────
function KpiCard({ label, value, icon, color }: { label: string; value: string | number; icon: React.ReactNode; color: string }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 relative overflow-hidden group hover:shadow-md transition-all">
      <div className={`absolute right-0 top-0 w-20 h-20 ${color} rounded-bl-full -z-0 opacity-50 transition-transform group-hover:scale-110`} />
      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-3">
          {icon}
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">{label}</span>
        </div>
        <p className="text-2xl font-black text-gray-900">{value}</p>
      </div>
    </div>
  )
}

// ── Modal de création ───────────────────────────────────────────────────────────
function CreateArticleModal({ isOpen, onClose, onCreated }: { isOpen: boolean; onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({
    code_article: '',
    designation: '',
    type_article: 'STANDARD',
    unite: 'UN',
    prix_unitaire: 0,
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await masterDataAPI.createArticle({
        nom: form.designation,
        categorie: form.type_article === 'STANDARD' ? 'PIECES_DETACHEES' : form.type_article,
        unite_mesure: form.unite === 'UN' ? 'UNITE' : form.unite,
        poids_unitaire: form.prix_unitaire,
        est_actif: true,
      } as any)
      setSuccess(true)
      setTimeout(() => {
        setSuccess(false)
        onCreated()
        onClose()
        setForm({ code_article: '', designation: '', type_article: 'STANDARD', unite: 'UNITE', prix_unitaire: 0 })
      }, 1200)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erreur lors de la création de l\'article.')
    } finally {
      setSubmitting(false)
    }
  }

  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[60] animate-in fade-in duration-200" onClick={onClose} />
      <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg animate-in zoom-in-95 fade-in duration-300 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-white">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-xl">
                <Package className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Nouvel Article</h3>
                <p className="text-sm text-gray-500">Ajouter un article au catalogue</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-xl text-gray-400 hover:text-gray-600 transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}
            {success && (
              <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-sm text-emerald-700">
                <CheckCircle className="w-4 h-4 shrink-0" />
                Article créé avec succès !
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Code Article</label>
                <input
                  type="text"
                  value={form.code_article}
                  onChange={(e) => setForm({ ...form, code_article: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all text-sm font-mono"
                  placeholder="ART-XXXXX (auto)"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Type *</label>
                <select
                  value={form.type_article}
                  onChange={(e) => setForm({ ...form, type_article: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all text-sm bg-white"
                >
                  <option value="STANDARD">Standard</option>
                  <option value="SERVICE">Service</option>
                  <option value="CONSOMMABLE">Consommable</option>
                  <option value="PIECE_RECHANGE">Pièce de Rechange</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Désignation *</label>
              <input
                required
                type="text"
                value={form.designation}
                onChange={(e) => setForm({ ...form, designation: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all text-sm"
                placeholder="Description de l'article"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Unité de Mesure</label>
                <select
                  value={form.unite}
                  onChange={(e) => setForm({ ...form, unite: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all text-sm bg-white"
                >
                  <option value="UN">Unité (UN)</option>
                  <option value="KG">Kilogramme (KG)</option>
                  <option value="L">Litre (L)</option>
                  <option value="M">Mètre (M)</option>
                  <option value="M2">Mètre² (M2)</option>
                  <option value="M3">Mètre³ (M3)</option>
                  <option value="T">Tonne (T)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Prix Unitaire (FCFA)</label>
                <input
                  type="number"
                  value={form.prix_unitaire}
                  onChange={(e) => setForm({ ...form, prix_unitaire: Number(e.target.value) })}
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all text-sm"
                  placeholder="0"
                />
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
              <button
                type="button"
                onClick={onClose}
                className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-sm shadow-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Création...' : 'Créer l\'Article'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}

// ── Page principale ─────────────────────────────────────────────────────────────
export default function MasterDataArticles() {
  const [articles, setArticles] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)

  const fetchArticles = useCallback(async () => {
    try {
      const res = await masterDataAPI.getArticles()
      setArticles(res.data || [])
    } catch (err) {
      console.error('Error fetching articles:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchArticles()
  }, [fetchArticles])

  // ── KPI computations ──────────────────────────────────────────────────────
  const kpis = useMemo(() => {
    const actifs = articles.filter((a) => a.statut !== 'INACTIF').length
    const inactifs = articles.filter((a) => a.statut === 'INACTIF').length
    const prixMoyen = articles.length > 0
      ? Math.round(articles.reduce((sum, a) => sum + (a.prix_unitaire || 0), 0) / articles.length)
      : 0
    const types = new Set(articles.map((a) => a.type_article || 'STANDARD'))
    return { total: articles.length, actifs, inactifs, prixMoyen, nbTypes: types.size }
  }, [articles])

  const kpiCards = (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Total Articles" value={kpis.total} icon={<Package className="w-4 h-4 text-blue-600" />} color="bg-blue-50" />
      <KpiCard label="Actifs" value={kpis.actifs} icon={<CheckCircle className="w-4 h-4 text-emerald-600" />} color="bg-emerald-50" />
      <KpiCard label="Types" value={kpis.nbTypes} icon={<Layers className="w-4 h-4 text-amber-600" />} color="bg-amber-50" />
      <KpiCard label="Prix Moyen" value={`${kpis.prixMoyen.toLocaleString()} FCFA`} icon={<DollarSign className="w-4 h-4 text-purple-600" />} color="bg-purple-50" />
    </div>
  )

  const columns = [
    {
      key: 'code_article',
      label: 'Code',
      render: (val: any) => (
        <span className="font-mono text-xs px-2 py-1 bg-slate-100 rounded text-slate-600 font-medium">
          {val || 'N/A'}
        </span>
      ),
    },
    {
      key: 'designation',
      label: 'Désignation',
      render: (val: any, row: any) => (
        <div>
          <div className="font-semibold text-slate-900">{val || 'Sans désignation'}</div>
          <div className="text-xs text-slate-500">Catégorie: {row.categorie?.nom || row.categorie_id || 'Aucune'}</div>
        </div>
      ),
    },
    {
      key: 'type_article',
      label: 'Type',
      render: (val: any) => {
        const typeStr = val || 'STANDARD'
        const colors: Record<string, string> = {
          STANDARD: 'bg-blue-50 text-blue-700 ring-blue-600/20',
          SERVICE: 'bg-violet-50 text-violet-700 ring-violet-600/20',
          CONSOMMABLE: 'bg-amber-50 text-amber-700 ring-amber-600/20',
          PIECE_RECHANGE: 'bg-rose-50 text-rose-700 ring-rose-600/20',
        }
        const style = colors[typeStr] || 'bg-blue-50 text-blue-700 ring-blue-600/20'
        return (
          <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${style}`}>
            {typeStr}
          </span>
        )
      }
    },
    {
      key: 'unite',
      label: 'Unité',
      render: (_val: any, row: any) => (
        <div className="text-sm text-slate-600">
          {row.unite?.code || row.unite || 'UN'}
        </div>
      )
    },
    {
      key: 'prix_unitaire',
      label: 'Prix Unitaire',
      render: (val: any) => (
        <div className="text-sm font-medium text-slate-900">
          {val ? `${val.toLocaleString()} FCFA` : '-'}
        </div>
      )
    },
    {
      key: 'statut',
      label: 'Statut',
      render: (val: any) => (
        <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${val !== 'INACTIF' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${val !== 'INACTIF' ? 'bg-emerald-600' : 'bg-red-600'}`}></span> {val !== 'INACTIF' ? 'Actif' : 'Inactif'}
        </span>
      )
    }
  ]

  return (
    <>
      <GenericDataPage
        title="Articles (Catalogue)"
        description="Gestion centralisée du catalogue d'articles, produits et pièces de rechange."
        icon={<Package className="w-6 h-6 text-blue-600" />}
        columns={columns}
        data={articles}
        isLoading={loading}
        onAdd={() => setModalOpen(true)}
        primaryActionLabel="Nouvel Article"
        kpiCards={kpiCards}
        onEdit={(row) => console.log('Edit article:', row)}
        onDelete={(row) => console.log('Delete article:', row)}
      />
      <CreateArticleModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={fetchArticles}
      />
    </>
  )
}

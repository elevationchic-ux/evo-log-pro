'use client'

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { masterDataAPI } from '@/lib/api-client'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { Package, Search, Plus, Edit, Trash2, Layers, HardHat } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'
import { toast } from 'sonner'

// ── Validation Schema (Zod) ───────────────────────────────────────────────────
const articleSchema = z.object({
  code_article: z.string().regex(/^\d+$/, "Le code article doit être uniquement numérique"),
  nom: z.string().min(1, "Le nom est requis"),
  description: z.string().optional(),
  categorie: z.string(),
  unite_mesure: z.string(),
  poids_unitaire: z.coerce.number().optional().nullable(),
  volume_unitaire: z.coerce.number().optional().nullable()
})

type ArticleFormValues = z.infer<typeof articleSchema>

// ── Passerelle modele Article backend <-> champs metiers de la page ─────────
// Le backend stocke code/designation/poids_kg/volume_m3 (app/schemas/
// magasin_store.py) ; la page raisonne en code_article/nom/... : alias
// explicites, reponse reellement persistee, jamais de donnee inventee.
function fromApiArticle(a: any) {
  return {
    ...a,
    code_article: a.code_article ?? a.code ?? '',
    nom: a.nom ?? a.designation ?? '',
    poids_unitaire: a.poids_unitaire ?? a.poids_kg ?? null,
    volume_unitaire: a.volume_unitaire ?? a.volume_m3 ?? null,
  }
}

function toApiArticle(f: any) {
  return {
    code: String(f.code_article ?? f.code ?? ''),
    designation: f.nom ?? f.designation ?? '',
    description: f.description || undefined,
    categorie: f.categorie || undefined,
    unite_mesure: f.unite_mesure || undefined,
    poids_kg: f.poids_unitaire === '' || f.poids_unitaire == null ? undefined : Number(f.poids_unitaire),
    volume_m3: f.volume_unitaire === '' || f.volume_unitaire == null ? undefined : Number(f.volume_unitaire),
  }
}


export default function ArticlesPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingArticle, setEditingArticle] = useState<any>(null)
  const [filterType, setFilterType] = useState('MARCHANDISE')

  const { data: articles = [], isLoading: loading } = useQuery({
    queryKey: ['articles'],
    queryFn: async () => {
      const res = await masterDataAPI.getArticles()
      // Endpoint reel renvoie une enveloppe {items,total} : normaliser pour
      // que .filter/.map de la page ne crashent jamais.
      const d = res.data
      const rows = Array.isArray(d) ? d : (d?.items ?? d?.results ?? [])
      return rows.map(fromApiArticle)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => masterDataAPI.deleteArticle(id),
    onSuccess: () => {
      toast.success('Article supprimé avec succès.')
      queryClient.invalidateQueries({ queryKey: ['articles'] })
    },
    onError: () => {
      toast.error("Erreur lors de la suppression de l'article.")
    }
  })

  const handleDelete = (id: number) => {
    if (confirm('Voulez-vous vraiment désactiver cet article ?')) {
      deleteMutation.mutate(id)
    }
  }

  const filteredArticles = articles.filter((a: any) => {
    const isAchat = a.categorie === 'EQUIPEMENT' || a.categorie === 'PIECES_DETACHEES' || a.categorie === 'MOBILIER_BUREAU_INFORMATIQUE';
    const matchType = filterType === 'ACHAT' ? isAchat : !isAchat;
    const matchSearch = a.code_article?.includes(searchQuery) || a.nom?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchType && matchSearch;
  })

  return (
    <ModuleLayout module="magasin">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-200 flex items-center gap-3">
              <Package className="w-8 h-8 text-blue-600" />
              Référentiel des Articles
            </h1>
            <p className="text-sm text-slate-500 mt-2">Gérez les codes numériques des marchandises et des achats internes.</p>
          </div>
          <button 
            onClick={() => { setEditingArticle(null); setShowModal(true); }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-sm transition-all"
          >
            <Plus className="w-5 h-5" />
            Créer un Article
          </button>
        </div>

        {/* Tabs & Search */}
        <div className="bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-700 mb-6 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="flex gap-2 w-full sm:w-auto p-1 bg-slate-900 rounded-xl">
            <button 
              onClick={() => setFilterType('MARCHANDISE')}
              className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 justify-center ${filterType === 'MARCHANDISE' ? 'bg-slate-900 text-blue-300 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
            >
              <Layers className="w-4 h-4" /> Marchandises Client
            </button>
            <button 
              onClick={() => setFilterType('ACHAT')}
              className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 justify-center ${filterType === 'ACHAT' ? 'bg-slate-900 text-blue-300 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
            >
              <HardHat className="w-4 h-4" /> Matériel & Achat Interne
            </button>
          </div>
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Rechercher (Code, Nom)..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-600 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm outline-none bg-slate-800"
            />
          </div>
        </div>

        {/* Table */}
        <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-700 overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-800/80 border-b border-slate-700 text-xs uppercase font-bold text-slate-500">
              <tr>
                <th className="px-6 py-4">Code Article</th>
                <th className="px-6 py-4">Nom du produit</th>
                <th className="px-6 py-4">Unité</th>
                <th className="px-6 py-4">Dimensions</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-12"><CardSkeletonLoader /></td></tr>
              ) : filteredArticles.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-16 text-center text-slate-500 font-medium">
                    Aucun article trouvé dans cette catégorie.
                  </td>
                </tr>
              ) : filteredArticles.map((article: any) => (
                <tr key={article.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <span className="font-mono font-black text-blue-600 bg-blue-500/10 px-2 py-1 rounded-md text-base">{article.code_article}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-bold text-slate-200">{article.nom}</div>
                    <div className="text-xs text-slate-500">{article.description}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex rounded-full bg-slate-900 px-2.5 py-1 text-xs font-bold text-slate-300">
                      {article.unite_mesure}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-slate-500">
                    {article.poids_unitaire && <div>{article.poids_unitaire} kg/u</div>}
                    {article.volume_unitaire && <div>{article.volume_unitaire} m³/u</div>}
                    {!article.poids_unitaire && !article.volume_unitaire && '-'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end gap-2">
                      <button onClick={() => { setEditingArticle(article); setShowModal(true); }} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-500/10 rounded-lg transition-colors">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleDelete(article.id)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-500/10 rounded-lg transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Modal Form */}
        {showModal && (
          <ArticleModal article={editingArticle} onClose={() => setShowModal(false)} filterType={filterType} />
        )}
      </div>
    </ModuleLayout>
  )
}

function ArticleModal({ article, onClose, filterType }: { article: any, onClose: () => void, filterType: string }) {
  const queryClient = useQueryClient()
  
  const { register, handleSubmit, formState: { errors } } = useForm<any>({
    resolver: zodResolver(articleSchema) as any,
    defaultValues: article || {
      code_article: '',
      nom: '',
      description: '',
      categorie: filterType === 'ACHAT' ? 'EQUIPEMENT' : 'ALIMENTAIRE',
      unite_mesure: 'KG',
      poids_unitaire: null,
      volume_unitaire: null
    }
  })

  const mutation = useMutation({
    mutationFn: (data: any) => article ? masterDataAPI.updateArticle(article.id, toApiArticle(data)) : masterDataAPI.createArticle(toApiArticle(data)),
    onSuccess: () => {
      toast.success(`Article ${article ? 'modifié' : 'créé'} avec succès !`)
      queryClient.invalidateQueries({ queryKey: ['articles'] })
      onClose()
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'enregistrement.")
    }
  })

  const onSubmit = (data: ArticleFormValues) => {
    mutation.mutate(data)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div className="bg-slate-900 rounded-2xl shadow-xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
        <div className="px-6 py-4 border-b border-slate-700 flex justify-between items-center bg-slate-800">
          <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
            <Package className="w-5 h-5 text-blue-600" />
            {article ? 'Modifier l\'Article' : 'Nouveau Code Article'}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-400"><span className="material-symbols-outlined">close</span></button>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
          
          <div>
            <label className="block text-sm font-bold text-slate-300 mb-1">Code Article (Chiffres uniquement) *</label>
            <input 
              type="text" 
              {...register('code_article')}
              placeholder="ex: 1234567"
              className={`w-full px-4 py-2 rounded-xl border ${errors.code_article ? 'border-red-500' : 'border-slate-600'} focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none font-mono text-lg`}
            />
            {errors.code_article && <p className="text-xs text-red-500 mt-1">{String(errors.code_article.message || '')}</p>}
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-300 mb-1">Nom du Produit *</label>
            <input 
              type="text" 
              {...register('nom')}
              placeholder="ex: Riz Bella Luna 50 Kg"
              className={`w-full px-4 py-2 rounded-xl border ${errors.nom ? 'border-red-500' : 'border-slate-600'} focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none`}
            />
            {errors.nom && <p className="text-xs text-red-500 mt-1">{String(errors.nom.message || '')}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-300 mb-1">Unité de Mesure</label>
              <select 
                {...register('unite_mesure')}
                className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none bg-slate-900"
              >
                <option value="UDB">Cartons/Sacs (UDB)</option>
                <option value="KG">Kilogrammes (Kg)</option>
                <option value="LITRE">Litres</option>
                <option value="UNITE">Unité</option>
                <option value="M3">Mètre cube (M3)</option>
                <option value="TONNE">Tonne</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-300 mb-1">Catégorie</label>
              <select 
                {...register('categorie')}
                className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none bg-slate-900"
              >
                {filterType === 'ACHAT' ? (
                  <>
                    <option value="EQUIPEMENT">Equipement</option>
                    <option value="PIECES_DETACHEES">Pièces détachées</option>
                    <option value="MOBILIER_BUREAU_INFORMATIQUE">Mobilier & Bureau</option>
                  </>
                ) : (
                  <>
                    <option value="ALIMENTAIRE">Alimentaire</option>
                    <option value="VRAC">Vrac</option>
                    <option value="PRODUITS_DANGEREUX">Produits Dangereux</option>
                    <option value="PRODUITS_FINIS">Produits Finis</option>
                  </>
                )}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-300 mb-1">Description (Optionnel)</label>
            <input 
              type="text" 
              {...register('description')}
              className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none"
            />
          </div>

          <div className="flex gap-3 justify-end mt-6 pt-4 border-t border-slate-700">
            <button type="button" onClick={onClose} className="px-5 py-2 rounded-xl text-sm font-bold text-slate-400 hover:bg-slate-800 transition-colors">Annuler</button>
            <button type="submit" disabled={mutation.isPending} className="px-5 py-2 rounded-xl text-sm font-bold bg-blue-600 hover:bg-blue-700 text-white transition-colors shadow-sm disabled:opacity-50">
              {mutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

'use client'

import { useState, useEffect } from 'react'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { FileText, Search, Plus, Calendar, Edit, Ship, PackageSearch, Package } from 'lucide-react'
import { CardSkeletonLoader } from '@/components/ui/Loaders'
import { magasinAPI } from '@/lib/api-client'
import { toast } from 'sonner'

export default function DeclarationsPage() {
  const [declarations, setDeclarations] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDeclarations()
  }, [])

  const fetchDeclarations = async () => {
    try {
      setLoading(true)
      const res = await magasinAPI.getDeclarations()
      setDeclarations(res.data || [])
    } catch (error) {
      console.error(error)
      toast.error('Erreur lors du chargement des déclarations')
    } finally {
      setLoading(false)
    }
  }

  const filteredDeclarations = declarations.filter(d => 
    d.numero_bl.includes(searchQuery) || 
    d.code_article.includes(searchQuery) ||
    d.client?.nom.toLowerCase().includes(searchQuery.toLowerCase())
  ).sort((a, b) => b.id - a.id)

  return (
    <ModuleLayout module="magasin">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-200 flex items-center gap-3">
              <Ship className="w-8 h-8 text-blue-600" />
              Déclarations Marchandises
            </h1>
            <p className="text-sm text-slate-500 mt-2">Déclarez les marchandises arrivées au port avant stockage.</p>
          </div>
          <button 
            onClick={() => setShowModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-sm transition-all"
          >
            <Plus className="w-5 h-5" />
            Nouvelle Déclaration
          </button>
        </div>

        {/* Search */}
        <div className="bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-700 mb-6 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="relative w-full sm:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Rechercher (BL, Code Article, Client)..." 
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
                <th className="px-6 py-4">BL & Navire</th>
                <th className="px-6 py-4">Client</th>
                <th className="px-6 py-4">Marchandise Déclarée</th>
                <th className="px-6 py-4">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr><td colSpan={4} className="px-6 py-12"><CardSkeletonLoader /></td></tr>
              ) : filteredDeclarations.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-16 text-center text-slate-500 font-medium">
                    Aucune déclaration trouvée.
                  </td>
                </tr>
              ) : filteredDeclarations.map((decl) => (
                <tr key={decl.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-mono font-black text-blue-600 flex items-center gap-2">
                      {decl.numero_bl}
                      {decl.numero_bl_externe && (
                        <span className="text-[10px] bg-slate-900 text-slate-500 px-1.5 py-0.5 rounded uppercase font-bold">EXT: {decl.numero_bl_externe}</span>
                      )}
                    </div>
                    <div className="text-xs text-slate-500 flex items-center gap-1 mt-1 font-bold">
                      <Ship className="w-3.5 h-3.5" />
                      {decl.nom_navire || "Navire non spécifié"} {decl.numero_voyage ? `(${decl.numero_voyage})` : ''}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-bold text-slate-200">{decl.client?.nom} {decl.client?.prenom}</div>
                    <div className="text-xs text-slate-500">{decl.client?.raison_sociale}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-start gap-2">
                      <Package className="w-4 h-4 text-slate-400 mt-0.5" />
                      <div>
                        <div className="font-bold text-slate-200">
                          Code: <span className="text-blue-600 font-mono">{decl.code_article}</span>
                        </div>
                        {decl.lignes && decl.lignes[0] && (
                          <div className="text-sm font-medium text-slate-400 mt-1">
                            Qté totale : <strong className="text-slate-200">{parseFloat(decl.lignes[0].quantite_declaree)} {decl.lignes[0].unite_mesure}</strong>
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                      decl.statut === 'VALIDEE' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'
                    }`}>
                      {decl.statut}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Modal Form */}
        {showModal && (
          <DeclarationModal 
            onClose={() => setShowModal(false)} 
            onSuccess={() => { setShowModal(false); fetchDeclarations(); }} 
          />
        )}
      </div>
    </ModuleLayout>
  )
}

function DeclarationModal({ onClose, onSuccess }: { onClose: () => void, onSuccess: () => void }) {
  const [activeTab, setActiveTab] = useState<'ident' | 'navire' | 'marchandise' | 'parties'>('ident')
  
  const [formData, setFormData] = useState({
    numero_bl: '',
    numero_bl_externe: '',
    reference_booking: '',
    numero_scelle: '',
    client_id: '',
    nom_navire: '',
    numero_voyage: '',
    port_chargement: '',
    port_dechargement: '',
    lieu_livraison: '',
    code_article: '',
    quantite_declaree: '',
    poids_brut_kg: '',
    poids_net_kg: '',
    volume_m3: '',
    nombre_colis: '',
    type_emballage: '',
    description_marchandises: '',
    expediteur_shipper: '',
    destinataire_consignee: '',
    notify_party: '',
    mode_fret: '',
    code_hs: '',
    numero_declaration_douane: '',
    numero_lot: '',
    date_fabrication: '',
    date_expiration: ''
  })
  
  const [clients, setClients] = useState<any[]>([])
  const [articleInfo, setArticleInfo] = useState<any>(null)
  const [articleError, setArticleError] = useState('')

  useEffect(() => {
    magasinAPI.getClients()
      .then(res => setClients(res.data || []))
      .catch(console.error)
  }, [])

  useEffect(() => {
    if (formData.code_article.length === 7) {
      magasinAPI
        .getArticleByCode(formData.code_article)
        .then(res => {
          setArticleInfo(res.data);
          setArticleError('');
        })
        .catch(e => {
          setArticleInfo(null);
          setArticleError(e.response?.data?.detail || 'Article introuvable');
        });
    } else {
      setArticleInfo(null);
      setArticleError('');
    }
  }, [formData.code_article]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!articleInfo) {
      toast.error("Code article invalide.");
      return
    }

    const payload = {
      ...formData,
      client_id: parseInt(formData.client_id),
      statut: "VALIDEE",
      poids_brut_kg: formData.poids_brut_kg ? parseFloat(formData.poids_brut_kg) : null,
      poids_net_kg: formData.poids_net_kg ? parseFloat(formData.poids_net_kg) : null,
      volume_m3: formData.volume_m3 ? parseFloat(formData.volume_m3) : null,
      nombre_colis: formData.nombre_colis ? parseInt(formData.nombre_colis) : null,
      mode_fret: formData.mode_fret || null,
      lignes: [
        {
          article_id: articleInfo.id,
          quantite_declaree: parseFloat(formData.quantite_declaree),
          unite_mesure: articleInfo.unite_mesure,
          numero_lot: formData.numero_lot || null,
          date_fabrication: formData.date_fabrication || null,
          date_expiration: formData.date_expiration || null
        }
      ]
    }

    // Nettoyer les champs vides pour ne pas envoyer de chaînes vides là où c'est optionnel
    Object.keys(payload).forEach(key => {
      if (payload[key as keyof typeof payload] === '') {
        (payload as any)[key] = null
      }
    })

    try {
      await magasinAPI.createDeclaration(payload)
      toast.success('Déclaration créée avec succès')
      onSuccess()
    } catch (err: any) {
      console.error(err)
      toast.error(`Erreur: ${err.response?.data?.detail || "Erreur inconnue"}`);
    }
  }

  const InputField = ({ label, field, type = "text", required = false, placeholder = "" }: { label: string, field: keyof typeof formData, type?: string, required?: boolean, placeholder?: string }) => (
    <div>
      <label className="block text-sm font-bold text-slate-300 mb-1">{label} {required && '*'}</label>
      <input 
        type={type} 
        required={required}
        value={formData[field]}
        onChange={e => setFormData({...formData, [field]: e.target.value})}
        placeholder={placeholder}
        className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-sm"
      />
    </div>
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 rounded-2xl shadow-xl w-full max-w-4xl overflow-hidden animate-in zoom-in-95 duration-200 my-8">
        <div className="px-6 py-4 border-b border-slate-700 flex justify-between items-center bg-slate-800">
          <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            Nouvelle Déclaration (Connaissement)
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-400"><span className="material-symbols-outlined">close</span></button>
        </div>
        
        {/* Tabs */}
        <div className="flex border-b border-slate-700 px-6 pt-4 gap-6 bg-slate-800">
          {[
            { id: 'ident', label: 'Identification' },
            { id: 'navire', label: 'Navire & Ports' },
            { id: 'marchandise', label: 'Marchandise' },
            { id: 'parties', label: 'Parties & Douane' }
          ].map(t => (
            <button
              key={t.id}
              type="button"
              onClick={() => setActiveTab(t.id as any)}
              className={`pb-3 text-sm font-bold border-b-2 transition-colors ${activeTab === t.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-300'}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          
          {/* TAB 1 : IDENTIFICATION */}
          <div className={activeTab === 'ident' ? 'block' : 'hidden'}>
            <div className="grid grid-cols-2 gap-6">
              <InputField label="Numéro BL Interne" field="numero_bl" required placeholder="Ex: BL-2026-001" />
              <InputField label="Numéro BL Externe (Vrai BL)" field="numero_bl_externe" placeholder="Ex: MAEU123456789" />
              <div>
                <label className="block text-sm font-bold text-slate-300 mb-1">Client Propriétaire *</label>
                <select 
                  required
                  value={formData.client_id}
                  onChange={e => setFormData({...formData, client_id: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-sm"
                >
                  <option value="">Sélectionner un client...</option>
                  {clients.map(c => (
                    <option key={c.id} value={c.id}>{c.nom} {c.prenom}</option>
                  ))}
                </select>
              </div>
              <InputField label="Référence Booking" field="reference_booking" placeholder="Ex: BK-2026-001" />
              <InputField label="Numéro de Scellé" field="numero_scelle" placeholder="Ex: SC-789456" />
            </div>
          </div>

          {/* TAB 2 : NAVIRE & PORTS */}
          <div className={activeTab === 'navire' ? 'block' : 'hidden'}>
            <div className="grid grid-cols-2 gap-6">
              <InputField label="Nom du Navire" field="nom_navire" placeholder="Ex: MSC FANTASIA" />
              <InputField label="Numéro de Voyage" field="numero_voyage" placeholder="Ex: V-2026-A" />
              <InputField label="Port de Chargement" field="port_chargement" placeholder="Ex: Bangkok" />
              <InputField label="Port de Déchargement" field="port_dechargement" placeholder="Ex: Douala" />
              <div className="col-span-2">
                <InputField label="Lieu de Livraison Finale" field="lieu_livraison" placeholder="Ex: Magasin EVO-LOG Douala" />
              </div>
            </div>
          </div>

          {/* TAB 3 : MARCHANDISE */}
          <div className={activeTab === 'marchandise' ? 'block' : 'hidden'}>
            <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 mb-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-slate-300 mb-1">Code Article (7 chiffres) *</label>
                  <input 
                    type="text" 
                    required
                    pattern="\d{7}"
                    maxLength={7}
                    value={formData.code_article}
                    onChange={e => setFormData({...formData, code_article: e.target.value.replace(/\D/g, '')})}
                    placeholder="Saisissez le code numérique..."
                    className="w-full px-4 py-2 rounded-xl border border-slate-600 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none font-mono text-sm bg-slate-900"
                  />
                  {articleError && <p className="text-red-500 text-xs mt-1 font-bold">{articleError}</p>}
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-300 mb-1">
                    Quantité {articleInfo ? `(en ${articleInfo.unite_mesure})` : ''} *
                  </label>
                  <input 
                    type="number" step="0.001" required disabled={!articleInfo}
                    value={formData.quantite_declaree}
                    onChange={e => setFormData({...formData, quantite_declaree: e.target.value})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-600 outline-none disabled:bg-slate-900 text-sm font-bold"
                  />
                </div>
                <div className="col-span-2">
                  <div className="bg-slate-900 p-2 rounded-lg border border-slate-700 text-sm flex items-center">
                    {articleInfo ? (
                      <span><span className="font-bold text-emerald-600 mr-2">Produit reconnu:</span> {articleInfo.nom}</span>
                    ) : (
                      <span className="text-slate-400 italic">Le produit s'affichera ici automatiquement...</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <InputField label="Poids Brut (kg)" field="poids_brut_kg" type="number" />
              <InputField label="Poids Net (kg)" field="poids_net_kg" type="number" />
              <InputField label="Volume (m³)" field="volume_m3" type="number" />
              <InputField label="Nombre de Colis" field="nombre_colis" type="number" />
              <InputField label="Type Emballage" field="type_emballage" placeholder="Ex: Sacs de 50kg" />
            </div>

            <div className="mt-6 border-t border-slate-700 pt-4">
              <h4 className="text-sm font-bold text-slate-200 mb-4">Informations de Lot (Vrac / Sacs)</h4>
              <div className="grid grid-cols-3 gap-4">
                <InputField label="Numéro de Lot" field="numero_lot" placeholder="Ex: L-2026-001" />
                <InputField label="Date de Fabrication" field="date_fabrication" type="date" />
                <InputField label="Date d'Expiration" field="date_expiration" type="date" />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-bold text-slate-300 mb-1">Description Détaillée</label>
              <textarea 
                value={formData.description_marchandises}
                onChange={e => setFormData({...formData, description_marchandises: e.target.value})}
                className="w-full px-4 py-2 rounded-xl border border-slate-600 outline-none text-sm h-20 resize-none"
                placeholder="Description telle qu'écrite sur le BL..."
              />
            </div>
          </div>

          {/* TAB 4 : PARTIES & DOUANE */}
          <div className={activeTab === 'parties' ? 'block' : 'hidden'}>
            <div className="grid grid-cols-2 gap-6">
              <InputField label="Expéditeur (Shipper)" field="expediteur_shipper" />
              <InputField label="Destinataire (Consignee)" field="destinataire_consignee" />
              <InputField label="Notify Party" field="notify_party" />
              
              <div>
                <label className="block text-sm font-bold text-slate-300 mb-1">Mode de Fret</label>
                <select 
                  value={formData.mode_fret}
                  onChange={e => setFormData({...formData, mode_fret: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-600 outline-none text-sm"
                >
                  <option value="">Non spécifié</option>
                  <option value="PREPAID">Prepaid</option>
                  <option value="COLLECT">Collect</option>
                </select>
              </div>
              <InputField label="Code HS" field="code_hs" placeholder="Ex: 1006.30" />
              <InputField label="Numéro Déclaration Douane" field="numero_declaration_douane" placeholder="Ex: SYDONIA-12345" />
            </div>
          </div>

          <div className="flex justify-between items-center mt-8 pt-4 border-t border-slate-700">
            <div className="text-xs text-slate-400">
              * Champs obligatoires
            </div>
            <div className="flex gap-3">
              <button type="button" onClick={onClose} className="px-5 py-2.5 rounded-xl text-sm font-bold text-slate-400 hover:bg-slate-800 transition-colors">Annuler</button>
              <button 
                type="submit" 
                disabled={!articleInfo}
                className="px-5 py-2.5 rounded-xl text-sm font-bold bg-blue-600 hover:bg-blue-700 text-white transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Créer la Déclaration BL
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

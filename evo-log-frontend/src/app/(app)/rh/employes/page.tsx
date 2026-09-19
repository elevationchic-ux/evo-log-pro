'use client'

import React, { useState, useEffect } from 'react'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { Users, UserPlus, Download, Upload, Search, Filter, Mail, Phone, Briefcase, Calendar, CheckCircle2, AlertCircle, FileSpreadsheet, X } from 'lucide-react'
import { rhAPI } from '@/lib/api-client'
import { toast } from 'sonner'
import { CardSkeletonLoader } from '@/components/ui/Loaders'

export default function EmployesPage() {
  const [employes, setEmployes] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDept, setSelectedDept] = useState('TOUS')
  const [selectedStatut, setSelectedStatut] = useState('TOUS')

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [importFile, setImportFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  // New Employee Form State
  const [formData, setFormData] = useState({
    matricule: '',
    nom: '',
    prenom: '',
    email: '',
    telephone: '+237 ',
    poste: '',
    departement: 'LOGISTIQUE',
    date_embauche: new Date().toISOString().split('T')[0],
    type_contrat: 'CDI',
    salaire_base_xaf: 450000,
    statut: 'ACTIF'
  })

  useEffect(() => {
    fetchEmployes()
  }, [])

  const fetchEmployes = async () => {
    setLoading(true)
    try {
      const res = await rhAPI.getEmployes().catch(() => ({ data: [] }))
      const list = Array.isArray(res.data) ? res.data : (res.data?.items || (Array.isArray(res) ? res : []))
      setEmployes(list)
    } catch (err) {
      console.error('Erreur chargement employés:', err)
      toast.error('Impossible de charger la liste des employés')
      setEmployes([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const matriculeGen = formData.matricule || `EMP-2026-${Math.floor(100 + Math.random() * 900)}`
      await rhAPI.createEmploye({ ...formData, matricule: matriculeGen })
      toast.success(`Employé ${formData.prenom} ${formData.nom} créé avec succès !`)
      setShowCreateModal(false)
      setFormData({
        matricule: '',
        nom: '',
        prenom: '',
        email: '',
        telephone: '+237 ',
        poste: '',
        departement: 'LOGISTIQUE',
        date_embauche: new Date().toISOString().split('T')[0],
        type_contrat: 'CDI',
        salaire_base_xaf: 450000,
        statut: 'ACTIF'
      })
      fetchEmployes()
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création de l'employé")
    }
  }

  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!importFile) {
      toast.error('Veuillez sélectionner un fichier Excel ou CSV')
      return
    }
    setUploading(true)
    try {
      const form = new FormData()
      form.append('file', importFile)
      const res = await rhAPI.importEmployesExcel(form)
      toast.success(res?.data?.detail || res?.data?.message || 'Importation terminée avec succès !')
      setShowImportModal(false)
      setImportFile(null)
      fetchEmployes()
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'importation du fichier")
    } finally {
      setUploading(false)
    }
  }

  const handleExportCSV = () => {
    if (employes.length === 0) {
      toast.error('Aucune donnée à exporter')
      return
    }
    const header = 'Matricule,Nom,Prenom,Email,Telephone,Poste,Departement,DateEmbauche,TypeContrat,SalaireBaseXAF,Statut\n'
    const rows = employes.map(e => 
      `"${e.matricule || ''}","${e.nom || ''}","${e.prenom || ''}","${e.email || ''}","${e.telephone || ''}","${e.poste || ''}","${e.departement || ''}","${e.date_embauche || ''}","${e.type_contrat || ''}","${e.salaire_base_xaf || 0}","${e.statut || ''}"`
    ).join('\n')
    
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `Annuaire_Employes_EVO-LOG_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success('Annuaire du personnel téléchargé en CSV Excel !')
  }

  const safeEmployes = Array.isArray(employes) ? employes : []
  const filteredEmployes = safeEmployes.filter(e => {
    const query = searchTerm.toLowerCase()
    const matchSearch = `${e.nom} ${e.prenom} ${e.matricule} ${e.email} ${e.poste}`.toLowerCase().includes(query)
    const matchDept = selectedDept === 'TOUS' || e.departement === selectedDept
    const matchStatut = selectedStatut === 'TOUS' || e.statut === selectedStatut
    return matchSearch && matchDept && matchStatut
  })

  const deptList = Array.from(new Set(safeEmployes.map(e => e.departement).filter(Boolean)))

  return (
    <ModuleLayout module="rh">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6">
        
        {/* Header Title Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4 bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div>
            <h1 className="text-3xl font-black text-slate-900 dark:text-white flex items-center gap-3">
              <Users className="w-8 h-8 text-pink-600 dark:text-pink-400" />
              Annuaire & Gestion des Employés
            </h1>
            <p className="text-slate-500 dark:text-slate-400 mt-1">
              Gérez le registre du personnel, importez/exportez la liste des collaborateurs EVO-LOG.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleExportCSV}
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold rounded-xl text-sm transition-colors shadow-sm"
            >
              <Download className="w-4 h-4 text-emerald-600" />
              Exporter Excel / CSV
            </button>

            <button
              onClick={() => setShowImportModal(true)}
              className="flex items-center gap-2 px-4 py-2.5 bg-pink-50 hover:bg-pink-100 dark:bg-pink-950/40 dark:hover:bg-pink-900/60 text-pink-700 dark:text-pink-300 font-bold rounded-xl text-sm transition-colors border border-pink-200 dark:border-pink-800 shadow-sm"
            >
              <Upload className="w-4 h-4 text-pink-600" />
              Importer Fichier Excel
            </button>

            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 text-white font-bold rounded-xl text-sm transition-all shadow-md shadow-pink-500/20"
            >
              <UserPlus className="w-4 h-4" />
              Ajouter un Employé
            </button>
          </div>
        </div>

        {/* Filters & Search */}
        <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 mb-6 flex flex-col md:flex-row gap-4 justify-between items-center shadow-sm">
          <div className="relative w-full md:w-96">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Rechercher par nom, matricule, poste, email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-pink-500"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <div className="flex items-center gap-2 text-sm text-slate-500 font-medium">
              <Filter className="w-4 h-4" />
              Département:
            </div>
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm font-semibold text-slate-800 dark:text-slate-200 focus:outline-none"
            >
              <option value="TOUS">Tous les départements</option>
              {deptList.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>

            <select
              value={selectedStatut}
              onChange={(e) => setSelectedStatut(e.target.value)}
              className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm font-semibold text-slate-800 dark:text-slate-200 focus:outline-none"
            >
              <option value="TOUS">Tous les statuts</option>
              <option value="ACTIF">ACTIF</option>
              <option value="CONGE">CONGÉ</option>
              <option value="SUSPENDU">SUSPENDU</option>
            </select>
          </div>
        </div>

        {/* Datatable Employees */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <CardSkeletonLoader key={i} />
            ))}
          </div>
        ) : filteredEmployes.length === 0 ? (
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-12 text-center border border-slate-200 dark:border-slate-800 shadow-sm">
            <Users className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-700 dark:text-slate-300">Aucun employé trouvé</h3>
            <p className="text-sm text-slate-400 mt-1">Modifiez vos critères de recherche ou ajoutez un nouveau collaborateur.</p>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700 text-xs font-black text-slate-500 uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-4">Collaborateur</th>
                    <th className="px-6 py-4">Poste & Dpt</th>
                    <th className="px-6 py-4">Contacts</th>
                    <th className="px-6 py-4">Contrat</th>
                    <th className="px-6 py-4">Salaire Base</th>
                    <th className="px-6 py-4">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-sm">
                  {filteredEmployes.map((emp) => (
                    <tr key={emp.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-pink-500 to-rose-500 text-white font-black text-sm flex items-center justify-center shadow-sm">
                            {emp.prenom?.[0] || ''}{emp.nom?.[0] || 'E'}
                          </div>
                          <div>
                            <p className="font-bold text-slate-900 dark:text-slate-100">{emp.prenom} {emp.nom}</p>
                            <p className="text-xs font-mono font-bold text-pink-600 dark:text-pink-400">{emp.matricule}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <p className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                          <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                          {emp.poste}
                        </p>
                        <span className="inline-block mt-1 px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-xs font-semibold rounded-md">
                          {emp.departement}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-xs text-slate-600 dark:text-slate-300 flex items-center gap-1">
                          <Mail className="w-3.5 h-3.5 text-slate-400" />
                          {emp.email}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1 mt-0.5">
                          <Phone className="w-3.5 h-3.5 text-slate-400" />
                          {emp.telephone || '-'}
                        </p>
                      </td>
                      <td className="px-6 py-4">
                        <p className="font-bold text-slate-700 dark:text-slate-300">{emp.type_contrat || 'CDI'}</p>
                        <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                          <Calendar className="w-3.5 h-3.5 text-slate-400" />
                          Depuis {emp.date_embauche ? new Date(emp.date_embauche).toLocaleDateString('fr-FR') : '-'}
                        </p>
                      </td>
                      <td className="px-6 py-4 font-mono font-bold text-emerald-600 dark:text-emerald-400">
                        {Number(emp.salaire_base_xaf || 0).toLocaleString('fr-FR')} XAF
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-black uppercase ${
                          emp.statut === 'ACTIF' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' :
                          emp.statut === 'CONGE' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' :
                          'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                        }`}>
                          <CheckCircle2 className="w-3 h-3" />
                          {emp.statut || 'ACTIF'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Modal Créer Employé */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in-95 duration-200">
              <div className="flex justify-between items-center pb-4 border-b border-slate-100 dark:border-slate-800">
                <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <UserPlus className="w-6 h-6 text-pink-600" />
                  Nouveau Collaborateur EVO-LOG
                </h3>
                <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateSubmit} className="space-y-4 mt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Nom *</label>
                    <input
                      type="text"
                      required
                      value={formData.nom}
                      onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold"
                      placeholder="Ex: MVONDO"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Prénom *</label>
                    <input
                      type="text"
                      required
                      value={formData.prenom}
                      onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold"
                      placeholder="Ex: Jean-Marc"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Email Professionnel *</label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold"
                      placeholder="Ex: mvondo@evo-log.cm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Téléphone</label>
                    <input
                      type="text"
                      value={formData.telephone}
                      onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold"
                      placeholder="+237 677 00 11 22"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Poste *</label>
                    <input
                      type="text"
                      required
                      value={formData.poste}
                      onChange={(e) => setFormData({ ...formData, poste: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold"
                      placeholder="Ex: Responsable Operations Portuaires"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Département *</label>
                    <select
                      value={formData.departement}
                      onChange={(e) => setFormData({ ...formData, departement: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold"
                    >
                      <option value="LOGISTIQUE">LOGISTIQUE</option>
                      <option value="TRANSPORT">TRANSPORT</option>
                      <option value="ACCONAGE">ACCONAGE</option>
                      <option value="TRANSIT">TRANSIT</option>
                      <option value="FINANCE">FINANCE</option>
                      <option value="RH">RH</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Type de Contrat</label>
                    <select
                      value={formData.type_contrat}
                      onChange={(e) => setFormData({ ...formData, type_contrat: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold"
                    >
                      <option value="CDI">CDI</option>
                      <option value="CDD">CDD</option>
                      <option value="Stage">Stage</option>
                      <option value="Prestation">Prestation</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Salaire de Base (XAF)</label>
                    <input
                      type="number"
                      value={formData.salaire_base_xaf}
                      onChange={(e) => setFormData({ ...formData, salaire_base_xaf: Number(e.target.value) })}
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold font-mono"
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold rounded-xl text-sm"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-pink-600 hover:bg-pink-700 text-white font-bold rounded-xl text-sm shadow-md"
                  >
                    Enregistrer l'Employé
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal Importer Fichier Excel */}
        {showImportModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in-95 duration-200">
              <div className="flex justify-between items-center pb-4 border-b border-slate-100 dark:border-slate-800">
                <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <FileSpreadsheet className="w-6 h-6 text-pink-600" />
                  Importer Fichier Excel / CSV
                </h3>
                <button onClick={() => setShowImportModal(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleImportSubmit} className="space-y-4 mt-4">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Sélectionnez un fichier Excel (`.xlsx`, `.xls`) ou CSV contenant la liste de vos collaborateurs (Colonnes : Nom, Prénom, Email, Poste).
                </p>

                <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-6 text-center hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer relative">
                  <input
                    type="file"
                    accept=".csv, .xlsx, .xls"
                    onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  <FileSpreadsheet className="w-10 h-10 text-pink-500 mx-auto mb-2" />
                  <p className="font-bold text-sm text-slate-700 dark:text-slate-300">
                    {importFile ? importFile.name : 'Cliquez ou glissez votre fichier ici'}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">Formats acceptés : CSV, XLSX, XLS</p>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowImportModal(false)}
                    className="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold rounded-xl text-sm"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    disabled={uploading}
                    className="px-5 py-2 bg-pink-600 hover:bg-pink-700 text-white font-bold rounded-xl text-sm shadow-md disabled:opacity-50"
                  >
                    {uploading ? 'Importation en cours...' : 'Lancer l\'Importation'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

      </div>
    </ModuleLayout>
  )
}

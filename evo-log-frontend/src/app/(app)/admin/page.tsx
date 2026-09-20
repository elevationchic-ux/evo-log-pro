'use client'

import React, { useState } from 'react'
import {
  Users,
  ShieldCheck,
  Building,
  KeyRound,
  UserPlus,
  Search,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Sliders,
  FileText,
  Lock,
  Mail,
  User as UserIcon,
  Building2,
  Sparkles,
  Plus,
  AlertTriangle,
  ArrowRight
} from 'lucide-react'
import { adminAPI, authAPI } from '@/lib/api-client'
import { toast } from 'sonner'

interface SystemUser {
  id: string
  email: string
  nom_complet: string
  role: string
  roles: string[]
  departement: string
  telephone?: string
  is_active: boolean
  must_change_password: boolean
  created_at: string
}

export default function AdminHubPage() {
  const [activeTab, setActiveTab] = useState<'users' | 'rbac' | 'agencies' | 'audit'>('users')
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState('ALL')

  // Initial Seeded Users List
  const [users, setUsers] = useState<SystemUser[]>([] /* [
    {
      id: 'usr-001',
      email: 'admin@evo-log.cm',
      nom_complet: 'Administrateur Système CADC',
      role: 'ADMIN',
      roles: ['ADMIN', 'DIRECTEUR_LOGISTIQUE'],
      departement: 'DIRECTION',
      telephone: '+237 690 00 00 01',
      is_active: true,
      must_change_password: false,
      created_at: '2026-01-01',
    },
    {
      id: 'usr-002',
      email: 'kamga@evo-log.cm',
      nom_complet: 'Monsieur Kamga',
      role: 'CHAUFFEUR',
      roles: ['CHAUFFEUR'],
      departement: 'TRANSPORT',
      telephone: '+237 670 12 34 56',
      is_active: true,
      must_change_password: true,
      created_at: '2026-02-10',
    },
    {
      id: 'usr-003',
      email: 'magasinier@evo-log.cm',
      nom_complet: 'Chef Magasinier MAG3',
      role: 'MAGASINIER',
      roles: ['MAGASINIER', 'MAGASIN'],
      departement: 'ENTREPÔT',
      telephone: '+237 699 88 77 66',
      is_active: true,
      must_change_password: true,
      created_at: '2026-02-15',
    },
    {
      id: 'usr-004',
      email: 'financier@evo-log.cm',
      nom_complet: 'Responsable Financier',
      role: 'FINANCE',
      roles: ['FINANCE', 'FINANCIER'],
      departement: 'COMPTABILITÉ',
      telephone: '+237 677 55 44 33',
      is_active: true,
      must_change_password: true,
      created_at: '2026-03-01',
    },
    {
      id: 'usr-005',
      email: 'qhse@evo-log.cm',
      nom_complet: 'Inspecteur QHSE Port',
      role: 'QHSE',
      roles: ['QHSE'],
      departement: 'SÉCURITÉ',
      telephone: '+237 691 22 33 44',
      is_active: true,
      must_change_password: true,
      created_at: '2026-03-05',
    },
    {
      id: 'usr-006',
      email: 'douane@evo-log.cm',
      nom_complet: 'Déclarant en Douane',
      role: 'DOUANE',
      roles: ['DOUANE', 'TRANSIT'],
      departement: 'TRANSIT',
      telephone: '+237 678 99 00 11',
      is_active: true,
      must_change_password: true,
      created_at: '2026-03-10',
    },
    {
      id: 'usr-007',
      email: 'parc@evo-log.cm',
      nom_complet: 'Gestionnaire Parc & Flotte',
      role: 'PARC',
      roles: ['PARC'],
      departement: 'PARC & GARAGE',
      telephone: '+237 694 44 55 66',
      is_active: true,
      must_change_password: true,
      created_at: '2026-03-12',
    },
    {
      id: 'usr-008',
      email: 'auditor@evo-log.cm',
      nom_complet: 'Auditeur Interne ERP',
      role: 'AUDITOR',
      roles: ['AUDITOR'],
      departement: 'AUDIT & COMPLIANCE',
      telephone: '+237 695 11 22 33',
      is_active: true,
      must_change_password: true,
      created_at: '2026-03-15',
    },
  ] */)

  // New User Creation Modal State
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newNomComplet, setNewNomComplet] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [newRole, setNewRole] = useState('CHAUFFEUR')
  const [newDepartement, setNewDepartement] = useState('LOGISTIQUE')
  const [newTelephone, setNewTelephone] = useState('')
  const [newModulesAllowed, setNewModulesAllowed] = useState<string[]>(['transport', 'tracking', 'fuel-guard'])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const ALL_AVAILABLE_MODULES = [
    { id: 'transport', label: 'K-Transport' },
    { id: 'magasin', label: 'K-Magasin' },
    { id: 'finance', label: 'K-Finance' },
    { id: 'acconage', label: 'K-Acconage' },
    { id: 'qhse', label: 'K-QHSE' },
    { id: 'transit', label: 'K-Transit' },
    { id: 'maintenance', label: 'K-Maintenance' },
    { id: 'cotations', label: 'K-Cotation' },
    { id: 'tracking', label: 'K-Tracking & e-POD' },
    { id: 'fuel-guard', label: 'K-FuelGuard' },
    { id: 'procurement', label: 'K-Procurement' },
    { id: 'compliance', label: 'K-Compliance' },
    { id: 'bi', label: 'K-Analytics BI' },
    { id: 'master-data', label: 'Gestion des Tiers' },
    { id: 'rh', label: 'Ressources Humaines' },
    { id: 'client-portal', label: 'Portail Client B2B' },
  ]

  // Roles Matrix State
  const [rolesList, setRolesList] = useState([
    { id: 'ADMIN', name: 'Administrateur', modules: ['TOUS LES MODULES'], count: 1 },
    { id: 'CHAUFFEUR', name: 'Chauffeur / Transporteur', modules: ['K-Transport', 'Tracking e-POD'], count: 1 },
    { id: 'MAGASINIER', name: 'Gestionnaire Entrepôt MAG3', modules: ['K-Magasin', 'Tiers'], count: 1 },
    { id: 'FINANCE', name: 'Responsable Finance', modules: ['K-Finance', 'Facturation'], count: 1 },
    { id: 'QHSE', name: 'Inspecteur QHSE', modules: ['K-QHSE', 'Conformité'], count: 1 },
    { id: 'DOUANE', name: 'Agent Douane & Transit', modules: ['K-Transit', 'Documents'], count: 1 },
  ])

  // Agencies List
  const [agencies] = useState([
    { id: 1, code: 'DLA-PORT', name: 'Agence Portuaire Douala (Siège)', ville: 'Douala', statut: 'ACTIF', usersCount: 4 },
    { id: 2, code: 'KRB-DEEP', name: 'Succursale Kribi Conteneurs', ville: 'Kribi', statut: 'ACTIF', usersCount: 2 },
    { id: 3, code: 'YDE-CENT', name: 'Bureau Régional Yaoundé', ville: 'Yaoundé', statut: 'ACTIF', usersCount: 1 },
    { id: 4, code: 'GAR-NORTH', name: 'Hangar Logistique Garoua', ville: 'Garoua', statut: 'MAINTENANCE', usersCount: 1 },
  ])

  // Audit Logs List
  const [auditLogs] = useState([
    { id: 'LOG-109', action: 'Création Compte Utilisateur', user: 'admin@evo-log.cm', target: 'kamga@evo-log.cm', timestamp: '22/07/2026 01:15', status: 'SUCCESS' },
    { id: 'LOG-108', action: 'Changement Obligatoire Mot de Passe', user: 'kamga@evo-log.cm', target: 'kamga@evo-log.cm', timestamp: '22/07/2026 01:05', status: 'SUCCESS' },
    { id: 'LOG-107', action: 'Connexion Réussie (NextAuth)', user: 'admin@evo-log.cm', target: 'Système ERP', timestamp: '22/07/2026 00:45', status: 'SUCCESS' },
    { id: 'LOG-106', action: 'Modification Matrice RBAC', user: 'admin@evo-log.cm', target: 'Rôle MAGASINIER', timestamp: '21/07/2026 23:30', status: 'SUCCESS' },
  ])

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newEmail || !newNomComplet) {
      toast.error("Veuillez remplir le nom et l'email de l'utilisateur.")
      return
    }

    setIsSubmitting(true)
    try {
      const password = window.prompt('Mot de passe initial (minimum 12 caractères) :')
      if (!password || password.length < 12) {
        toast.error('Un mot de passe initial de 12 caractères minimum est requis.')
        return
      }
      try {
        await adminAPI.createUser({
          email: newEmail,
          username: newEmail,
          password,
          nom_complet: newNomComplet,
          role: newRole,
          roles: [newRole],
          modules_allowed: newModulesAllowed,
          departement: newDepartement,
          telephone: newTelephone
        })
      } catch (err) {
        toast.error("Le compte n'a pas pu être créé car l'API est indisponible.")
        return
      }

      const newUserObj: SystemUser = {
        id: `usr-${String(users.length + 1).padStart(3, '0')}`,
        email: newEmail.toLowerCase().trim ? newEmail.toLowerCase().trim() : newEmail,
        nom_complet: newNomComplet,
        role: newRole,
        roles: [newRole],
        departement: newDepartement,
        telephone: newTelephone || '+237 600 00 00 00',
        is_active: true,
        must_change_password: true,
        created_at: new Date().toISOString().split('T')[0]
      }

      setUsers([newUserObj, ...users])
      toast.success(`Compte créé avec succès pour ${newNomComplet}.`)
      
      // Reset form
      setNewNomComplet('')
      setNewEmail('')
      setNewRole('CHAUFFEUR')
      setNewTelephone('')
      setNewModulesAllowed(['transport', 'tracking', 'fuel-guard'])
      setShowCreateModal(false)
    } catch (error: any) {
      toast.error(error?.message || "Erreur lors de la création du compte.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const toggleUserStatus = (userId: string) => {
    setUsers(users.map(u => {
      if (u.id === userId) {
        const updated = !u.is_active
        toast.info(`Statut du compte ${u.email} mis à jour : ${updated ? 'Actif' : 'Désactivé'}`)
        return { ...u, is_active: updated }
      }
      return u
    }))
  }

  const handleResetPassword = (email: string) => {
    toast.info(`Utilisez la gestion utilisateurs pour définir un nouveau mot de passe pour ${email}.`)
  }

  const filteredUsers = users.filter(u => {
    const matchesSearch = u.nom_complet.toLowerCase().includes(searchQuery.toLowerCase()) || u.email.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRole = roleFilter === 'ALL' || u.role === roleFilter
    return matchesSearch && matchesRole
  })

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12">
      {/* Header Administration */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-2xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" /> Centre d'Administration ERP • CADC
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Administration Système & RBAC
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Gestion centrale des identités, droits d'accès rattachés aux modules, agences et journaux d'audit.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-5 py-3 bg-gradient-to-r from-amber-500 via-yellow-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-black text-sm rounded-xl flex items-center justify-center gap-2 shadow-xl shadow-amber-500/20 transition-all cursor-pointer active:scale-95"
        >
          <UserPlus className="w-4 h-4" /> Créer un Nouvel Utilisateur
        </button>
      </div>

      {/* KPI Cards Admin */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl flex items-center gap-4 shadow-xl">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center shrink-0">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Comptes Actifs</span>
            <div className="text-2xl font-black text-white mt-0.5">{users.filter(u => u.is_active).length} / {users.length}</div>
            <span className="text-[11px] text-emerald-400 font-semibold">Seul l'Admin crée les comptes</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl flex items-center gap-4 shadow-xl">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Matrice de Rôles</span>
            <div className="text-2xl font-black text-amber-300 mt-0.5">{rolesList.length} Rôles RBAC</div>
            <span className="text-[11px] text-slate-400">Accès restreint par module</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl flex items-center gap-4 shadow-xl">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center justify-center shrink-0">
            <Building className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Succursales & Agences</span>
            <div className="text-2xl font-black text-cyan-300 mt-0.5">{agencies.length} Agences</div>
            <span className="text-[11px] text-cyan-400 font-semibold">Douala, Kribi, Yaoundé, Garoua</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl flex items-center gap-4 shadow-xl">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <KeyRound className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Renouvellement 90j</span>
            <div className="text-2xl font-black text-emerald-300 mt-0.5">Mot de Passe Fort</div>
            <span className="text-[11px] text-amber-400 font-semibold">Expiration trimestrielle</span>
          </div>
        </div>
      </div>

      {/* Tabs Menu */}
      <div className="flex border-b border-slate-800 gap-2 overflow-x-auto pb-1">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex items-center gap-2 px-5 py-3 rounded-t-xl font-bold text-xs uppercase tracking-wider transition ${
            activeTab === 'users'
              ? 'bg-slate-900 text-amber-400 border-t-2 border-amber-400 border-x border-slate-800'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <Users className="w-4 h-4" /> Utilisateurs & Identités ({users.length})
        </button>

        <button
          onClick={() => setActiveTab('rbac')}
          className={`flex items-center gap-2 px-5 py-3 rounded-t-xl font-bold text-xs uppercase tracking-wider transition ${
            activeTab === 'rbac'
              ? 'bg-slate-900 text-amber-400 border-t-2 border-amber-400 border-x border-slate-800'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <ShieldCheck className="w-4 h-4" /> Config Rôles RBAC ({rolesList.length})
        </button>

        <button
          onClick={() => setActiveTab('agencies')}
          className={`flex items-center gap-2 px-5 py-3 rounded-t-xl font-bold text-xs uppercase tracking-wider transition ${
            activeTab === 'agencies'
              ? 'bg-slate-900 text-amber-400 border-t-2 border-amber-400 border-x border-slate-800'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <Building className="w-4 h-4" /> Agences & Regional Hubs ({agencies.length})
        </button>

        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center gap-2 px-5 py-3 rounded-t-xl font-bold text-xs uppercase tracking-wider transition ${
            activeTab === 'audit'
              ? 'bg-slate-900 text-amber-400 border-t-2 border-amber-400 border-x border-slate-800'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <FileText className="w-4 h-4" /> Journal d'Audit ({auditLogs.length})
        </button>
      </div>

      {/* Tab 1: Utilisateurs */}
      {activeTab === 'users' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Rechercher par nom ou email..."
                className="w-full h-10 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <span className="text-xs font-bold text-slate-400 uppercase">Filtrer rôle:</span>
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
              >
                <option value="ALL">Tous les rôles</option>
                <option value="ADMIN">ADMIN</option>
                <option value="CHAUFFEUR">CHAUFFEUR</option>
                <option value="MAGASINIER">MAGASINIER</option>
                <option value="FINANCE">FINANCE</option>
                <option value="QHSE">QHSE</option>
                <option value="DOUANE">DOUANE</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto border border-slate-800 rounded-2xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="p-4">Utilisateur / Email</th>
                  <th className="p-4">Rôle Attribué</th>
                  <th className="p-4">Département</th>
                  <th className="p-4">Mot de Passe Expiration</th>
                  <th className="p-4">Statut</th>
                  <th className="p-4 text-right">Actions Admin</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/40 transition">
                    <td className="p-4 font-semibold text-slate-100">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-amber-400">
                          {u.nom_complet.charAt(0)}
                        </div>
                        <div>
                          <div className="font-bold text-slate-100">{u.nom_complet}</div>
                          <div className="text-[11px] text-slate-400 font-mono">{u.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 font-bold text-[11px] uppercase">
                        {u.role}
                      </span>
                    </td>
                    <td className="p-4 text-slate-300 font-mono">{u.departement}</td>
                    <td className="p-4 text-slate-300">
                      {u.must_change_password ? (
                        <span className="text-amber-400 font-semibold flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5" /> Réinitialisation requise
                        </span>
                      ) : (
                        <span className="text-emerald-400 font-semibold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Fort (Valide 90j)
                        </span>
                      )}
                    </td>
                    <td className="p-4">
                      {u.is_active ? (
                        <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold text-[10px]">
                          ACTIF
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/30 font-bold text-[10px]">
                          SUSPENDU
                        </span>
                      )}
                    </td>
                    <td className="p-4 text-right space-x-2">
                      <button
                        onClick={() => handleResetPassword(u.email)}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-lg font-semibold text-[11px] transition cursor-pointer"
                        title="Réinitialiser le mot de passe"
                      >
                        Reset Password
                      </button>
                      <button
                        onClick={() => toggleUserStatus(u.id)}
                        className={`px-2.5 py-1 rounded-lg font-semibold text-[11px] transition cursor-pointer ${
                          u.is_active
                            ? 'bg-red-950/60 text-red-300 hover:bg-red-900 border border-red-500/30'
                            : 'bg-emerald-950/60 text-emerald-300 hover:bg-emerald-900 border border-emerald-500/30'
                        }`}
                      >
                        {u.is_active ? 'Suspendre' : 'Activer'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Matrice RBAC */}
      {activeTab === 'rbac' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-amber-400" /> Matrice des Rôles & Permissions par Module
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Chaque rôle rattaché donne un accès exclusif à son module dédié.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rolesList.map((r) => (
              <div key={r.id} className="bg-slate-950 border border-slate-800 p-5 rounded-2xl space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 font-bold text-xs">
                    {r.id}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">{r.count} Utilisateur(s)</span>
                </div>
                <h3 className="text-base font-bold text-white">{r.name}</h3>
                <div className="text-xs text-slate-400">
                  <span className="block font-semibold text-slate-300 mb-1">Modules Autorisés :</span>
                  <div className="flex flex-wrap gap-1.5">
                    {r.modules.map((m, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-200 text-[11px] font-mono">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Agences */}
      {activeTab === 'agencies' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Building className="w-5 h-5 text-cyan-400" /> Regional Hubs & Succursales CADC
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Gestion des agences régionales EVO-LOG au Cameroun (Douala Port, Kribi, Yaoundé, Garoua).
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {agencies.map((a) => (
              <div key={a.id} className="bg-slate-950 border border-slate-800 p-5 rounded-2xl flex items-center justify-between shadow-lg">
                <div>
                  <span className="text-xs font-mono text-cyan-400 font-bold">{a.code}</span>
                  <h3 className="text-base font-bold text-white mt-0.5">{a.name}</h3>
                  <div className="text-xs text-slate-400 mt-1">Ville: {a.ville} • Utilisateurs: {a.usersCount}</div>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                  a.statut === 'ACTIF' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                }`}>
                  {a.statut}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Audit */}
      {activeTab === 'audit' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-emerald-400" /> Traçabilité & Journal de Sécurité ERP
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Audits en temps réel des actions administrateurs et accès utilisateurs.
              </p>
            </div>
          </div>

          <div className="divide-y divide-slate-800/80 font-sans">
            {auditLogs.map((log) => (
              <div key={log.id} className="py-3.5 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center font-mono text-xs font-bold">
                    ✓
                  </div>
                  <div>
                    <div className="font-bold text-slate-100 text-xs">{log.action}</div>
                    <div className="text-[11px] text-slate-400 font-mono">Par: {log.user} → Cible: {log.target}</div>
                  </div>
                </div>
                <span className="text-xs text-slate-400 font-mono">{log.timestamp}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal Création Utilisateur par l'Admin */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-amber-500/40 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl space-y-5 animate-in zoom-in-95 duration-300">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2 text-amber-400 font-bold text-base">
                <UserPlus className="w-5 h-5" /> Créer un Utilisateur ERP
              </div>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-white">
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Nom Complet</label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={newNomComplet}
                    onChange={(e) => setNewNomComplet(e.target.value)}
                    placeholder="ex: Monsieur Kamga"
                    className="w-full h-10 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Email Institutionnel / Identifiant</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    placeholder="kamga@evo-log.cm"
                    className="w-full h-10 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Rôle Principal</label>
                <select
                  value={newRole}
                  onChange={(e) => {
                    const role = e.target.value;
                    setNewRole(role);
                    if (role === 'CHAUFFEUR') setNewModulesAllowed(['transport', 'tracking', 'fuel-guard']);
                    else if (role === 'MAGASINIER') setNewModulesAllowed(['magasin', 'master-data']);
                    else if (role === 'FINANCE') setNewModulesAllowed(['finance', 'cotations', 'procurement']);
                    else if (role === 'QHSE') setNewModulesAllowed(['qhse', 'compliance']);
                    else if (role === 'DOUANE') setNewModulesAllowed(['transit', 'master-data', 'acconage']);
                    else if (role === 'PARC') setNewModulesAllowed(['parc', 'transport', 'maintenance', 'fuel-guard']);
                    else if (role === 'AUDITOR') setNewModulesAllowed(['audit', 'compliance', 'bi']);
                    else if (role === 'ADMIN') setNewModulesAllowed(ALL_AVAILABLE_MODULES.map(m => m.id));
                  }}
                  className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500 font-semibold"
                >
                  <option value="CHAUFFEUR">CHAUFFEUR (Accès restreint au Transport & Suivi)</option>
                  <option value="MAGASINIER">MAGASINIER (Accès restreint à l'Entrepôt)</option>
                  <option value="FINANCE">FINANCE (Accès restreint à la Comptabilité & Cotation)</option>
                  <option value="QHSE">QHSE (Accès restreint à la Sécurité & Conformité)</option>
                  <option value="DOUANE">DOUANE / TRANSIT (Accès restreint aux Déclarations & Acconage)</option>
                  <option value="PARC">PARC (Accès restreint à la Flotte & Maintenance)</option>
                  <option value="AUDITOR">AUDITOR (Accès restreint à l'Audit, Conformité & BI)</option>
                  <option value="ADMIN">ADMIN (Accès Total à Tous les Modules)</option>
                </select>
              </div>

              {/* Sélection interactive des modules autorisés */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-bold text-amber-400 uppercase">
                    Modules Autorisés pour ce Profil ({newModulesAllowed.length})
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      if (newModulesAllowed.length === ALL_AVAILABLE_MODULES.length) {
                        setNewModulesAllowed([]);
                      } else {
                        setNewModulesAllowed(ALL_AVAILABLE_MODULES.map(m => m.id));
                      }
                    }}
                    className="text-[10px] text-amber-300 hover:underline font-mono"
                  >
                    {newModulesAllowed.length === ALL_AVAILABLE_MODULES.length ? "Tout désélectionner" : "Tout sélectionner"}
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2 p-3 bg-slate-950 border border-slate-800 rounded-2xl max-h-36 overflow-y-auto">
                  {ALL_AVAILABLE_MODULES.map((mod) => (
                    <label key={mod.id} className="flex items-center gap-2 text-[11px] text-slate-300 hover:text-white cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={newModulesAllowed.includes(mod.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewModulesAllowed([...newModulesAllowed, mod.id]);
                          } else {
                            setNewModulesAllowed(newModulesAllowed.filter(m => m !== mod.id));
                          }
                        }}
                        className="w-3.5 h-3.5 rounded border-slate-700 bg-slate-900 text-amber-500 focus:ring-amber-500"
                      />
                      <span className="truncate">{mod.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Département</label>
                <input
                  type="text"
                  value={newDepartement}
                  onChange={(e) => setNewDepartement(e.target.value)}
                  placeholder="ex: TRANSPORT, ENTREPÔT, FINANCE"
                  className="w-full h-10 px-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-[11px] font-semibold flex items-center gap-2">
                <Lock className="w-4 h-4 shrink-0" />
                <span>Un mot de passe initial sera demandé et ne sera jamais affiché dans cette interface.</span>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-black rounded-xl text-xs shadow-xl shadow-amber-500/20 transition-all cursor-pointer"
              >
                {isSubmitting ? 'Création en cours...' : 'Créer le Compte Utilisateur'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

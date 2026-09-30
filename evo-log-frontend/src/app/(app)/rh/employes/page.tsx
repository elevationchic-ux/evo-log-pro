'use client'

import React, { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Users, UserPlus, Download, Upload, Search, Mail, Phone, Briefcase,
  Calendar, FileSpreadsheet, X, RefreshCw, Loader2, Copy, AlertTriangle,
  Plane, KeyRound, Info,
} from 'lucide-react'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { apiClient, rhAPI } from '@/lib/api-client'
import { useSettings } from '@/components/layout/SettingsProvider'
import { toast } from 'sonner'

/**
 * Annuaire du personnel.
 *
 * La fiche affichée est exactement celle que l'API renvoie (`_employee_dict`) :
 * un seul champ d'identite `full_name`, un contrat portant (type, dates,
 * salaire) ou rien du tout. Les colonnes sans donnee restent vides : un CDI par
 * defaut ou un salaire a 0 pretendrait une situation sociale que personne n'a
 * saisie.
 */

interface Fiche {
  id: number
  username: string
  email: string
  full_name: string | null
  matricule: string | null
  phone: string | null
  poste: string | null
  departement: string | null
  date_embauche: string | null
  type_contrat: string | null
  date_fin_contrat: string | null
  salaire_base: number | null
  devise: string | null
  statut: string | null
  en_conge: boolean
  is_active: boolean
  temporary_password?: string
  avertissements?: string[]
}

interface RoleOption {
  name: string
  label: string
}

interface ImportImporte {
  ligne: number
  matricule: string | null
  full_name: string | null
  email: string
  temporary_password: string
  avertissements: string[]
}

interface ImportRejet {
  ligne: number
  raison: string
}

interface ImportResultat {
  importes: ImportImporte[]
  rejets: ImportRejet[]
  total_lignes: number
  message: string
  fichier: string | null
}

// Le backend n'admet que ces quatre types (ContratService.TYPES_CONTRAT).
// "Prestation", propose par l'ancienne maquette, aurait ete refuse en 400.
const TYPES_CONTRAT = ['CDI', 'CDD', 'STAGE', 'APPRENTISSAGE']
const TYPES_AVEC_FIN = ['CDD', 'STAGE', 'APPRENTISSAGE']

// Statuts reels de la colonne contrats_travail.statut, completee par le
// "inactif" du compte synthetise par l'API.
const STATUTS: Record<string, { fr: string; en: string; cls: string }> = {
  actif: { fr: 'Actif', en: 'Active', cls: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30' },
  suspendu: { fr: 'Suspendu', en: 'Suspended', cls: 'text-amber-400 bg-amber-400/10 border-amber-400/30' },
  expire: { fr: 'Expiré', en: 'Expired', cls: 'text-orange-400 bg-orange-400/10 border-orange-400/30' },
  resilie: { fr: 'Résilié', en: 'Terminated', cls: 'text-red-400 bg-red-400/10 border-red-400/30' },
  inactif: { fr: 'Compte désactivé', en: 'Account disabled', cls: 'text-slate-400 bg-slate-400/10 border-slate-400/30' },
}

const LIMITE_ANNUAIRE = 500

const aujourdhui = () => new Date().toISOString().split('T')[0]

const formVide = () => ({
  email: '',
  nom: '',
  prenom: '',
  phone: '',
  matricule: '',
  poste: '',
  departement: '',
  date_embauche: aujourdhui(),
  type_contrat: 'CDI',
  date_fin_contrat: '',
  salaire_base: '',
  horaire_travail: '',
  lieu_travail: '',
  manager_email: '',
  role: '',
})

type FormEmploye = ReturnType<typeof formVide>

export default function EmployesPage() {
  const { language } = useSettings()
  const lang = language || 'fr'
  const t = useCallback((fr: string, en: string) => (lang === 'en' ? en : fr), [lang])
  const locale = lang === 'en' ? 'en-GB' : 'fr-FR'

  const [employes, setEmployes] = useState<Fiche[]>([])
  const [loading, setLoading] = useState(true)
  const [erreur, setErreur] = useState<string | null>(null)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDept, setSelectedDept] = useState('TOUS')
  const [selectedStatut, setSelectedStatut] = useState('TOUS')

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState<FormEmploye>(formVide)
  const [creation, setCreation] = useState<Fiche | null>(null)

  const [importFile, setImportFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [resultatImport, setResultatImport] = useState<ImportResultat | null>(null)

  const [roles, setRoles] = useState<RoleOption[]>([])

  const champ = (k: keyof FormEmploye) => (e: React.ChangeEvent<HTMLInputElement> | React.ChangeEvent<HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }))

  // ---------------------------------------------------------------- lectures

  const charger = useCallback(async () => {
    setLoading(true)
    setErreur(null)
    try {
      const res = await rhAPI.getEmployes({ include_inactive: includeInactive, limit: LIMITE_ANNUAIRE })
      const data = res?.data
      setEmployes(Array.isArray(data) ? data : (data?.items || []))
    } catch (err: any) {
      setEmployes([])
      setErreur(
        typeof err?.response?.data?.detail === 'string'
          ? err.response.data.detail
          : t('Le personnel na pas pu être chargé. Vérifiez votre connexion.', 'Staff could not be loaded. Check your connection.')
      )
    } finally {
      setLoading(false)
    }
  }, [includeInactive, t])

  useEffect(() => {
    charger()
  }, [charger])

  useEffect(() => {
    // Liste des casquettes du backend : la saisie libre d'un role inexistant
    // serait ignoree sans que l'ecran en prévienne personne.
    let annule = false
    apiClient
      .get('/api/v1/admin/roles')
      .then((res) => {
        const liste = Array.isArray(res?.data) ? res.data : []
        if (!annule) setRoles(liste.map((r: any) => ({ name: r.name, label: r.label || r.name })))
      })
      .catch(() => {
        if (!annule) setRoles([])
      })
    return () => {
      annule = true
    }
  }, [])

  // ---------------------------------------------------------------- ecritures

  const validerForm = (): string | null => {
    if (!form.email.trim()) return t('L’adresse email est obligatoire.', 'Email address is required.')
    if (!form.nom.trim() || !form.prenom.trim())
      return t('Le nom et le prénom sont obligatoires.', 'Last name and first name are required.')
    if (!form.poste.trim())
      return t('Le poste est obligatoire : sans lui, aucun contrat ne peut être établi.', 'Job title is required: no contract can be drawn up without it.')
    const salaire = Number(form.salaire_base)
    if (!form.salaire_base.trim() || !Number.isFinite(salaire) || salaire <= 0)
      return t('Le salaire de base doit être un montant supérieur à 0.', 'Base salary must be an amount greater than 0.')
    if (TYPES_AVEC_FIN.includes(form.type_contrat)) {
      if (!form.date_fin_contrat)
        return t(`Un contrat ${form.type_contrat} a une date de fin : elle est obligatoire.`, `A ${form.type_contrat} contract has an end date: it is required.`)
      if (form.date_fin_contrat < form.date_embauche)
        return t('La date de fin ne peut pas précéder la date d’embauche.', 'The end date cannot precede the hire date.')
    } else if (form.date_fin_contrat) {
      return t('Un CDI ne peut pas avoir de date de fin.', 'An open-ended contract cannot have an end date.')
    }
    return null
  }

  const creuser = (e: React.FormEvent) => {
    e.preventDefault()
    const pb = validerForm()
    if (pb) {
      toast.error(pb)
      return
    }
    enregistrer()
  }

  const enregistrer = async () => {
    setSaving(true)
    try {
      const payload: Record<string, unknown> = {
        email: form.email.trim(),
        nom: form.nom.trim(),
        prenom: form.prenom.trim(),
        poste: form.poste.trim(),
        type_contrat: form.type_contrat,
        date_embauche: form.date_embauche,
        salaire_base: Number(form.salaire_base),
      }
      // Une ligne vide reste vide : rien n'est invente pour remplir le payload.
      if (form.phone.trim()) payload.phone = form.phone.trim()
      if (form.matricule.trim()) payload.matricule = form.matricule.trim()
      if (form.departement.trim()) payload.departement = form.departement.trim()
      if (form.date_fin_contrat) payload.date_fin_contrat = form.date_fin_contrat
      if (form.horaire_travail.trim()) payload.horaire_travail = form.horaire_travail.trim()
      if (form.lieu_travail.trim()) payload.lieu_travail = form.lieu_travail.trim()
      if (form.manager_email.trim()) payload.manager_email = form.manager_email.trim()
      if (form.role) payload.role = form.role

      const res = await rhAPI.createEmploye(payload)
      const fiche: Fiche = res.data
      setCreation(fiche)
      charger()
      if (fiche.avertissements?.length) {
        toast.warning(lang === 'en' ? 'Employee created, with reservations.' : 'Collaborateur créé, avec des réserves.')
      } else {
        toast.success(lang === 'en' ? 'Employee created.' : 'Collaborateur créé.')
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      if (err?.response?.status === 403) {
        toast.error(t('Accès réservé : casquette RH, DRH ou Direction.', 'Restricted: HR, HR Director or Management role required.'))
      } else if (typeof detail === 'string') {
        toast.error(detail)
      } else if (Array.isArray(detail)) {
        toast.error(detail.map((d: any) => d.msg || JSON.stringify(d)).join('  '))
      } else {
        toast.error(t('Création impossible.', 'Could not create the employee.'))
      }
    } finally {
      setSaving(false)
    }
  }

  const fermerCreation = () => {
    setCreation(null)
    setForm(formVide())
    setShowCreateModal(false)
  }

  const importer = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!importFile) {
      toast.error(t('Sélectionnez un fichier Excel ou CSV.', 'Select an Excel or CSV file.'))
      return
    }
    setUploading(true)
    setResultatImport(null)
    try {
      const body = new FormData()
      body.append('file', importFile)
      const res = await rhAPI.importEmployesExcel(body)
      setResultatImport(res.data)
      charger()
      const n = res.data?.importes?.length ?? 0
      if (n > 0) {
        toast.success(
          lang === 'en'
            ? `${n} employee(s) imported.`
            : `${n} collaborateur(s) importé(s).`
        )
      } else {
        toast.warning(
          lang === 'en' ? 'No row could be imported.' : 'Aucune ligne n’a pu être importée.'
        )
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      if (err?.response?.status === 403) {
        toast.error(t('Accès réservé : casquette RH, DRH ou Direction.', 'Restricted: HR, HR Director or Management role required.'))
      } else if (typeof detail === 'string') {
        setResultatImport({ importes: [], rejets: [], total_lignes: 0, message: detail, fichier: importFile.name })
      } else {
        toast.error(t('Importation impossible.', 'Import failed.'))
      }
    } finally {
      setUploading(false)
    }
  }

  const libelleStatut = (e: Fiche): string => {
    if (!e.is_active) return t('Compte désactivé', 'Account disabled')
    if (!e.statut) return t('Sans contrat', 'No contract')
    const s = STATUTS[e.statut]
    return s ? t(s.fr, s.en) : e.statut
  }

  const exporterCSV = () => {
    if (filtered.length === 0) {
      toast.error(t('Aucune donnée à exporter.', 'Nothing to export.'))
      return
    }
    const heads = [
      t('Matricule', 'Staff ID'), t('Nom complet', 'Full name'), t('Email', 'Email'),
      t('Téléphone', 'Phone'), t('Poste', 'Job title'), t('Département', 'Department'),
      t("Date d'embauche", 'Hire date'), t('Type de contrat', 'Contract type'),
      t('Fin de contrat', 'Contract end'), t('Salaire de base', 'Base salary'),
      t('Devise', 'Currency'), t('Statut', 'Status'), t('En congé', 'On leave'),
    ]
    const lignes = filtered.map((e) =>
      [
        e.matricule ?? '', e.full_name ?? '', e.email ?? '', e.phone ?? '',
        e.poste ?? '', e.departement ?? '', e.date_embauche ?? '',
        e.type_contrat ?? '', e.date_fin_contrat ?? '',
        e.salaire_base ?? '', e.devise ?? '', libelleStatut(e) ?? '',
        e.en_conge ? t('Oui', 'Yes') : t('Non', 'No'),
      ]
        .map((v) => `"${String(v).replace(/"/g, '""')}"`)
        .join(',')
    )
    const csv = '\ufeff' + heads.join(',') + '\n' + lignes.join('\n')
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }))
    const lien = document.createElement('a')
    lien.href = url
    lien.setAttribute('download', `Annuaire_Employes_${aujourdhui()}.csv`)
    document.body.appendChild(lien)
    lien.click()
    document.body.removeChild(lien)
    URL.revokeObjectURL(url)
    toast.success(t('Annuaire exporté.', 'Staff directory exported.'))
  }

  const copier = (texte: string) => {
    navigator.clipboard?.writeText(texte).then(
      () => toast.success(t('Copié.', 'Copied.')),
      () => toast.error(t('Copie impossible.', 'Could not copy.'))
    )
  }

  // ---------------------------------------------------------------- filtres

  const deptList = useMemo(
    () => Array.from(new Set(employes.map((e) => e.departement).filter(Boolean) as string[])).sort(),
    [employes]
  )

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase()
    return employes.filter((e) => {
      const cible = `${e.full_name ?? ''} ${e.matricule ?? ''} ${e.email ?? ''} ${e.poste ?? ''} ${e.phone ?? ''}`.toLowerCase()
      const matchSearch = !q || cible.includes(q)
      const matchDept = selectedDept === 'TOUS' || (e.departement ?? '') === selectedDept
      let matchStatut = true
      if (selectedStatut === 'SANS_CONTRAT') matchStatut = !e.statut
      else if (selectedStatut === 'EN_CONGE') matchStatut = !!e.en_conge
      else if (selectedStatut !== 'TOUS') matchStatut = e.statut === selectedStatut
      return matchSearch && matchDept && matchStatut
    })
  }, [employes, searchTerm, selectedDept, selectedStatut])

  const dateFr = (iso: string | null) =>
    iso ? new Date(iso).toLocaleDateString(locale, { day: '2-digit', month: 'short', year: 'numeric' }) : '-'

  const montant = (n: number | null) =>
    n === null ? '-' : new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(n)

  // ---------------------------------------------------------------- rendu

  const enTete = (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <h1 className="flex items-center gap-2 text-xl font-bold text-foreground sm:text-2xl">
          <Users className="shrink-0 text-pink-500" size={26} />
          {t('Annuaire & Gestion des Employés', 'Staff Directory & Management')}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {t(
            'Registre du personnel, contrats portés et import/export du fichier de paie.',
            'Staff register, active contracts and payroll file import/export.'
          )}
        </p>
      </div>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-3 lg:flex lg:shrink-0">
        <button
          onClick={exporterCSV}
          className="flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-accent"
        >
          <Download size={16} className="text-emerald-400" />
          {t('Exporter CSV', 'Export CSV')}
        </button>
        <button
          onClick={() => {
            setResultatImport(null)
            setImportFile(null)
            setShowImportModal(true)
          }}
          className="flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-pink-500/40 bg-pink-500/10 px-4 py-2.5 text-sm font-medium text-pink-300 transition-colors hover:bg-pink-500/20"
        >
          <Upload size={16} />
          {t('Importer', 'Import')}
        </button>
        <button
          onClick={() => {
            setCreation(null)
            setForm(formVide())
            setShowCreateModal(true)
          }}
          className="flex min-h-[44px] items-center justify-center gap-2 rounded-xl bg-pink-600 px-4 py-2.5 text-sm font-medium text-white shadow-md shadow-pink-900/30 transition-colors hover:bg-pink-700"
        >
          <UserPlus size={16} />
          {t('Ajouter un employé', 'Add employee')}
        </button>
      </div>
    </div>
  )

  const filtres = (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
      <div className="relative lg:flex-1">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input
          type="search"
          inputMode="search"
          placeholder={t('Rechercher nom, matricule, poste, email…', 'Search name, staff ID, job title, email…')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="min-h-[44px] w-full rounded-xl border border-border bg-card py-2.5 pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-pink-500/40"
        />
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:flex lg:items-center">
        <label className="col-span-2 flex min-h-[44px] cursor-pointer items-center gap-2 rounded-xl border border-border bg-card px-3 text-sm text-muted-foreground sm:col-span-1">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="h-4 w-4 accent-pink-600"
          />
          {t('Comptes désactivés', 'Disabled accounts')}
        </label>
        <select
          value={selectedDept}
          onChange={(e) => setSelectedDept(e.target.value)}
          aria-label={t('Filtrer par département', 'Filter by department')}
          className="min-h-[44px] rounded-xl border border-border bg-card px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-pink-500/40"
        >
          <option value="TOUS">{t('Tous les départements', 'All departments')}</option>
          {deptList.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        <select
          value={selectedStatut}
          onChange={(e) => setSelectedStatut(e.target.value)}
          aria-label={t('Filtrer par statut', 'Filter by status')}
          className="min-h-[44px] rounded-xl border border-border bg-card px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-pink-500/40"
        >
          <option value="TOUS">{t('Tous les statuts', 'All statuses')}</option>
          <option value="actif">{t('Contrat actif', 'Active contract')}</option>
          <option value="suspendu">{t('Suspendu', 'Suspended')}</option>
          <option value="expire">{t('Expiré', 'Expired')}</option>
          <option value="resilie">{t('Résilié', 'Terminated')}</option>
          <option value="inactif">{t('Compte désactivé', 'Account disabled')}</option>
          <option value="SANS_CONTRAT">{t('Sans contrat', 'No contract')}</option>
          <option value="EN_CONGE">{t('En congé', 'On leave')}</option>
        </select>
        <button
          onClick={charger}
          title={t('Actualiser', 'Refresh')}
          aria-label={t('Actualiser', 'Refresh')}
          className="col-span-2 flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-border bg-card px-3 text-sm text-muted-foreground transition-colors hover:text-pink-400 sm:col-span-1"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          {t('Actualiser', 'Refresh')}
        </button>
      </div>
    </div>
  )

  const celluleStatut = (e: Fiche) => {
    const cle = !e.is_active ? 'inactif' : e.statut && STATUTS[e.statut] ? e.statut : null
    const cls = cle ? STATUTS[cle].cls : 'text-slate-400 bg-slate-400/10 border-slate-400/30'
    return (
      <span className="flex flex-wrap items-center gap-1">
        <span className={`inline-flex items-center gap-1 rounded-lg border px-2 py-0.5 text-[11px] font-semibold ${cls}`}>
          {libelleStatut(e)}
        </span>
        {e.en_conge && (
          <span className="inline-flex items-center gap-1 rounded-lg border border-sky-400/30 bg-sky-400/10 px-2 py-0.5 text-[11px] font-semibold text-sky-300">
            <Plane size={11} />
            {t('En congé', 'On leave')}
          </span>
        )}
      </span>
    )
  }

  const corpsTableau = (
    <div className="overflow-x-auto rounded-2xl border border-border bg-card">
      <table className="w-full min-w-[820px] text-left text-sm">
        <thead className="border-b border-border text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          <tr>
            <th className="px-4 py-3">{t('Collaborateur', 'Employee')}</th>
            <th className="px-4 py-3">{t('Poste / Département', 'Job title / Department')}</th>
            <th className="px-4 py-3">{t('Contact', 'Contact')}</th>
            <th className="px-4 py-3">{t('Contrat', 'Contract')}</th>
            <th className="px-4 py-3 text-right">{t('Salaire de base', 'Base salary')}</th>
            <th className="px-4 py-3">{t('Statut', 'Status')}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {filtered.map((e) => (
            <tr key={e.id} className="transition-colors hover:bg-accent/60">
              <td className="px-4 py-3">
                <div className="flex items-center gap-3">
                  <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-tr from-pink-500 to-rose-500 text-xs font-bold text-white">
                    {(e.full_name || '?').trim().slice(0, 1)}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate font-medium text-foreground">{e.full_name || '-'}</span>
                    <span className="block font-mono text-xs text-pink-400">{e.matricule || '-'}</span>
                  </span>
                </div>
              </td>
              <td className="px-4 py-3">
                <span className="flex items-center gap-1.5 text-foreground">
                  <Briefcase size={13} className="shrink-0 text-muted-foreground" />
                  <span className="truncate">{e.poste || '-'}</span>
                </span>
                <span className="mt-1 inline-block rounded-md border border-border px-2 py-0.5 text-xs text-muted-foreground">
                  {e.departement || '-'}
                </span>
              </td>
              <td className="px-4 py-3">
                <a href={`mailto:${e.email}`} className="flex items-start gap-1.5 break-all text-xs text-muted-foreground hover:text-pink-400">
                  <Mail size={13} className="mt-0.5 shrink-0" />
                  {e.email || '-'}
                </a>
                <span className="mt-0.5 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Phone size={13} className="shrink-0" />
                  {e.phone || '-'}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className="font-medium text-foreground">{e.type_contrat || t('Aucun', 'None')}</span>
                <span className="mt-0.5 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Calendar size={13} className="shrink-0" />
                  {dateFr(e.date_embauche)}
                </span>
                {e.date_fin_contrat && (
                  <span className="block text-xs text-muted-foreground">
                    {t('→', 'to')} {dateFr(e.date_fin_contrat)}
                  </span>
                )}
              </td>
              <td className="px-4 py-3 text-right font-mono text-emerald-400">
                {e.salaire_base === null ? '-' : `${montant(e.salaire_base)} ${e.devise || 'XAF'}`}
              </td>
              <td className="px-4 py-3">{celluleStatut(e)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )

  const cartesMobile = (
    <div className="space-y-3 md:hidden">
      {filtered.map((e) => (
        <div key={e.id} className="rounded-2xl border border-border bg-card p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-tr from-pink-500 to-rose-500 text-xs font-bold text-white">
                {(e.full_name || '?').trim().slice(0, 1)}
              </span>
              <div className="min-w-0">
                <p className="truncate font-medium text-foreground">{e.full_name || '-'}</p>
                <p className="font-mono text-xs text-pink-400">{e.matricule || '-'}</p>
              </div>
            </div>
            {celluleStatut(e)}
          </div>
          <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
            <div>
              <dt className="text-muted-foreground">{t('Poste', 'Job title')}</dt>
              <dd className="text-foreground">{e.poste || '-'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">{t('Département', 'Department')}</dt>
              <dd className="text-foreground">{e.departement || '-'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">{t('Contrat', 'Contract')}</dt>
              <dd className="text-foreground">
                {e.type_contrat || t('Aucun', 'None')} · {dateFr(e.date_embauche)}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">{t('Salaire de base', 'Base salary')}</dt>
              <dd className="font-mono text-emerald-400">
                {e.salaire_base === null ? '-' : `${montant(e.salaire_base)} ${e.devise || 'XAF'}`}
              </dd>
            </div>
            <div className="col-span-2">
              <dt className="text-muted-foreground">{t('Contact', 'Contact')}</dt>
              <dd className="break-all">
                <a href={`mailto:${e.email}`} className="text-foreground hover:text-pink-400">{e.email}</a>
                {e.phone ? <span className="text-muted-foreground"> · {e.phone}</span> : null}
              </dd>
            </div>
          </dl>
        </div>
      ))}
    </div>
  )

  return (
    <ModuleLayout module="rh">
      <div className="mx-auto max-w-7xl space-y-5 py-6">
        {enTete}
        {filtres}

        {erreur && (
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
            <span className="flex items-center gap-2">
              <AlertTriangle size={16} className="shrink-0" />
              {erreur}
            </span>
            <button onClick={charger} className="min-h-[40px] rounded-lg border border-red-500/40 px-3 py-1.5 font-medium hover:bg-red-500/20">
              {t('Réessayer', 'Try again')}
            </button>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center gap-2 rounded-2xl border border-border bg-card py-16 text-sm text-muted-foreground">
            <Loader2 size={16} className="animate-spin" />
            {t('Chargement du personnel…', 'Loading staff…')}
          </div>
        ) : filtered.length === 0 ? (
          <div className="rounded-2xl border border-border bg-card p-10 text-center">
            <Users size={40} className="mx-auto mb-3 text-muted-foreground" />
            <p className="font-medium text-foreground">
              {employes.length === 0
                ? t('Aucun collaborateur enregistré.', 'No employee on record.')
                : t('Aucun collaborateur ne correspond à ces critères.', 'No employee matches these filters.')}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              {employes.length === 0
                ? t('Ajoutez le premier salarié ou importez un fichier.', 'Add the first employee or import a file.')
                : t('Modifiez la recherche ou les filtres.', 'Adjust the search or the filters.')}
            </p>
          </div>
        ) : (
          <>
            <div className="hidden md:block">{corpsTableau}</div>
            {cartesMobile}
            <p className="text-xs text-muted-foreground">
              {filtered.length} / {employes.length}{' '}
              {t('collaborateur(s) affiché(s)', 'employee(s) shown')}
              {employes.length >= LIMITE_ANNUAIRE
                ? t(
                    '  liste tronquée à 500, affinez la recherche.',
                    '  list capped at 500, refine your search.'
                  )
                : ''}
            </p>
          </>
        )}
      </div>

      {/* -------------------------------------------------- modal création */}
      {showCreateModal && (
        <div className="fixed inset-0 z-[100] flex items-end justify-center bg-slate-950/80 backdrop-blur-sm sm:items-center sm:p-4">
          <div
            role="dialog"
            aria-modal="true"
            aria-label={t('Nouveau collaborateur', 'New employee')}
            className="max-h-[92vh] w-full overflow-y-auto rounded-t-3xl border border-border bg-card p-5 shadow-2xl sm:max-w-2xl sm:rounded-3xl"
          >
            {!creation ? (
              <>
                <div className="flex items-start justify-between gap-3 border-b border-border pb-4">
                  <h3 className="flex items-center gap-2 text-lg font-bold text-foreground">
                    <UserPlus size={20} className="text-pink-500" />
                    {t('Nouveau collaborateur', 'New employee')}
                  </h3>
                  <button
                    onClick={() => setShowCreateModal(false)}
                    aria-label={t('Fermer', 'Close')}
                    className="-m-2 rounded-lg p-2 text-muted-foreground hover:text-foreground"
                  >
                    <X size={20} />
                  </button>
                </div>

                <form onSubmit={creuser} className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <Champ label={t('Nom', 'Last name')} required>
                    <input {...inputCls} required value={form.nom} onChange={champ('nom')} placeholder={t('Ex : MVONDO', 'e.g. MVONDO')} />
                  </Champ>
                  <Champ label={t('Prénom', 'First name')} required>
                    <input {...inputCls} required value={form.prenom} onChange={champ('prenom')} placeholder={t('Ex : Jean-Marc', 'e.g. Jean-Marc')} />
                  </Champ>
                  <Champ label="Email" required className="sm:col-span-2">
                    <input {...inputCls} type="email" required value={form.email} onChange={champ('email')} placeholder="prenom.nom@evo-log.cm" />
                  </Champ>
                  <Champ label={t('Téléphone', 'Phone')}>
                    <input {...inputCls} type="tel" value={form.phone} onChange={champ('phone')} placeholder="+237 6 00 00 00 00" />
                  </Champ>
                  <Champ label={t('Matricule', 'Staff ID')} hint={t('Attribué automatiquement si vide', 'Assigned automatically if left blank')}>
                    <input {...inputCls} value={form.matricule} onChange={champ('matricule')} placeholder="EMP-…" />
                  </Champ>
                  <Champ label={t('Poste', 'Job title')} required className="sm:col-span-2">
                    <input {...inputCls} required value={form.poste} onChange={champ('poste')} placeholder={t('Ex : Déclarant en douane', 'e.g. Customs declarant')} />
                  </Champ>
                  <Champ label={t('Département', 'Department')} hint={t('Créé s’il est inédit', 'Created if new')}>
                    <input {...inputCls} list="departements-existants" value={form.departement} onChange={champ('departement')} />
                    <datalist id="departements-existants">
                      {deptList.map((d) => <option key={d} value={d} />)}
                    </datalist>
                  </Champ>
                  <Champ label={t('Casquette (rôle)', 'Role')}>
                    <select {...inputCls} value={form.role} onChange={champ('role')}>
                      <option value="">{t('Aucune', 'None')}</option>
                      {roles.map((r) => (
                        <option key={r.name} value={r.name}>{r.label}</option>
                      ))}
                    </select>
                  </Champ>
                  <Champ label={t('Type de contrat', 'Contract type')} required>
                    <select {...inputCls} value={form.type_contrat} onChange={champ('type_contrat')}>
                      {TYPES_CONTRAT.map((c) => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </Champ>
                  <Champ
                    label={t('Date de fin du contrat', 'Contract end date')}
                    required={TYPES_AVEC_FIN.includes(form.type_contrat)}
                    hint={
                      form.type_contrat === 'CDI'
                        ? t('Sans objet pour un CDI', 'Not applicable to an open-ended contract')
                        : t('Obligatoire pour un contrat à durée déterminée', 'Required for a fixed-term contract')
                    }
                  >
                    <input
                      {...inputCls}
                      type="date"
                      disabled={form.type_contrat === 'CDI'}
                      value={form.date_fin_contrat}
                      onChange={champ('date_fin_contrat')}
                    />
                  </Champ>
                  <Champ label={t('Date d’embauche', 'Hire date')}>
                    <input {...inputCls} type="date" value={form.date_embauche} onChange={champ('date_embauche')} />
                  </Champ>
                  <Champ label={`${t('Salaire de base', 'Base salary')} (XAF)`} required>
                    <input {...inputCls} type="number" min="0" step="1000" inputMode="numeric" required value={form.salaire_base} onChange={champ('salaire_base')} />
                  </Champ>
                  <Champ label={t('Horaire de travail', 'Working hours')} hint={t('Ex : 40h, 35h', 'e.g. 40h, 35h')}>
                    <input {...inputCls} value={form.horaire_travail} onChange={champ('horaire_travail')} />
                  </Champ>
                  <Champ label={t('Lieu de travail', 'Work location')}>
                    <input {...inputCls} value={form.lieu_travail} onChange={champ('lieu_travail')} placeholder={t('Ex : Douala, Port de Kribi', 'e.g. Douala, Kribi Port')} />
                  </Champ>
                  <Champ
                    label={t('Supérieur hiérarchique (email)', 'Line manager (email)')}
                    hint={t('Doit correspondre à un compte existant', 'Must match an existing account')}
                    className="sm:col-span-2"
                  >
                    <input {...inputCls} type="email" value={form.manager_email} onChange={champ('manager_email')} />
                  </Champ>

                  <p className="flex items-start gap-2 text-xs text-muted-foreground sm:col-span-2">
                    <Info size={14} className="mt-0.5 shrink-0" />
                    {t(
                      'Le statut ne se saisit pas : il se lit du compte, du contrat et des congés approuvés.',
                      'Status is not entered: it is derived from the account, the contract and approved leave.'
                    )}
                  </p>

                  <div className="flex flex-col-reverse gap-2 border-t border-border pt-4 sm:col-span-2 sm:flex-row sm:justify-end">
                    <button
                      type="button"
                      onClick={() => setShowCreateModal(false)}
                      className="min-h-[44px] rounded-xl border border-border px-4 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent"
                    >
                      {t('Annuler', 'Cancel')}
                    </button>
                    <button
                      type="submit"
                      disabled={saving}
                      className="flex min-h-[44px] items-center justify-center gap-2 rounded-xl bg-pink-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-pink-700 disabled:opacity-50"
                    >
                      {saving && <Loader2 size={15} className="animate-spin" />}
                      {saving ? t('Enregistrement…', 'Saving…') : t('Enregistrer', 'Save')}
                    </button>
                  </div>
                </form>
              </>
            ) : (
              <div className="space-y-4">
                <div className="flex items-start justify-between gap-3 border-b border-border pb-4">
                  <h3 className="flex items-center gap-2 text-lg font-bold text-foreground">
                    <KeyRound size={20} className="text-pink-500" />
                    {t('Compte créé', 'Account created')}
                  </h3>
                  <button onClick={fermerCreation} aria-label={t('Fermer', 'Close')} className="-m-2 rounded-lg p-2 text-muted-foreground hover:text-foreground">
                    <X size={20} />
                  </button>
                </div>

                <dl className="space-y-2 rounded-2xl border border-border bg-slate-900/60 p-4 text-sm">
                  <Ligne cle={t('Collaborateur', 'Employee')} valeur={creation.full_name} />
                  <Ligne cle={t('Matricule', 'Staff ID')} valeur={creation.matricule} />
                  <Ligne cle="Email" valeur={creation.email} />
                  <Ligne cle={t('Identifiant de connexion', 'Login')} valeur={creation.username} />
                  <Ligne
                    cle={t('Mot de passe provisoire', 'Temporary password')}
                    valeur={creation.temporary_password}
                    mono
                    onCopier={creation.temporary_password ? () => copier(creation.temporary_password as string) : undefined}
                  />
                </dl>

                <p className="text-xs text-muted-foreground">
                  {t(
                    'Ce mot de passe n’est affiché qu’ici : il n’est stocké que sous forme chiffrée et sera refusé à la première connexion.',
                    'This password is shown only here: it is stored hashed and will be rejected at first sign-in.'
                  )}
                </p>

                {!!creation.avertissements?.length && (
                  <div className="space-y-2 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
                    {creation.avertissements.map((a, i) => (
                      <p key={i} className="flex items-start gap-2">
                        <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                        {a}
                      </p>
                    ))}
                  </div>
                )}

                <div className="flex flex-col-reverse gap-2 border-t border-border pt-4 sm:flex-row sm:justify-end">
                  <button
                    onClick={() => {
                      setCreation(null)
                      setForm(formVide())
                    }}
                    className="min-h-[44px] rounded-xl border border-border px-4 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent"
                  >
                    {t('Nouveau collaborateur', 'New employee')}
                  </button>
                  <button onClick={fermerCreation} className="min-h-[44px] rounded-xl bg-pink-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-pink-700">
                    {t('Terminer', 'Done')}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* -------------------------------------------------- modal import */}
      {showImportModal && (
        <div className="fixed inset-0 z-[100] flex items-end justify-center bg-slate-950/80 backdrop-blur-sm sm:items-center sm:p-4">
          <div
            role="dialog"
            aria-modal="true"
            aria-label={t('Importer du personnel', 'Import staff')}
            className="max-h-[92vh] w-full overflow-y-auto rounded-t-3xl border border-border bg-card p-5 shadow-2xl sm:max-w-2xl sm:rounded-3xl"
          >
            <div className="flex items-start justify-between gap-3 border-b border-border pb-4">
              <h3 className="flex items-center gap-2 text-lg font-bold text-foreground">
                <FileSpreadsheet size={20} className="text-pink-500" />
                {t('Importer du personnel', 'Import staff')}
              </h3>
              <button onClick={() => setShowImportModal(false)} aria-label={t('Fermer', 'Close')} className="-m-2 rounded-lg p-2 text-muted-foreground hover:text-foreground">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={importer} className="mt-4 space-y-4">
              <p className="text-sm text-muted-foreground">
                {t(
                  'Fichier .xlsx ou .csv. Les en-têtes sont reconnus en français comme en anglais (Nom, Prénom, Email, Poste, Département, Type de contrat, Date d’embauche, Salaire de base…).',
                  '.xlsx or .csv file. Headers are recognised in French and English (Name, First name, Email, Job title, Department, Contract type, Hire date, Base salary…).'
                )}
              </p>

              <label className="relative flex cursor-pointer flex-col items-center gap-2 rounded-2xl border-2 border-dashed border-border p-6 text-center transition-colors hover:border-pink-500/60">
                <input
                  type="file"
                  accept=".csv,text/csv,.xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                  onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                  className="absolute inset-0 cursor-pointer opacity-0"
                />
                <FileSpreadsheet size={32} className="text-pink-500" />
                <span className="text-sm font-medium text-foreground">
                  {importFile ? importFile.name : t('Cliquez ou déposez votre fichier', 'Click or drop your file')}
                </span>
                <span className="text-xs text-muted-foreground">
                  {t('Formats acceptés : CSV, XLSX  5 Mo au plus', 'Accepted formats: CSV, XLSX  5 MB max')}
                </span>
              </label>

              {resultatImport && (
                <div className="space-y-3 rounded-2xl border border-border bg-slate-900/60 p-4">
                  <p className="text-sm font-medium text-foreground">{resultatImport.message}</p>

                  {resultatImport.importes.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                        {t('Importés', 'Imported')} ({resultatImport.importes.length})
                      </p>
                      <ul className="max-h-52 space-y-2 overflow-y-auto pr-1 text-xs">
                        {resultatImport.importes.map((i) => (
                          <li key={i.ligne} className="rounded-lg border border-border p-2">
                            <span className="font-medium text-foreground">{i.full_name || i.email}</span>
                            <span className="text-muted-foreground"> · {i.matricule}</span>
                            <Ligne
                              cle={t('Mot de passe provisoire', 'Temporary password')}
                              valeur={i.temporary_password}
                              mono
                              compact
                              onCopier={() => copier(i.temporary_password)}
                            />
                            {i.avertissements?.map((a, k) => (
                              <p key={k} className="mt-1 text-amber-300">{a}</p>
                            ))}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {resultatImport.rejets.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-wider text-red-400">
                        {t('Lignes rejetées', 'Rejected rows')} ({resultatImport.rejets.length})
                      </p>
                      <ul className="max-h-52 space-y-1 overflow-y-auto pr-1 text-xs">
                        {resultatImport.rejets.map((r) => (
                          <li key={`${r.ligne}-${r.raison}`} className="flex items-start gap-2 rounded-lg border border-red-500/20 bg-red-500/5 p-2 text-red-200">
                            <AlertTriangle size={13} className="mt-0.5 shrink-0" />
                            <span>
                              <span className="font-mono">{t('Ligne', 'Row')} {r.ligne}</span> · {r.raison}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              <div className="flex flex-col-reverse gap-2 border-t border-border pt-4 sm:flex-row sm:justify-end">
                <button
                  type="button"
                  onClick={() => setShowImportModal(false)}
                  className="min-h-[44px] rounded-xl border border-border px-4 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent"
                >
                  {t('Fermer', 'Close')}
                </button>
                <button
                  type="submit"
                  disabled={uploading || !importFile}
                  className="flex min-h-[44px] items-center justify-center gap-2 rounded-xl bg-pink-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-pink-700 disabled:opacity-50"
                >
                  {uploading && <Loader2 size={15} className="animate-spin" />}
                  {uploading ? t('Importation…', 'Importing…') : t('Lancer l’importation', 'Run import')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </ModuleLayout>
  )
}

// ------------------------------------------------------------ sous-composants

const inputCls = {
  className:
    'min-h-[44px] w-full rounded-xl border border-border bg-slate-900/60 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-pink-500/40 disabled:opacity-50',
}

function Champ({
  label, hint, required, className = '', children,
}: {
  label: string
  hint?: string
  required?: boolean
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={className}>
      <label className="mb-1 block text-xs font-semibold text-foreground">
        {label}
        {required && <span className="text-pink-400"> *</span>}
      </label>
      {children}
      {hint && <p className="mt-1 text-[11px] text-muted-foreground">{hint}</p>}
    </div>
  )
}

function Ligne({
  cle, valeur, mono = false, compact = false, onCopier,
}: {
  cle: string
  valeur?: string | number | null
  mono?: boolean
  compact?: boolean
  onCopier?: () => void
}) {
  return (
    <div className={`flex items-center justify-between gap-3 ${compact ? 'mt-1' : ''}`}>
      <span className="text-xs text-muted-foreground">{cle}</span>
      <span className="flex min-w-0 items-center gap-1.5">
        <span className={`truncate text-sm text-foreground ${mono ? 'font-mono' : ''}`}>
          {valeur === null || valeur === undefined || valeur === '' ? '-' : valeur}
        </span>
        {onCopier && valeur && (
          <button
            type="button"
            onClick={onCopier}
            aria-label={cle}
            className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-pink-400"
          >
            <Copy size={13} />
          </button>
        )}
      </span>
    </div>
  )
}

'use client'

import { useState, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { magasinAPI } from '@/lib/api-client'
import { masterDataAPI } from '@/lib/api-client'

interface DropdownOption {
  value: string | number
  label: string
}

interface DropdownSelectProps {
  label: string
  options: DropdownOption[]
  value?: string | number
  onChange: (value: string) => void
  placeholder?: string
  required?: boolean
  disabled?: boolean
}

export function DropdownSelect({
  label,
  options,
  value,
  onChange,
  placeholder = 'Sélectionner...',
  required = false,
  disabled = false,
}: DropdownSelectProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor={`select-${label}`}>
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      <Select value={value?.toString()} onValueChange={onChange} disabled={disabled}>
        <SelectTrigger id={`select-${label}`}>
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option.value.toString()} value={option.value.toString()}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

// Composants spécialisés pour chaque type de dropdown avec données dynamiques

export function MagasinDropdown({ value, onChange, required = false }: { value?: string; onChange: (value: string) => void; required?: boolean }) {
  const [magasins, setMagasins] = useState<Array<{value: string; label: string}>>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadMagasins = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await magasinAPI.getMagasins()
        // Assuming API returns { id, code, nom } objects
        const data = res.data || []
        setMagasins(
          data.map((m: any) => ({
            value: m.id.toString(),
            label: `${m.code} - ${m.nom}`
          }))
        )
      } catch (err) {
        console.error('Failed to load magasins', err)
        setError('Failed to load magasins')
        setMagasins([])
      } finally {
        setLoading(false)
      }
    }

    loadMagasins()
  }, [])

  if (loading) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-Magasin">
          Magasin
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="flex items-center space-x-2">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500"></div>
          <span>Chargement des magasins...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-Magasin">
          Magasin
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <DropdownSelect
      label="Magasin"
      options={magasins}
      value={value}
      onChange={onChange}
      placeholder="Sélectionner un magasin"
      required={required}
    />
  )
}

export function CategorieArticleDropdown({ value, onChange, required = false }: { value?: string; onChange: (value: string) => void; required?: boolean }) {
  const [categories, setCategories] = useState<DropdownOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadCategories = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await masterDataAPI.getArticleCategories()
        // API returns { value, label } objects directly
        setCategories(res.data || [])
      } catch (err) {
        console.error('Failed to load categories', err)
        setError('Failed to load categories')
        setCategories([])
      } finally {
        setLoading(false)
      }
    }

    loadCategories()
  }, [])

  if (loading) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-CategorieArticle">
          Catégorie d'Article
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="flex items-center space-x-2">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500"></div>
          <span>Chargement des catégories...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-CategorieArticle">
          Catégorie d'Article
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <DropdownSelect
      label="Catégorie d'Article"
      options={categories}
      value={value}
      onChange={onChange}
      placeholder="Sélectionner une catégorie"
      required={required}
    />
  )
}

export function IncotermDropdown({ value, onChange, required = false }: { value?: string; onChange: (value: string) => void; required?: boolean }) {
  const [incoterms, setIncoterms] = useState<DropdownOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadIncoterms = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await masterDataAPI.getIncoterms()
        // Assuming API returns objects with code and nom fields
        const data = res.data || []
        setIncoterms(
          data.map((i: any) => ({
            value: i.code,
            label: `${i.code} - ${i.nom}`
          }))
        )
      } catch (err) {
        console.error('Failed to load incoterms', err)
        setError('Failed to load incoterms')
        setIncoterms([])
      } finally {
        setLoading(false)
      }
    }

    loadIncoterms()
  }, [])

  if (loading) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-Incoterm">
          Incoterm
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="flex items-center space-x-2">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500"></div>
          <span>Chargement des incoterms...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-Incoterm">
          Incoterm
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <DropdownSelect
      label="Incoterm"
      options={incoterms}
      value={value}
      onChange={onChange}
      placeholder="Sélectionner un incoterm"
      required={required}
    />
  )
}

export function TypeConteneurDropdown({ value, onChange, required = false }: { value?: string; onChange: (value: string) => void; required?: boolean }) {
  const [types, setTypes] = useState<DropdownOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadTypes = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await masterDataAPI.getContainerTypes()
        // Assuming API returns objects with longueur and type_conteneur fields
        const data = res.data || []
        setTypes(
          data.map((t: any) => ({
            value: t.code || t.id?.toString() || '',
            label: `${t.longueur} ${t.type_conteneur}`
          }))
        )
      } catch (err) {
        console.error('Failed to load container types', err)
        setError('Failed to load container types')
        setTypes([])
      } finally {
        setLoading(false)
      }
    }

    loadTypes()
  }, [])

  if (loading) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-TypeConteneur">
          Type de Conteneur
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="flex items-center space-x-2">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500"></div>
          <span>Chargement des types de conteneur...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-TypeConteneur">
          Type de Conteneur
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <DropdownSelect
      label="Type de Conteneur"
      options={types}
      value={value}
      onChange={onChange}
      placeholder="Sélectionner un type de conteneur"
      required={required}
    />
  )
}

export function StatutStockDropdown({ value, onChange, required = false }: { value?: string; onChange: (value: string) => void; required?: boolean }) {
  const [statuts, setStatuts] = useState<DropdownOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadStatuts = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await magasinAPI.getStockStatuses()
        // API returns array of strings (statut values)
        const data = res.data || []
        setStatuts(
          data.map((s: string) => ({
            value: s,
            label: s // We could map to a more readable label, but keep as is for now
          }))
        )
      } catch (err) {
        console.error('Failed to load stock statuses', err)
        setError('Failed to load stock statuses')
        setStatuts([])
      } finally {
        setLoading(false)
      }
    }

    loadStatuts()
  }, [])

  if (loading) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-StatutStock">
          Statut du Stock
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="flex items-center space-x-2">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500"></div>
          <span>Chargement des statuts de stock...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-2">
        <Label htmlFor="select-StatutStock">
          Statut du Stock
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <DropdownSelect
      label="Statut du Stock"
      options={statuts}
      value={value}
      onChange={onChange}
      placeholder="Sélectionner un statut"
      required={required}
    />
  )
}
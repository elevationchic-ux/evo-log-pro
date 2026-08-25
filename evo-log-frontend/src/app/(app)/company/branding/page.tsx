'use client'

import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Palette, Save, XCircle, Brush, Image, Link } from 'lucide-react'

const b2bAPI = {
  getPortal: async (companyId: number) => {
    return {
      data: {
        id: 1,
        company_id: companyId,
        primary_color: '#3B82F6',
        secondary_color: '#10B981',
        accent_color: '#F59E0B',
        background_color: '#FFFFFF',
        text_color: '#1F2937',
        logo_url: 'https://example.com/logo.png',
        banner_url: 'https://example.com/banner.png',
        subdomain: 'camlog.evolog.cm',
        custom_domain: null,
        enable_chat: true,
        enable_quotes: true,
        enable_tracking: true,
        enable_api: false
      }
    }
  },
  updatePortal: async (companyId: number, data: any) => {
    return { data: { success: true } }
  }
}

export default function B2BBrandingPage() {
  const [mounted, setMounted] = useState(false)
  const [primaryColor, setPrimaryColor] = useState('#3B82F6')
  const [secondaryColor, setSecondaryColor] = useState('#10B981')
  const [accentColor, setAccentColor] = useState('#F59E0B')
  const [logoUrl, setLogoUrl] = useState('')
  const [bannerUrl, setBannerUrl] = useState('')
  const [subdomain, setSubdomain] = useState('')
  const queryClient = useQueryClient()

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: portal } = useQuery({
    queryKey: ['b2b-portal', 1],
    queryFn: async () => {
      const res = await b2bAPI.getPortal(1)
      return res.data
    },
    enabled: mounted,
  })

  useEffect(() => {
    if (portal) {
      setPrimaryColor(portal.primary_color)
      setSecondaryColor(portal.secondary_color)
      setAccentColor(portal.accent_color)
      setLogoUrl(portal.logo_url || '')
      setBannerUrl(portal.banner_url || '')
      setSubdomain(portal.subdomain || '')
    }
  }, [portal])

  const updateMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await b2bAPI.updatePortal(1, data)
      return res.data
    },
    onSuccess: () => {
      console.log('Portail personnalisé avec succès')
      queryClient.invalidateQueries({ queryKey: ['b2b-portal'] })
    },
    onError: () => {
      console.log('Erreur lors de la personnalisation')
    },
  })

  const handleSave = () => {
    updateMutation.mutate({
      primary_color: primaryColor,
      secondary_color: secondaryColor,
      accent_color: accentColor,
      logo_url: logoUrl,
      banner_url: bannerUrl,
      subdomain: subdomain
    })
  }

  if (!mounted) return null

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Personnalisation Portail B2B</h1>
          <p className="text-gray-600 mt-1">Personnaliser l'apparence et le branding de votre portail client</p>
        </div>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Save className="w-4 h-4" />
          Enregistrer
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Colors */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Palette className="w-5 h-5" />
            Couleurs
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Couleur Principale</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="w-12 h-12 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Couleur Secondaire</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={secondaryColor}
                  onChange={(e) => setSecondaryColor(e.target.value)}
                  className="w-12 h-12 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={secondaryColor}
                  onChange={(e) => setSecondaryColor(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Couleur d'Accent</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={accentColor}
                  onChange={(e) => setAccentColor(e.target.value)}
                  className="w-12 h-12 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={accentColor}
                  onChange={(e) => setAccentColor(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Assets */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Image className="w-5 h-5" />
            Assets
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">URL Logo</label>
              <input
                type="text"
                value={logoUrl}
                onChange={(e) => setLogoUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="https://example.com/logo.png"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">URL Bannière</label>
              <input
                type="text"
                value={bannerUrl}
                onChange={(e) => setBannerUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="https://example.com/banner.png"
              />
            </div>
          </div>
        </div>

        {/* Domain */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Link className="w-5 h-5" />
            Domaine
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sous-domaine</label>
              <input
                type="text"
                value={subdomain}
                onChange={(e) => setSubdomain(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="camlog.evolog.cm"
              />
              <p className="text-xs text-gray-500 mt-1">Votre portail sera accessible à cette adresse</p>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Brush className="w-5 h-5" />
            Fonctionnalités
          </h2>
          <div className="space-y-3">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm text-gray-700">Activer Chat Support</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm text-gray-700">Activer Devis en ligne</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm text-gray-700">Activer Tracking</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" className="rounded" />
              <span className="text-sm text-gray-700">Activer API</span>
            </label>
          </div>
        </div>
      </div>

      {/* Preview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Aperçu</h2>
        <div 
          className="p-6 rounded-lg border-2 border-dashed"
          style={{ 
            backgroundColor: '#FFFFFF',
            borderColor: primaryColor 
          }}
        >
          <div className="flex items-center gap-4 mb-4">
            <div 
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: primaryColor }}
            >
              <span className="text-white font-bold">LOGO</span>
            </div>
            <div>
              <h3 className="font-bold" style={{ color: primaryColor }}>Votre Entreprise</h3>
              <p className="text-sm text-gray-600">Portail B2B</p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div 
              className="p-4 rounded-lg text-center"
              style={{ backgroundColor: primaryColor + '10' }}
            >
              <p className="text-2xl font-bold" style={{ color: primaryColor }}>45</p>
              <p className="text-xs text-gray-600">Commandes</p>
            </div>
            <div 
              className="p-4 rounded-lg text-center"
              style={{ backgroundColor: secondaryColor + '10' }}
            >
              <p className="text-2xl font-bold" style={{ color: secondaryColor }}>38</p>
              <p className="text-xs text-gray-600">Livraisons</p>
            </div>
            <div 
              className="p-4 rounded-lg text-center"
              style={{ backgroundColor: accentColor + '10' }}
            >
              <p className="text-2xl font-bold" style={{ color: accentColor }}>2</p>
              <p className="text-xs text-gray-600">Litiges</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

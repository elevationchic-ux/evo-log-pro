'use client'

import React, { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ModuleLayout } from '@/components/layout/ModuleLayout'
import { ArrowLeft, Edit, FileText, CheckCircle2, ShieldAlert, Package, Calendar, Download, Printer, HelpCircle, Truck } from 'lucide-react'
import { magasinAPI } from '@/lib/api-client'
import { FullScreenLoader } from '@/components/ui/Loaders'
import { toast } from 'sonner'
import Link from 'next/link'

export default function BandeLivraisonDetailPage({ params }: { params: { id: string } }) {
  const bandeId = parseInt(params.id)
  const [bande, setBande] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [showEditModal, setShowEditModal] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const router = useRouter()

  useEffect(() => {
    fetchBande()
  }, [])

  const fetchBande = async () => {
    try {
      setLoading(true)
      const res = await magasinAPI.getBande(bandeId)
      setBande(res.data || null)
    } catch (error) {
      console.error(error)
      toast.error('Erreur lors du chargement de la bande de livraison')
      router.push('/magasin/bandes-livraison')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette bande de livraison ? Cette action est irréversible.')) {
      return
    }
    setDeleting(true)
    try {
      // Note: delete endpoint may not exist; we assume it does via magasinAPI? Not in our API.
      // We'll skip delete for now as not required.
      toast.error('Suppression non implémentée')
    } catch (err) {
      console.error(err)
      toast.error('Erreur lors de la suppression')
    } finally {
      setDeleting(false)
    }
  }

  if (loading || !bande) {
    return null;
  }
  return <div><h1>Bande Livraison</h1></div>;
}

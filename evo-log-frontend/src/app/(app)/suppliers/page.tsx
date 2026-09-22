'use client';

import React, { useEffect, useState } from 'react';
import GenericDataPage from '@/components/ui/GenericDataPage';
import { suppliersAPI } from '@/lib/api-client';
import { useI18n } from '@/hooks/useI18n';
import { Briefcase } from 'lucide-react';

export default function SuppliersPage() {
  const t = useI18n();
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSuppliers() {
      try {
        const res = await suppliersAPI.getSuppliers();
        setSuppliers(res.data || []);
      } catch (error) {
        console.error("Failed to fetch suppliers:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchSuppliers();
  }, []);

  const columns = [
    { key: 'code_supplier', label: 'Code' },
    { key: 'raison_sociale', label: 'Raison Sociale' },
    { key: 'categorie', label: 'Catégorie' },
    { key: 'telephone_principal', label: 'Téléphone' },
    { key: 'email_principal', label: 'Email' },
    { 
      key: 'statut', 
      label: 'Statut',
      render: (val: string) => {
        let badgeClass = 'status-info';
        if (val === 'ACTIF') badgeClass = 'status-delivered';
        if (val === 'INACTIF') badgeClass = 'status-maintenance';
        if (val === 'EN_ATTENTE_VALIDATION') badgeClass = 'status-transit';
        return <span className={`status-badge ${badgeClass}`}>{val}</span>;
      }
    }
  ];

  return (
    <GenericDataPage
      title="Fournisseurs (K-Achats)"
      description="Gestion du référentiel des fournisseurs et prestataires."
      icon={<Briefcase className="w-5 h-5 text-primary" />}
      columns={columns}
      data={suppliers}
      isLoading={loading}
      primaryActionLabel="Nouveau Fournisseur"
      onAdd={() => console.log('Add Supplier')}
      onEdit={(row) => console.log('Edit Supplier', row)}
      onDelete={(row) => console.log('Delete Supplier', row)}
    />
  );
}

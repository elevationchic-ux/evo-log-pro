'use client';

import React, { useEffect, useState } from 'react';
import GenericDataPage from '@/components/ui/GenericDataPage';
import { adminAPI } from '@/lib/api-client';
import { useI18n } from '@/hooks/useI18n';
import { Building2 } from 'lucide-react';

export default function AgenciesPage() {
  const t = useI18n();
  const [agencies, setAgencies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAgencies() {
      try {
        const res = await adminAPI.getAgencies();
        setAgencies(res.data || []);
      } catch (error) {
        console.error("Failed to fetch agencies:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchAgencies();
  }, []);

  const columns = [
    { key: 'code', label: 'Code Agence' },
    { key: 'name', label: 'Nom' },
    { key: 'city', label: 'Ville' },
    { key: 'country', label: 'Pays' },
    { 
      key: 'is_active', 
      label: 'Statut',
      render: (val: boolean) => (
        <span className={`status-badge ${val ? 'status-delivered' : 'status-maintenance'}`}>
          {val ? 'Actif' : 'Inactif'}
        </span>
      )
    }
  ];

  return (
    <GenericDataPage
      title="Agences Portuaires"
      description="Gestion des agences et succursales EVO-LOG."
      icon={<Building2 className="w-5 h-5 text-primary" />}
      columns={columns}
      data={agencies}
      isLoading={loading}
      primaryActionLabel="Nouvelle Agence"
      onAdd={() => console.log('Add Agency')}
      onEdit={(row) => console.log('Edit Agency', row)}
      onDelete={(row) => console.log('Delete Agency', row)}
    />
  );
}

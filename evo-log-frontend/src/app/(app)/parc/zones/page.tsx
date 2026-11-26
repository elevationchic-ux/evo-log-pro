'use client';

import React, { useEffect, useState } from 'react';
import GenericDataPage from '@/components/ui/GenericDataPage';
import { parcAPI } from '@/lib/api-client';
import { useI18n } from '@/hooks/useI18n';
import { LayoutGrid } from 'lucide-react';

export default function ParcZonesPage() {
  const t = useI18n();
  const [zones, setZones] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchZones() {
      try {
        const res = await parcAPI.getZones();
        setZones(res.data || []);
      } catch (error) {
        console.error("Failed to fetch parc zones:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchZones();
  }, []);

  const columns = [
    { key: 'code', label: 'Code Zone' },
    { key: 'nom', label: 'Nom' },
    { key: 'type_zone', label: 'Type' },
    { 
      key: 'capacite_max_teu', 
      label: t.parc.capacity,
      render: (val: any) => val ? `${val} TEU` : 'N/A'
    },
    { 
      key: 'est_active', 
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
      title={t.parc.zoneManagement}
      description={t.parc.subtitle}
      icon={<LayoutGrid className="w-5 h-5 text-primary" />}
      columns={columns}
      data={zones}
      isLoading={loading}
      primaryActionLabel={t.parc.newZone}
      onAdd={() => console.log('Add Zone')}
      onEdit={(row) => console.log('Edit Zone', row)}
      onDelete={(row) => console.log('Delete Zone', row)}
    />
  );
}

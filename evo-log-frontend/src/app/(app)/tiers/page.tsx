'use client';

import React, { useEffect, useState } from 'react';
import GenericDataPage from '@/components/ui/GenericDataPage';
import { tiersAPI } from '@/lib/api-client';
import { useI18n } from '@/hooks/useI18n';
import { Users } from 'lucide-react';

export default function TiersPage() {
  const t = useI18n();
  const [tiers, setTiers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTiers() {
      try {
        const res = await tiersAPI.getTiers();
        setTiers(res.data || []);
      } catch (error) {
        console.error("Failed to fetch tiers:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchTiers();
  }, []);

  const columns = [
    { key: 'code_tiers', label: 'Code' },
    { key: 'raison_sociale', label: 'Raison Sociale' },
    { key: 'type_tiers', label: 'Type' },
    { key: 'telephone_principal', label: 'Téléphone' },
    { key: 'email_principal', label: 'Email' },
    { 
      key: 'est_actif', 
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
      title="Clients & Partenaires"
      description="Gestion de la base de données des clients et partenaires EVO-LOG."
      icon={<Users className="w-5 h-5 text-primary" />}
      columns={columns}
      data={tiers}
      isLoading={loading}
      primaryActionLabel="Nouveau Client"
      onAdd={() => console.log('Add Tiers')}
      onEdit={(row) => console.log('Edit Tiers', row)}
      onDelete={(row) => console.log('Delete Tiers', row)}
    />
  );
}

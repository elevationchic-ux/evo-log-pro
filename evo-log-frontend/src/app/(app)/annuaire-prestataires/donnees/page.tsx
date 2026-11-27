'use client';

import React from 'react';
import Link from 'next/link';
import { DeepDomainPage } from '@/lib/deep-crud';
import { RESOURCES } from '@/lib/deep-configs/annuaire-prestataires';

export default function Page() {
  return (
    <DeepDomainPage
      titre="Annuaire Prestataires"
      description="Registres CRUD exposes par l'API — donnees reelles."
      backHref="/referentiels"
      backLabel="Référentiels"
      resources={RESOURCES}
    />
  );
}

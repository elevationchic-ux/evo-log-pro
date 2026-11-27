'use client';

import React from 'react';
import Link from 'next/link';
import { DeepDomainPage } from '@/lib/deep-crud';
import { RESOURCES } from '@/lib/deep-configs/port-operations';

export default function Page() {
  return (
    <DeepDomainPage
      titre="Port Operations"
      description="Registres CRUD exposes par l'API — donnees reelles."
      backHref="/referentiels"
      backLabel="Référentiels"
      resources={RESOURCES}
    />
  );
}

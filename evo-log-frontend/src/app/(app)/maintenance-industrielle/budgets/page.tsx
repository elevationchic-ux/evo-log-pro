'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBudget } from '@/components/maintenance-industrielle/registres';

export default function PageMaintenanceBudget() {
  return <RegistreGenerique config={registreBudget} />;
}

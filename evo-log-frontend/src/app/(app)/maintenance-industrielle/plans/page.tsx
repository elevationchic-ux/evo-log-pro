'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePlan } from '@/components/maintenance-industrielle/registres';

export default function PageMaintenancePlan() {
  return <RegistreGenerique config={registrePlan} />;
}

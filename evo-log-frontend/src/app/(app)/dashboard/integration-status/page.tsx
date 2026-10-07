'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreIntegrationStatus } from '@/components/dashboard/registres';

export default function PageIntegrationStatus() {
  return <RegistreGenerique config={registreIntegrationStatus} />;
}

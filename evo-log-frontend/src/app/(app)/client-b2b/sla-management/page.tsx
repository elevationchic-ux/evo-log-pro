'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSlaContract } from '@/components/client-b2b/registres';

export default function PageSlaContract() {
  return <RegistreGenerique config={registreSlaContract} />;
}

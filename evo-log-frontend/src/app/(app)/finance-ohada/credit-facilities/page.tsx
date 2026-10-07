'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCreditFacility } from '@/components/finance-ohada/registres';

export default function PageCreditFacility() {
  return <RegistreGenerique config={registreCreditFacility} />;
}

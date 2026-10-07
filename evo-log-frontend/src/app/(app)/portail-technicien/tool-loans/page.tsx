'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechToolLoan } from '@/components/portail-technicien/registres_c';

export default function PageTechToolLoan() {
  return <RegistreGenerique config={registreTechToolLoan} />;
}

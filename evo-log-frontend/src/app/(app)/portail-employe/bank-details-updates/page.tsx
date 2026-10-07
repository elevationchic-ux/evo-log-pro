'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpBankDetailsUpdate } from '@/components/portail-employe/registres_c';

export default function PageEmpBankDetailsUpdate() {
  return <RegistreGenerique config={registreEmpBankDetailsUpdate} />;
}

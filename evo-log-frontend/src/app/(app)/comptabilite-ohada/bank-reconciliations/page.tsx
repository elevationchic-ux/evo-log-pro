'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCmptcBankReconciliation } from '@/components/comptabilite-ohada/registres_c';

export default function PageCmptcBankReconciliation() {
  return <RegistreGenerique config={registreCmptcBankReconciliation} />;
}

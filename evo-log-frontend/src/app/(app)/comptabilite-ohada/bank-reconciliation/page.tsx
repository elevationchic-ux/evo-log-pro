'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBankReconciliation } from '@/components/comptabilite-ohada/registres';

export default function PageBankReconciliation() {
  return <RegistreGenerique config={registreBankReconciliation} />;
}

'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBankGuarantee } from '@/components/finance-ohada/registres';

export default function PageBankGuarantee() {
  return <RegistreGenerique config={registreBankGuarantee} />;
}

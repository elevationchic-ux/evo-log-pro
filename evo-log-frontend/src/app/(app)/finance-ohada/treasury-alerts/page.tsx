'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTreasuryAlert } from '@/components/finance-ohada/registres';

export default function PageTreasuryAlert() {
  return <RegistreGenerique config={registreTreasuryAlert} />;
}

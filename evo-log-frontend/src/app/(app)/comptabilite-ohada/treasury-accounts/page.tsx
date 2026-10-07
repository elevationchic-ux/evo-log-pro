'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTreasuryAccount } from '@/components/comptabilite-ohada/registres';

export default function PageTreasuryAccount() {
  return <RegistreGenerique config={registreTreasuryAccount} />;
}

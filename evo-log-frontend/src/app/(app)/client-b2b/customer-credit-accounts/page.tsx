'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreB2bCCreditAccount } from '@/components/client-b2b/registres_c';

export default function PageB2bCCreditAccount() {
  return <RegistreGenerique config={registreB2bCCreditAccount} />;
}

'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreClientCreditLimit } from '@/components/client-b2b/registres';

export default function PageClientCreditLimit() {
  return <RegistreGenerique config={registreClientCreditLimit} />;
}

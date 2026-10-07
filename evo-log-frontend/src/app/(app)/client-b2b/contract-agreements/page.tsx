'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreB2bCContractAgreement } from '@/components/client-b2b/registres_c';

export default function PageB2bCContractAgreement() {
  return <RegistreGenerique config={registreB2bCContractAgreement} />;
}

'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollContractRenewalRequest } from '@/components/portail-collaborateur/registres_c';

export default function PageCollContractRenewalRequest() {
  return <RegistreGenerique config={registreCollContractRenewalRequest} />;
}

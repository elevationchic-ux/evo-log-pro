'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePricingAgreement } from '@/components/client-b2b/registres';

export default function PagePricingAgreement() {
  return <RegistreGenerique config={registrePricingAgreement} />;
}

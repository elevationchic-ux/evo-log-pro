'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreConsent } from '@/components/tracabilite/registres';

export default function PageConsentGrant() {
  return <RegistreGenerique config={registreConsent} />;
}

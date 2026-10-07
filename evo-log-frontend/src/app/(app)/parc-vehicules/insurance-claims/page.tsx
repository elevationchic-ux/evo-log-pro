'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreInsuranceClaim } from '@/components/parc-vehicules/registres';

export default function PageInsuranceClaim() {
  return <RegistreGenerique config={registreInsuranceClaim} />;
}

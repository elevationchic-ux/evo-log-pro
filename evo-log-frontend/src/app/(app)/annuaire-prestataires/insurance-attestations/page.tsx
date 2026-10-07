'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvInsuranceAttestation } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvInsuranceAttestation() {
  return <RegistreGenerique config={registreProvInsuranceAttestation} />;
}

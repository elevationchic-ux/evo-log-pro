'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspPpeAttestation } from '@/components/portail-qhse/registres_c';

export default function PageQspPpeAttestation() {
  return <RegistreGenerique config={registreQspPpeAttestation} />;
}

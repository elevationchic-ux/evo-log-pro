'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspSafetyObservation } from '@/components/portail-qhse/registres_c';

export default function PageQspSafetyObservation() {
  return <RegistreGenerique config={registreQspSafetyObservation} />;
}

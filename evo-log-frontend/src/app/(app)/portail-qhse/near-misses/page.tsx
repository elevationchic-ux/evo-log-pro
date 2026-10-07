'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspNearMiss } from '@/components/portail-qhse/registres_c';

export default function PageQspNearMiss() {
  return <RegistreGenerique config={registreQspNearMiss} />;
}

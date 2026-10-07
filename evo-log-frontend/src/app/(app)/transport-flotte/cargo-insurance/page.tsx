'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCargoInsurance } from '@/components/transport-flotte/registres';

export default function PageCargoInsurance() {
  return <RegistreGenerique config={registreCargoInsurance} />;
}

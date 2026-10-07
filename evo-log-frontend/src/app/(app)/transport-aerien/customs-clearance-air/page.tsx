'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAirCustomsClearance } from '@/components/transport-aerien/registres_b';

export default function PageAirCustomsClearance() {
  return <RegistreGenerique config={registreAirCustomsClearance} />;
}

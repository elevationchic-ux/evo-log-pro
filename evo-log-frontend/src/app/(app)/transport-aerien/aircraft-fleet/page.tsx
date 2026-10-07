'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAircraft } from '@/components/transport-aerien/registres';

export default function PageAircraft() {
  return <RegistreGenerique config={registreAircraft} />;
}

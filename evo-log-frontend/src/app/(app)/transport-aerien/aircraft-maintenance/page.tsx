'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAircraftCheck } from '@/components/transport-aerien/registres';

export default function PageAircraftCheck() {
  return <RegistreGenerique config={registreAircraftCheck} />;
}

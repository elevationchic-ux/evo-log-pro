'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAirSlot } from '@/components/transport-aerien/registres';

export default function PageAirSlot() {
  return <RegistreGenerique config={registreAirSlot} />;
}

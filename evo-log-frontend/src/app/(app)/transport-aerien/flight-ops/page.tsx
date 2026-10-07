'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFlightOperation } from '@/components/transport-aerien/registres';

export default function PageFlightOperation() {
  return <RegistreGenerique config={registreFlightOperation} />;
}

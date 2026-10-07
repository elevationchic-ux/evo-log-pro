'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreApronMovement } from '@/components/transport-aerien/registres_b';

export default function PageApronMovement() {
  return <RegistreGenerique config={registreApronMovement} />;
}

'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialPosition } from '@/components/transport-fluvial/registres';

export default function PageFluvialPosition() {
  return <RegistreGenerique config={registreFluvialPosition} />;
}

'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialBarge } from '@/components/transport-fluvial/registres';

export default function PageFluvialBarge() {
  return <RegistreGenerique config={registreFluvialBarge} />;
}

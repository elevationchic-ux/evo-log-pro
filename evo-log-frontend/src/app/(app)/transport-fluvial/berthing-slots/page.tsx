'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialBerthingSlot } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialBerthingSlot() {
  return <RegistreGenerique config={registreFluvialBerthingSlot} />;
}

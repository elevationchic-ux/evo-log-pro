'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialTariff } from '@/components/transport-fluvial/registres';

export default function PageFluvialTariff() {
  return <RegistreGenerique config={registreFluvialTariff} />;
}

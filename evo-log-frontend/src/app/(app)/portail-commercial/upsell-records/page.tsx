'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommUpsellRecord } from '@/components/portail-commercial/registres_c';

export default function PageCommUpsellRecord() {
  return <RegistreGenerique config={registreCommUpsellRecord} />;
}

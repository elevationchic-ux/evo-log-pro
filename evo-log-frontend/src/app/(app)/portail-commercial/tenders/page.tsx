'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommTender } from '@/components/portail-commercial/registres_c';

export default function PageCommTender() {
  return <RegistreGenerique config={registreCommTender} />;
}

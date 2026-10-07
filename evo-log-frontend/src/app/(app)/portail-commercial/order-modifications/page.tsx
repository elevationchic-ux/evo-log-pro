'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommOrderModification } from '@/components/portail-commercial/registres_c';

export default function PageCommOrderModification() {
  return <RegistreGenerique config={registreCommOrderModification} />;
}

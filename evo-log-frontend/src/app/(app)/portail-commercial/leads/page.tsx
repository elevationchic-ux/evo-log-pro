'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommLead } from '@/components/portail-commercial/registres_c';

export default function PageCommLead() {
  return <RegistreGenerique config={registreCommLead} />;
}

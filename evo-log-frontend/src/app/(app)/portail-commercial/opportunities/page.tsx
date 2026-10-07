'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommOpportunity } from '@/components/portail-commercial/registres_c';

export default function PageCommOpportunity() {
  return <RegistreGenerique config={registreCommOpportunity} />;
}

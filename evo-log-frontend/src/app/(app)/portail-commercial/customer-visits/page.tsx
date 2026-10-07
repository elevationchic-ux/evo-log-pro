'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommCustomerVisit } from '@/components/portail-commercial/registres_c';

export default function PageCommCustomerVisit() {
  return <RegistreGenerique config={registreCommCustomerVisit} />;
}

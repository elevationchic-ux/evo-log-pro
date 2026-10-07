'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommCustomerComplaint } from '@/components/portail-commercial/registres_c';

export default function PageCommCustomerComplaint() {
  return <RegistreGenerique config={registreCommCustomerComplaint} />;
}

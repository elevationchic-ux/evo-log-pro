'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommCreditRequest } from '@/components/portail-commercial/registres_c';

export default function PageCommCreditRequest() {
  return <RegistreGenerique config={registreCommCreditRequest} />;
}

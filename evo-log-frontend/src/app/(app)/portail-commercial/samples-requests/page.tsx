'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommSampleRequest } from '@/components/portail-commercial/registres_c';

export default function PageCommSampleRequest() {
  return <RegistreGenerique config={registreCommSampleRequest} />;
}

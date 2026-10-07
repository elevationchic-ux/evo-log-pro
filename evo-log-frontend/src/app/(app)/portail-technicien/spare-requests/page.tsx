'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechSpareRequest } from '@/components/portail-technicien/registres_c';

export default function PageTechSpareRequest() {
  return <RegistreGenerique config={registreTechSpareRequest} />;
}

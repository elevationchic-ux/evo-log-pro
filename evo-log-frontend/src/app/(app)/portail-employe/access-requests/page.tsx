'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpAccessRequest } from '@/components/portail-employe/registres_c';

export default function PageEmpAccessRequest() {
  return <RegistreGenerique config={registreEmpAccessRequest} />;
}

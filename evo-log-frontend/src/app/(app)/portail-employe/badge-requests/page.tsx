'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpBadgeRequest } from '@/components/portail-employe/registres_c';

export default function PageEmpBadgeRequest() {
  return <RegistreGenerique config={registreEmpBadgeRequest} />;
}

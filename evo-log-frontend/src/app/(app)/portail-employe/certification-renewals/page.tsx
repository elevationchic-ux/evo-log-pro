'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpCertificationRenewal } from '@/components/portail-employe/registres_c';

export default function PageEmpCertificationRenewal() {
  return <RegistreGenerique config={registreEmpCertificationRenewal} />;
}

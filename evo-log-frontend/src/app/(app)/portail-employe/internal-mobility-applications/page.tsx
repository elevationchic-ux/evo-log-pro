'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpMobilityApplication } from '@/components/portail-employe/registres_c';

export default function PageEmpMobilityApplication() {
  return <RegistreGenerique config={registreEmpMobilityApplication} />;
}

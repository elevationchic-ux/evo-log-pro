'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpPersonalInfoChange } from '@/components/portail-employe/registres_c';

export default function PageEmpPersonalInfoChange() {
  return <RegistreGenerique config={registreEmpPersonalInfoChange} />;
}

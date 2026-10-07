'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpEmergencyContact } from '@/components/portail-employe/registres_c';

export default function PageEmpEmergencyContact() {
  return <RegistreGenerique config={registreEmpEmergencyContact} />;
}

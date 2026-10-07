'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechRepairReport } from '@/components/portail-technicien/registres_c';

export default function PageTechRepairReport() {
  return <RegistreGenerique config={registreTechRepairReport} />;
}

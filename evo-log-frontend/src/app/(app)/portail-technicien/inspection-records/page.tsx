'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechInspectionRecord } from '@/components/portail-technicien/registres_c';

export default function PageTechInspectionRecord() {
  return <RegistreGenerique config={registreTechInspectionRecord} />;
}

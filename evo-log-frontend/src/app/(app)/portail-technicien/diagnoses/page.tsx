'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechDiagnosis } from '@/components/portail-technicien/registres_c';

export default function PageTechDiagnosis() {
  return <RegistreGenerique config={registreTechDiagnosis} />;
}

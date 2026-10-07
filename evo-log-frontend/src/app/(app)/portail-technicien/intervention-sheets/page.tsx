'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechInterventionSheet } from '@/components/portail-technicien/registres_c';

export default function PageTechInterventionSheet() {
  return <RegistreGenerique config={registreTechInterventionSheet} />;
}

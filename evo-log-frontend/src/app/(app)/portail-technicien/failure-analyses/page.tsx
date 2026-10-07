'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechFailureAnalysis } from '@/components/portail-technicien/registres_c';

export default function PageTechFailureAnalysis() {
  return <RegistreGenerique config={registreTechFailureAnalysis} />;
}

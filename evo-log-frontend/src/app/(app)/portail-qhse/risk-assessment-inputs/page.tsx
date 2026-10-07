'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspRiskAssessmentInput } from '@/components/portail-qhse/registres_c';

export default function PageQspRiskAssessmentInput() {
  return <RegistreGenerique config={registreQspRiskAssessmentInput} />;
}

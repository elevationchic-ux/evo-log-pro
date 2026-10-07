'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRiskAssessment } from '@/components/qhse-securite/registres';

export default function PageRiskAssessment() {
  return <RegistreGenerique config={registreRiskAssessment} />;
}

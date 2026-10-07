'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCohortAnalysis } from '@/components/reports-bi/registres';

export default function PageCohortAnalysis() {
  return <RegistreGenerique config={registreCohortAnalysis} />;
}

'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspErgonomicsAssessment } from '@/components/portail-qhse/registres_c';

export default function PageQspErgonomicsAssessment() {
  return <RegistreGenerique config={registreQspErgonomicsAssessment} />;
}

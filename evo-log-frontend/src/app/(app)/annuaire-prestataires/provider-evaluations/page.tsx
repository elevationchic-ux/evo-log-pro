'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvEvaluation } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvEvaluation() {
  return <RegistreGenerique config={registreProvEvaluation} />;
}

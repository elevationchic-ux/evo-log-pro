'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfPpeIssue } from '@/components/portail-chauffeur/registres_c';

export default function PageChfPpeIssue() {
  return <RegistreGenerique config={registreChfPpeIssue} />;
}

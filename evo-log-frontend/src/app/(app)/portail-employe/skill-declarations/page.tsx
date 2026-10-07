'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpSkillDeclaration } from '@/components/portail-employe/registres_c';

export default function PageEmpSkillDeclaration() {
  return <RegistreGenerique config={registreEmpSkillDeclaration} />;
}

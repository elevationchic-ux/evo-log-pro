'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpSicknessDeclaration } from '@/components/portail-employe/registres_c';

export default function PageEmpSicknessDeclaration() {
  return <RegistreGenerique config={registreEmpSicknessDeclaration} />;
}

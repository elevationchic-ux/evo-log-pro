'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfLoadSecuringCheck } from '@/components/portail-chauffeur/registres_c';

export default function PageChfLoadSecuringCheck() {
  return <RegistreGenerique config={registreChfLoadSecuringCheck} />;
}
